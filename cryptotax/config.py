import configparser
from typing import List, Dict
from cryptotax import analysis_strategies
from cryptotax.analysis_strategies import AnalysisStrategy

class Config:
    def __init__(self, path) -> None:
        self.config = self.read_config(path)
        
        self.analysis_strategy: AnalysisStrategy
        self.csv_filepath: str
        self.buy_types: List[str]
        self.sell_types: List[str]
        self.col_rename_map: Dict[str,str]
        
        # Cache
        self._analysis_strategy = None
        self._csv_filepath = None
        self._buy_types = None
        self._sell_types = None
        self._col_rename_map = None
        

    def read_config(self, path: str):
        config = configparser.ConfigParser()
        config.read(path)
        return config
    

    @property
    def analysis_strategy(self):
        if not self._analysis_strategy:
            type =  self.config['accounting_type']['accounting_type']
            self._analysis_strategy = getattr(analysis_strategies, f"{type.title()}Strategy")()
        return self._analysis_strategy
    
    
    @property     
    def csv_filepath(self) -> str:
        if not self._csv_filepath:
            if self.config['file_info'].get('dir', None) == None:
                self._csv_filepath = self.config['file_info']['filename']
            else:
                self._csv_filepath = self.config['file_info']['dir'] + self.config['file_info']['filename']
        return self._csv_filepath
        
    

    @property
    def buy_types(self) -> List[str]:
        if not self._buy_types:
            self._buy_types = [ _ for _ in list(self.config['buy_txn_types'].values())]
        return  self._buy_types
        

    @property
    def sell_types(self) -> List[str]:
        if not self._sell_types:
            self._sell_types = [ _ for _ in list(self.config['sell_txn_types'].values())]
        return self._sell_types


    @property     
    def col_rename_map(self) -> Dict[str,str]:
        if not self._col_rename_map:
            self._col_rename_map = {val: key for key, val in self.config['csv_columns'].items()}
        return self._col_rename_map