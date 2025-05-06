from datetime import datetime

import streamlit as st
from streamlit import runtime
from sqlalchemy import text
from streamlit.runtime.scriptrunner import get_script_run_ctx

# https://discuss.streamlit.io/t/streamlit-get-the-client-ip-address/55299


def get_client_ip():
    ctx = get_script_run_ctx()
    session_info = runtime.get_instance().get_client(ctx.session_id)
    remote_ip = session_info.request.remote_ip  # 由于nginx反向代理可能都为127.0.0.1
    remote_ip = session_info.request.headers.get("X-Forwarded-For", remote_ip)
    return remote_ip


def botton_callback(label: str, *args, **kwargs):
    username = st.session_state.get("username")
    ip = get_client_ip()
    now = datetime.now()
    print(f"{now} {username}({ip}) 点击了 {label}")
    conn = st.session_state.get("db")
    if not conn:
        return
    try:
        with conn.session as s:
            sql = f"INSERT INTO public.action_log (time,username,action,addr) values ('{now}', '{username}','{label}', '{ip}')"
            s.execute(text(sql))
            s.commit()
    except Exception:
        pass


# 注册/重置密码的数据库操作
def db_callback(data: dict):
    if data["widget"] == "Register user":
        username = data["new_username"]
        info = st.session_state["credentials"]["usernames"][username]
        with st.session_state["db"].session as s:
            sql = "INSERT INTO public.user (username,email,first_name,last_name,logged_in,password) values (:username,:email,:first_name,:last_name,:logged_in,:password)"
            params = dict(username=username, **info)
            s.execute(text(sql), params=params)
            s.commit()

    elif data["widget"] in ("Reset password", "Forgot password"):
        username = data["username"]
        password = st.session_state["credentials"]["usernames"][username]["password"]
        with st.session_state["db"].session as s:
            sql = f"UPDATE public.user SET password='{password}' WHERE username='{username}'"
            s.execute(text(sql))
            s.commit()
    # print(data)
