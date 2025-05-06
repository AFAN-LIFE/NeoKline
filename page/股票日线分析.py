import datetime
from io import BytesIO

import pandas as pd
import streamlit as st
import mplfinance as mpf
import matplotlib.pyplot as plt

from view.llm_qa import single_content_qa, BASE_USER_CONTENT, BASE_SYSTEM_CONTENT
from tools.callback import botton_callback
from tools.stock_data import StockData
from rag.base import UserKnowledgeBase

st.markdown("# 📈 股票日线分析")

if "stock_day_bar" not in st.session_state:
    st.session_state.stock_day_bar = False
if "cache_stock_day_bar" not in st.session_state:
    st.session_state.cache_stock_day_bar = {}
if "last_click_time" not in st.session_state:
    st.session_state.last_click_time = None
if "user_tushare_token" not in st.session_state:
    st.session_state.user_tushare_token = ""


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

def get_start_date(end_date, window, open_date_df):
    """获取指定日期的前N天的交易日作为开始时间"""
    calendar_dates = open_date_df["cal_date"].sort_values(ascending=True)
    end_idx = calendar_dates[calendar_dates == pd.to_datetime(end_date)].index[0]
    start_idx = end_idx - window + 1
    return calendar_dates.iloc[start_idx].date()

def stock_kline_analysis():
    """股票K线分析"""
    stock_basic_df = load_stock_basic()
    open_date_df = load_stock_open_day()
    stock_list = stock_basic_df["ts_code"].tolist()

    s1, s2, s3 = st.columns([1, 1, 1])
    stock_id = s1.selectbox("请选择股票ID，支持手动输入", options=stock_list, index=None)
    now = datetime.datetime.now()
    end_date: datetime.date = s2.date_input("请选择截止日期", value=now)
    real_end_date: datetime.date = get_nearest_trading_day(end_date, open_date_df)
    if real_end_date is None:
        st.error("所选日期无有效交易日，请重新选择")
        st.stop()

    window = s3.selectbox("请选择历史分析时间窗口(日)", options=[5, 10, 20, 60, 120, 240], index=0)
    p1, p2 = st.columns([1, 2])
    if ('rag_meta_data' not in st.session_state) or (st.session_state.rag_meta_data == []):
        use_rag = p1.checkbox('是否结合知识库', disabled=True)
        p2.badge('当前无知识保存，请到“知识库管理”上传知识', color='orange')
    else:
        use_rag = p1.checkbox('是否结合知识库')
        p2.badge(f'请确认知识库的信息和当前股票相关；默认查询最匹配的前3条知识块', color='blue')

    # 反过来理解：只有选择股票ID，并且之前没有缓存的，才可以生成
    b1, b2, b3 = st.columns([1, 1, 1])
    if b3.button("订阅该股票公告", help="订阅后该股票有新公告会以邮件形式发送到您邮箱", disabled=(stock_id is None), on_click=botton_callback, args=['订阅该股票公告']):
        if not st.session_state.get("authentication_status"):
            st.toast('请登录后再订阅', icon='❌')
        else:
            from tools.subscribe import get_subscriptions, MAX_SUBSCRIPTION, add_subscription
            subscriptions = get_subscriptions()
            total_df = pd.DataFrame(subscriptions)
            now = datetime.datetime.now()
            if total_df.shape[0] == 0:
                add_subscription(stock_id, 'stock', subscriptions)
                st.toast('订阅成功！', icon='✅')
            else:
                on_df = total_df[total_df["失效时间"] > now]
                if len(on_df) < MAX_SUBSCRIPTION:
                    add_subscription(stock_id, 'stock', subscriptions)
                st.toast('订阅成功！', icon='✅')
    if b2.button("清除重新生成", on_click=botton_callback, args=("清除重新生成",)):
        st.session_state.cache_stock_day_bar = {}
        st.session_state.stock_day_bar = False
    if b1.button(
        "生成图像",
        on_click=botton_callback,
        args=("生成图像",),
        disabled=(stock_id is None) or (len(st.session_state.cache_stock_day_bar) > 0),
    ):
        if st.session_state.user_tushare_token == "":
            if st.session_state.last_click_time is None:  # 第一次点击
                st.session_state.stock_day_bar = True
                st.session_state.last_click_time = datetime.datetime.now()
            else:
                time_since_last_click = datetime.datetime.now() - st.session_state.last_click_time
                if time_since_last_click.total_seconds() > 60:  # 超过60秒才能再次点击
                    st.session_state.stock_day_bar = True
                    st.session_state.last_click_time = datetime.datetime.now()
                else:
                    st.error(
                        "您未配置个人tushare token的用户，故1分钟才能访问一次，您可以进入个人中心设置自己的tushare token"
                    )
                    st.session_state.stock_day_bar = False
                    st.stop()
        else:  # 如果配置了自己的token，直接放行
            st.session_state.stock_day_bar = True

    if st.session_state.stock_day_bar:
        if not st.session_state.cache_stock_day_bar:
            real_start_date: datetime.date = get_start_date(real_end_date, window, open_date_df)
            if st.session_state.user_tushare_token == "":
                sd = StockData()
            else:  # 如果自定义了token
                sd = StockData(token=st.session_state.user_tushare_token)
            stock_info_dict = sd.stock_info(stock_id)
            adj_df = sd.daily(stock_id, real_start_date, real_end_date)
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
            # 知识库查询
            rag_result = []
            if use_rag:
                query = f"**股票代码**：{stock_id} **股票名称**：{stock_info_dict['name']} "
                f"**行业**：{stock_info_dict['industry']} **地区**：{stock_info_dict['area']} **上市日期**：{stock_info_dict['list_date']}"
                rag_result = UserKnowledgeBase.search(query, k=3)

            st.session_state.cache_stock_day_bar = {
                "stock_day_bar_img_path": buffer,
                "stock_info_dict": stock_info_dict,
                "rag_result": rag_result
            }
            st.rerun()
        else:
            stock_day_bar_img_path = st.session_state.cache_stock_day_bar["stock_day_bar_img_path"]
            stock_info_dict = st.session_state.cache_stock_day_bar["stock_info_dict"]
            rag_result = st.session_state.cache_stock_day_bar["rag_result"]
        if rag_result:
            system_content = BASE_SYSTEM_CONTENT + '\n以下是知识库中检索到的相关内容，请结合一起进行分析'
            for idx, item in enumerate(rag_result):
                system_content += f"\n知识{idx}：{item['text']}"
            user_content = BASE_USER_CONTENT + '结合知识库检索到的内容一起分析'
        else:
            system_content = BASE_SYSTEM_CONTENT
            user_content = BASE_USER_CONTENT
        content = {"img": [{"value": stock_day_bar_img_path}]}
        single_content_qa(img_content=content, system_content=system_content, user_content=user_content)
        st.markdown(
            f"**股票代码**：{stock_id} **股票名称**：{stock_info_dict['name']} "
            f"**行业**：{stock_info_dict['industry']} **地区**：{stock_info_dict['area']} **上市日期**：{stock_info_dict['list_date']}"
        )
        st.image(stock_day_bar_img_path)


stock_kline_analysis()
