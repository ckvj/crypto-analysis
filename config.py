import configparser
from decimal import Decimal


def process_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    config_dict = {s:dict(config.items(s)) for s in config.sections()}
    
    # Set dir to None if not provided
    if config_dict['file_info'].get('dir', None) == None:
        config_dict['file_info']['dir'] = None
        
    # Create Buy Type List
    config_dict['buy_types_list'] = [x for x in list(config_dict['buy_txn_types'].values())]

    # Create Sell Type List
    config_dict['sell_types_list'] = [x for x in list(config_dict['sell_txn_types'].values())]

    # Identify Columns to convert from string
    _column_dtypes = {config_dict['csv_columns']['price_paid'] : float, config_dict['csv_columns']['quote_asset_amount'] : float}
    _converter = {config_dict['csv_columns']['base_asset_amount'] : Decimal}
    
    # Data Validations
    _supported_accounting_types = ['FIFO', 'LIFO', 'HIFO']
    if config_dict['accounting_type']['accounting_type'] not in _supported_accounting_types:
        raise ValueError('Unsupported Analysis Type')
    
    return config_dict, _column_dtypes, _converter

