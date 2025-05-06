import time
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from tools.callback import botton_callback
from tools.stock_data import load_stock_basic
from tools.subscribe import get_subscriptions, MAX_SUBSCRIPTION, del_subscription, add_subscription


@st.dialog("添加订阅")
def add_subscription_dialog(subscriptions: list):
    add_form = st.form("add subscription")
    cols = add_form.columns(3)
    type_ = cols[0].selectbox("类型", ["stock"])
    stock_id = cols[1].selectbox("股票", stock_basic_df["ts_code"])
    if cols[-1].form_submit_button("确定", on_click=botton_callback, args=(f"添加订阅 {stock_id}",)):
        try:
            add_subscription(stock_id, type_, subscriptions)
            st.success("订阅成功")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(e)

@st.dialog("删除订阅")
def del_subscription_dialog(subscriptions: list):
    add_form = st.form("del subscription")
    cols = add_form.columns(3)
    type_ = cols[0].selectbox("类型", ["stock"])
    stock_ids = set(item["股票"] for item in subscriptions)
    stock_id = cols[1].selectbox("股票", stock_ids)
    if cols[-1].form_submit_button("确定", on_click=botton_callback, args=(f"删除订阅 {stock_id}",)):
        try:
            del_subscription(stock_id, type_, subscriptions)
            st.success("成功")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(e)

st.markdown("# 🔔订阅管理")

st.markdown('## 🔔股票公告订阅')
st.markdown('订阅后该股票有新公告会以邮件形式发送到您邮箱')
if st.session_state.get("authentication_status"):
    subscriptions = get_subscriptions()
    total_df = pd.DataFrame(subscriptions)
    now = datetime.now()
    if total_df.shape[0] == 0:
        on_df = total_df
        st.badge("当前无订阅股票公告", color='orange')
    else:
        on_df = total_df[total_df["失效时间"] > now]
        if len(subscriptions):
            st.dataframe(on_df)
        else:
            st.badge("当前无订阅股票公告", color='orange')

    stock_basic_df = load_stock_basic()
    bts = st.columns(3)
    if len(on_df) < MAX_SUBSCRIPTION:
        if bts[0].button("添加订阅"):
            add_subscription_dialog(subscriptions)

    if len(on_df) > 0:
        if bts[1].button("删除订阅"):
            del_subscription_dialog(subscriptions)
else:
    st.badge('请先登录后再管理订阅', color='orange')