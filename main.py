import streamlit as st

from config import ST_AUTHENTICATE_KEY
from authenticate import MyAuthenticate
from tools.callback import db_callback


@st.cache_resource
def get_db_conn():
    conn = st.connection("postgresql", type="sql")
    return conn


@st.cache_resource
def get_credentials():
    sql = "SELECT username,email,first_name,last_name,failed_login_attempts,logged_in,password,roles FROM public.user;"
    df = conn.query(sql)
    credentials = {}
    credentials["usernames"] = {item["username"]: item for item in df.to_dict("records")}
    return credentials


conn = get_db_conn()
st.session_state["db"] = conn
credentials = get_credentials()
st.session_state["credentials"] = credentials
authenticator = MyAuthenticate(credentials, "auth", "NeoKline", 1, api_key=ST_AUTHENTICATE_KEY)

if not st.session_state.get("authentication_status"):  # 把登录状态存在了浏览器的缓存LocalMemory
    token = authenticator.cookie_controller.get_cookie()
    if token:
        authenticator.authentication_controller.login(token=token)


def login():
    fields = {"Form name": "登陆", "Username": "用户名", "Password": "密码", "Login": "登陆", "Captcha": "验证码"}
    try:
        authenticator.login(fields=fields, captcha=True, max_login_attempts=3, callback=db_callback)
    except Exception as e:
        st.error(e)
    if st.session_state.get("authentication_status") is False:
        st.error("用户名密码错误")


def logout():
    authenticator.logout("登出", location="unrendered")


def reset_password():
    action = "重置密码"
    fields = {
        "Form name": action,
        "Current password": "当前密码",
        "New password": "新密码",
        "Repeat password": "重复密码",
        "Reset": "重置",
    }
    try:
        ret = authenticator.reset_password(st.session_state.get("username"), fields=fields, callback=db_callback)
        if ret is True:
            st.success(f"{action}成功")
        elif ret is False:
            st.warning(f"{action}失败")
    except Exception as e:
        st.error(e)


def forget_password():
    action = "忘记密码"
    fields = {
        "Form name": action,
        "Username": "用户名",
        "Captcha": "验证码",
        "Submit": "提交",
        "Dialog name": "邮箱验证码校验",
        "Code": "请输入您邮箱收到的验证码",
        "Error": "验证码错误",
    }
    try:
        ret = authenticator.forgot_password(
            "main", fields, captcha=True, send_email=True, two_factor_auth=True, callback=db_callback
        )
        if ret[0]:
            st.success("密码重置成功，请登陆邮箱查看密码")
    except Exception as e:
        st.error(e)


def register():
    fields = {
        "Form name": "用户注册",
        "Email": "邮箱（用于验证/订阅服务）",
        "Username": "用户名（登录账号）",
        "Password": "密码（格式要求查看问号） ",
        "Repeat password": "重复密码",
        "Password hint": "密码要求：8-20个字符，需包含至少一个小写字母、一个大写字母和一个特殊符号（@$!%*?&）",
        "Captcha": "验证码",
        "Register": "注册",
        "Dialog name": "邮箱验证码校验",
        "Code": "请输入您邮箱收到的验证码",
        "Submit": "提交",
        "Error": "验证码错误",
    }
    try:
        r = authenticator.register_user(
            "main", None, None, fields, captcha=True, two_factor_auth=True, callback=db_callback, password_hint=False
        )
        if not r:
            return
        email_of_registered_user, username_of_registered_user, name_of_registered_user = r
        if email_of_registered_user:
            st.success("注册成功")
            # st.switch_page("page/01_🔧_个人中心.py")
    except Exception as e:
        st.error(e)


st.logo("assets/logo-gray.png", icon_image="assets/logo-gray.png")


if not st.session_state.get("authentication_status"):
    login_page = st.Page(login, title="登陆")
    register_page = st.Page(register, title="注册")
    forget_password_page = st.Page(forget_password, title="忘记密码")
    account_pages = [login_page, register_page, forget_password_page]
else:
    logout_page = st.Page(logout, title="登出", icon=":material/logout:")
    reset_password_page = st.Page(reset_password, title="重置密码")
    account_pages = [logout_page, reset_password_page]
introduce_page = [st.Page("page/NeoKline.py", title="🌟NeoKline介绍", default=True)]
function_pages = []
py2pages = [
    {"file": "page/API配置.py", "title": "🌏个人中心"},
    {"file": "page/我的订阅.py", "title": "🔔我的订阅"},
    {"file": "page/知识库管理.py", "title": "📚知识库管理"},
    {"file": "page/股票日线分析.py", "title": "📈股票日线分析"},
    {"file": "page/股票分钟分析.py", "title": "📈股票分钟分析"},
]
for one_page in py2pages:
    function_pages.append(st.Page(one_page["file"], title=one_page["title"]))
pg = st.navigation(
    {
        "首页": introduce_page,
        "账户": account_pages,
        "股票分析": function_pages,
    }
)
pg.run()
