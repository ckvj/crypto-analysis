import datetime
from decimal import Decimal
from dataclasses import dataclass
from typing import Dict, List, Optional
import csv
import copy

from cryptotax.trade import TradeBuilder, Trade


def import_trades(_config_dict):
    """pass"""
    
    def rename_col(col, rename_map: Dict[str,str]):
        for key, value in rename_map.items():
            if col == key:
                col = value
                break
        return col


    trades: List[Trade] = []
    with open(_config_dict['file_path'], newline='') as csvfile:
        
        reader = csv.DictReader(csvfile)
        reader.fieldnames = [rename_col(col, _config_dict['col_rename']) for col in reader.fieldnames]

        for row in reader:
            
            trade = TradeBuilder(). \
                set_trade_time(row['timestamp']). \
                set_txn_type(row['txn_type']). \
                set_base_asset(row['base_asset']). \
                set_base_asset_amount(row['base_asset_amount']). \
                set_quote_asset(row['quote_asset']). \
                set_quote_asset_amount(row['quote_asset_amount']). \
                build_trade()
            
            trades.append(copy.deepcopy(trade))

    return trades
