from datetime import datetime
from cachetools import func

import pandas as pd
import tushare as ts

from config import TUSHARE_TOKEN

@func.lru_cache(maxsize=1)
def load_stock_basic():
    return pd.read_csv("data/stock_basic.csv")

class StockData:
    def __init__(self, source: str = "tushare", token: str = TUSHARE_TOKEN):
        if source == "tushare":
            self.api = ts.pro_api(token)

    def _daily_tushare(
        self, order_book_id: str, start_date: datetime, end_date: datetime
    ):
        # 参数格式修改
        start_dt = start_date.strftime("%Y%m%d")
        end_dt = end_date.strftime("%Y%m%d")

        # 查询
        stock_df = self.api.query(
            "daily", ts_code=order_book_id, start_date=start_dt, end_date=end_dt
        )

        name_map = {
            "trade_date": "trade_date",
            "ts_code": "order_book_id",
            "open": "open",
            "close": "close",
            "high": "high",
            "low": "low",
            "vol": "volume",
            "amount": "amount",
        }

        stock_df.rename(columns=name_map, inplace=True)  # 重命名
        stock_df = stock_df[list(name_map.values())]  # 筛选列
        return stock_df

    @staticmethod
    def check_order_book_id(order_book_id: str):
        if not order_book_id:
            raise ValueError("order_book_id is null")

        stock_basic_df = load_stock_basic()
        df_filter = order_book_id == stock_basic_df["ts_code"]
        if not df_filter.any():
            raise ValueError(f"not find the order_book_id {order_book_id}")

    def stock_info(self, order_book_id: str):
        """股票基本信息"""
        self.check_order_book_id(order_book_id)
        stock_basic_df = load_stock_basic()
        stock_info = stock_basic_df[order_book_id == stock_basic_df["ts_code"]].iloc[0]
        return stock_info.to_dict()

    def daily(self, order_book_id: str, start_date: datetime, end_date: datetime):
        """日度数据"""
        self.check_order_book_id(order_book_id)
        stock_df = self._daily_tushare(order_book_id, start_date, end_date)
        stock_df.set_index("trade_date", inplace=True)
        stock_df.sort_index(inplace=True)
        stock_df.index = pd.DatetimeIndex(stock_df.index)

        return stock_df
