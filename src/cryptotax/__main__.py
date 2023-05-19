
from .sales import Sales
from .trades import Trades
from .cli_input import collect_config_filepath


def main():

    config_path = collect_config_filepath()

    trades = Trades(config_path)

    sales = Sales(trades)
    sales.create_sale_list()
    sales.create_annual_summary()

    # Print sale results
    print(sales.sale_events)
    print(sales.annual_summary.to_markdown())

    # # Download sale results
    # sales.download_sale_list
    # sales.download_annual_summary()


if __name__ == "__main__":
    main()
