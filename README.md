# Purpose
Processes financial transactions for use in annual capital gains tax reporting

# Overview
Current tax portfolio tools do not accurately render many transaction types. Therefore, many crypto users have resorted to populating important transactions into a spreadsheet and working with external auditing companies to calculate their tax basis.

The crypto-tax package is a tool that enables individuals to easily calculate their tax basis across assets.

The package relies on transactions being populated in the 'Base Asset' and 'Quote Asset' model which is common in trading platforms.
- Base Asset: Asset being traded
- Quote Asset: Asset that Base Asset is being quoted in. Typically USD or other fiat.

For trades that do not use Quote Asset as the taxable Fiat asset (e.g. crypto<>crypto trades or crypto<>NFT), users should use a double entry system where trades route through a tax-demoninated Asset. For example, a trade involving purchasing a NFT for 2 ETH, when ETH trading at $2k USD:

|DateTime|Txn Type|Base Asset|Base Asset Amount|Quote Asset|Quote Asset Amount| Price|
|--------|---------|------|-----------------|-----------|------------------|------|
|2021-09-27T01:46:03.000Z|SELL|ETH|2|USD|4000|2000|
|2021-09-27T01:46:03.000Z|BUY|NFT_NAME|1|USD|4000|4000|

# Usage
- cryptotax is a package which can can be utilized to import and process trades
- call 'python3 -m cryptotax PATH/TO/YOUR/CONFIG/FILE' to print list of sale events and annual summary to the terminal
- User can also download sale log and annual summary as csv


#### Trade Information
- **timestamp:** Preferred format 2021-09-27T01:46:03.000Z, though dates are imported using dateparser.parse which should accomodate other date syntax.
- **txn_type:** eg Buy, Airdrop, Redeem, Sell, etc. User can config which types of transactions are considered buy or sell for tax reasons.
- **base_asset:** Asset being traded
- **base_asset_amount:** How much of asset is traded
- **quote_asset:** Asset the traded asset is being quoted in (typically fiat, but asset tax base is being calculated in)
- **quote_asset_amount:** Amount of Quote Asset

#### Optional Columns:
- **user_txn_id:** Optional user-provided identifier that is populated into resulting sale log 

# Configuration
Users should create a config.ini file and populate with below information. An example is in the repo at [config.ini](https://github.com/ckvj/crypto-tax/blob/master/config.ini).

Default use is labeling file 'config.ini' and locating in the same directory, but optional file path can be provided when initializing Sales.

Config file has five Sections:

### [accounting_type]
#Must be FIFO, HIFO, LIFO\
**accounting_type:** required

### [csv_info]
#Information about where the csv of transactions is stored\
**filename:** required. Should end in .csv\
**dir:** optional. Do not include if file is in current directory

### [csv_columns]
#Identifies which column names contain which values\
**timestamp:** When trade occured. Value should be in format YYYY-MM-DDTHH:MM:SS.000Z\
**txn_type:** 
**base_asset:** Name of asset name being traded / sold\
**base_asset_amount:** \
**quote_asset:** Quote asset name, typically USD or Fiat\
**quote_asset_amount:** Amount asset is sold for
 
### [opt_csv_columns]
 - **user_txn_id:** optional user provided id that can be populated into the Sale Log

### [buy_txn_types]
#Enter which values correspond to buy transactions. Specifically, values that are contained in column txn_type. For example, AIRDROP can be added to be a buy transaction.\
**buy1:** BUY
**buy2:** AIRDROP
...

### [sell_txn_types]
#Enter which values correspond to sell transactions
**sell1:** SELL


# Helpful Hints:
- In the config.ini file, DO NOT use '' or "" around entries. Values are ingested as strings and converted when needed.
- Columns txn_type entries should contain words that are in both [buy_txn_types] and [sell_txn_types], otherwise they will be double counted
- Example transaction list can be found in tests/fixtures
