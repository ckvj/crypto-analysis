import csv

from typing import Dict, List

from cryptotax.config import Config
from cryptotax.trade import Trade, TradeBuilder
from cryptotax.asset import Asset


class Trades:

    config_file_path = "config.ini"  # Set default config file path (same dir)

    def __init__(self, path=config_file_path) -> None:
        # using property method
        # or using init to set the variables
        config = (
            Config(path)
            .set_accounting_type()
            .set_csv_filepath()
            .set_buy_types()
            .set_sell_types()
            .create_col_rename_map()
        )
        # why not pass the config per object?
        Asset.apply_config(config)
        self.import_trades(config)
        self.group_trades()

    def import_trades(self, config: Config):
        """Import trades based on config"""

        def rename_col(col: str, rename_map: Dict[str, str]) -> str:
            """Small helped function to convert user-input column name to program-compatible name"""
            for key, value in rename_map.items():
                if col == key:
                    col = value
                    break
            return col

        trades: List[Trade] = []
        with open(config.csv_filepath, newline="") as csvfile:

            # dict_mapping = {"csv_col": "dest_col"}
            # [dict_mapping[col] for col in reader.fieldnames]

            reader = csv.DictReader(csvfile)
            reader.fieldnames = [
                rename_col(col, config.col_rename) for col in reader.fieldnames
            ]

            # list comprehsion can be used
            # trades = [create_trade(row) cor row in reader]
            for row in reader:
                # Change all of these to propertie
                trade = (
                    TradeBuilder()
                    .set_trade_time(row["timestamp"])
                    .set_txn_type(row["txn_type"])
                    .set_base_asset(row["base_asset"])
                    .set_base_asset_amount(row["base_asset_amount"])
                    .set_quote_asset(row["quote_asset"])
                    .set_quote_asset_amount(row["quote_asset_amount"])
                    .build_trade()
                )

                trades.append(trade)

        # you can create an empty list and append to it, instead of this.
        self.trades = trades
        # Why return self
        return self

    def group_trades(self):
        """Group list of trades by asset"""

        grouped_trades: Dict[str, Asset] = {}

        # if it's a better option to use Df from here on...???

        for trade in self.trades:
            # None has a falsy value
            # get by default returns None
            if grouped_trades.get(trade.base_asset):
                asset = Asset(trade.base_asset)
                asset.append_trade(trade)
                grouped_trades[trade.base_asset] = asset
            else:
                grouped_trades[trade.base_asset].append_trade(trade)

        # you can create an empty dict and append to it, instead of this.
        self.grouped_trades = grouped_trades
        return self
