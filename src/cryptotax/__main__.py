from cryptotax.sales import Sales
from cryptotax.trades import Trades
from cryptotax.cli_input import process_config_location

def main():
    
    config_path = process_config_location()
    
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
