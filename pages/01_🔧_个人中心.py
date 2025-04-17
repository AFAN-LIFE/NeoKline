import streamlit as st

st.markdown("# 🔧 个人中心 ")

st.markdown("## 🌐 数据API配置")
if "user_tushare_token" not in st.session_state:
    st.session_state.user_tushare_token = ''
st.markdown('平台当前的数据接口来自Tushare，Tushare是一个免费、开源的python财经数据接口包，已经运营超过10年。使用您自己的tushare token可以不受限制的使用本平台。')
u1, u2 = st.columns([1, 1])
user_tushare_token = u1.text_input('请输入您的tushare token', value=st.session_state.user_tushare_token, type='password')
if u2.button('保存', disabled=user_tushare_token == ''):
    st.session_state.user_tushare_token = user_tushare_token
    st.toast('✅保存成功！')
st.markdown('如果您没有tushare token账号，可以通过以下链接注册获取')
st.code('https://tushare.pro/register?reg=afan')