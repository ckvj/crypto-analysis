from typing import List
from cryptotax.trade import Trade


class Asset:
    
    def __init__(self, asset_name, config) -> None:
        self.apply_config(config)
        self.asset_name: str = asset_name
        self.txn_list: List[Trade] = []

    def apply_config(self, config):
        self.analysis_strategy = config.analysis_strategy
        self.buy_types = config.buy_types
        self.sell_types = config.sell_types

    
    def append_trade(self, trade: Trade):
        self.txn_list.append(trade)
        return self
    
    def build_buy_list(self):
        """Generates list of BUY events and orders according to analysis type"""

        buy_txn_list = []

        for trade in self.txn_list:
            if any(buy_type in trade.txn_type for buy_type in self.buy_types):
                buy_txn_list.append(trade)

        if buy_txn_list == []:
            self.buy_txn_list = buy_txn_list
            return
        
        self.buy_txn_list = self.analysis_strategy.sort(buy_txn_list)
        return self

    def build_sell_list(self):
        """Generates list of SELL events and orders chronologically"""

        sell_txn_list = []

        for trade in self.txn_list:
            if any(sell_type in trade.txn_type for sell_type in self.sell_types):
                sell_txn_list.append(trade)

        self.sell_txn_list = sorted(sell_txn_list, key = lambda x : x.epoch_time)

        return self
