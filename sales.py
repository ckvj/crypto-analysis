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

    dust_threshold = 0.00001 # Used for rounding errors

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
            index_is_datetime = True,
            converter = _converter,
            column_types = _col_dtypes,
            _headers = _config_dict['csv_columns'])
        
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
            base_amount: Decimal
            usd_amount: float

            def __post_init__(self):
                self.epoch_time = self.trade_time.replace(tzinfo=timezone.utc).timestamp()
                self.remaining = self.base_amount
                self.price = self.usd_amount / float(self.base_amount)
        
        
        unprocessed_trades: Dict[str, List[Trade]] = {}

        for index, row in self.trades.iterrows():

            trade = Trade(index.to_pydatetime(), row['txn_type'], row['base_asset'], row['base_asset_amount'], row['quote_asset_amount'])

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
            print('Long Term Trade!')
        elif time_delta.years < 1:
            long_term = False
        
        return long_term
        
        
    @staticmethod
    def build_row(asset: str, buy_date: datetime, sell_date: datetime, size, buy_price: float, sell_price: float, gain_loss: float, long_term: bool) -> pd.DataFrame:

        row = pd.DataFrame([{'Asset' : asset, 'BuyDate' : buy_date, 'SellDate' : sell_date, 'Amount' : size, 'BuyPrice' : buy_price, 'SellPrice' : sell_price, 'gain-loss' : gain_loss, 'long-term' : long_term, 'Sell Year' : sell_date.year}])
        
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
        sell_txn_list = []

        for trade in trades:
            if any(sell_type in trade.txn_type for sell_type in sell_types):
                sell_txn_list.append(trade)

        sell_txn_list = sorted(sell_txn_list, key = lambda x : x.epoch_time)

        return sell_txn_list


    def process_trades(self, unprocessed_trades: pd.DataFrame, analysis_type: str, buy_types: List[str], sell_types: List[str]) -> pd.DataFrame:

        sale_log = pd.DataFrame()

        for asset_name, txn_list in unprocessed_trades.items():

            cap_gain_loss = 0
            overall_gain_loss = 0

            # Create Buy List
            buy_txn_list = self.build_buy_list(txn_list, analysis_type, buy_types)

            # Create Sell List
            sell_txn_list = self.build_sell_list(txn_list, sell_types)
            
            if not sell_txn_list: # Continue if no Sales
                continue
            
            dust_threshold = Sales.dust_threshold

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
                            row = Sales.build_row(sale.base_asset, buy.trade_time, sale.trade_time, clip_size, buy.price, sale.price, cap_gain_loss, is_long_term)
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
        
        return sale_log

    
    def create_sale_summary(self) -> pd.DataFrame:
        
        sale_log = self.sale_list

        unique_assets = sale_log['Asset'].unique()
        year_list = sale_log['Sell Year'].unique()
        annual_summary = pd.DataFrame(columns = year_list, index=unique_assets)

        for year in year_list:
            df = sale_log[sale_log['Sell Year'] == year]
            for asset in unique_assets:
                small_df = df.loc[df['Asset'] == asset]
                sum = small_df['gain-loss'].sum()
                annual_summary.at[asset, year] = sum
            
        annual_summary.loc['Total'] = annual_summary.sum()    
            
        return annual_summary
    
