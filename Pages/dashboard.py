from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Line



class SpendingChart(Widget):
    CATEGORY_COLORS = {
        "Household": (0.30, 0.60, 0.90, 1),
        "Credit":    (0.90, 0.45, 0.30, 1),
        "Travel":    (0.40, 0.80, 0.55, 1),
        "Medical":   (0.85, 0.35, 0.55, 1),
        "Shopping":  (0.95, 0.75, 0.25, 1),
        "Fun":       (0.65, 0.45, 0.85, 1),
    }
    CATEGORIES  = ["Household", "Credit", "Travel", "Medical", "Shopping", "Fun"]
    CAT_LETTERS = ["U", "C", "T", "M", "S", "F"]
    CAT_SHORT   = ["Util", "Cred", "Trvl", "Med", "Shop", "Fun"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bud = None
        self._chart_bg   = [1, 1, 1, 1]
        self._text_color = (0.15, 0.15, 0.15, 1)
        self._axis_color = (0.55, 0.61, 0.60, 1)
        self._grid_color = (0.84, 0.88, 0.86, 1)
        self.bind(pos=self._redraw, size=self._redraw)

    def refresh(self, bud):
        self.bud = bud
        self._redraw()

    def set_theme(self, chart_bg, text_color, axis_color, grid_color):
        self._chart_bg   = chart_bg
        self._text_color = text_color
        self._axis_color = axis_color
        self._grid_color = grid_color
        self._redraw()

    def _redraw(self, *args):
        if not self.bud:
            return

        from kivy.core.text import Label as CoreLabel
        from kivy.graphics  import Color, Rectangle, Line

        self.canvas.clear()

        values  = [self.bud.category_spent[k] for k in self.CAT_LETTERS]
        max_val = max(values) if any(v > 0 for v in values) else 1

        w, h    = self.size
        x0, y0  = self.pos
        pad_l, pad_r, pad_t, pad_b = 12, 12, 26, 34
        chart_w = w - pad_l - pad_r
        chart_h = h - pad_t - pad_b
        n       = len(self.CATEGORIES)
        bar_w   = (chart_w / n) * 0.58
        gap     = (chart_w / n) * 0.42

        def draw_text(canvas, text, tx, ty, font_size, color):
            lbl = CoreLabel(text=text, font_size=font_size, color=color)
            lbl.refresh()
            tex = lbl.texture
            with canvas:
                Color(1, 1, 1, 1) 
                Rectangle(texture=tex,
                          pos=(tx - tex.width / 2, ty),
                          size=tex.size)

        with self.canvas:
            Color(*self._chart_bg)
            Rectangle(pos=(x0, y0), size=(w, h))

            for ratio in (0.25, 0.50, 0.75, 1.0):
                grid_y = y0 + pad_b + chart_h * ratio
                Color(*self._grid_color)
                Line(points=[x0 + pad_l, grid_y,
                             x0 + w - pad_r, grid_y],
                     width=0.8)

            for i, (cat, key, short) in enumerate(
                    zip(self.CATEGORIES, self.CAT_LETTERS, self.CAT_SHORT)):
                spent = self.bud.category_spent[key]
                bar_h = (spent / max_val) * chart_h if max_val > 0 else 0
                bar_x = x0 + pad_l + i * (bar_w + gap)
                bar_y = y0 + pad_b
                bar_cx = bar_x + bar_w / 2 

                Color(*self.CATEGORY_COLORS[cat])
                Rectangle(pos=(bar_x, bar_y), size=(bar_w, bar_h))

                if spent > 0:
                    draw_text(self.canvas,
                              f"${spent:,.0f}",
                              bar_cx, min(bar_y + bar_h + 4, y0 + h - 18),
                              11, self._text_color)

                draw_text(self.canvas,
                          short,
                          bar_cx, y0 + 4,
                          10, self._text_color)

            Color(*self._axis_color)
            Line(points=[x0 + pad_l, y0 + pad_b,
                         x0 + w - pad_r, y0 + pad_b], width=1.2)



class DashboardScreen(Screen):
    balance_text = StringProperty("$0.00")
    spent_text   = StringProperty("$0.00")
    initial_text = StringProperty("Click to set")
    bg_color     = ListProperty([0.85, 0.4, 0.4, 1])
    card_color   = ListProperty([1, 1, 1, 1])
    card_color_p = ListProperty([0.95, 0.95, 0.95, 1])
    text_color   = ListProperty([0, 0, 0, 1])
    icon_tint    = ListProperty([1, 1, 1, 1])
    header_color = ListProperty([1, 1, 1, 1])
    button_color = ListProperty([0.16, 0.36, 0.38, 1])

    CAT_LETTERS = {"Household": "U", "Credit": "C", "Travel": "T",
                   "Medical": "M", "Shopping": "S", "Fun": "F"}

    def __init__(self, bud, **kwargs):
        super().__init__(**kwargs)
        self.bud = bud
        self.update_labels()

    def on_enter(self):
        self._refresh_chart()

    def _refresh_chart(self):
        if hasattr(self, "ids") and "spending_chart" in self.ids:
            self.ids.spending_chart.refresh(self.bud)

    def update_labels(self):
        self.balance_text = f"${self.bud.balance:,.2f}"
        self.spent_text   = f"${self.bud.spent:,.2f}"
        self.initial_text = (
            f"${self.bud.iniBud:,.2f}" if self.bud.iniBud > 0 else "Click to set"
        )
        self._refresh_chart()

    def apply_theme(self, colors):
        self.bg_color     = colors["bg"]
        self.card_color   = colors["card_bg"]
        self.card_color_p = colors["card_bg_p"]
        self.text_color   = colors["text"]
        self.icon_tint    = colors.get("icon_tint", [1, 1, 1, 1])
        self.header_color = colors.get("header_text", [1, 1, 1, 1])
        self.button_color = colors.get("button", [0.16, 0.36, 0.38, 1])
        if hasattr(self, "ids") and "spending_chart" in self.ids:
            self.ids.spending_chart.set_theme(
                colors["chart_bg"],
                tuple(colors.get("chart_text", colors["text"])),
                tuple(colors.get("chart_axis", [0.7, 0.7, 0.7, 1])),
                tuple(colors.get("chart_grid", [0.82, 0.82, 0.82, 1])),
            )

    def open_settings(self):
        self.manager.current = "settings"

    def open_budget_popup(self):
        from kivy.uix.popup import Popup
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from persistence import save_data

        layout       = BoxLayout(orientation="vertical", padding=10, spacing=10)
        input_box    = TextInput(hint_text="Enter budget amount",
                                 multiline=False, input_filter="float")
        status_label = Label(text="")

        def set_budget(instance):
            try:
                value = float(input_box.text)
                if not self.bud.set_budget_gui(value):
                    status_label.text = "Enter a value greater than 0"
                else:
                    save_data(self.bud)
                    self.update_labels()
                    popup.dismiss()
            except Exception:
                status_label.text = "Invalid input"

        btn = Button(text="Set Budget", size_hint_y=None, height=40)
        btn.bind(on_press=set_budget)
        layout.add_widget(Label(text="Set Initial Budget"))
        layout.add_widget(input_box)
        layout.add_widget(status_label)
        layout.add_widget(btn)
        popup = Popup(title="Initial Budget", content=layout,
                      size_hint=(0.6, 0.4))
        popup.open()

    def open_category_popup(self, category_name):
        from kivy.uix.popup import Popup
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from persistence import save_data

        key           = self.CAT_LETTERS.get(category_name, "U")
        cur_limit     = self.bud.category_limits[key]
        cur_spent     = self.bud.category_spent[key]

        layout = BoxLayout(orientation="vertical", padding=10, spacing=8)
        layout.add_widget(Label(
            text=(f"[b]{category_name}[/b]\n"
                  f"Spent: ${cur_spent:,.2f}   "
                  f"Current limit: {'${:,.2f}'.format(cur_limit) if cur_limit > 0 else 'None'}"),
            markup=True, halign="center",
        ))

        input_box = TextInput(
            hint_text="Budget limit (leave blank or 0 to remove)",
            multiline=False, input_filter="float",
            text=str(cur_limit) if cur_limit > 0 else "",
        )
        status_label = Label(text="", size_hint_y=None, height=24,
                             color=(1, 0.3, 0.3, 1))

        def apply_limit(inst):
            try:
                val = float(input_box.text) if input_box.text.strip() else 0.0
                if val < 0:
                    status_label.text = "Limit must be 0 or greater"
                    return
                if val == 0:
                    self.bud.category_limits[key] = 0.0
                    self.bud.CatLim_Check[key]    = False
                else:
                    self.bud.category_limits[key] = val
                    self.bud.CatLim_Check[key]    = True
                save_data(self.bud)
                popup.dismiss()
            except Exception:
                status_label.text = "Invalid input"

        btn = Button(text="Save Limit", size_hint_y=None, height=40)
        btn.bind(on_press=apply_limit)
        layout.add_widget(input_box)
        layout.add_widget(status_label)
        layout.add_widget(btn)
        popup = Popup(title=f"{category_name} Budget",
                      content=layout, size_hint=(0.62, 0.46))
        popup.open()

    def add_transaction(self):
        self.manager.current = "transaction"

    def show_balance(self):
        self.manager.current = "balance"

    def show_spent(self):
        self.manager.current = "spent"

    def show_bills(self):
        self.manager.current = "bills"


Builder.load_file("Pages/dashboard.kv")
