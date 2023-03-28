import pandas as pd

from cryptotax.sale_event import SaleEventBuilder
from cryptotax.trades import Trades


class Sales:
    def __init__(self, trades: Trades) -> None:
        self.trades = trades.trades
        self.grouped_trades = trades.grouped_trades
        pass

    def create_sale_list(self) -> pd.DataFrame:
        """Returns log of sale events"""

        sales_list = []

        for _, asset in self.grouped_trades.items():

            asset.build_buy_list()
            asset.build_sell_list()

            if not asset.sell_txn_list:  # Continue to next asset if no sales
                continue

            dust_threshold = 0.00001  # Used for rounding errors

            # Helper Function
            def get_buy():  # TODO: What is asset and sale available locally in this function?
                """Returns next logical buy event that occured before sale event"""
                for buy in asset.buy_txn_list:
                    if (buy.epoch_time <= sale.epoch_time) & (buy.remaining > 0):
                        return buy

                # Should always be a buy that matches conditions. If not, raise error that more sold that bought.
                raise Exception("More amount sold that bought. Fix amounts on CSV")

            for sale_ind, sale in enumerate(asset.sell_txn_list):
                while sale.remaining > 0:

                    buy = get_buy()  # Get next buy event

                    # use property method
                    # initialize in __init__
                    sale_event = (
                        SaleEventBuilder(buy, sale)
                        .calc_clip_size()
                        .calc_gain_loss()
                        .is_long_term()
                        .build_sale()
                    )

                    # row = sale_event.create_sale_row()
                    # defer df concat to outside for loop, until then keep appending to a list
                    sales_list.append(sale.to_dict())

                    # Decrement
                    buy.remaining -= sale_event.clip_size
                    sale.remaining -= sale_event.clip_size

                    if sale.remaining < dust_threshold:
                        break

                    # End Loop if Sales are complete
                    if (sale.remaining < dust_threshold) and (
                        sale_ind == len(asset.sell_txn_list) - 1
                    ):
                        break

        sale_list = pd.Dataframe(sale_list)
        sales_list.reset_index(inplace=True, drop=True)
        sales_list.index.name = "Txn"
        self.sales_list = sales_list
        return self

    def create_annual_summary(self) -> pd.DataFrame:
        """Returns annual summary of sale_list"""

        # Initialize empty dataFrame
        unique_assets = self.sales_list["BaseAsset"].unique()
        year_list = self.sales_list["SellYear"].unique()
        annual_summary = pd.DataFrame(columns=year_list, index=unique_assets)
        annual_summary.index.name = "BaseAsset"

        # groupby asset, year with sum() aggregate ????
        # Pivot table??

        for year in year_list:
            df = self.sales_list[self.sales_list["SellYear"] == year]
            for asset in unique_assets:
                small_df = df.loc[df["BaseAsset"] == asset]
                sum = small_df["Gain/Loss"].sum()
                annual_summary.at[asset, year] = sum

        annual_summary.loc["Total"] = annual_summary.sum()

        self.annual_summary = annual_summary

        return self

    def download_sale_list(self):
        self.sale_list.to_csv("sale_log.csv")
        return

    def download_annual_summary(self):
        self.annual_summary.to_csv("annual_summary.csv")
        return
