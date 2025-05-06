import json
import time
from typing import Any, Dict, List, Tuple, Union, Literal, Callable, Optional
from datetime import datetime, timedelta

import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator import params
from streamlit_authenticator.utilities import (
    Helpers,
    Encryptor,
    Validator,
    LoginError,
    ForgotError,
    RegisterError,
    DeprecationError,
)
from streamlit_authenticator.controllers import CookieController, AuthenticationController


class MyAuthenticationController(AuthenticationController):
    def check_register_user(
        self,
        new_first_name: str,
        new_last_name: str,
        new_email: str,
        new_username: str,
        new_password: str,
        new_password_repeat: str,
        password_hint: str,
        pre_authorized: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        roles: Optional[List[str]] = None,
        callback: Optional[Callable] = None,
        captcha: bool = False,
        entered_captcha: Optional[str] = None,
    ):
        if not self.validator.validate_email(new_email):
            raise RegisterError("Email is not valid")
        if domains and new_email.split("@")[-1] not in domains:
            raise RegisterError("Email domain is not allowed to register")
        if not self.validator.validate_username(new_username):
            raise RegisterError("Username is not valid")
        if not self.validator.validate_length(new_password, 1) or not self.validator.validate_length(
            new_password_repeat, 1
        ):
            raise RegisterError("Password/repeat password fields cannot be empty")
        if new_password != new_password_repeat:
            raise RegisterError("Passwords do not match")
        if password_hint and not self.validator.validate_length(password_hint, 1):
            raise RegisterError("Password hint cannot be empty")
        if not self.validator.validate_password(new_password):
            raise RegisterError(self.validator.diagnose_password(new_password))
        if roles and not isinstance(roles, list):
            raise LoginError("Roles must be provided as a list")
        if captcha:
            if not entered_captcha:
                raise RegisterError("Captcha not entered")
            entered_captcha = entered_captcha.strip()
            self._check_captcha("register_user_captcha", RegisterError, entered_captcha)
        if self.authentication_model._credentials_contains_value(new_email):
            raise RegisterError("Email already taken")
        if new_username in self.authentication_model.credentials["usernames"]:
            raise RegisterError("Username/email already taken")

    def register_user(
        self,
        new_first_name: str,
        new_last_name: str,
        new_email: str,
        new_username: str,
        new_password: str,
        new_password_repeat: str,
        password_hint: str,
        pre_authorized: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        roles: Optional[List[str]] = None,
        callback: Optional[Callable] = None,
        captcha: bool = False,
        entered_captcha: Optional[str] = None,
    ) -> Tuple[str, str, str]:
        """
        Handles user registration requests.

        Parameters
        ----------
        new_first_name: str
            First name of the new user.
        new_last_name: str
            Last name of the new user.
        new_email: str
            Email of the new user.
        new_username: str
            Username of the new user.
        new_password: str
            Password of the new user.
        new_password_repeat: str
            Repeated password of the new user.
        password_hint: str
            A hint for remembering the password.
        pre-authorized: list, optional
            List of emails of unregistered users who are authorized to register.
        domains: list, optional
            Required list of domains a new email must belong to i.e. ['gmail.com', 'yahoo.com'],
            list: the required list of domains,
            None: any domain is allowed.
        roles: list, optional
            User roles for registered users.
        callback : Callable, optional
            Function to be executed upon successful login.
        captcha : bool, default=False
            If True, a captcha check is required.
        entered_captcha : str, optional
            User-entered captcha value for validation.

        Returns
        -------
        Tuple[str, str, str]
            Tuple containing (email, username, full name).
        """
        self.check_register_user(
            new_first_name,
            new_last_name,
            new_email,
            new_username,
            new_password,
            new_password_repeat,
            password_hint,
            pre_authorized,
            domains,
            roles,
            callback,
            False,
            entered_captcha,
        )
        return self.authentication_model.register_user(
            new_first_name,
            new_last_name,
            new_email,
            new_username,
            new_password,
            password_hint,
            pre_authorized,
            roles,
            callback,
        )


