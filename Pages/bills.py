from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ListProperty


class BillsScreen(Screen):
    bg_color   = ListProperty([0.85, 0.4, 0.4, 1])
    card_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0, 0, 0, 1])
    icon_tint  = ListProperty([1, 1, 1, 1])

    def __init__(self, bud, **kwargs):
        super().__init__(**kwargs)
        self.bud = bud

    def on_pre_enter(self):
        self._build_cards()

    def _build_cards(self):
        from kivy.uix.boxlayout  import BoxLayout
        from kivy.uix.label      import Label
        from kivy.uix.button     import Button
        from kivy.uix.widget     import Widget
        from kivy.graphics       import Color, RoundedRectangle
        from kivy.metrics        import dp

        container = self.ids.bill_list
        container.clear_widgets()

        if not self.bud.usr_bills:
            container.add_widget(Label(
                text="No bills added yet.\nTap '+ Add Bill' to get started.",
                color=(1, 1, 1, 0.7),
                font_size="15sp",
                halign="center",
                size_hint_y=None,
                height=dp(70),
            ))
            return

        labels = getattr(self.bud, "bill_labels", [""] * len(self.bud.usr_bills))

        for i, (amount, due, label) in enumerate(
                zip(self.bud.usr_bills, self.bud.bill_due, labels)):

            days_diff, status_str = self.bud.get_bill_status(i)

            if days_diff < 0:
                accent = (0.9, 0.25, 0.25, 1)
                status_color = (0.9, 0.25, 0.25, 1)
            elif days_diff <= 7:
                accent = (0.95, 0.65, 0.1, 1)
                status_color = (0.95, 0.65, 0.1, 1)
            else:
                accent = (0.25, 0.75, 0.45, 1)
                status_color = (0.25, 0.75, 0.45, 1)

            card = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(90),
                padding=(0, 0),
                spacing=0,
            )

            def _draw(w, *a, ac=accent, cc=list(self.card_color)):
                w.canvas.before.clear()
                with w.canvas.before:
                    Color(*cc)
                    RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(8)])
                    Color(*ac)
                    RoundedRectangle(
                        pos=(w.x, w.y),
                        size=(dp(5), w.height),
                        radius=[dp(8), 0, 0, dp(8)],
                    )
            card.bind(pos=_draw, size=_draw)

            inner = BoxLayout(
                orientation="vertical",
                padding=(dp(16), dp(8), dp(12), dp(8)),
                spacing=dp(4),
            )

            top = BoxLayout(size_hint_y=None, height=dp(24))
            bill_name = label if label else f"Bill #{i + 1}"

            name_lbl = Label(
                text=f"[b]{bill_name}[/b]",
                markup=True,
                font_size="15sp",
                color=self.text_color,
                halign="left", valign="middle",
            )
            name_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))

            amt_lbl = Label(
                text=f"[b]${amount:,.2f}[/b]",
                markup=True,
                font_size="15sp",
                color=self.text_color,
                halign="right", valign="middle",
            )
            amt_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
            top.add_widget(name_lbl)
            top.add_widget(amt_lbl)
            inner.add_widget(top)

            mid = BoxLayout(size_hint_y=None, height=dp(18))

            due_lbl = Label(
                text=f"Due: {due.date()}",
                font_size="12sp",
                color=(0.55, 0.55, 0.55, 1),
                halign="left", valign="middle",
            )
            due_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))

            status_lbl = Label(
                text=status_str,
                font_size="12sp",
                color=status_color,
                halign="right", valign="middle",
            )
            status_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
            mid.add_widget(due_lbl)
            mid.add_widget(status_lbl)
            inner.add_widget(mid)

            def make_remove(idx):
                def _remove(inst):
                    self.bud.remove_bill_gui(idx)
                    from persistence import save_data
                    save_data(self.bud)
                    self._build_cards()
                return _remove

            remove_btn = Button(
                text="Remove",
                size_hint_y=None,
                height=dp(26),
                font_size="11sp",
                background_color=(0.6, 0.18, 0.18, 1),
            )
            remove_btn.bind(on_press=make_remove(i))
            inner.add_widget(remove_btn)

            card.add_widget(inner)
            container.add_widget(card)

    def open_add_popup(self):
        from kivy.uix.popup     import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label     import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.button    import Button
        from persistence        import save_data

        layout = BoxLayout(orientation="vertical", padding=12, spacing=10)

        lbl_input  = TextInput(hint_text="Bill name (e.g. Rent, Electric)...",
                               multiline=False)
        amt_input  = TextInput(hint_text="Amount ($)",
                               input_filter="float", multiline=False)
        date_input = TextInput(hint_text="Due date: YYYY-MM-DD or MM/DD/YYYY",
                               multiline=False)
        err_lbl    = Label(text="", size_hint_y=None, height=24,
                           color=(1, 0.4, 0.4, 1))

        def submit(inst):
            ok = self.bud.add_bill_gui(
                amt_input.text,
                date_input.text,
                lbl_input.text,
            )
            if ok:
                save_data(self.bud)
                popup.dismiss()
                self._build_cards()
            else:
                err_lbl.text = "Invalid amount or date — please check and try again."

        layout.add_widget(Label(text="Bill Name"))
        layout.add_widget(lbl_input)
        layout.add_widget(Label(text="Amount"))
        layout.add_widget(amt_input)
        layout.add_widget(Label(text="Due Date"))
        layout.add_widget(date_input)
        layout.add_widget(err_lbl)

        btn = Button(text="Add Bill", size_hint_y=None, height=42,
                     background_color=(0.2, 0.6, 0.3, 1))
        btn.bind(on_press=submit)
        layout.add_widget(btn)

        popup = Popup(title="Add New Bill", content=layout,
                      size_hint=(0.85, 0.72))
        popup.open()

    def apply_theme(self, colors):
        self.bg_color   = colors["bg"]
        self.card_color = colors["card_bg"]
        self.text_color = colors["text"]
        self.icon_tint  = colors.get("icon_tint", [1, 1, 1, 1])
        if hasattr(self, "ids") and "bill_list" in self.ids:
            self._build_cards()

    def go_back(self):
        self.manager.current = "dashboard"


Builder.load_file("Pages/bills.kv")
