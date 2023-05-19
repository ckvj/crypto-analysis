import pytest
from src.cryptotax.trades import Trades
from src.cryptotax.sales import Sales

class TestFixture():
    config_filepath = "/Users/carlvogel/Projects/crypto-analysis/tests/test_config.ini"
    line_number_to_update = 1 #Line of Config File that is updated for Analysis Type
    test_data = [
        ('FIFO', -2577.723414),
        ('LIFO', -5249.973603),
        ('HIFO', -5754.592296),
        ]
    
    @staticmethod
    def replace_line(file_name, line_num, text):
        """Replaces 1 line of text in file"""
        lines = open(file_name, 'r').readlines()
        lines[line_num] = text
        out = open(file_name, 'w')
        out.writelines(lines)
        out.close()


@pytest.mark.parametrize("analysis_type, expected", TestFixture.test_data)
def test_create_sales_list(analysis_type, expected):

    analysis_type_line = f'accounting_type = {analysis_type}\n'

    TestFixture.replace_line(TestFixture.config_filepath, TestFixture.line_number_to_update, analysis_type_line)
    
    trades = Trades(TestFixture.config_filepath)
    sale_list = Sales(trades).create_sale_list()

    assert round(sale_list['Gain/Loss'].sum(),2) == round(expected,2)
