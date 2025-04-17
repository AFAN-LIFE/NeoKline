import time
import logging
from typing import Callable, Optional

import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator import Helpers, params


class MyAuthenticate(stauth.Authenticate):
    def __init__(self, path: str):
        config = Helpers.read_config_file(path)

        super().__init__(
            path,
            config["cookie"]["name"],
            config["cookie"]["key"],
            config["cookie"]["expiry_days"],
            api_key=config["api_key"],
        )

    # def reset_password_btn(self, clear_on_submit):
    #     action = "重置密码"
    #     if st.sidebar.button(action):
    #         try:
    #             ret = self.reset_password(st.session_state.get("username"), "main", None, clear_on_submit)
    #             logging.warning(ret)
    #             if ret is True:
    #                 st.success(f"{action}成功")
    #             elif ret is False:
    #                 st.warning(f"{action}失败")
    #         except Exception as e:
    #             st.error(e)

    # def login(
    #     self,
    #     max_concurrent_users: Optional[int] = None,
    #     max_login_attempts: Optional[int] = None,
    #     captcha: bool = False,
    #     single_session: bool = False,
    #     clear_on_submit: bool = True,
    #     key: str = "Login",
    #     callback: Optional[Callable] = None,
    # ) -> bool:
    #     """
    #     max_concurrent_users : int, optional
    #         Maximum number of users allowed to log in concurrently.
    #     max_login_attempts : int, optional
    #         Maximum number of failed login attempts allowed.
    #     captcha : bool, default=False
    #         If True, requires captcha validation.
    #     single_session : bool, default=False
    #         If True, prevents users from logging into multiple sessions simultaneously.
    #     clear_on_submit : bool, default=False
    #         If True, clears input fields after form submission.
    #     key : str, default='Login'
    #         Unique key for the widget to prevent duplicate WidgetID errors.
    #     callback : Callable, optional
    #         Function to execute when the form is submitted.
    #     """
    #     if not st.session_state["authentication_status"]:
    #         token = self.cookie_controller.get_cookie()
    #         if token:
    #             self.authentication_controller.login(token=token)
    #         time.sleep(self.attrs.get("login_sleep_time", params.PRE_LOGIN_SLEEP_TIME))
    #     if st.session_state["authentication_status"]:
    #         self.logout("登出", "sidebar")
    #         self.reset_password_btn(clear_on_submit)
    #         return True
    #     ct = st.empty()
    #     login_form = ct.form(key, clear_on_submit=clear_on_submit)
    #     login_form.subheader("登陆")
    #     username = login_form.text_input("用户名", autocomplete="off")
    #     password = login_form.text_input("密码", type="password", autocomplete="off")
    #     entered_captcha = login_form.text_input("验证码", autocomplete="off")
    #     login_form.image(Helpers.generate_captcha("login_captcha", self.secret_key))

    #     if login_form.form_submit_button("登陆"):
    #         try:
    #             if self.authentication_controller.login(
    #                 username,
    #                 password,
    #                 max_concurrent_users,
    #                 max_login_attempts,
    #                 single_session=single_session,
    #                 callback=callback,
    #                 captcha=captcha,
    #                 entered_captcha=entered_captcha,
    #             ):
    #                 self.cookie_controller.set_cookie()
    #                 if self.path and self.cookie_controller.get_cookie():
    #                     st.rerun()
    #         except Exception as e:
    #             login_form.error(e)

    #     if st.sidebar.button("注册"):
    #         ct.empty()
    #         fields = {
    #             "Form name": "用户注册",
    #             "First name": "名",
    #             "Last name": "姓",
    #             "Email": "邮箱",
    #             "Username": "用户名",
    #             "Password": "密码",
    #             "Repeat password": "重复密码",
    #             "Password hint": "提示",
    #             "Captcha": "验证码",
    #             "Register": "注册",
    #             "Dialog name": "验证码",
    #             "Code": "验证码",
    #             "Submit": "提交",
    #             "Error": "验证码错误",
    #         }
    #         email_of_registered_user, username_of_registered_user, name_of_registered_user = self.register_user(
    #             "main", None, None, fields, captcha, two_factor_auth=True, clear_on_submit=clear_on_submit
    #         )
    #         if email_of_registered_user:
    #             st.success("注册成功")
    #         return
    #     if st.sidebar.button("忘记密码"):
    #         ct.empty()
    #         self.forgot_password(
    #             "忘记密码", None, captcha, send_email=True, two_factor_auth=True, clear_on_submit=clear_on_submit
    #         )
    #         return
    #     if st.session_state.get("authentication_status") is False:
    #         st.error("用户名密码错误")
    #     elif st.session_state.get("authentication_status") is None:
    #         st.warning("请输入用户名密码")
