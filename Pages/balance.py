from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ListProperty


class BalanceScreen(Screen):
    bg_color   = ListProperty([0.85, 0.4, 0.4, 1])
    card_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0, 0, 0, 1])
    icon_tint  = ListProperty([1, 1, 1, 1])

    CATEGORIES  = ["Household", "Credit", "Travel", "Medical", "Shopping", "Fun", "Misc"]
    CAT_LETTERS = ["U",         "C",      "T",      "M",       "S",        "F",   "X"  ]

    BAR_COLORS = {
        "Household": (0.30, 0.60, 0.90),
        "Credit":    (0.90, 0.45, 0.30),
        "Travel":    (0.40, 0.80, 0.55),
        "Medical":   (0.85, 0.35, 0.55),
        "Shopping":  (0.95, 0.75, 0.25),
        "Fun":       (0.65, 0.45, 0.85),
        "Misc":      (0.55, 0.55, 0.60),
    }

    def __init__(self, bud, **kwargs):
        super().__init__(**kwargs)
        self.bud = bud

    def on_pre_enter(self):
        self._build_rows()

    def _build_rows(self):
        from kivy.uix.widget import Widget
        from kivy.metrics    import dp

        container = self.ids.balance_list
        container.clear_widgets()

        bud = self.bud

        self._add_row(container, "Total Budget", None,
                      bud.spent, bud.iniBud, (0.4, 0.4, 0.4))

        container.add_widget(Widget(size_hint_y=None, height=dp(6)))

        named_limits  = sum(bud.category_limits[k]
                            for k in ["U","C","T","M","S","F"]
                            if bud.category_limits[k] > 0)
        misc_limit    = max(bud.iniBud - named_limits, 0) if bud.iniBud > 0 else 0
        misc_spent    = bud.category_spent.get("X", 0.0)
        if bud.iniBud > 0 or misc_spent > 0:
            self._add_row(container, "Misc", "X",
                          misc_spent, misc_limit, self.BAR_COLORS["Misc"])
            container.add_widget(Widget(size_hint_y=None, height=dp(4)))

        for cat, key in zip(self.CATEGORIES[:-1], self.CAT_LETTERS[:-1]):
            limit = bud.category_limits[key]
            spent = bud.category_spent[key]
            if spent == 0 and limit == 0:
                continue
            self._add_row(container, cat, key,
                          spent, limit, self.BAR_COLORS[cat])

    def _add_row(self, container, label_text, cat_key, spent, limit, bar_rgb):
        from kivy.uix.boxlayout     import BoxLayout
        from kivy.uix.label         import Label
        from kivy.uix.widget        import Widget
        from kivy.uix.behaviors     import ButtonBehavior
        from kivy.graphics          import Color, RoundedRectangle
        from kivy.metrics           import dp

        has_limit = limit > 0
        pct       = min(spent / limit, 1.0) if has_limit else 0.0
        over      = has_limit and spent > limit

        class TappableCard(ButtonBehavior, BoxLayout):
            pass

        card = TappableCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(80) if has_limit else dp(68),
            padding=(dp(12), dp(8)),
            spacing=dp(4),
        )

        def _draw_card(w, *args):
            w.canvas.before.clear()
            with w.canvas.before:
                alpha = 0.85 if w.state == "down" else 1.0
                Color(*(list(self.card_color[:3]) + [alpha]))
                RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(8)])

        card.bind(pos=_draw_card, size=_draw_card,
                  state=lambda w, s: _draw_card(w))

        if cat_key is not None:
            def _on_tap(inst, cat=cat_key, name=label_text):
                self._open_limit_popup(cat, name)
            card.bind(on_press=_on_tap)

        top = BoxLayout(size_hint_y=None, height=dp(22))

        name_lbl = Label(
            text=label_text + ("  [size=11sp][color=aaaaaa]tap to edit[/color][/size]"
                               if cat_key else ""),
            markup=True,
            bold=True,
            font_size="14sp",
            halign="left",
            valign="middle",
            color=self.text_color,
        )
        name_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))

        if has_limit:
            amt_text = f"${spent:,.2f} / ${limit:,.2f}"
        else:
            amt_text = f"${spent:,.2f}  (no limit set)"

        amt_lbl = Label(
            text=amt_text,
            font_size="13sp",
            halign="right",
            valign="middle",
            color=(0.85, 0.3, 0.3, 1) if over else self.text_color,
        )
        amt_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))

        top.add_widget(name_lbl)
        top.add_widget(amt_lbl)
        card.add_widget(top)

        track = Widget(size_hint_y=None, height=dp(10))

        def _draw_bar(w, *args):
            w.canvas.clear()
            ww, hh = w.size
            x, y   = w.pos
            with w.canvas:
                Color(0.82, 0.82, 0.82, 1)
                RoundedRectangle(pos=(x, y), size=(ww, hh), radius=[dp(4)])
                fill_w = ww * pct if has_limit else 0
                fill_c = (0.85, 0.25, 0.25, 1) if over else (*bar_rgb, 1)
                Color(*fill_c)
                RoundedRectangle(pos=(x, y),
                                 size=(max(fill_w, 0), hh),
                                 radius=[dp(4)])

        track.bind(pos=_draw_bar, size=_draw_bar)
        card.add_widget(track)

        if has_limit:
            pct_lbl = Label(
                text="OVER BUDGET" if over else f"{pct*100:.0f}% used",
                font_size="11sp",
                halign="right",
                valign="middle",
                color=(0.85, 0.25, 0.25, 1) if over else (0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(14),
            )
            pct_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
            card.add_widget(pct_lbl)

        container.add_widget(card)

    def _open_limit_popup(self, cat_key, cat_name):
        from kivy.uix.popup     import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label     import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.button    import Button
        from persistence        import save_data

        cur_limit = self.bud.category_limits.get(cat_key, 0.0)
        cur_spent = self.bud.category_spent.get(cat_key, 0.0)

        layout = BoxLayout(orientation="vertical", padding=10, spacing=8)
        layout.add_widget(Label(
            text=(f"[b]{cat_name}[/b]\n"
                  f"Spent: ${cur_spent:,.2f}   "
                  f"Current limit: {'${:,.2f}'.format(cur_limit) if cur_limit > 0 else 'None'}"),
            markup=True, halign="center",
        ))

        inp = TextInput(
            hint_text="Budget limit (blank or 0 to remove)",
            multiline=False, input_filter="float",
            text=str(cur_limit) if cur_limit > 0 else "",
        )
        err = Label(text="", size_hint_y=None, height=24,
                    color=(1, 0.3, 0.3, 1))

        def apply(inst):
            try:
                val = float(inp.text) if inp.text.strip() else 0.0
                if val < 0:
                    err.text = "Must be 0 or greater"
                    return
                self.bud.category_limits[cat_key] = val
                self.bud.CatLim_Check[cat_key]    = val > 0
                save_data(self.bud)
                popup.dismiss()
                self._build_rows()
            except Exception:
                err.text = "Invalid input"

        btn = Button(text="Save Limit", size_hint_y=None, height=40)
        btn.bind(on_press=apply)
        layout.add_widget(inp)
        layout.add_widget(err)
        layout.add_widget(btn)
        popup = Popup(title=f"{cat_name} Budget Limit",
                      content=layout, size_hint=(0.65, 0.46))
        popup.open()

    def apply_theme(self, colors):
        self.bg_color   = colors["bg"]
        self.card_color = colors["card_bg"]
        self.text_color = colors["text"]
        self.icon_tint  = colors.get("icon_tint", [1, 1, 1, 1])
        if hasattr(self, "ids") and "balance_list" in self.ids:
            self._build_rows()

    def go_back(self):
        self.manager.current = "dashboard"


Builder.load_file("Pages/balance.kv")
