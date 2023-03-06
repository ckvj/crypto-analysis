# crypto-tax
The crypto-tax package processes transactions using various tax accounting methods

# Configuration
Must use a 'config.ini' file

Config file has three Sections. 

[accounting_type]\
accounting_type: # Must be FIFO, HIFO, LIFO\

[csv_info]\
#Information about where the csv of transactions is stored\
filename: required. Should end in .csv\
dir: optional. Leave value equal to empty if file is in current directory\

[csv_columns]\
#Identifies which column names contain which values
timestamp: required. When trade occured. Value should be in format YYYY-MM-DDTHH:MM:SS.000Z\
txn_id: optional. Unique user providedid for transaction\
txn_type: required.\
base_asset: required. Asset being traded / sold\
base_asset_amount: required\
quote_asset: optional. Quote asset, typically USD\
quote_asset_amount: required. Amount asset sold for\
price_paid: optional. Price paid for asset, in terms of quote_asset_amount / base_asset_amount\ 

[txn_types]
Opportunity to enter which values correspond to buy and sell transactions. Specifically, based on string search of column txn_type. For example, Airdrop can be added to be a buy transaction. 

## Example File
config.ini
_______________
[accounting_type]
accounting_type = HIFO

[csv_info]
filename = crypto_tax_txns.csv
dir = 

[csv_columns]
timestamp = DateTime
txn_id = internal_txn_id
txn_type = Transaction Type
base_asset = Base Asset
base_asset_amount = Base Asset Amount
quote_asset = Quote Asset
quote_asset_amount = Quote Asset Amount
price_paid = Price Paid

[txn_types]
buy = BUY, AIRDROP, REDEEM
sell = SELL

# Usage


### Helpful Hints:
- In the config.ini file, DO NOT use '' or "" around entries. Every value is already ingested as a string already, 
- Supported accounting methods are FIFO, LIFO, HIFO
- Columns txn_type should NOT contain words in the txn_types | buy and txn_types | sell, otherwise it will be double counted
