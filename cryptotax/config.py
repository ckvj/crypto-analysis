import configparser
from typing import List, Dict, Optional
from cryptotax.asset import FifoStrategy, LifoStrategy, HifoStrategy

class Config:
    def __init__(self, path) -> None:
        self.config = self.read_config(path)

    def read_config(self, path: str):
        config = configparser.ConfigParser()
        config.read(path)
        return config
    
    @property
    def analysis_strategy(self):
        type =  self.config['accounting_type']['accounting_type']
        if type == 'FIFO':
            return FifoStrategy()
        elif type == 'LIFO':
            return LifoStrategy()
        elif type == 'HIFO':
            return HifoStrategy()
        else:
            raise ValueError ('Invalid analysis type. Use FIFO, LIFO, or HIFO')
    
    
    @property     
    def csv_filepath(self):
        
        if self.config['file_info'].get('dir', None) == None:
            return self.config['file_info']['filename']
        else:
            return self.config['file_info']['dir'] + self.config['file_info']['filename']
    
    @property
    def buy_types(self):
        return [ _ for _ in list(self.config['buy_txn_types'].values())]
        
    @property
    def sell_types(self):
        return [ _ for _ in list(self.config['sell_txn_types'].values())]

    @property     
    def col_rename_map(self):
        return {val: key for key, val in self.config['csv_columns'].items()}