import configparser
from decimal import Decimal


def process_config():
    """Pulls info from config.ini which must be stored in same folder as main.py
    
    Returns:
        config_dict: dictionary of config.ini
        _column_dtypes: dictionary of {column names : dtype } to apply to data frame
        _converter: dictionary of {column names : dtype } to apply via converter (eg needed for Decimal type)
    
    """

    config = configparser.ConfigParser()
    config.read('config.ini')
    
    config_dict = {s:dict(config.items(s)) for s in config.sections()}
    
    # Set dir of CSV to None if not provided
    if config_dict['file_info'].get('dir', None) == None:
        config_dict['file_info']['dir'] = None
        
    # Create List of buy types
    config_dict['buy_types_list'] = [x for x in list(config_dict['buy_txn_types'].values())]

    # Create List of sell types
    config_dict['sell_types_list'] = [x for x in list(config_dict['sell_txn_types'].values())]
    
    # Create dictionary to rename required & optional columns
    config_dict['col_rename'] = {y: x for x, y in config_dict['csv_columns'].items()}
    opt_cols = {y: x for x, y in config_dict['opt_csv_columns'].items() if y != ''}
    config_dict['col_rename'].update(opt_cols)

    # Identify Columns to convert from string to other dtype
    _column_dtypes = {config_dict['csv_columns']['quote_asset_amount'] : float}

    if config_dict['opt_csv_columns']['user_txn_id'] != '':
        _column_dtypes.update({config_dict['opt_csv_columns']['user_txn_id'] : str})

    _converter = {config_dict['csv_columns']['base_asset_amount'] : Decimal}

    # Accounting Type Validations
    _supported_accounting_types = ['FIFO', 'LIFO', 'HIFO']
    if config_dict['accounting_type']['accounting_type'] not in _supported_accounting_types:
        raise ValueError('Unsupported Analysis Type')
    
    return config_dict, _column_dtypes, _converter

