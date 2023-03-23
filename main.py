from cryptotax.sales import Sales
from cryptotax.trades import Trades

def main():
    
    trades = Trades()
    sales = Sales(trades)
    
    sales.create_sale_list()
    sales.create_annual_summary()
    print(sales.sales_list.to_markdown())
    print(sales.annual_summary.to_markdown())

if __name__ == "__main__":
    main()
