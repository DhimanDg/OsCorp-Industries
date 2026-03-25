from bud_app_class import BudApp

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class DashboardScreen(BoxLayout):
    balance_text = StringProperty("$0.00")
    spent_text = StringProperty("$0.00")
    initial_text = StringProperty("Click to set")

    def __init__(self, bud, **kwargs):
        super().__init__(**kwargs)
        self.bud = bud
        self.update_labels()

    def update_labels(self):
        self.balance_text = f"${self.bud.balance:,.2f}"
        self.spent_text = f"${self.bud.spent:,.2f}"
        self.initial_text = (
            f"${self.bud.iniBud:,.2f}" if self.bud.iniBud > 0 else "Click to set"
        )

    def open_budget_popup(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        input_box = TextInput(
            hint_text="Enter budget amount",
            multiline=False,
            input_filter='float'
        )

        status_label = Label(text="")

        def set_budget(instance):
            try:
                value = float(input_box.text)
                if value <= 0:
                    status_label.text = "Enter a value greater than 0"
                else:
                    self.bud.iniBud = value
                    self.bud.balance = value
                    self.update_labels()
                    popup.dismiss()
            except:
                status_label.text = "Invalid input"

        btn = Button(text="Set Budget", size_hint_y=None, height=40)
        btn.bind(on_press=set_budget)

        layout.add_widget(Label(text="Set Initial Budget"))
        layout.add_widget(input_box)
        layout.add_widget(status_label)
        layout.add_widget(btn)

        popup = Popup(
            title="Initial Budget",
            content=layout,
            size_hint=(0.6, 0.4)
        )
        popup.open()

    def add_transaction(self):
        print("Add transaction clicked (GUI placeholder)")

    def show_balance(self):
        self.update_labels()

    def show_spent(self):
        self.update_labels()


class OsCorpApp(App): 
    def __init__(self, bud, **kwargs):
        super().__init__(**kwargs)
        self.bud = bud

    def build(self):
        Builder.load_file("dashboard.kv")
        return DashboardScreen(self.bud)


def starting_main():
    bud = BudApp(0.0, 0.0, 0.0, 0.0)

    OsCorpApp(bud).run()


if __name__ == "__main__":
    starting_main()