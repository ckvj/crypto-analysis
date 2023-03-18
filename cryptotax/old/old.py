# @staticmethod
# def package_trades(trades: pd.DataFrame) -> dict: #Question: How to annote List[Trade]? Trade not recognized.
    
#     @dataclass
#     class Trade:
#         trade_time: datetime
#         txn_type: str
#         base_asset: str
#         base_asset_amount: Decimal
#         quote_asset: str
#         quote_asset_amount: float
#         user_txn_id: Optional[str]


#     def build_trade(row: pd.DataFrame) -> Trade:
            
#         try:
#             if row['user_txn_id'] == '':
#                 row['user_txn_id'] = None
#             else:
#                 pass
#         except KeyError:
#             row['user_txn_id'] = None


#         trade =  Trade(
#             index.to_pydatetime(),
#             row['txn_type'],
#             row['base_asset'],
#             row['base_asset_amount'],
#             row['quote_asset'],
#             row['quote_asset_amount'],
#             row['user_txn_id'])

#         return trade