from sales import Sales

def main():
    
    sales = Sales()
    
    sales.download_sale_list()
    sales.download_annual_summary()

    print(sales.sale_list.to_markdown())
    print(sales.annual_summary.to_markdown())

if __name__ == "__main__":
    main()

