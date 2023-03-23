import pandas as pd
from dateutil import relativedelta
from cryptotax.trade import Trade

class SaleEvent:
    def __init__(self) -> None:
        self.purchase: Trade
        self.sale: Trade
        self.clip_size: float
        self.gain_loss: float
        self.long_term: bool

    def create_sale_row(self) -> pd.DataFrame:

        row = pd.DataFrame([
            {'BaseAsset' : self.sale.base_asset,
             'QuoteAsset' : self.sale.quote_asset,
             'BuyDate' : self.purchase.trade_time, 
             'BuyPrice' : self.purchase.price, 
             'SellDate' : self.sale.trade_time, 
             'SellPrice' : self.sale.price,
             'Amount' : self.clip_size,
             'Gain/Loss' : self.gain_loss,
             'Long-Term' : self.long_term, 
             'SellYear' : self.sale.trade_time.year
             }])
        
        return row
    

class SaleEventBuilder:
    def __init__(self, purchase, sale, sale_event = None):
        if not sale_event:
            self.sale_event = SaleEvent()
        else:
            self.sale_event = sale_event
        
        self.sale_event.purchase = purchase
        self.sale_event.sale = sale

    def calc_clip_size(self):
        self.sale_event.clip_size = min(self.sale_event.purchase.remaining, self.sale_event.sale.remaining)
        return self
    
    def calc_gain_loss(self):
        self.sale_event.gain_loss = float(self.sale_event.clip_size) * (self.sale_event.sale.price - self.sale_event.purchase.price)
        return self
    
    def is_long_term(self):
        
        time_delta = relativedelta.relativedelta(self.sale_event.sale.trade_time, self.sale_event.purchase.trade_time)

        if time_delta.years >= 1:
            long_term = True
        elif time_delta.years < 1:
            long_term = False
        
        self.sale_event.long_term = long_term
        return self
         
    def build_sale(self):
        return self.sale_event


    

