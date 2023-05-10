from typing import List
from .trade import Trade
from .analysis_strategies import AnalysisStrategy


class Asset:
    
    def __init__(self, asset_name, config) -> None:
        self.asset_name: str = asset_name
        
        # Apply Config
        self.analysis_strategy: AnalysisStrategy = config.analysis_strategy
        self.buy_types: List[str] = config.buy_types
        self.sell_types: List[str] = config.sell_types
        
        self.txn_list: List[Trade] = []
        self.buy_txn_list: List[str] = []
        self.sell_txn_list: List[str] = []


    def append_trade(self, trade: Trade):
        self.txn_list.append(trade)
        return self
    

    def build_buy_list(self):
        """Generates list of BUY events and orders according to analysis type"""

        for trade in self.txn_list:
            if any(buy_type in trade.txn_type for buy_type in self.buy_types):
                self.buy_txn_list.append(trade)
        
        self.buy_txn_list = self.analysis_strategy.sort(self.buy_txn_list)
        return


    def build_sell_list(self):
        """Generates list of SELL events and orders chronologically"""

        for trade in self.txn_list:
            if any(sell_type in trade.txn_type for sell_type in self.sell_types):
                self.sell_txn_list.append(trade)

        self.sell_txn_list = sorted(self.sell_txn_list, key = lambda x : x.epoch_time)
        return
