import csv

from typing import Dict, List

from .config import Config
from .trade import Trade
from .asset import Asset

class Trades:
    """ Imports trades based on config file

    Args:
        config_filepath: Filepath to INI config file
    """
    
    def __init__(self, config_filepath) -> None:
        self.config = Config(config_filepath)
        self.trades: Dict[str, Asset] = {}
        self.import_trades()
        
    def import_trades(self):

        with open(self.config.csv_filepath, newline='') as csvfile:
            
            reader = csv.DictReader(csvfile)
            reader.fieldnames = [Trades.rename_col(col, self.config.col_rename_map) for col in reader.fieldnames]

            for row in reader:
                trade = Trade(row)

                # Initialize Asset if needed and append trade
                if self.trades.get(trade.base_asset) == None:
                    self.trades[trade.base_asset] = Asset(trade.base_asset, self.config).append_trade(trade)
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


