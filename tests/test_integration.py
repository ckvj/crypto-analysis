import pytest
from src.cryptotax.trades import Trades
from src.cryptotax.sales import Sales

@pytest.fixture
def FIFO_sales_test_data():
    trades = Trades('/Users/carlvogel/Projects/crypto-analysis/tests/fixtures/FIFO_test_config.ini')
    sales = Sales(trades)
    return sales

def test_integration_FIFO_create_sales_list(FIFO_sales_test_data):
    
    df = FIFO_sales_test_data.create_sale_list()

    assert len(df) == 11
    assert round(df['Gain/Loss'].sum(),2) == round(-2577.723414,2)

@pytest.fixture
def LIFO_sales_test_data():
    trades = Trades('/Users/carlvogel/Projects/crypto-analysis/tests/fixtures/LIFO_test_config.ini')
    sales = Sales(trades)
    return sales

def test_integration_LIFO_create_sales_list(LIFO_sales_test_data):
    
    df = LIFO_sales_test_data.create_sale_list()
    print(df.to_markdown())
    assert len(df) == 10
    assert round(df['Gain/Loss'].sum(),2) == round(-5249.973603,2)

@pytest.fixture
def HIFO_sales_test_data():
    trades = Trades('/Users/carlvogel/Projects/crypto-analysis/tests/fixtures/HIFO_test_config.ini')
    sales = Sales(trades)
    return sales

def test_integration_HIFO_create_sales_list(HIFO_sales_test_data):
    
    df = HIFO_sales_test_data.create_sale_list()
    print(df.to_markdown())
    assert len(df) == 11
    assert round(df['Gain/Loss'].sum(),2) == round(-5754.592296,2)
