from typing import List
from cryptotax.trade import Trade


class Asset:
    def __init__(self, asset_name) -> None:
        self.asset_name: str = asset_name
        self.txn_list: List[Trade] = []

    @classmethod
    def apply_config(cls, config):
        cls.analysis_type = config.accounting_type
        cls.buy_types = config.buy_types
        cls.sell_types = config.sell_types

    def append_trade(self, trade: Trade):
        self.txn_list.append(trade)
        # return self

    def build_buy_list(self):
        """Generates list of BUY events and orders according to analysis type"""

        buy_txn_list = []

        for trade in self.txn_list:
            if any(buy_type in trade.txn_type for buy_type in self.buy_types):
                buy_txn_list.append(trade)

        if buy_txn_list == []:
            self.buy_txn_list = buy_txn_list
            return

        if self.analysis_type == "FIFO":
            buy_txn_list = sorted(buy_txn_list, key=lambda x: x.epoch_time)
        elif self.analysis_type == "LIFO":
            buy_txn_list = sorted(
                buy_txn_list, key=lambda x: x.epoch_time, reverse=True
            )
        elif self.analysis_type == "HIFO":
            buy_txn_list = sorted(buy_txn_list, key=lambda x: x.price, reverse=True)

        self.buy_txn_list = buy_txn_list
        return 

    def build_sell_list(self):
        """Generates list of SELL events and orders chronologically"""

        sell_txn_list = []

        for trade in self.txn_list:
            if any(sell_type in trade.txn_type for sell_type in self.sell_types):
                sell_txn_list.append(trade)

        self.sell_txn_list = sorted(sell_txn_list, key=lambda x: x.epoch_time)

        return self
