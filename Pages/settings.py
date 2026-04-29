from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ListProperty
from persistence import (
    save_settings, load_settings, reset_settings,
    reset_data, save_data, get_theme_colors,
)


class SettingsScreen(Screen):
    bg_color      = ListProperty([0.85, 0.4, 0.4, 1])
    card_color    = ListProperty([1, 1, 1, 1])
    text_color    = ListProperty([0, 0, 0, 1])
    icon_tint     = ListProperty([1, 1, 1, 1])

    def __init__(self, bud, app_state, **kwargs):
        super().__init__(**kwargs)
        self.bud       = bud
        self.app_state = app_state  

    def on_enter(self):
        self.ids.theme_btn.text = (
            "Switch to Dark Mode"
            if self.app_state["theme"] == "default"
            else "Switch to Default Theme"
        )

    def toggle_theme(self):
        new = "dark" if self.app_state["theme"] == "default" else "default"
        self.app_state["theme"] = new
        save_settings(self.app_state)
        self._broadcast_theme(new)
        self.ids.theme_btn.text = (
            "Switch to Dark Mode" if new == "default" else "Switch to Default Theme"
        )

    def _broadcast_theme(self, theme_name):
        colors = get_theme_colors(theme_name)
        for screen_name in self.manager.screen_names:
            screen = self.manager.get_screen(screen_name)
            if hasattr(screen, "apply_theme"):
                screen.apply_theme(colors)

    def confirm_reset_data(self):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        layout.add_widget(Label(
            text="This will erase ALL budget data\nand transactions. Are you sure?",
            halign="center",
        ))
        btns = BoxLayout(size_hint_y=None, height=44, spacing=10)

        def do_reset(inst):
            reset_data(self.bud)
            dash = self.manager.get_screen("dashboard")
            dash.update_labels()
            popup.dismiss()

        yes = Button(text="Yes, reset")
        no  = Button(text="Cancel")
        yes.bind(on_press=do_reset)
        no.bind(on_press=lambda i: popup.dismiss())
        btns.add_widget(yes)
        btns.add_widget(no)
        layout.add_widget(btns)
        popup = Popup(title="Reset Data", content=layout, size_hint=(0.7, 0.35))
        popup.open()

    def confirm_reset_settings(self):
        new_settings = reset_settings()
        self.app_state.update(new_settings)
        self._broadcast_theme(new_settings["theme"])
        self.ids.theme_btn.text = "Switch to Dark Mode"

    def go_back(self):
        self.manager.current = "dashboard"

    def apply_theme(self, colors):
        self.bg_color   = colors["bg"]
        self.card_color = colors["card_bg"]
        self.text_color = colors["text"]
        self.icon_tint  = colors.get("icon_tint", [1, 1, 1, 1])


Builder.load_file("Pages/settings.kv")
