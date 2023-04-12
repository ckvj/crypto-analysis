import datetime as dt
from decimal import Decimal
from datetime import timezone
from dateutil import parser

class Trade:
    def __init__(self, row) -> None:

        self._trade_time = parser.parse((row['timestamp']))
        self._txn_type = str(row['txn_type'])
        self._base_asset = str(row['base_asset'])
        self._base_asset_amount = Decimal(row['base_asset_amount'])
        self._quote_asset = str(row['quote_asset'])
        self._quote_asset_amount = Decimal(row['quote_asset_amount'])
        self._epoch_time = self.trade_time.replace(tzinfo=timezone.utc).timestamp()
        self._remaining = self.base_asset_amount
        self._price = float(self.quote_asset_amount) / float(self.base_asset_amount)

    # Enable Getters. Only attribute with a setter is 'remaining' because it is updated throughout processing
    @property
    def trade_time(self):
        return self._trade_time

    @property
    def txn_type(self):
        return self._txn_type

    @property
    def base_asset(self):
        return self._base_asset
    
    @property
    def base_asset_amount(self):
        return self._base_asset_amount
    
    @property
    def quote_asset(self):
        return self._quote_asset

    @property
    def quote_asset_amount(self):
        return self._quote_asset_amount
    
    @property
    def epoch_time(self):
        return self._epoch_time
    
    @property
    def remaining(self):
        return self._remaining
    
    @remaining.setter
    def remaining(self, value):
        self._remaining = Decimal(value)
    
    @property
    def price(self) -> float:
        return self._price

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