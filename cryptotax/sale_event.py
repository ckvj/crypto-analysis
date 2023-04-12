import pandas as pd
from dateutil import relativedelta
from cryptotax.trade import Trade
from decimal import Decimal

class SaleEvent:
    def __init__(self, purchase, sale):        
        self.purchase = purchase
        self.sale = sale
        self._clip_size: Decimal
        self._gain_loss: float
        self._long_term: bool
        self.set_clip_size()

    
    @property
    def clip_size(self):
        return self._clip_size
    
    def set_clip_size(self) -> Decimal: # Couldn't use @clipsize.setter since no input param and therefore not triggered in init
        self._clip_size = min(self.purchase.remaining, self.sale.remaining)

    @property
    def gain_loss(self):
        return float(self.clip_size) * (self.sale.price - self.purchase.price)
    
    @property
    def long_term(self):
        time_delta = relativedelta.relativedelta(self.sale.trade_time, self.purchase.trade_time)
        return time_delta.years >= 1

    @property
    def sale_row(self) -> dict:

        row = {
            'BaseAsset' : self.sale.base_asset,
            'QuoteAsset' : self.sale.quote_asset,
            'BuyDate' : self.purchase.trade_time, 
            'BuyPrice' : self.purchase.price, 
            'SellDate' : self.sale.trade_time, 
            'SellPrice' : self.sale.price,
            'Amount' : self.clip_size,
            'Gain/Loss' : self.gain_loss,
            'Long-Term' : self.long_term, 
            'SellYear' : self.sale.trade_time.year
            }
        
        return row