from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivy.uix.screenmanager import Screen

from persistence import (
    authenticate_login,
    get_security_question,
    get_login_username,
    login_account_exists,
    reset_login_password,
    save_security_answer,
    security_answer_exists,
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
        if "security_answer" in self.ids:
            self.ids.security_answer.text = ""
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
            ok, message = save_login_credentials(
                username,
                password,
                self.ids.security_answer.text,
            )
            self.status_text = message
            if ok:
                self.manager.current = "dashboard"
            return

        if authenticate_login(username, password):
            self.status_text = ""
            if security_answer_exists():
                self.manager.current = "dashboard"
            else:
                self.show_security_setup_popup()
        else:
            self.status_text = "Username or password is incorrect."

    def password_enter(self):
        if self.setup_mode:
            self.ids.security_answer.focus = True
        else:
            self.submit()

    def show_security_setup_popup(self):
        from kivy.metrics import dp
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.uix.popup import Popup
        from kivy.uix.textinput import TextInput

        username = get_login_username()
        layout = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        layout.add_widget(Label(
            text="Set your security answer before continuing.",
            color=self.text_color,
            size_hint_y=None,
            height=dp(34),
            halign="center",
            valign="middle",
        ))
        layout.add_widget(Label(
            text=get_security_question(),
            color=self.text_color,
            size_hint_y=None,
            height=dp(42),
            halign="center",
            valign="middle",
        ))

        answer_input = TextInput(
            hint_text="Answer",
            multiline=False,
            size_hint_y=None,
            height=dp(42),
            background_normal="",
            background_active="",
            background_color=self.field_bg,
            foreground_color=self.field_text,
            hint_text_color=self.field_hint,
            cursor_color=self.field_text,
            write_tab=False,
        )
        status_label = Label(
            text="",
            color=self.danger_color,
            size_hint_y=None,
            height=dp(24),
            halign="center",
            valign="middle",
        )
        status_label.bind(size=lambda inst, value: setattr(inst, "text_size", value))

        buttons = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        save_btn = Button(
            text="Save Answer",
            background_normal="",
            background_down="",
            background_color=self.button_color,
            color=(1, 1, 1, 1),
        )
        cancel_btn = Button(
            text="Cancel",
            background_normal="",
            background_down="",
            background_color=self.button_color,
            color=(1, 1, 1, 1),
        )

        def save_answer(instance):
            ok, message = save_security_answer(username, answer_input.text)
            status_label.color = self.success_color if ok else self.danger_color
            status_label.text = message
            if ok:
                self.status_text = message
                popup.dismiss()
                self.manager.current = "dashboard"

        save_btn.bind(on_press=save_answer)
        cancel_btn.bind(on_press=lambda instance: popup.dismiss())
        buttons.add_widget(save_btn)
        buttons.add_widget(cancel_btn)

        layout.add_widget(answer_input)
        layout.add_widget(status_label)
        layout.add_widget(buttons)

        popup = Popup(
            title="Security Question",
            content=layout,
            size_hint=(0.82, None),
            height=dp(300),
        )
        popup.open()

    def show_reset_password_popup(self):
        if self.setup_mode:
            self.status_text = "Create an account first."
            return

        from kivy.metrics import dp
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.uix.popup import Popup
        from kivy.uix.textinput import TextInput

        layout = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        layout.add_widget(Label(
            text="Answer your security question to reset your password.",
            color=self.text_color,
            size_hint_y=None,
            height=dp(34),
            halign="center",
            valign="middle",
        ))

        username_input = TextInput(
            text=get_login_username(),
            hint_text="Username",
            multiline=False,
            size_hint_y=None,
            height=dp(42),
            background_normal="",
            background_active="",
            background_color=self.field_bg,
            foreground_color=self.field_text,
            hint_text_color=self.field_hint,
            cursor_color=self.field_text,
            write_tab=False,
        )
        question_label = Label(
            text=get_security_question(),
            color=self.text_color,
            size_hint_y=None,
            height=dp(42),
            halign="center",
            valign="middle",
        )
        answer_input = TextInput(
            hint_text="Security answer",
            multiline=False,
            size_hint_y=None,
            height=dp(42),
            background_normal="",
            background_active="",
            background_color=self.field_bg,
            foreground_color=self.field_text,
            hint_text_color=self.field_hint,
            cursor_color=self.field_text,
            write_tab=False,
        )
        password_input = TextInput(
            hint_text="New password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(42),
            background_normal="",
            background_active="",
            background_color=self.field_bg,
            foreground_color=self.field_text,
            hint_text_color=self.field_hint,
            cursor_color=self.field_text,
            write_tab=False,
        )
        confirm_input = TextInput(
            hint_text="Confirm new password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(42),
            background_normal="",
            background_active="",
            background_color=self.field_bg,
            foreground_color=self.field_text,
            hint_text_color=self.field_hint,
            cursor_color=self.field_text,
            write_tab=False,
        )
        status_label = Label(
            text="",
            color=self.danger_color,
            size_hint_y=None,
            height=dp(24),
            halign="center",
            valign="middle",
        )
        status_label.bind(size=lambda inst, value: setattr(inst, "text_size", value))

        buttons = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        save_btn = Button(
            text="Save Password",
            background_normal="",
            background_down="",
            background_color=self.button_color,
            color=(1, 1, 1, 1),
        )
        cancel_btn = Button(
            text="Cancel",
            background_normal="",
            background_down="",
            background_color=self.button_color,
            color=(1, 1, 1, 1),
        )

        def do_reset(instance):
            ok, message = reset_login_password(
                username_input.text,
                answer_input.text,
                password_input.text,
                confirm_input.text,
            )
            status_label.color = self.success_color if ok else self.danger_color
            status_label.text = message
            if ok:
                self.ids.username.text = username_input.text.strip()
                self.ids.password.text = ""
                self.status_text = message
                popup.dismiss()

        save_btn.bind(on_press=do_reset)
        cancel_btn.bind(on_press=lambda instance: popup.dismiss())
        buttons.add_widget(save_btn)
        buttons.add_widget(cancel_btn)

        layout.add_widget(username_input)
        layout.add_widget(question_label)
        layout.add_widget(answer_input)
        layout.add_widget(password_input)
        layout.add_widget(confirm_input)
        layout.add_widget(status_label)
        layout.add_widget(buttons)

        popup = Popup(
            title="Reset Password",
            content=layout,
            size_hint=(0.82, None),
            height=dp(420),
        )
        popup.open()

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
