import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List
from datetime import timezone

import pandas as pd
from dateutil import relativedelta

from config import process_config
from import_csv import import_csv_as_df


class Sales():

    def __init__(self) -> None:
        self.trades = self.create_trades_csv()
        self.sale_list = self.create_sale_list()
        self.annual_summary = self.create_sale_summary()
        
    
    def create_trades_csv(self):
        _config_dict, _col_dtypes, _converter = process_config()

        self._config_dict = _config_dict # Store for later use

        raw_csv = import_csv_as_df(
            filename = _config_dict['file_info']['filename'],
            dir = _config_dict['file_info']['dir'],
            index_col_name = _config_dict['csv_columns']['timestamp'],
            index_rename = 'timestamp',
            index_is_datetime = True,
            converter = _converter,
            column_types = _col_dtypes,
            column_rename = _config_dict['csv_columns'])
        
        return raw_csv
    

    def create_sale_list(self):
            
            unprocessed_trades = self.populate_trades(self.trades)
            
            sale_list = self.process_trades(unprocessed_trades, self._config_dict['accounting_type']['accounting_type'], self._config_dict['buy_types_list'], self._config_dict['sell_types_list'])

            return sale_list
    
    
    def populate_trades(self, raw_csv: pd.DataFrame) -> dict:
        
        @dataclass
        class Trade:
            trade_time: datetime
            txn_type: str
            base_asset: str
            base_asset_amount: Decimal
            quote_asset: str
            quote_asset_amount: float

            def __post_init__(self):
                self.epoch_time = self.trade_time.replace(tzinfo=timezone.utc).timestamp()
                self.remaining = self.base_asset_amount
                self.price = self.quote_asset_amount / float(self.base_asset_amount)
        
        
        unprocessed_trades: Dict[str, List[Trade]] = {}

        for index, row in self.trades.iterrows():

            trade = Trade(index.to_pydatetime(), row['txn_type'], row['base_asset'], row['base_asset_amount'], row['quote_asset'],row['quote_asset_amount'])

            if unprocessed_trades.get(trade.base_asset) == None:
                unprocessed_trades[trade.base_asset] = [trade]
                continue
            
            unprocessed_trades[trade.base_asset].append(trade)
        return unprocessed_trades
    
    @staticmethod
    def is_long_term_gain(buy_date: datetime, sell_date: datetime) -> bool:
        time_delta = relativedelta.relativedelta(sell_date, buy_date)

        if time_delta.years >= 1:
            long_term = True
        elif time_delta.years < 1:
            long_term = False
        
        return long_term
        
        
    @staticmethod
    def build_row(buy, sale, size: float, gain_loss: float, long_term: bool) -> pd.DataFrame:


        row = pd.DataFrame([{'BaseAsset' : sale.base_asset, 'QuoteAsset' : sale.quote_asset, 'BuyDate' : buy.trade_time, 'SellDate' : sale.trade_time, 'Amount' : size, 'BuyPrice' : buy.price, 'SellPrice' : sale.price, 'Gain/Loss' : gain_loss, 'Long-Term' : long_term, 'SellYear' : sale.trade_time.year}])
        
        return row

    
    def build_buy_list(self, trades, analysis_type: str, buy_types: List[str]):
        """Generates list of BUY events and orders according to analysis type"""

        buy_txn_list = []

        for trade in trades:
            if any(buy_type in trade.txn_type for buy_type in buy_types):
                buy_txn_list.append(trade)

            
        if buy_txn_list == []:
            print('Error: No Buy events for ', trades[0].base_asset)
            return buy_txn_list
        
        if analysis_type == 'FIFO':
            buy_txn_list = sorted(buy_txn_list, key = lambda x : x.epoch_time)
        elif analysis_type == 'LIFO':
            buy_txn_list = sorted(buy_txn_list, key = lambda x : x.epoch_time, reverse=True)
        elif analysis_type == 'HIFO':
            buy_txn_list = sorted(buy_txn_list, key = lambda x : x.price, reverse=True)
        
        return buy_txn_list

    
    def build_sell_list(self, trades, sell_types: List[str]):
        """Generates list of SELL events and orders chronologically"""

        sell_txn_list = []

        for trade in trades:
            if any(sell_type in trade.txn_type for sell_type in sell_types):
                sell_txn_list.append(trade)

        sell_txn_list = sorted(sell_txn_list, key = lambda x : x.epoch_time)

        return sell_txn_list


    def process_trades(self, unprocessed_trades: pd.DataFrame, analysis_type: str, buy_types: List[str], sell_types: List[str]) -> pd.DataFrame:
        """Returns log of sale events given dictionary of unprocessed trades
        
        Args:
            unprocessed_trades: dictionary of {'asset' : List[Trades]}
            analysis_type: HIFO, LIFO, or FIFO
            buy_types: List of strings that equal buy transaction types (eg BUY, AIRDROP)
            sell_types: List of strings that equal buy transaction types (eg SELL, PURCHASE)
        
        Returns:
            sale_log: List of Sale events, including gain-loss per sale 

        """


        sale_log = pd.DataFrame()

        for asset_name, txn_list in unprocessed_trades.items():

            cap_gain_loss = 0
            overall_gain_loss = 0

            # Create Buy List
            buy_txn_list = self.build_buy_list(txn_list, analysis_type, buy_types)

            # Create Sell List
            sell_txn_list = self.build_sell_list(txn_list, sell_types)
            
            if not sell_txn_list: # Continue to next asset if no sales
                continue
            
            dust_threshold = 0.00001 # Used for rounding errors

            for sale_ind, sale in enumerate(sell_txn_list):
                while sale.remaining > 0:
                    for buy in buy_txn_list:
                        if (buy.epoch_time <= sale.epoch_time) & (buy.remaining > 0):

                            if buy.epoch_time == sale.epoch_time:
                                raise Exception ('WARNING: Trade Buy Time == Sell Time')

                            clip_size = min(buy.remaining, sale.remaining)
                            cap_gain_loss = float(clip_size) * (sale.price - buy.price)

                            is_long_term = Sales.is_long_term_gain(buy.trade_time, sale.trade_time)

                            
                            # Log Sale
                            row = Sales.build_row(buy, sale, clip_size, cap_gain_loss, is_long_term)
                            sale_log = pd.concat([sale_log, row])

                            # Cleanup & Increment
                            buy.remaining -= clip_size
                            sale.remaining -= clip_size
                            overall_gain_loss += cap_gain_loss
                            
                            if sale.remaining < dust_threshold:
                                break
                                
                    # End Loop if Sales are complete
                    if (sale.remaining < dust_threshold) & (sale_ind == len(sell_txn_list)-1):
                        break
        
        sale_log.reset_index(inplace=True, drop = True)
        sale_log.index.name = 'Txn'
        return sale_log

    
    def create_sale_summary(self) -> pd.DataFrame:
        """Returns annual summary of sale_list"""
        
        sale_log = self.sale_list

        unique_assets = sale_log['BaseAsset'].unique()
        year_list = sale_log['SellYear'].unique()
        annual_summary = pd.DataFrame(columns = year_list, index=unique_assets)
        annual_summary.index.name = 'BaseAsset'

        for year in year_list:
            df = sale_log[sale_log['SellYear'] == year]
            for asset in unique_assets:
                small_df = df.loc[df['BaseAsset'] == asset]
                sum = small_df['Gain/Loss'].sum()
                annual_summary.at[asset, year] = sum
            
        annual_summary.loc['Total'] = annual_summary.sum()    
            
        return annual_summary
    
