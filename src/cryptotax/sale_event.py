import pandas as pd
from dateutil import relativedelta
from cryptotax.trade import Trade
from decimal import Decimal


class SaleEvent:
    def __init__(self, purchase, sale):
        self.purchase = purchase
        self.sale = sale
        self.clip_size: Decimal = min(
            self.purchase.remaining, self.sale.remaining)
        self.gain_loss: float = float(
            self.clip_size) * (self.sale.price - self.purchase.price)
        self.long_term: bool

    @property
    def long_term(self):
        time_delta = relativedelta.relativedelta(
            self.sale.trade_time, self.purchase.trade_time)
        return time_delta.years >= 1

    @property
    def sale_row(self) -> dict:

        row = {
            'BaseAsset': self.sale.base_asset,
            'QuoteAsset': self.sale.quote_asset,
            'BuyDate': self.purchase.trade_time,
            'BuyPrice': self.purchase.price,
            'SellDate': self.sale.trade_time,
            'SellPrice': self.sale.price,
            'Amount': self.clip_size,
            'Gain/Loss': self.gain_loss,
            'Long-Term': self.long_term,
            'SellYear': self.sale.trade_time.year
        }

        return row
