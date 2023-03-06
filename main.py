
import configparser
import datetime
from dataclasses import dataclass
from datetime import timezone
from decimal import Decimal

import pandas as pd
from dateutil import relativedelta

from typing import Dict, List, Any, Optional

def process_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    config_dict = {s:dict(config.items(s)) for s in config.sections()}
    
    # Add dir as None if not provided
    if config_dict['file_info'].get('dir', None) == None:
        config_dict['file_info']['dir'] = None
    
    # Column DTypes
    _column_dtypes = {config_dict['csv_columns']['price_paid'] : float, config_dict['csv_columns']['quote_asset_amount'] : float}
    _converter = {config_dict['csv_columns']['base_asset_amount'] : Decimal}
    
    # Data Validations
    _supported_accounting_types = ['FIFO', 'LIFO', 'HIFO']
    if config_dict['accounting_type']['accounting_type'] not in _supported_accounting_types:
        raise ValueError('Unsupported Analysis Type')
    
    # Buy List
    config_dict['buy_types_list'] = [x for x in list(config_dict['buy_txn_types'].values())]

    # Sell List
    config_dict['sell_types_list'] = [x for x in list(config_dict['sell_txn_types'].values())]

    return config_dict, _column_dtypes, _converter


def import_csv_as_df(filename: str, dir: Optional[str] = None, index_col_name: Optional[str] = None, index_is_datetime: bool = False, converter: Optional[Dict[str, Any]] = None, column_types: Optional[Dict[str, Any]] = None, _headers: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """ Imports CSV as dataframe. Enables user to specify which column to make index and if type is datetime.
    
    Args:
        filename: Filename of the CSV
        dir: Directory of the CSV
        index_name: Name of column to make index
        index_is_datetime: Optional set index to datetime
        converter: specify dictionary for {column name : converter function}
        column_type: specify dictionary of {column name : dtype}. Uses ',' as thousands seperator
        _headers: provide dictionary of renamed values
        
    Returns:
        df: Dataframe of CSV  
    """
    
    # Build filepath
    if dir == None:
        path = filename
    else:
        path = dir + filename

    # Import CSV
    df = pd.read_csv(path, index_col = index_col_name, converters = converter, dtype=column_types, thousands=',')

    # Update Index
    df.index.name = 'timestamp'
    if index_is_datetime == True:
        df.index = pd.to_datetime(df.index)   
        
    # Rename Columns
    column_rename = {y: x for x, y in _headers.items()}
    df = df.rename(columns = column_rename)
    
    return df


def populate_trades(raw_csv: pd.DataFrame) -> dict:
    
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

    for index, row in raw_csv.iterrows():

        trade = Trade(index.to_pydatetime(), row['txn_type'], row['base_asset'], row['base_asset_amount'], row['quote_asset_amount'])

        if unprocessed_trades.get(trade.base_asset) == None:
            unprocessed_trades[trade.base_asset] = [trade]
            continue
        
        unprocessed_trades[trade.base_asset].append(trade)
    return unprocessed_trades
 

def is_long_term_gain(buy_date: datetime, sell_date: datetime) -> bool:
    time_delta = relativedelta.relativedelta(sell_date, buy_date)

    if time_delta.years >= 1:
        long_term = True
        print('Long Term Trade!')
    elif time_delta.years < 1:
        long_term = False
    
    return long_term
    

def build_row(asset: str, buy_date: datetime, sell_date: datetime, size, buy_price: float, sell_price: float, gain_loss: float, long_term: bool) -> pd.DataFrame:
    row = pd.DataFrame([{'Asset' : asset, 'BuyDate' : buy_date, 'SellDate' : sell_date, 'Amount' : size, 'BuyPrice' : buy_price, 'SellPrice' : sell_price, 'gain-loss' : gain_loss, 'long-term' : long_term}])
    return row


def build_buy_list(trades, analysis_type: str, buy_types: List[str]):
    """Generates list of BUY events and orders according to analysis type"""
    buy_txn_list = []

    for trade in trades:
        for buy_type in buy_types:
            if buy_type in trade.txn_type:
                buy_txn_list.append(trade)
                break
        
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
        
def build_sell_list(trades, sell_types: List[str]):
    sell_txn_list = []

    for trade in trades:
        for sell_type in sell_types:
            if sell_type in trade.txn_type:
                sell_txn_list.append(trade)
                break

    sell_txn_list = sorted(sell_txn_list, key = lambda x : x.epoch_time)

    return sell_txn_list


def process_trades(unprocessed_trades: pd.DataFrame, analysis_type: str, buy_types: List[str], sell_types: List[str]) -> pd.DataFrame:

    sale_log = pd.DataFrame()

    dust_threshold = 0.00001

    for asset_name, txn_list in unprocessed_trades.items():

        cap_gain_loss = 0
        overall_gain_loss = 0

        # Create Buy List
        buy_txn_list = build_buy_list(txn_list, analysis_type, buy_types)

        # Create Sell List
        sell_txn_list = build_sell_list(txn_list, sell_types)
        
        if not sell_txn_list:
            print(f'{asset_name}: No Sales')
            continue

        for sale_ind, sale in enumerate(sell_txn_list):
            while sale.remaining > 0:
                for buy in buy_txn_list:
                    if (buy.epoch_time <= sale.epoch_time) & (buy.remaining > 0):

                        if buy.epoch_time == sale.epoch_time:
                            raise Exception ('WARNING: Trade Buy Time == Sell Time')

                        clip_size = min(buy.remaining, sale.remaining)
                        cap_gain_loss = float(clip_size) * (sale.price - buy.price)

                        is_long_term = is_long_term_gain(buy.trade_time, sale.trade_time)

                        # Log Sale
                        row = build_row(sale.base_asset, buy.trade_time, sale.trade_time, clip_size, buy.price, sale.price, cap_gain_loss, is_long_term)
                        sale_log = pd.concat([sale_log, row])

                        # Cleanup & Increment
                        buy.remaining -= clip_size
                        sale.remaining -= clip_size
                        overall_gain_loss += cap_gain_loss
                        
                        if sale.remaining < dust_threshold:
                            break
                            
                # End Loop if Sales are complete
                if (sale.remaining < dust_threshold) & (sale_ind == len(sell_txn_list)-1):
                    print(f'{asset_name}: Analyzed {sale_ind + 1} of {len(sell_txn_list)} Sales. Overall Cap Gain/Loss is {overall_gain_loss}')
                    break
        
    return sale_log

def process_sale_log(sale_log: pd.DataFrame) -> pd.DataFrame:
    def get_year(row):
        return row['SellDate'].year

    sale_log['Year'] = sale_log.apply(get_year, axis = 1)

    unique_assets = sale_log['Asset'].unique()

    year_list = sale_log['Year'].unique()
    sale_summary = pd.DataFrame(columns = year_list, index=unique_assets)

    for year in year_list:
        df = sale_log[sale_log['Year'] == year]
        for asset in unique_assets:
            small_df = df.loc[df['Asset'] == asset]
            sum = small_df['gain-loss'].sum()
            sale_summary.at[asset, year] = sum
        print(sale_summary[year].sum())
        
    return sale_summary

def main():
    
    config_dict, _col_dtypes, _converter = process_config()


    raw_csv = import_csv_as_df(
        filename = config_dict['file_info']['filename'],
        dir = config_dict['file_info']['dir'],
        index_col_name = config_dict['csv_columns']['timestamp'],
        index_is_datetime = True,
        converter = _converter,
        column_types = _col_dtypes,
        _headers = config_dict['csv_columns'])

    
    trades = populate_trades(raw_csv)
    sale_log = process_trades(trades, config_dict['accounting_type']['accounting_type'], config_dict['buy_types_list'], config_dict['sell_types_list'])
    sale_summary = process_sale_log(sale_log)
    
    print(sale_log.to_markdown())
    print(sale_summary.to_markdown())

if __name__ == "__main__":
    main()