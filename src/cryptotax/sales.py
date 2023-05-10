import pandas as pd

from cryptotax.sale_event import SaleEvent
from cryptotax.trades import Trades
from cryptotax.const import DUST_THRESHOLD


class Sales:

    def __init__(self, trades: Trades) -> None:
        self.trades = trades.trades

        self.sale_events: pd.DataFrame
        self.annual_summary: pd.DataFrame

    def create_sale_list(self) -> pd.DataFrame:
        """Returns dataframe of sale events"""
        sales_list = []

        for _, asset in self.trades.items():

            asset.build_buy_list()
            asset.build_sell_list()

            if not asset.sell_txn_list:  # Continue to next asset if no sales
                continue

            # Helper Function
            def get_buy():
                """Returns next logical buy event"""
                for buy in asset.buy_txn_list:
                    if (buy.epoch_time <= sale.epoch_time) & (buy.remaining > 0):
                        return buy

                # Should always be a buy that matches conditions. If not, raise error that more sold that bought.
                raise Exception(
                    f"More {sale.base_asset} sold that bought. Fix amounts on CSV")

            for sale in asset.sell_txn_list:
                while sale.remaining > 0:

                    buy = get_buy()  # Get next buy event

                    sale_event = SaleEvent(buy, sale)

                    sales_list.append(sale_event.sale_row)

                    # Decrement
                    buy.remaining -= sale_event.clip_size
                    sale.remaining -= sale_event.clip_size

                    if buy.remaining < DUST_THRESHOLD:
                        # Shorten buy_txn_list to remove accounted for purchases
                        asset.buy_txn_list.remove(buy)

                    if sale.remaining < DUST_THRESHOLD:
                        break

        # Convert to df
        self.sale_events = pd.DataFrame(sales_list)
        self.sale_events.index.name = 'Txn'
        return self.sale_events

    def create_annual_summary(self, events=None) -> pd.DataFrame:
        """Returns annual summary of sale events."""

        if events is None:
            events = self.sale_events

        # Calculate gain/loss per asset per year
        self.annual_summary = pd.pivot_table(events,
                                             values='Gain/Loss',
                                             columns='SellYear',
                                             index='BaseAsset',
                                             aggfunc=sum,
                                             fill_value=0,
                                             )

        # Calculate Annual Total Gain/Loss
        self.annual_summary.loc['Total'] = self.annual_summary.sum()
        return self.annual_summary

    def download_sale_list(self):
        self.sale_list.to_csv('sale_log.csv')
        return

    def download_annual_summary(self):
        self.annual_summary.to_csv('annual_summary.csv')
        return
