import datetime
from io import BytesIO

import pandas as pd
import streamlit as st
import mplfinance as mpf
import matplotlib.pyplot as plt

from view.llm_qa import single_content_qa
from tools.callback import botton_callback
from tools.stock_data import StockData

st.markdown("# 📈 股票分钟分析")

if "stock_min_bar" not in st.session_state:
    st.session_state.stock_min_bar = False
if "cache_stock_min_bar" not in st.session_state:
    st.session_state.cache_stock_min_bar = {}


# 如果不是交易日，往前找最近的交易日
def get_nearest_trading_day(selected_date, open_date_df):
    calendar_dates = pd.to_datetime(open_date_df["cal_date"]).dt.date
    valid_dates = calendar_dates[calendar_dates <= selected_date]
    if len(valid_dates) == 0:
        return None
    return valid_dates.max()


@st.cache_data
def load_stock_basic():
    return pd.read_csv("data/stock_basic.csv")


@st.cache_data
def load_stock_open_day():
    df = pd.read_csv("data/stock_calender.csv").sort_values(by="cal_date", ascending=True)
    df["cal_date"] = pd.to_datetime(df["cal_date"], format="%Y%m%d")
    df = df[df["is_open"] == 1]
    df.index = range(df.shape[0])
    return df


def stock_kline_analysis():
    """股票K线分析"""
    stock_basic_df = load_stock_basic()
    open_date_df = load_stock_open_day()
    stock_list = stock_basic_df["ts_code"].tolist()

    s1, s2, s3 = st.columns([1, 1, 1])
    stock_id = s1.selectbox("请选择股票ID，支持手动输入", options=stock_list, index=None)
    now = datetime.datetime.now()
    end_date: datetime.date = s2.date_input("请选择日期，分析仅限日内", value=now)
    real_end_date: datetime.date = get_nearest_trading_day(end_date, open_date_df)
    if real_end_date is None:
        st.error("所选日期非有效交易日，请重新选择")
        st.stop()

    frequency = s3.selectbox("请选择日内分钟频率", options=["1min", "5min", "15min", "30min", "60min"], index=0)

    # 反过来理解：只有选择股票ID，并且之前没有缓存的，才可以生成
    b1, b2 = st.columns([1, 1])
    if b2.button("清除重新生成", on_click=botton_callback, args=("清除重新生成",)):
        st.session_state.cache_stock_min_bar = {}
        st.session_state.stock_min_bar = False
    if b1.button(
        "生成图像",
        on_click=botton_callback,
        args=("生成图像",),
        disabled=(stock_id is None) or (len(st.session_state.cache_stock_min_bar) > 0),
    ):
        if st.session_state.user_tushare_token == "":
            st.error("股票分钟分析必须要配置自己的tushare token，请进入个人中心设置自己的tushare token")
            st.session_state.stock_min_bar = False
            st.stop()
        else:  # 如果配置了自己的token，直接放行
            st.session_state.stock_min_bar = True

    if st.session_state.stock_min_bar:
        if not st.session_state.cache_stock_min_bar:
            if st.session_state.user_tushare_token == "":
                sd = StockData()
            else:  # 如果自定义了token
                sd = StockData(token=st.session_state.user_tushare_token)
            stock_info_dict = sd.stock_info(stock_id)
            adj_df = sd.min(
                stock_id,
                frequency,
                datetime.datetime.combine(end_date, datetime.time(9, 0, 0)),
                datetime.datetime.combine(end_date, datetime.time(15, 0, 0)),
            )
            # 设置mplfinance的蜡烛颜色，up为阳线颜色，down为阴线颜色
            my_color = mpf.make_marketcolors(up="r", down="g", edge="inherit", wick="inherit", volume="inherit")
            # 设置图表的背景色
            my_style = mpf.make_mpf_style(
                marketcolors=my_color,
                figcolor="(0.82, 0.83, 0.85)",
                gridcolor="(0.82, 0.83, 0.85)",
            )
            mpf.plot(adj_df, style=my_style, type="candle", volume=True, returnfig=True)
            # 保存到内存缓冲区
            buffer = BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)
            # 显示图片
            st.image(buffer)
            st.session_state.cache_stock_min_bar = {
                "stock_min_bar_img_path": buffer,
                "stock_info_dict": stock_info_dict,
            }
            st.rerun()
        else:
            stock_min_bar_img_path = st.session_state.cache_stock_min_bar["stock_min_bar_img_path"]
            stock_info_dict = st.session_state.cache_stock_min_bar["stock_info_dict"]

        content = {"img": [{"value": stock_min_bar_img_path}]}
        single_content_qa(content=content)
        st.markdown(
            f"**股票代码**：{stock_id} **股票名称**：{stock_info_dict['name']} "
            f"**行业**：{stock_info_dict['industry']}  **地区**：{stock_info_dict['area']} **上市日期**：{stock_info_dict['list_date']}"
        )
        st.image(stock_min_bar_img_path)


stock_kline_analysis()
