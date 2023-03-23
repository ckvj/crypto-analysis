import configparser
from typing import List, Dict, Optional


class Config:
    def __init__(self, path) -> None:
        self.read_config(path)
        self.accounting_type: str
        self.csv_filepath: str
        self.buy_types: List[str]
        self.sell_types: List[str]
        self.col_rename: Dict[str,str]


    def read_config(self, path: str):
        config = configparser.ConfigParser()
        config.read(path)
        self.config = config
        return self
    
    def set_accounting_type(self):
        self.accounting_type = self.config['accounting_type']['accounting_type']
        return self
         
    def set_csv_filepath(self):
        if self.config['file_info'].get('dir', None) == None:
            self.csv_filepath = self.config['file_info']['filename']
        else:
            self.csv_filepath = self.config['file_info']['dir'] + self.config['file_info']['filename']
        
        return self
    
    def set_buy_types(self):
        self.buy_types = [x for x in list(self.config['buy_txn_types'].values())]
        return self
    
    def set_sell_types(self):
         self.sell_types = [x for x in list(self.config['sell_txn_types'].values())]
         return self
         
    def create_col_rename_map(self):
         self.col_rename = {y: x for x, y in self.config['csv_columns'].items()}
         return self