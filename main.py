from cryptotax.sales import Sales
from cryptotax.trades import Trades

def main():
    
    trades = Trades() #optional param path enables custom path to config file
    
    sales = Sales(trades)
    sales.create_sale_list()
    sales.create_annual_summary()
    
    # Print sale results
    print(sales.sale_events.to_markdown())
    print(sales.annual_summary.to_markdown())

    # # Download sale results
    # sales.download_sale_list
    # sales.download_annual_summary()
    

if __name__ == "__main__":
    main()
