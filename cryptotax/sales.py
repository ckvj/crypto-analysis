import pandas as pd

from cryptotax.sale_event import SaleEvent
from cryptotax.trades import Trades


class Sales:

    def __init__(self, trades: Trades) -> None:
        self.trades = trades.trades
        
        self.sale_events: pd.DataFrame
        self.annual_summary: pd.DataFrame      
        
    def create_sale_list(self) -> pd.DataFrame:
        """Returns dataframe of sale events"""
        sales_list = []

        for _ , asset in self.trades.items():

            asset.build_buy_list()
            asset.build_sell_list()
            
            if not asset.sell_txn_list: # Continue to next asset if no sales
                continue
            
            dust_threshold = 0.00001 # Used for small rounding errors
            
            # Helper Function
            def get_buy():
                """Returns next logical buy event"""
                for buy in asset.buy_txn_list:
                        if (buy.epoch_time <= sale.epoch_time) & (buy.remaining > 0):
                            return buy
                
                # Should always be a buy that matches conditions. If not, raise error that more sold that bought.
                raise Exception(f"More {sale.base_asset} sold that bought. Fix amounts on CSV")

            for sale_ind, sale in enumerate(asset.sell_txn_list):
                while sale.remaining > 0:

                    buy = get_buy() # Get next buy event
                    
                    sale_event = SaleEvent(buy, sale)
                    
                    sales_list.append(sale_event.sale_row)

                    # Decrement
                    buy.remaining -= sale_event.clip_size
                    sale.remaining -= sale_event.clip_size
                    
                    if buy.remaining < dust_threshold:
                        asset.buy_txn_list.remove(buy) # Shorten buy_txn_list to remove accounted for purchases

                    if sale.remaining < dust_threshold:
                        break

        # Convert to df
        self.sale_events = pd.DataFrame(sales_list)
        self.sale_events.index.name = 'Txn'
        return self.sale_events

    
    def create_annual_summary(self, events = None) -> pd.DataFrame:
        """Returns annual summary of sale events."""

        if events is None:
            events = self.sale_events

        # Initialize empty DataFrame
        unique_assets = events['BaseAsset'].unique() # Update
        year_list = events['SellYear'].unique()
        self.annual_summary = pd.DataFrame(columns = year_list, index=unique_assets)
        self.annual_summary.index.name = 'BaseAsset'

        # Determine gain/loss per asset per year
        gain_loss_totals = events.groupby(['SellYear', 'BaseAsset'])['Gain/Loss'].sum()
        # pivot_table 

        # Populate annual_summary df
        for year in year_list:
            _dict_ = dict.fromkeys(unique_assets, 0) # Initialize dictionary with 0 values
            _ = dict(zip(gain_loss_totals[year].index, gain_loss_totals[year]))
            _dict_.update(_) # Apply gain/loss per asset if applicable
            
            self.annual_summary[year] = list(_dict_.values())

        # Calculate Annual Total Gain/Loss    
        self.annual_summary.loc['Total'] = self.annual_summary.sum()

        return self.annual_summary


    def download_sale_list(self):
        self.sale_list.to_csv('sale_log.csv')
        return

    def download_annual_summary(self):
        self.annual_summary.to_csv('annual_summary.csv')
        return
