import pandas as pd

from cryptotax.sale_event import SaleEventBuilder
from cryptotax.trades import Trades


class Sales:

    def __init__(self, trades: Trades) -> None:
        self.trades = trades.trades
        self.grouped_trades = trades.grouped_trades
        pass        
        
    def create_sale_list(self) -> pd.DataFrame:
        """Returns log of sale events given dictionary of unprocessed trades
        
        Args:
            unprocessed_trades: dictionary of {'asset' : List[Trades]}
            analysis_type: HIFO, LIFO, or FIFO
            buy_types: List of strings that equal buy transaction types (eg BUY, AIRDROP)
            sell_types: List of strings that equal buy transaction types (eg SELL, PURCHASE)
        
        Returns:
            sale_log: List of Sale events, including gain-loss per sale 

        """

        sales_list = pd.DataFrame()

        for _ , asset in self.grouped_trades.items():

            asset.build_buy_list()
            asset.build_sell_list()
            
            if not asset.sell_txn_list: # Continue to next asset if no sales
                continue
            
            dust_threshold = 0.00001 # Used for rounding errors

            for sale_ind, sale in enumerate(asset.sell_txn_list):
                while sale.remaining > 0:
                    for buy in asset.buy_txn_list:
                        if (buy.epoch_time <= sale.epoch_time) & (buy.remaining > 0):

                            sale_event = SaleEventBuilder(buy, sale). \
                                calc_clip_size(). \
                                calc_gain_loss(). \
                                is_long_term(). \
                                build_sale()
                            
                            row = sale_event.create_sale_row()
                            sales_list = pd.concat([sales_list, row])

                            # Decrement
                            buy.remaining -= sale_event.clip_size
                            sale.remaining -= sale_event.clip_size
                            
                            if sale.remaining < dust_threshold:
                                break
                                
                    # End Loop if Sales are complete
                    if (sale.remaining < dust_threshold) & (sale_ind == len(asset.sell_txn_list)-1):
                        break
        
        sales_list.reset_index(inplace=True, drop = True)
        sales_list.index.name = 'Txn'
        self.sales_list = sales_list
        return self

    
    def create_annual_summary(self) -> pd.DataFrame:
        """Returns annual summary of sale_list"""

        # Initialize empty dataFrame
        unique_assets = self.sales_list['BaseAsset'].unique()
        year_list = self.sales_list['SellYear'].unique()
        annual_summary = pd.DataFrame(columns = year_list, index=unique_assets)
        annual_summary.index.name = 'BaseAsset'

        for year in year_list:
            df = self.sales_list[self.sales_list['SellYear'] == year]
            for asset in unique_assets:
                small_df = df.loc[df['BaseAsset'] == asset]
                sum = small_df['Gain/Loss'].sum()
                annual_summary.at[asset, year] = sum
            
        annual_summary.loc['Total'] = annual_summary.sum()

        self.annual_summary = annual_summary   
            
        return self


    def download_sale_list(self):
        self.sale_list.to_csv('sale_log.csv')
        return

    def download_annual_summary(self):
        self.annual_summary.to_csv('annual_summary.csv')
        return