class MyAuthenticate(stauth.Authenticate):
    """
    This class renders login, logout, register user, reset password, forgot password,
    forgot username, and modify user details widgets.
    """

    def __init__(
        self,
        credentials: Union[Dict[str, Any], str],
        cookie_name: str = "some_cookie_name",
        cookie_key: str = "some_key",
        cookie_expiry_days: float = 30.0,
        validator: Optional[Validator] = None,
        auto_hash: bool = True,
        api_key: Optional[str] = None,
        **kwargs: Optional[Dict[str, Any]],
    ) -> None:
        """
        Initializes an instance of Authenticate.

        Parameters
        ----------
        credentials : dict or str
            Dictionary of user credentials or path to a configuration file.
        cookie_name : str, default='some_cookie_name'
            Name of the re-authentication cookie stored in the client's browser.
        cookie_key : str, default='some_key'
            Secret key used for encrypting the re-authentication cookie.
        cookie_expiry_days : float, default=30.0
            Expiry time for the re-authentication cookie in days.
        validator : Validator, optional
            Validator object for checking username, name, and email validity.
        auto_hash : bool, default=True
            If True, passwords will be automatically hashed.
        api_key : str, optional
            API key for sending password reset and authentication emails.
        **kwargs : dict, optional
            Additional keyword arguments.
        """
        self.api_key = api_key
        self.attrs = kwargs
        self.secret_key = cookie_key
        if isinstance(validator, dict):
            raise DeprecationError(f"""Please note that the 'pre_authorized' parameter has been
                                   removed from the Authenticate class and added directly to the
                                   'register_user' function. For further information please refer to
                                   {params.REGISTER_USER_LINK}.""")
        self.path = credentials if isinstance(credentials, str) else None
        self.cookie_controller = CookieController(cookie_name, cookie_key, cookie_expiry_days, self.path)
        self.authentication_controller = MyAuthenticationController(
            credentials, validator, auto_hash, self.path, self.api_key, self.secret_key, self.attrs.get("server_url")
        )
        self.encryptor = Encryptor(self.secret_key)

    def forgot_password(
        self,
        location: Literal["main", "sidebar"] = "main",
        fields: Optional[Dict[str, str]] = None,
        captcha: bool = False,
        send_email: bool = False,
        two_factor_auth: bool = False,
        clear_on_submit: bool = False,
        key: str = "Forgot password",
        callback: Optional[Callable] = None,
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Renders a forgot password widget.

        Parameters
        ----------
        location : {'main', 'sidebar'}, default='main'
            Location of the forgot password widget.
        fields : dict, optional
            Custom labels for form fields and buttons.
        captcha : bool, default=False
            If True, requires captcha validation.
        send_email : bool, default=False
            If True, sends the new password to the user's email.
        two_factor_auth : bool, default=False
            If True, enables two-factor authentication.
        clear_on_submit : bool, default=False
            If True, clears input fields after form submission.
        key : str, default='Forgot password'
            Unique key for the widget to prevent duplicate WidgetID errors.
        callback : Callable, optional
            Function to be executed after form submission.

        Returns
        -------
        tuple[str, str, str] or (None, None, None)
            - Username associated with the forgotten password.
            - Email associated with the forgotten password.
            - New plain-text password to be securely transferred to the user.
        """
        if fields is None:
            fields = {
                "Form name": "Forgot password",
                "Username": "Username",
                "Captcha": "Captcha",
                "Submit": "Submit",
                "Dialog name": "Verification code",
                "Code": "Code",
                "Error": "Code is incorrect",
            }
        if location not in ["main", "sidebar"]:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == "main":
            forgot_password_form = st.form(key=key, clear_on_submit=clear_on_submit)
        elif location == "sidebar":
            forgot_password_form = st.sidebar.form(key=key, clear_on_submit=clear_on_submit)
        forgot_password_form.subheader(fields.get("Form name", "Forgot password"))
        username = forgot_password_form.text_input(fields.get("Username", "Username"), autocomplete="off")
        entered_captcha = None
        if captcha:
            entered_captcha = forgot_password_form.text_input(fields.get("Captcha", "Captcha"), autocomplete="off")
            cols = forgot_password_form.columns(5)
            captcha_name = "forgot_password_captcha"
            if cols[1].form_submit_button("刷新") and st.session_state.get(captcha_name):
                del st.session_state[captcha_name]
            cols[0].image(Helpers.generate_captcha(captcha_name, self.secret_key))

        result = (None, None, None)
        b1, b2 = forgot_password_form.columns(2)
        if b2.form_submit_button("返回登陆"):
            st.session_state["first_page"] = "登陆"
            st.rerun()
        if b1.form_submit_button(fields.get("Submit", "Submit")):
            result = self.authentication_controller.forgot_password(username, callback, captcha, entered_captcha)
            if not two_factor_auth:
                if send_email:
                    self.authentication_controller.send_password(result)
                return result
            self.__two_factor_auth(result[1], result, widget="forgot_password", fields=fields)
        if two_factor_auth and st.session_state.get("2FA_check_forgot_password"):
            decrypted = self.encryptor.decrypt(st.session_state["2FA_content_forgot_password"])
            result = json.loads(decrypted)
            if send_email:
                self.authentication_controller.send_password(result)
            del st.session_state["2FA_check_forgot_password"]
            return result

        return None, None, None

    def login(
        self,
        location: Literal["main", "sidebar", "unrendered"] = "main",
        max_concurrent_users: Optional[int] = None,
        max_login_attempts: Optional[int] = None,
        fields: Optional[Dict[str, str]] = None,
        captcha: bool = False,
        single_session: bool = False,
        clear_on_submit: bool = False,
        key: str = "Login",
        callback: Optional[Callable] = None,
    ) -> Optional[Tuple[Optional[str], Optional[bool], Optional[str]]]:
        """
        Renders a login widget.

        Parameters
        ----------
        location : {'main', 'sidebar', 'unrendered'}, default='main'
            Location where the login widget is rendered.
        max_concurrent_users : int, optional
            Maximum number of users allowed to log in concurrently.
        max_login_attempts : int, optional
            Maximum number of failed login attempts allowed.
        fields : dict, optional
            Custom labels for form fields and buttons.
        captcha : bool, default=False
            If True, requires captcha validation.
        single_session : bool, default=False
            If True, prevents users from logging into multiple sessions simultaneously.
        clear_on_submit : bool, default=False
            If True, clears input fields after form submission.
        key : str, default='Login'
            Unique key for the widget to prevent duplicate WidgetID errors.
        callback : Callable, optional
            Function to execute when the form is submitted.

        Returns
        -------
        tuple[str, bool, str] or None
            - If `location='unrendered'`, returns (user's name, authentication status, username).
            - Otherwise, returns None.
        """
        if fields is None:
            fields = {
                "Form name": "Login",
                "Username": "Username",
                "Password": "Password",
                "Login": "Login",
                "Captcha": "Captcha",
            }
        if location not in ["main", "sidebar", "unrendered"]:
            raise ValueError("Location must be one of 'main' or 'sidebar' or 'unrendered'")
        if not st.session_state.get("authentication_status"):
            token = self.cookie_controller.get_cookie()
            if token:
                self.authentication_controller.login(token=token)
            time.sleep(self.attrs.get("login_sleep_time", params.PRE_LOGIN_SLEEP_TIME))
            if not st.session_state.get("authentication_status"):
                if location == "main":
                    login_form = st.form(key=key, clear_on_submit=clear_on_submit)
                elif location == "sidebar":
                    login_form = st.sidebar.form(key=key, clear_on_submit=clear_on_submit)
                elif location == "unrendered":
                    return (
                        st.session_state["name"],
                        st.session_state["authentication_status"],
                        st.session_state["username"],
                    )
                login_form.subheader("Login" if "Form name" not in fields else fields["Form name"])
                username = login_form.text_input(
                    "Username" if "Username" not in fields else fields["Username"], autocomplete="off"
                )
                if "password_hint" in st.session_state:
                    password = login_form.text_input(
                        "Password" if "Password" not in fields else fields["Password"],
                        type="password",
                        help=st.session_state["password_hint"],
                        autocomplete="off",
                    )
                else:
                    password = login_form.text_input(
                        "Password" if "Password" not in fields else fields["Password"],
                        type="password",
                        autocomplete="off",
                    )
                entered_captcha = None
                if captcha:
                    entered_captcha = login_form.text_input(fields.get("Captcha", "Captcha"), autocomplete="off")
                    cols = login_form.columns(5)
                    captcha_name = "login_captcha"
                    if cols[1].form_submit_button("刷新") and st.session_state.get(captcha_name):
                        del st.session_state[captcha_name]
                    cols[0].image(Helpers.generate_captcha(captcha_name, self.secret_key))
                b1, b2, b3 = login_form.columns(3)
                if b1.form_submit_button("Login" if "Login" not in fields else fields["Login"]):
                    credentials = self.authentication_controller.authentication_model.credentials
                    failed_login_attempts = credentials["usernames"].get(username, {}).get("failed_login_attempts", 0)
                    now = datetime.now()
                    if failed_login_attempts != 0:
                        last_failed_time = credentials["usernames"].get(username, {}).get("last_failed_time", now)
                        if (now - last_failed_time) > timedelta(minutes=5):
                            credentials["usernames"].get(username, {})["last_failed_time"] = now
                            credentials["usernames"].get(username, {})["failed_login_attempts"] = 0
                    try:
                        logined = self.authentication_controller.login(
                            username,
                            password,
                            max_concurrent_users,
                            max_login_attempts,
                            single_session=single_session,
                            callback=callback,
                            captcha=captcha,
                            entered_captcha=entered_captcha,
                        )
                    except LoginError as e:
                        credentials["usernames"].get(username, {})["last_failed_time"] = now
                        raise e
                    if logined:
                        if credentials["usernames"].get(username, {}).get("last_failed_time", None):
                            del credentials["usernames"].get(username, {})["last_failed_time"]
                        self.cookie_controller.set_cookie()
                        if self.path and self.cookie_controller.get_cookie():
                            st.rerun()
                if b2.form_submit_button("注册"):
                    st.session_state["first_page"] = "注册"
                    st.rerun()
                if b3.form_submit_button("忘记密码"):
                    st.session_state["first_page"] = "忘记密码"
                    st.rerun()

    def register_user(
        self,
        location: Literal["main", "sidebar"] = "main",
        pre_authorized: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        fields: Optional[Dict[str, str]] = None,
        captcha: bool = True,
        roles: Optional[List[str]] = None,
        merge_username_email: bool = False,
        password_hint: bool = True,
        two_factor_auth: bool = False,
        clear_on_submit: bool = False,
        key: str = "Register user",
        callback: Optional[Callable] = None,
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Renders a register new user widget.

        Parameters
        ----------
        location : {'main', 'sidebar'}, default='main'
            Location where the registration widget is rendered.
        pre_authorized : list of str, optional
            List of emails of unregistered users who are authorized to register.
        domains : list of str, optional
            List of allowed email domains (e.g., ['gmail.com', 'yahoo.com']).
        fields : dict, optional
            Custom labels for form fields and buttons.
        captcha : bool, default=True
            If True, requires captcha validation.
        roles : list of str, optional
            User roles for registered users.
        merge_username_email : bool, default=False
            If True, uses the email as the username.
        password_hint : bool, default=True
            If True, includes a password hint field.
        two_factor_auth : bool, default=False
            If True, enables two-factor authentication.
        clear_on_submit : bool, default=False
            If True, clears input fields after form submission.
        key : str, default='Register user'
            Unique key for the widget to prevent duplicate WidgetID errors.
        callback : Callable, optional
            Function to execute when the form is submitted.

        Returns
        -------
        tuple[str, str, str] or (None, None, None)
            - Email associated with the new user.
            - Username associated with the new user.
            - Name associated with the new user.
        """
        if isinstance(pre_authorized, bool) or isinstance(pre_authorized, dict):
            raise DeprecationError(f"""Please note that the 'pre_authorized' parameter now
                                   requires a list of pre-authorized emails. For further
                                   information please refer to {params.REGISTER_USER_LINK}.""")
        if fields is None:
            fields = {
                "Form name": "Register user",
                "First name": "First name",
                "Last name": "Last name",
                "Email": "Email",
                "Username": "Username",
                "Password": "Password",
                "Repeat password": "Repeat password",
                "Password hint": "Password hint",
                "Captcha": "Captcha",
                "Register": "Register",
                "Dialog name": "Verification code",
                "Code": "Code",
                "Submit": "Submit",
                "Error": "Code is incorrect",
            }
        if location not in ["main", "sidebar"]:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == "main":
            register_user_form = st.form(key=key, clear_on_submit=clear_on_submit)
        elif location == "sidebar":
            register_user_form = st.sidebar.form(key=key, clear_on_submit=clear_on_submit)
        register_user_form.subheader("Register user" if "Form name" not in fields else fields["Form name"])
        col1_1, col2_1 = register_user_form.columns(2)
        if merge_username_email:
            new_email = register_user_form.text_input(
                "Email" if "Email" not in fields else fields["Email"], autocomplete="off"
            )
            new_username = new_email
        else:
            new_email = col1_1.text_input("Email" if "Email" not in fields else fields["Email"], autocomplete="off")
            new_username = col2_1.text_input(
                "Username" if "Username" not in fields else fields["Username"], autocomplete="off"
            )
        new_first_name = new_username
        new_last_name = new_username
        col1_2, col2_2 = register_user_form.columns(2)
        password_instructions = self.attrs.get("password_instructions", params.PASSWORD_INSTRUCTIONS)
        new_password = col1_2.text_input(
            "Password" if "Password" not in fields else fields["Password"],
            type="password",
            help=password_instructions,
            autocomplete="off",
        )
        new_password_repeat = col2_2.text_input(
            "Repeat password" if "Repeat password" not in fields else fields["Repeat password"],
            type="password",
            autocomplete="off",
        )
        if password_hint:
            password_hint = register_user_form.text_input(
                "Password hint" if "Password hint" not in fields else fields["Password hint"], autocomplete="off"
            )
        entered_captcha = None
        if captcha:
            entered_captcha = register_user_form.text_input(
                fields.get("Captcha", "Captcha"), autocomplete="off"
            ).strip()
            cols = register_user_form.columns(5)
            captcha_name = "register_user_captcha"
            if cols[1].form_submit_button("刷新") and st.session_state.get(captcha_name):
                del st.session_state[captcha_name]
            cols[0].image(Helpers.generate_captcha(captcha_name, self.secret_key))
        new_first_name = new_first_name.strip()
        new_last_name = new_last_name.strip()
        new_email = new_email.strip()
        new_username = new_username.lower().strip()
        new_password = new_password.strip()
        new_password_repeat = new_password_repeat.strip()
        password_hint = password_hint.strip() if password_hint else None

        b1, b2 = register_user_form.columns(2)
        if b2.form_submit_button("返回登陆"):
            st.session_state["first_page"] = "登陆"
            st.rerun()
        if b1.form_submit_button("Register" if "Register" not in fields else fields["Register"]):
            self.authentication_controller.check_register_user(
                new_first_name,
                new_last_name,
                new_email,
                new_username,
                new_password,
                new_password_repeat,
                password_hint,
                pre_authorized,
                domains,
                roles,
                callback,
                captcha,
                entered_captcha,
            )
            if two_factor_auth:
                self.__two_factor_auth(new_email, widget="register", fields=fields)
            else:
                return self.authentication_controller.register_user(
                    new_first_name,
                    new_last_name,
                    new_email,
                    new_username,
                    new_password,
                    new_password_repeat,
                    password_hint,
                    pre_authorized,
                    domains,
                    roles,
                    callback,
                    captcha,
                    entered_captcha,
                )

        if two_factor_auth and st.session_state.get("2FA_check_register"):
            del st.session_state["2FA_check_register"]
            return self.authentication_controller.register_user(
                new_first_name,
                new_last_name,
                new_email,
                new_username,
                new_password,
                new_password_repeat,
                password_hint,
                pre_authorized,
                domains,
                roles,
                callback,
                captcha,
                entered_captcha,
            )

    def __two_factor_auth(
        self,
        email: str,
        content: Optional[Dict[str, Any]] = None,
        fields: Optional[Dict[str, str]] = None,
        widget: Optional[str] = None,
    ) -> None:
        """
        Renders a two-factor authentication widget.

        Parameters
        ----------
        email : str
            Email address to which the two-factor authentication code is sent.
        content : dict, optional
            Optional content to save in session state.
        fields : dict, optional
            Custom labels for form fields and buttons.
        widget : str, optional
            Widget name used as a key in session state variables.
        """
        self.authentication_controller.generate_two_factor_auth_code(email, widget)

        @st.dialog("Verification code" if "Dialog name" not in fields else fields["Dialog name"])
        def two_factor_auth_form():
            code = st.text_input(
                "Code" if "Code" not in fields else fields["Code"],
                help="Please enter the code sent to your email"
                if "Instructions" not in fields
                else fields["Instructions"],
                autocomplete="off",
            )
            if st.button("Submit" if "Submit" not in fields else fields["Submit"]):
                if self.authentication_controller.check_two_factor_auth_code(code, content, widget):
                    st.rerun()
                else:
                    st.error("Code is incorrect" if "Error" not in fields else fields["Error"])

        two_factor_auth_form()
