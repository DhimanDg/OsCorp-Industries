import json
import os

USER_DATA_DIR = "User Data"
os.makedirs(USER_DATA_DIR, exist_ok=True)

DATA_FILE     = os.path.join(USER_DATA_DIR, "oscorp_data.json")
SETTINGS_FILE = os.path.join(USER_DATA_DIR, "oscorp_settings.json")

DEFAULT_SETTINGS = {
    "theme": "default",  
}

DEFAULT_THEME = {
    "default": {
        "bg":        [0.85, 0.4, 0.4, 1],
        "card_bg":   [1, 1, 1, 1],
        "card_bg_p": [0.95, 0.95, 0.95, 1],
        "text":      [0, 0, 0, 1],
        "header_text": [1, 1, 1, 1],
        "chart_bg":  [1, 1, 1, 1],
        "icon_tint": [0.25, 0.25, 0.25, 1],
    },
    "dark": {
        "bg":        [0.12, 0.12, 0.15, 1],
        "card_bg":   [0.2, 0.2, 0.25, 1],
        "card_bg_p": [0.28, 0.28, 0.33, 1],
        "text":      [0.9, 0.9, 0.9, 1],
        "header_text": [0.9, 0.9, 0.9, 1],
        "chart_bg":  [0.18, 0.18, 0.22, 1],
        "icon_tint": [1, 1, 1, 1],
    },
}



def save_data(bud):
    data = {
        "iniBud":  bud.iniBud,
        "balance": bud.balance,
        "spent":   bud.spent,
        "BudLimit":      bud.BudLimit,
        "BudLim_Check":  bud.BudLim_Check,
        "CatLim_Check":  bud.CatLim_Check,
        "category_limits": bud.category_limits,
        "category_spent":  bud.category_spent,
        "usr_bills":  bud.usr_bills,
        "bill_due":   [d.isoformat() for d in bud.bill_due],
        "tra_spent":    bud.tra_spent,
        "tra_desc":     bud.tra_desc,
        "tra_date":     [d.isoformat() for d in bud.tra_date],
        "cat_letter":   bud.cat_letter,
        "tra_category": bud.tra_category,
        "bill_labels":  getattr(bud, "bill_labels", []),
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_data(bud):
    if not os.path.exists(DATA_FILE):
        return
    from datetime import datetime
    with open(DATA_FILE) as f:
        data = json.load(f)

    bud.iniBud   = data.get("iniBud",   0.0)
    bud.balance  = data.get("balance",  0.0)
    bud.spent    = data.get("spent",    0.0)
    bud.BudLimit     = data.get("BudLimit",     0.0)
    bud.BudLim_Check = data.get("BudLim_Check", False)
    bud.CatLim_Check     = data.get("CatLim_Check",     bud.CatLim_Check)
    bud.category_limits  = data.get("category_limits",  bud.category_limits)
    bud.category_spent   = data.get("category_spent",   bud.category_spent)
    bud.usr_bills        = data.get("usr_bills", [])
    bud.bill_due         = [datetime.fromisoformat(d) for d in data.get("bill_due", [])]
    bud.tra_spent        = data.get("tra_spent",    [])
    bud.tra_desc         = data.get("tra_desc",     [])
    bud.tra_date         = [datetime.fromisoformat(d) for d in data.get("tra_date", [])]
    bud.cat_letter       = data.get("cat_letter",   [])
    bud.tra_category     = data.get("tra_category", [])
    bud.bill_labels      = data.get("bill_labels",  [])
    bud.Gen_Tra()


def reset_data(bud):
    bud.iniBud  = 0.0
    bud.balance = 0.0
    bud.spent   = 0.0
    bud.BudLimit     = 0.0
    bud.BudLim_Check = False
    for k in bud.CatLim_Check:
        bud.CatLim_Check[k]    = False
        bud.category_limits[k] = 0.0
        bud.category_spent[k]  = 0.0
    bud.usr_bills    = []
    bud.bill_due     = []
    bud.tra_spent    = []
    bud.tra_desc     = []
    bud.tra_date     = []
    bud.cat_letter   = []
    bud.tra_category = []
    bud.tra_overview = []
    bud.bill_labels  = []
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)



def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def load_settings() -> dict:
    if not os.path.exists(SETTINGS_FILE):
        return dict(DEFAULT_SETTINGS)
    with open(SETTINGS_FILE) as f:
        return json.load(f)


def reset_settings():
    if os.path.exists(SETTINGS_FILE):
        os.remove(SETTINGS_FILE)
    return dict(DEFAULT_SETTINGS)


def get_theme_colors(theme_name: str) -> dict:
    return DEFAULT_THEME.get(theme_name, DEFAULT_THEME["default"])
