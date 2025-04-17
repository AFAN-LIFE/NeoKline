import tushare as ts
from config import TUSHARE_TOKEN
pro = ts.pro_api(TUSHARE_TOKEN)

# 查询当前所有正常上市交易的股票列表：stock_basic
stock_basic_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
stock_basic_df.to_csv('../data/stock_basic.csv', index=False)

# 交易日历：https://tushare.pro/document/2?doc_id=26
stock_calender_df = pro.query('trade_cal', start_date='20160101', end_date='20251231')
stock_calender_df.to_csv('../data/stock_calender.csv', index=False)