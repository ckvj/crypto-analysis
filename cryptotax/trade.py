import datetime as dt
from decimal import Decimal
from datetime import timezone
from dateutil import parser

class Trade:
    def __init__(self, row) -> None:

        self.trade_time = parser.parse((row['timestamp']))
        self.txn_type: str = str(row['txn_type'])
        self.base_asset: str = str(row['base_asset'])
        self.base_asset_amount: Decimal = Decimal(row['base_asset_amount'])
        self.quote_asset: str = str(row['quote_asset'])
        self.quote_asset_amount: Decimal = Decimal(row['quote_asset_amount'])
        self.epoch_time: float = float(self.trade_time.replace(tzinfo=timezone.utc).timestamp())
        self.remaining: Decimal = self.base_asset_amount
        self.price: float = float(self.quote_asset_amount) / float(self.base_asset_amount)


    def __str__(self) -> str:
        return f"trade_time: {self.trade_time}\n\
            txn_type: {self.txn_type}\n\
            base_asset: {self.base_asset}\n\
            base_asset_amount: {self.base_asset_amount}\n\
            quote_asset: {self.quote_asset}\n\
            quote_asset_amount: {self.quote_asset_amount}\n\
            epoch_time: {self.epoch_time}\n\
            remaining: {self.remaining}\n\
            price: {self.price}"