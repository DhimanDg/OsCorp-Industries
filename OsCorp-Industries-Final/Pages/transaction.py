from datetime import datetime

from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen


class TransactionScreen(Screen):
    selected_category = StringProperty("U")
    bg_color = ListProperty([0.85, 0.4, 0.4, 1])
    card_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0, 0, 0, 1])
    icon_tint = ListProperty([1, 1, 1, 1])
    header_color = ListProperty([1, 1, 1, 1])
    muted_color = ListProperty([0.40, 0.45, 0.45, 1])
    field_bg = ListProperty([1, 1, 1, 1])
    field_text = ListProperty([0.09, 0.12, 0.13, 1])
    field_hint = ListProperty([0.50, 0.55, 0.55, 1])
    success_color = ListProperty([0.18, 0.55, 0.38, 1])
    danger_color = ListProperty([0.72, 0.20, 0.22, 1])
    current_datetime = StringProperty("")

    CATEGORY_MAP = {
        "Household": "U", "Credit": "C", "Travel": "T",
        "Medical": "M", "Shopping": "S", "Fun": "F", "Misc": "X",
    }

    def __init__(self, bud, **kwargs):
        super().__init__(**kwargs)
        self.bud = bud

    def on_pre_enter(self):
        self._sync_datetime()

    def _sync_datetime(self):
        now = datetime.now()
        self._auto_date = now.strftime("%Y-%m-%d")
        self.current_datetime = now.strftime("%A, %B %d %Y - %I:%M %p")

    def on_category_select(self, spinner_text):
        self.selected_category = self.CATEGORY_MAP.get(spinner_text, "U")

    def submit_transaction(self, description, amount, comments):
        from persistence import save_data

        status_label = self.ids.status_label

        if not amount.strip():
            status_label.text = "Please enter an amount."
            return
        try:
            amt = float(amount)
        except ValueError:
            status_label.text = "Amount must be a number."
            return

        desc = description.strip() or None
        if comments.strip():
            desc = f"{desc} - {comments.strip()}" if desc else comments.strip()

        self._sync_datetime()

        success = self.bud.add_transaction_gui(
            amt, desc, self.selected_category, self._auto_date,
        )

        if success:
            save_data(self.bud)
            self.ids.desc.text = ""
            self.ids.amt.text = ""
            self.ids.comments.text = ""
            self.ids.category_spinner.text = "Household"
            self.selected_category = "U"
            status_label.text = ""
            self.manager.get_screen("dashboard").update_labels()
            self.manager.current = "dashboard"
        else:
            status_label.text = "Transaction failed - check category limits."

    def open_remove_popup(self):
        from kivy.uix.button import Button
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.popup import Popup
        from kivy.uix.scrollview import ScrollView
        from persistence import save_data

        if not self.bud.tra_overview:
            self.ids.status_label.text = "No transactions to remove."
            return

        layout = BoxLayout(orientation="vertical", padding=8, spacing=8)
        layout.add_widget(Label(
            text="Tap a transaction to remove it",
            size_hint_y=None, height=30, color=self.text_color,
        ))

        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=6, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        popup_ref = []

        def make_remove(idx):
            def _remove(inst):
                self.bud.remove_transaction_gui(idx)
                save_data(self.bud)
                self.manager.get_screen("dashboard").update_labels()
                if popup_ref:
                    popup_ref[0].dismiss()
                self.ids.status_label.text = "Transaction removed."
            return _remove

        for i, (cat, amt, desc, date) in enumerate(self.bud.tra_overview):
            sign = "-$" if amt < 0 else "$"
            label = f"({i + 1}) {cat}  {sign}{abs(amt):,.2f}  {date.date()}"
            if desc:
                label += f"\n    {desc[:40]}"
            btn = Button(
                text=label,
                size_hint_y=None, height=60,
                halign="left", valign="middle",
                text_size=(None, None),
                background_normal="",
                background_down="",
                background_color=self.danger_color,
                color=(1, 1, 1, 1),
            )
            btn.bind(on_press=make_remove(i))
            grid.add_widget(btn)

        scroll.add_widget(grid)
        layout.add_widget(scroll)

        cancel_btn = Button(text="Cancel", size_hint_y=None, height=40)
        layout.add_widget(cancel_btn)

        popup = Popup(title="Remove Transaction",
                      content=layout, size_hint=(0.85, 0.75))
        popup_ref.append(popup)
        cancel_btn.bind(on_press=lambda i: popup.dismiss())
        popup.open()

    def apply_theme(self, colors):
        self.bg_color = colors["bg"]
        self.card_color = colors["card_bg"]
        self.text_color = colors["text"]
        self.icon_tint = colors.get("icon_tint", [1, 1, 1, 1])
        self.header_color = colors.get("header_text", [1, 1, 1, 1])
        self.muted_color = colors.get("muted_text", [0.40, 0.45, 0.45, 1])
        self.field_bg = colors.get("field_bg", [1, 1, 1, 1])
        self.field_text = colors.get("field_text", colors["text"])
        self.field_hint = colors.get("field_hint", [0.5, 0.5, 0.5, 1])
        self.success_color = colors.get("success", [0.18, 0.55, 0.38, 1])
        self.danger_color = colors.get("danger", [0.72, 0.20, 0.22, 1])

    def cancel(self):
        self.manager.current = "dashboard"


Builder.load_file("Pages/transaction.kv")
