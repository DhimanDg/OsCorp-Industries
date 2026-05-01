import sqlite3
import hashlib
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock

def init_db():
    """Initializes the SQLite database and users table."""
    conn = sqlite3.connect('oscorp.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

# UI COMPONENTS 
class GradientBackground(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._update_canvas, pos=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            steps = 60
            for i in range(steps):
                t = i / steps
                r = 0.910 - t * 0.808
                g = 0.451 - t * 0.412
                b = 0.416 - t * 0.406
                Color(r, g, b, 1)
                slice_h = self.height / steps
                Rectangle(
                    pos=(self.x, self.y + self.height - (i + 1) * slice_h),
                    size=(self.width, slice_h + 1),
                )

class RoundedBox(FloatLayout):
    def __init__(self, bg_color=(1, 1, 1, 1), radius=12, **kwargs):
        super().__init__(**kwargs)
        self._bg_color = bg_color
        self._radius = radius
        self.bind(size=self._draw, pos=self._draw)

    def _draw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])

# LOGIN SCREEN
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        init_db()
        self._mode = 'signup'
        self._build_ui()

    def _build_ui(self):
        from kivy.uix.anchorlayout import AnchorLayout

        root = GradientBackground()
        self.add_widget(root)

        outer = AnchorLayout(anchor_x='center', anchor_y='center')
        root.add_widget(outer)

        col = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(24), dp(20), dp(24), dp(20)],
            size_hint=(None, None),
            width=dp(340),
        )
        col.bind(minimum_height=col.setter('height'))
        outer.add_widget(col)

        def clabel(**kw):
            lbl = Label(**kw)
            lbl.bind(size=lambda w, v: setattr(w, 'text_size', v))
            return lbl

        def crow(widget):
            a = AnchorLayout(
                anchor_x='center', anchor_y='center',
                size_hint_y=None,
                height=widget.height,
            )
            a.add_widget(widget)
            return a

        # App title 
        col.add_widget(clabel(
            text='OsCorp Industries',
            font_size=dp(34),
            bold=True,
            color=(1.0, 0.96, 0.90, 1),
            size_hint=(1, None),
            height=dp(60),
            halign='center',
            valign='middle',
        ))

        from kivy.uix.widget import Widget
        sep = Widget(size_hint=(1, None), height=dp(1))
        with sep.canvas:
            Color(1.0, 0.96, 0.90, 0.35)
            self._sep_rect = Rectangle(pos=sep.pos, size=sep.size)
        sep.bind(
            pos=lambda w, v: setattr(self._sep_rect, 'pos', v),
            size=lambda w, v: setattr(self._sep_rect, 'size', v),
        )
        col.add_widget(sep)

        tab_row = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(36),
            spacing=dp(6),
        )
        col.add_widget(tab_row)

        self.signup_tab = Button(
            text='Create account',
            size_hint=(1, 1),
            bold=True,
            background_normal='',
            background_color=(0.1, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            halign='center',
        )
        self.signup_tab.bind(on_release=lambda *a: self._switch_mode('signup'))
        tab_row.add_widget(self.signup_tab)

        self.signin_tab = Button(
            text='Sign in',
            size_hint=(1, 1),
            bold=True,
            background_normal='',
            background_color=(0.75, 0.75, 0.75, 1),
            color=(0.1, 0.1, 0.1, 1),
            halign='center',
        )
        self.signin_tab.bind(on_release=lambda *a: self._switch_mode('signin'))
        tab_row.add_widget(self.signin_tab)

        self.heading_label = clabel(
            text='Create an account',
            font_size=dp(20),
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint=(1, None),
            height=dp(32),
            halign='center',
            valign='middle',
        )
        col.add_widget(self.heading_label)

        self.subheading_label = clabel(
            text='Enter your email to sign up for this app',
            font_size=dp(13),
            bold=True,
            color=(0.18, 0.35, 0.50, 1),
            size_hint=(1, None),
            height=dp(24),
            halign='center',
            valign='middle',
        )
        col.add_widget(self.subheading_label)

        # Email Input
        self.email_input = TextInput(
            hint_text='email@domain.com',
            multiline=False,
            size_hint=(1, None),
            height=dp(44),
            padding=[dp(10), dp(12)],
        )
        col.add_widget(self.email_input)

        # Password Input 
        self.pass_input = TextInput(
            hint_text='password',
            password=True,
            multiline=False,
            size_hint=(1, None),
            height=dp(44),
            padding=[dp(10), dp(12)],
        )
        col.add_widget(self.pass_input)

        # Primary Action Button
        self.action_btn = Button(
            text='Sign up with email',
            size_hint=(1, None),
            height=dp(48),
            bold=True,
            background_normal='',
            background_color=(0.1, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            halign='center',
        )
        self.action_btn.bind(on_release=self._on_action)
        col.add_widget(self.action_btn)


        # Terms notice 
        col.add_widget(clabel(
            text='By clicking continue, you agree to our [b]Terms of\nService[/b] and [b]Privacy Policy[/b]',
            markup=True,
            font_size=dp(11),
            color=(0.55, 0.50, 0.50, 1),
            size_hint=(1, None),
            height=dp(40),
            halign='center',
            valign='middle',
        ))

        # Error / Status Label 
        self.error_label = clabel(
            text='',
            color=(1, 0, 0, 1),
            size_hint=(1, None),
            height=dp(24),
            halign='center',
            valign='middle',
        )
        col.add_widget(self.error_label)

    # TAB SWITCHING 
    def _switch_mode(self, mode):
        self._mode = mode
        self.error_label.text = ""
        self.email_input.text = ""
        self.pass_input.text = ""

        if mode == 'signup':
            self.heading_label.text = "Create an account"
            self.subheading_label.text = "Enter your email to sign up for this app"
            self.action_btn.text = "Sign up with email"
            self.signup_tab.background_color = (0.1, 0.1, 0.1, 1)
            self.signup_tab.color = (1, 1, 1, 1)
            self.signin_tab.background_color = (0.75, 0.75, 0.75, 1)
            self.signin_tab.color = (0.1, 0.1, 0.1, 1)
        else:
            self.heading_label.text = "Welcome back"
            self.subheading_label.text = "Enter your credentials to sign in"
            self.action_btn.text = "Sign in"
            self.signin_tab.background_color = (0.1, 0.1, 0.1, 1)
            self.signin_tab.color = (1, 1, 1, 1)
            self.signup_tab.background_color = (0.75, 0.75, 0.75, 1)
            self.signup_tab.color = (0.1, 0.1, 0.1, 1)
 
    def _show_message(self, msg, is_error=True):
        """Displays a message that auto-clears after 3 seconds."""
        self.error_label.color = (1, 0, 0, 1) if is_error else (0.1, 0.5, 0.2, 1)
        self.error_label.text = msg
        Clock.schedule_once(lambda dt: setattr(self.error_label, 'text', ''), 3)

    def _hash_password(self, password):
        """Returns a SHA-256 hash of the given password string."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _on_action(self, *args):
        if self._mode == 'signup':
            self._on_signup()
        else:
            self._on_signin()

    def _on_signup(self):
        email = self.email_input.text.strip()
        password = self.pass_input.text.strip()

        if not email or "@" not in email or len(password) < 4:
            self._show_message("Invalid email or password (min 4 chars)")
            return

        conn = sqlite3.connect('oscorp.db')
        cursor = conn.cursor()
        try:
            hashed_pw = self._hash_password(password)
            cursor.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                (email, hashed_pw),
            )
            conn.commit()
            print(f"[OsCorp] User {email} registered successfully.")
            self._navigate_to_dashboard()
        except sqlite3.IntegrityError:
            self._show_message("User already exists.")
        finally:
            conn.close()

    def _on_signin(self):
        email = self.email_input.text.strip()
        password = self.pass_input.text.strip()

        if not email or "@" not in email or len(password) < 4:
            self._show_message("Invalid email or password (min 4 chars)")
            return

        conn = sqlite3.connect('oscorp.db')
        cursor = conn.cursor()
        try:
            hashed_pw = self._hash_password(password)
            cursor.execute(
                "SELECT id FROM users WHERE email = ? AND password = ?",
                (email, hashed_pw),
            )
            row = cursor.fetchone()
            if row:
                print(f"[OsCorp] User {email} signed in successfully.")
                self._navigate_to_dashboard()
            else:
                self._show_message("Incorrect email or password.")
        finally:
            conn.close()

    def _navigate_to_dashboard(self):
        """
        Switches to 'dashboard' when your team's screen is registered.
        Until then, confirms success on this screen.
        """
        if self.manager and 'dashboard' in self.manager.screen_names:
            self.manager.current = 'dashboard'
        else:
            self._show_message("Login successful!", is_error=False)

# add Dashboard screen to the ScreenManager below with name='dashboard' 
class OsCorpApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        # sm.add_widget(YourDashboardScreen(name='dashboard'))
        return sm
