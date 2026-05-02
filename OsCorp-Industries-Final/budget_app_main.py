from kivy.config import Config
Config.set('graphics', 'width',  '488')
Config.set('graphics', 'height', '1024')
Config.set('graphics', 'resizable', '1')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from bud_app_class import BudApp
from Pages.login       import LoginScreen
from Pages.dashboard   import DashboardScreen
from Pages.transaction import TransactionScreen
from Pages.spent       import SpentScreen
from Pages.settings    import SettingsScreen
from Pages.balance     import BalanceScreen
from Pages.bills       import BillsScreen
from persistence import load_data, load_settings, get_theme_colors


class OsCorpApp(App):
    def __init__(self, bud, **kwargs):
        super().__init__(**kwargs)
        self.bud       = bud
        self.app_state = load_settings()

    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen      (self.app_state,           name="login"))
        sm.add_widget(DashboardScreen  (self.bud,                 name="dashboard"))
        sm.add_widget(TransactionScreen(self.bud,                 name="transaction"))
        sm.add_widget(SpentScreen      (self.bud,                 name="spent"))
        sm.add_widget(SettingsScreen   (self.bud, self.app_state, name="settings"))
        sm.add_widget(BalanceScreen    (self.bud,                 name="balance"))
        sm.add_widget(BillsScreen      (self.bud,                 name="bills"))

        colors = get_theme_colors(self.app_state["theme"])
        for screen_name in sm.screen_names:
            screen = sm.get_screen(screen_name)
            if hasattr(screen, "apply_theme"):
                screen.apply_theme(colors)

        sm.current = "login"
        return sm


def starting_main():
    bud = BudApp(0.0, 0.0)
    load_data(bud)
    OsCorpApp(bud).run()


if __name__ == "__main__":
    starting_main()
