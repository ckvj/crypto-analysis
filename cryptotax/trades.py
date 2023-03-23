import csv

from typing import Dict, List

from cryptotax.config import Config
from cryptotax.trade import Trade, TradeBuilder
from cryptotax.asset import Asset

class Trades:
    
    config_file_path = 'config.ini' # Set default config file path (same dir)
    
    def __init__(self, path = config_file_path) -> None:
        config = Config(path). \
            set_accounting_type(). \
            set_csv_filepath(). \
            set_buy_types().\
            set_sell_types().\
            create_col_rename_map()
        
        Asset.apply_config(config)
        self.import_trades(config)
        self.group_trades()

    def import_trades(self, config: Config):
        """Import trades based on config"""

        def rename_col(col: str, rename_map: Dict[str,str]) -> str:
            """Small helped function to convert user-input column name to program-compatible name"""
            for key, value in rename_map.items():
                if col == key:
                    col = value
                    break
            return col
        
        trades: List[Trade] = []
        with open(config.csv_filepath, newline='') as csvfile:
            
            reader = csv.DictReader(csvfile)
            reader.fieldnames = [rename_col(col, config.col_rename) for col in reader.fieldnames]

            for row in reader:
                
                trade = TradeBuilder(). \
                    set_trade_time(row['timestamp']). \
                    set_txn_type(row['txn_type']). \
                    set_base_asset(row['base_asset']). \
                    set_base_asset_amount(row['base_asset_amount']). \
                    set_quote_asset(row['quote_asset']). \
                    set_quote_asset_amount(row['quote_asset_amount']). \
                    build_trade()
                
                trades.append(trade)

        self.trades = trades
        return self
    

    def group_trades(self):
        """Group list of trades by asset"""

        grouped_trades: Dict[str, Asset] = {}
        
        for trade in self.trades:
            if grouped_trades.get(trade.base_asset, None) == None:
                grouped_trades[trade.base_asset] = Asset(trade.base_asset).append_trade(trade)
            else:
                grouped_trades[trade.base_asset].append_trade(trade)
        
        self.grouped_trades = grouped_trades
        return self


