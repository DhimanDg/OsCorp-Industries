from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivy.uix.screenmanager import Screen

from persistence import (
    authenticate_login,
    get_login_username,
    login_account_exists,
    save_login_credentials,
)


class LoginScreen(Screen):
    bg_color = ListProperty([0.18, 0.42, 0.43, 1])
    card_color = ListProperty([0.97, 0.98, 0.96, 1])
    text_color = ListProperty([0.09, 0.12, 0.13, 1])
    muted_color = ListProperty([0.40, 0.45, 0.45, 1])
    header_color = ListProperty([1, 1, 1, 1])
    field_bg = ListProperty([1, 1, 1, 1])
    field_text = ListProperty([0.09, 0.12, 0.13, 1])
    field_hint = ListProperty([0.50, 0.55, 0.55, 1])
    button_color = ListProperty([0.16, 0.36, 0.38, 1])
    success_color = ListProperty([0.18, 0.55, 0.38, 1])
    danger_color = ListProperty([0.72, 0.20, 0.22, 1])

    setup_mode = BooleanProperty(False)
    title_text = StringProperty("Welcome Back")
    subtitle_text = StringProperty("Sign in to continue")
    action_text = StringProperty("Sign In")
    status_text = StringProperty("")

    def __init__(self, app_state, **kwargs):
        super().__init__(**kwargs)
        self.app_state = app_state

    def on_pre_enter(self):
        self._refresh_mode()
        if "username" in self.ids:
            self.ids.username.text = get_login_username()
        if "password" in self.ids:
            self.ids.password.text = ""
        self.status_text = ""

    def _refresh_mode(self):
        self.setup_mode = not login_account_exists()
        if self.setup_mode:
            self.title_text = "Create Login"
            self.subtitle_text = "Set up local access"
            self.action_text = "Create Account"
        else:
            self.title_text = "Welcome Back"
            self.subtitle_text = "Sign in to continue"
            self.action_text = "Sign In"

    def submit(self):
        username = self.ids.username.text
        password = self.ids.password.text

        if self.setup_mode:
            ok, message = save_login_credentials(username, password)
            self.status_text = message
            if ok:
                self.manager.current = "dashboard"
            return

        if authenticate_login(username, password):
            self.status_text = ""
            self.manager.current = "dashboard"
        else:
            self.status_text = "Username or password is incorrect."

    def apply_theme(self, colors):
        self.bg_color = colors["bg"]
        self.card_color = colors["card_bg"]
        self.text_color = colors["text"]
        self.muted_color = colors.get("muted_text", colors["text"])
        self.header_color = colors.get("header_text", [1, 1, 1, 1])
        self.field_bg = colors.get("field_bg", [1, 1, 1, 1])
        self.field_text = colors.get("field_text", colors["text"])
        self.field_hint = colors.get("field_hint", [0.5, 0.5, 0.5, 1])
        self.button_color = colors.get("button", [0.16, 0.36, 0.38, 1])
        self.success_color = colors.get("success", [0.18, 0.55, 0.38, 1])
        self.danger_color = colors.get("danger", [0.72, 0.20, 0.22, 1])


Builder.load_file("Pages/login.kv")
