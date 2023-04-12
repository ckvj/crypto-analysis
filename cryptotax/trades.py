import csv

from typing import Dict, List

from cryptotax.config import Config
from cryptotax.trade import Trade
from cryptotax.asset import Asset

class Trades:
    
    config_file_path = 'config.ini' # Default config file path (same dir)
    
    def __init__(self, path = config_file_path) -> None:
        self.config = Config(path)

        self.trades: Dict[str, Asset] = {}
        self.import_trades(self.config)
        
    def import_trades(self, config: Config):
        """Import trades based on config"""

        Asset.apply_config(self.config) # Apply configuration to Asset Class

        with open(config.csv_filepath, newline='') as csvfile:
            
            reader = csv.DictReader(csvfile)
            reader.fieldnames = [Trades.rename_col(col, config.col_rename_map) for col in reader.fieldnames]

            for row in reader:
                trade = Trade(row)

                # Initialize Asset if needed and append trade
                if self.trades.get(trade.base_asset) == None: #TODO Error when I remove
                    self.trades[trade.base_asset] = Asset(trade.base_asset).append_trade(trade)
                else:
                    self.trades[trade.base_asset].append_trade(trade)
        return
    
    @staticmethod
    def rename_col(col: str, rename_map: Dict[str,str]) -> str:
        """Helper function to convert user-input column name to program-compatible name"""
        for key, value in rename_map.items():
            if col == key:
                col = value
                break
        return col


