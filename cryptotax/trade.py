import datetime as dt
from decimal import Decimal
from datetime import timezone
from dateutil import parser

class Trade:
    def __init__(self) -> None:
        self.trade_time: dt = None
        self.txn_type: str = None
        self.base_asset: str = None
        self.base_asset_amount: Decimal = None
        self.quote_asset: str = None
        self.quote_asset_amount: float = None

        # Assigned in TradeBuilder.build_trade method. References above required values.
        self.epoch_time: dt = None
        self.remaining: Decimal = None
        self.price: float = None
    
    def __str__(self) -> str:
        print(f"trade_time: {self.trade_time}\n\
            txn_type: {self.txn_type}\n\
            base_asset: {self.base_asset}\n\
            base_asset_amount: {self.base_asset_amount}\n\
            quote_asset: {self.quote_asset}\n\
            quote_asset_amount: {self.quote_asset_amount}\n\
            epoch_time: {self.epoch_time}\n\
            remaining: {self.remaining}\n\
            price: {self.price}")



class TradeBuilder:
    def __init__(self, trade=Trade()):
        self.trade = trade
    
    def set_trade_time(self, timestamp):
        self.trade.trade_time = parser.parse(timestamp)
        return self

    def set_txn_type(self, txn_type):
        self.trade.txn_type = str(txn_type)
        return self

    def set_base_asset(self,base_asset):
        self.trade.base_asset = str(base_asset)
        return self
    
    def set_base_asset_amount(self,base_asset_amount):
        self.trade.base_asset_amount = Decimal(base_asset_amount)
        return self
    
    def set_quote_asset(self, quote_asset):
        self.trade.quote_asset = str(quote_asset)
        return self
    
    def set_quote_asset_amount(self, quote_asset_amount):
        self.trade.quote_asset_amount = Decimal(quote_asset_amount)
        return self
    
    def set_user_txn_id(self, user_txn_id):
        self.trade.user_txn_id = str(user_txn_id)
        return self

    def build_trade(self):
        self.trade.epoch_time = self.trade.trade_time.replace(tzinfo=timezone.utc).timestamp()
        self.trade.remaining = self.trade.base_asset_amount
        self.trade.price = float(self.trade.quote_asset_amount) / float(self.trade.base_asset_amount)
        
        return self.trade

    






# class Trade:
#     trade_time: datetime
#     txn_type: str
#     base_asset: str
#     base_asset_amount: Decimal
#     quote_asset: str
#     quote_asset_amount: float
#     user_txn_id: Optional[str]

#     def __post_init__(self):
#         self.epoch_time = self.trade_time.replace(tzinfo=timezone.utc).timestamp()
#         self.remaining = self.base_asset_amount
    
    
# class Trades:
#     def __init__(self) -> None:
#         pass