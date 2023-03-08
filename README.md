# Purpose
Processes financial transactions for use in annual capital gains tax reporting

# Usage
Current tax portfolio tools do not accurately render many transaction types. Therefore, many have resorted to populating important transactionsinto a spreadsheet.

The crypto-tax package uses the 'Base Asset' and 'Quote Asset' model which is common in trading platforms.
- Base Asset: Asset being traded
- Quote Asset: Asset that Base Asset is being quoted in. Typically USD or other fiat

For trades that do not use Quote Asset as taxable Fiat asset, for example crypto<>crypto or crypto<>NFT, users should use a double entry system where trade rounds through tax-demoninated Asset. 

For example, purchasing a NFT for 2 ETH, when ETH trading at $2k USD:
|DateTime|Txn Type|Base Asset|Base Asset Amount|Quote Asset|Quote Asset Amount| Price|
|--------|---------|------|-----------------|-----------|------------------|------|
|2021-09-27T01:46:03.000Z|SELL|ETH|2|USD|4000|2000|
|2021-09-27T01:46:03.000Z|BUY|NFT_NAME|1|USD|4000|4000|

Minimum Required Columns:
- **DateTime:** Format 2021-09-27T01:46:03.000Z
- **Txn Type:** eg Buy, Airdrop, Redeem, Sell, etc. User can config which types of transactions are considered buy or sell for tax reasons.
- **Base Asset:** Asset being traded
- **Base Asset Amount:** How much of asset is traded
- **Quote Asset:** Asset the traded asset is being quoted in
- **Quote Asset Amount:** Amount of Quote Asset

Users should create a config.ini file and populate with below information.

# Configuration
Must use a 'config.ini' file. An exmaple is in the repo.

Config file has five Sections:

### [accounting_type]
#Must be FIFO, HIFO, LIFO\
**accounting_type:** required

### [csv_info]
#Information about where the csv of transactions is stored\
**filename:** required. Should end in .csv\
**dir:** optional. Leave value equal to empty if file is in current directory\

### [csv_columns]
#Identifies which column names contain which values\
**DateTime:** required. When trade occured. Value should be in format YYYY-MM-DDTHH:MM:SS.000Z\
**txn_id:** ***NOT USED YET*** optional. Unique user provided transaction id\
**txn_type:** required.\
**base_asset:** required. Asset being traded / sold\
**base_asset_amount:** required\
**quote_asset:** ***NOT USED YET.*** optional. Quote asset, typically USD\
**quote_asset_amount:** required. Amount asset sold for\
 

### [buy_txn_types]
#Enter which values correspond to buy transactions. Specifically, based on string search of column txn_type. For example, Airdrop can be added to be a buy transaction.\
**buy1:** BUY
**buy2:** AIRDROP
...

### [sell_txn_types]
#Enter which values correspond to buy transactions
**sell:** SELL

## Example File
[config.ini](https://github.com/ckvj/crypto-tax/blob/master/config.ini)

# Helpful Hints:
- In the config.ini file, DO NOT use '' or "" around entries. Values are ingested as strings and converted when needed.
- Columns txn_type entries should contain words that are in both [buy_txn_types] and [sell_txn_types], otherwise they will be double counted
