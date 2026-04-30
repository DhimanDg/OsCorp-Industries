from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty


class SpentScreen(Screen):
    bg_color   = ListProperty([0.85, 0.4, 0.4, 1])
    card_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0, 0, 0, 1])
    icon_tint  = ListProperty([1, 1, 1, 1])  
    search_text = StringProperty("")

    CAT_COLORS = {
        "Household": (0.30, 0.60, 0.90, 1),
        "Credit":    (0.90, 0.45, 0.30, 1),
        "Travel":    (0.40, 0.80, 0.55, 1),
        "Medical":   (0.85, 0.35, 0.55, 1),
        "Shopping":  (0.95, 0.75, 0.25, 1),
        "Fun":       (0.65, 0.45, 0.85, 1),
        "Misc":      (0.55, 0.55, 0.60, 1),
    }

    def __init__(self, bud, **kwargs):
        super().__init__(**kwargs)
        self.bud = bud

    def on_pre_enter(self):
        if hasattr(self, "ids") and "search_input" in self.ids:
            self.ids.search_input.text = ""
        self._build_cards("")

    def on_search(self, query):
        self._build_cards(query.strip().lower())

    def go_back(self):
        self.manager.current = "dashboard"

    def go_add_transaction(self):
        self.manager.current = "transaction"

    def open_remove_popup(self):
        from kivy.uix.popup      import Popup
        from kivy.uix.boxlayout  import BoxLayout
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.label      import Label
        from kivy.uix.button     import Button
        from persistence         import save_data

        if not self.bud.tra_overview:
            self._build_cards("") 
            return

        layout = BoxLayout(orientation="vertical", padding=8, spacing=8)
        layout.add_widget(Label(
            text="Tap a transaction to remove it",
            size_hint_y=None, height=30,
            color=(0.9, 0.9, 0.9, 1),
        ))

        scroll = ScrollView()
        grid   = GridLayout(cols=1, spacing=6, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        popup_ref = []

        def make_remove(idx):
            def _remove(inst):
                self.bud.remove_transaction_gui(idx)
                save_data(self.bud)
                self.manager.get_screen("dashboard").update_labels()
                if popup_ref:
                    popup_ref[0].dismiss()
                if hasattr(self, "ids") and "search_input" in self.ids:
                    self._build_cards(self.ids.search_input.text.strip().lower())
                else:
                    self._build_cards("")
            return _remove

        for i, (cat, amt, desc, date) in enumerate(self.bud.tra_overview):
            sign  = "-$" if amt < 0 else "$"
            label = f"({i+1}) {cat}  {sign}{abs(amt):,.2f}  {date.date()}"
            if desc:
                label += f"\n    {str(desc)[:45]}"
            btn = Button(
                text=label,
                size_hint_y=None, height=60,
                halign="left", valign="middle",
                text_size=(None, None),
                background_color=(0.65, 0.15, 0.15, 1),
            )
            btn.bind(on_press=make_remove(i))
            grid.add_widget(btn)

        scroll.add_widget(grid)
        layout.add_widget(scroll)

        cancel_btn = Button(text="Cancel", size_hint_y=None, height=44)
        cancel_btn.bind(on_press=lambda i: popup_ref[0].dismiss())
        layout.add_widget(cancel_btn)

        popup = Popup(title="Remove Transaction",
                      content=layout, size_hint=(0.88, 0.78))
        popup_ref.append(popup)
        popup.open()

    def _build_cards(self, query=""):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label     import Label
        from kivy.uix.widget    import Widget
        from kivy.graphics      import Color, RoundedRectangle
        from kivy.metrics       import dp

        container = self.ids.transaction_list
        container.clear_widgets()

        all_tra  = list(enumerate(self.bud.tra_overview))
        if query:
            filtered = [
                (orig_i, t) for orig_i, t in all_tra
                if query in t[0].lower()
                or query in str(t[2]).lower()
                or query in str(t[3].date())
                or query in f"{abs(t[1]):,.2f}"
            ]
        else:
            filtered = all_tra

        if not filtered:
            msg = "No transactions match your search." if query else "No transactions yet."
            container.add_widget(Label(
                text=msg,
                color=(1, 1, 1, 0.7),
                font_size="15sp",
                size_hint_y=None,
                height=dp(50),
            ))
            return

        for orig_i, (category, amount, desc, date) in reversed(filtered):
            is_negative = amount < 0
            sign        = "-$" if is_negative else "$"
            amt_color   = (0.35, 0.85, 0.45, 1) if is_negative else (0.95, 0.35, 0.35, 1)
            accent      = self.CAT_COLORS.get(category, (0.6, 0.6, 0.6, 1))
            display_num = orig_i + 1

            card = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(86) if desc else dp(68),
                padding=(0, 0),
                spacing=0,
            )

            def _draw_card(w, *a, accent=accent, cc=list(self.card_color)):
                w.canvas.before.clear()
                with w.canvas.before:
                    Color(*cc)
                    RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(8)])
                    Color(*accent)
                    RoundedRectangle(
                        pos=(w.x, w.y),
                        size=(dp(5), w.height),
                        radius=[dp(8), 0, 0, dp(8)],
                    )
            card.bind(pos=_draw_card, size=_draw_card)

            inner = BoxLayout(
                orientation="vertical",
                padding=(dp(16), dp(10), dp(12), dp(10)),
                spacing=dp(4),
            )

            top_row = BoxLayout(size_hint_y=None, height=dp(22))
            idx_cat = Label(
                text=f"[b]#{display_num}  {category}[/b]",
                markup=True, font_size="14sp",
                color=self.text_color,
                halign="left", valign="middle",
            )
            idx_cat.bind(size=lambda w, s: setattr(w, "text_size", s))
            amt_lbl = Label(
                text=f"[b]{sign}{abs(amount):,.2f}[/b]",
                markup=True, font_size="15sp",
                color=amt_color,
                halign="right", valign="middle",
            )
            amt_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
            top_row.add_widget(idx_cat)
            top_row.add_widget(amt_lbl)
            inner.add_widget(top_row)

            date_lbl = Label(
                text=str(date.date()),
                font_size="12sp",
                color=(0.55, 0.55, 0.55, 1),
                size_hint_y=None, height=dp(16),
                halign="left", valign="middle",
            )
            date_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
            inner.add_widget(date_lbl)

            if desc:
                desc_lbl = Label(
                    text=str(desc),
                    font_size="12sp",
                    color=(0.55, 0.55, 0.55, 1),
                    size_hint_y=None, height=dp(16),
                    halign="left", valign="middle",
                )
                desc_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
                inner.add_widget(desc_lbl)

            card.add_widget(inner)
            container.add_widget(card)

    def apply_theme(self, colors):
        self.bg_color   = colors["bg"]
        self.card_color = colors["card_bg"]
        self.text_color = colors["text"]
        # Invert icon tint in dark mode
        self.icon_tint  = colors.get("icon_tint", [1, 1, 1, 1])
        if hasattr(self, "ids") and "transaction_list" in self.ids:
            query = self.ids.search_input.text.strip().lower() if "search_input" in self.ids else ""
            self._build_cards(query)


Builder.load_file("Pages/spent.kv")
