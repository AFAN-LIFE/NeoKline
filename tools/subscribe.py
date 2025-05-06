import streamlit as st
from sqlalchemy import text
from datetime import datetime, timedelta

MAX_SUBSCRIPTION = 3  # 最大订阅数

def _get_subscriptions():
    if not st.session_state.get("authentication_status"):
        return
    username = st.session_state.get("username")
    sql = f"SELECT subscription_type as 类型,stock_id as 股票,start_time as 生效时间,end_time as 失效时间 FROM public.subscriptions where username='{username}';"
    conn = st.session_state["db"]
    df = conn.query(sql)
    subscriptions = df.to_dict("records")
    return subscriptions


@st.cache_resource
def get_subscriptions():
    return _get_subscriptions()


def add_subscription(stock_id: str, type_: str, subscriptions: list):
    if len(subscriptions) >= MAX_SUBSCRIPTION:
        raise ValueError("订阅数超过3个！")
    stock_ids = set(item["股票"] for item in subscriptions)
    if stock_id in stock_ids:
        raise ValueError("该股票已经订阅，请重新选择")
    now = datetime.now()
    item = {"类型": type_, "股票": stock_id, "生效时间": now, "失效时间": now + timedelta(days=30)}
    with st.session_state["db"].session as s:
        username = st.session_state.get("username")
        sql = "INSERT INTO public.subscriptions (username,subscription_type,stock_id,start_time,end_time) values (:username,:类型,:股票,:生效时间,:失效时间)"
        params = dict(username=username, **item)
        s.execute(text(sql), params=params)
        s.commit()
    subscriptions.append(item)

def del_subscription(stock_id: str, type_: str, subscriptions: list):
    with st.session_state["db"].session as s:
        username = st.session_state.get("username")
        sql = f"DELETE FROM public.subscriptions WHERE username='{username}' and subscription_type='{type_}' and stock_id='{stock_id}'"
        s.execute(text(sql))
        s.commit()
    del_item = None
    for item in subscriptions:
        if item["股票"] == stock_id and item["类型"] == type_:
            del_item = item
    if del_item:
        subscriptions.remove(del_item)
