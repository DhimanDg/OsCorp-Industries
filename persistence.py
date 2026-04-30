import json
import os
import sqlite3
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.environ.get(
    "OSCORP_DATA_DIR",
    os.path.join(BASE_DIR, "User Data"),
)
os.makedirs(USER_DATA_DIR, exist_ok=True)

DATABASE_FILE = os.path.join(USER_DATA_DIR, "oscorp_budget.db")

# Kept for one-time migration from the older JSON storage.
DATA_FILE = os.path.join(USER_DATA_DIR, "oscorp_data.json")
SETTINGS_FILE = os.path.join(USER_DATA_DIR, "oscorp_settings.json")

DEFAULT_SETTINGS = {
    "theme": "default",
}

DEFAULT_CATEGORIES = {
    "U": "Household",
    "C": "Credit",
    "T": "Travel",
    "M": "Medical",
    "S": "Shopping",
    "F": "Fun",
    "X": "Misc",
}

DEFAULT_THEME = {
    "default": {
        "bg": [0.85, 0.4, 0.4, 1],
        "card_bg": [1, 1, 1, 1],
        "card_bg_p": [0.95, 0.95, 0.95, 1],
        "text": [0, 0, 0, 1],
        "header_text": [1, 1, 1, 1],
        "chart_bg": [1, 1, 1, 1],
        "icon_tint": [0.25, 0.25, 0.25, 1],
    },
    "dark": {
        "bg": [0.12, 0.12, 0.15, 1],
        "card_bg": [0.2, 0.2, 0.25, 1],
        "card_bg_p": [0.28, 0.28, 0.33, 1],
        "text": [0.9, 0.9, 0.9, 1],
        "header_text": [0.9, 0.9, 0.9, 1],
        "chart_bg": [0.18, 0.18, 0.22, 1],
        "icon_tint": [1, 1, 1, 1],
    },
}


def _connect():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _ensure_schema(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS budget_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            initial_budget REAL NOT NULL DEFAULT 0,
            balance REAL NOT NULL DEFAULT 0,
            spent REAL NOT NULL DEFAULT 0,
            budget_limit REAL NOT NULL DEFAULT 0,
            budget_limit_enabled INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS categories (
            letter TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            limit_enabled INTEGER NOT NULL DEFAULT 0,
            spending_limit REAL NOT NULL DEFAULT 0,
            spent REAL NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            description TEXT,
            transaction_date TEXT NOT NULL,
            category_letter TEXT NOT NULL,
            category_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (category_letter) REFERENCES categories(letter)
        );

        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT,
            amount REAL NOT NULL,
            due_date TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
    )

    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """
        INSERT OR IGNORE INTO budget_state (
            id, initial_budget, balance, spent,
            budget_limit, budget_limit_enabled, updated_at
        )
        VALUES (1, 0, 0, 0, 0, 0, ?)
        """,
        (now,),
    )

    for letter, name in DEFAULT_CATEGORIES.items():
        conn.execute(
            """
            INSERT OR IGNORE INTO categories (
                letter, name, limit_enabled, spending_limit, spent
            )
            VALUES (?, ?, 0, 0, 0)
            """,
            (letter, name),
        )

    for key, value in DEFAULT_SETTINGS.items():
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, json.dumps(value)),
        )

    conn.commit()


def _parse_datetime(value):
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


def _normalise_budget_totals(bud):
    categories = dict(getattr(bud, "categories", DEFAULT_CATEGORIES))
    bud.category_spent = {letter: 0.0 for letter in categories}

    normalised_dates = []
    normalised_categories = []
    normalised_letters = []

    for amount, letter, category, value in zip(
        bud.tra_spent,
        bud.cat_letter,
        bud.tra_category,
        bud.tra_date,
    ):
        letter = letter if letter in categories else "X"
        category = categories.get(letter, category or "Misc")
        bud.category_spent[letter] += float(amount)
        normalised_letters.append(letter)
        normalised_categories.append(category)
        normalised_dates.append(_parse_datetime(value))

    bud.cat_letter = normalised_letters
    bud.tra_category = normalised_categories
    bud.tra_date = normalised_dates
    bud.spent = round(sum(float(amount) for amount in bud.tra_spent), 2)
    bud.balance = round(float(bud.iniBud) - bud.spent, 2)
    bud.Gen_Tra()


def _load_json_if_present():
    if not os.path.exists(DATA_FILE):
        return None
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def _remove_legacy_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def _migrate_json_data(conn):
    if not os.path.exists(DATA_FILE):
        return
    existing_count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    existing_bills = conn.execute("SELECT COUNT(*) FROM bills").fetchone()[0]
    state = conn.execute("SELECT initial_budget FROM budget_state WHERE id = 1").fetchone()
    if existing_count or existing_bills or (state and state["initial_budget"]):
        return

    data = _load_json_if_present()
    if not data:
        return

    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """
        UPDATE budget_state
        SET initial_budget = ?, balance = ?, spent = ?,
            budget_limit = ?, budget_limit_enabled = ?, updated_at = ?
        WHERE id = 1
        """,
        (
            float(data.get("iniBud", 0.0)),
            float(data.get("balance", 0.0)),
            float(data.get("spent", 0.0)),
            float(data.get("BudLimit", 0.0)),
            int(bool(data.get("BudLim_Check", False))),
            now,
        ),
    )

    limits_enabled = data.get("CatLim_Check", {})
    limits = data.get("category_limits", {})
    spent = data.get("category_spent", {})
    for letter, name in DEFAULT_CATEGORIES.items():
        conn.execute(
            """
            UPDATE categories
            SET name = ?, limit_enabled = ?, spending_limit = ?, spent = ?
            WHERE letter = ?
            """,
            (
                name,
                int(bool(limits_enabled.get(letter, False))),
                float(limits.get(letter, 0.0)),
                float(spent.get(letter, 0.0)),
                letter,
            ),
        )

    transactions = zip(
        data.get("tra_spent", []),
        data.get("tra_desc", []),
        data.get("tra_date", []),
        data.get("cat_letter", []),
        data.get("tra_category", []),
    )
    for amount, desc, date_value, letter, category in transactions:
        letter = letter if letter in DEFAULT_CATEGORIES else "X"
        conn.execute(
            """
            INSERT INTO transactions (
                amount, description, transaction_date,
                category_letter, category_name, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                float(amount),
                desc,
                _parse_datetime(date_value).isoformat(),
                letter,
                DEFAULT_CATEGORIES.get(letter, category or "Misc"),
                now,
            ),
        )

    bill_labels = data.get("bill_labels", [])
    for index, (amount, date_value) in enumerate(
        zip(data.get("usr_bills", []), data.get("bill_due", []))
    ):
        label = bill_labels[index] if index < len(bill_labels) else ""
        conn.execute(
            """
            INSERT INTO bills (label, amount, due_date, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (label, float(amount), _parse_datetime(date_value).isoformat(), now),
        )

    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            settings = json.load(f)
        for key, value in {**DEFAULT_SETTINGS, **settings}.items():
            conn.execute(
                """
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, json.dumps(value)),
            )

    conn.commit()
    _remove_legacy_file(DATA_FILE)
    _remove_legacy_file(SETTINGS_FILE)


def save_data(bud):
    with _connect() as conn:
        _ensure_schema(conn)
        _normalise_budget_totals(bud)

        now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            """
            UPDATE budget_state
            SET initial_budget = ?, balance = ?, spent = ?,
                budget_limit = ?, budget_limit_enabled = ?, updated_at = ?
            WHERE id = 1
            """,
            (
                float(bud.iniBud),
                float(bud.balance),
                float(bud.spent),
                float(bud.BudLimit),
                int(bool(bud.BudLim_Check)),
                now,
            ),
        )

        for letter, name in bud.categories.items():
            conn.execute(
                """
                INSERT INTO categories (
                    letter, name, limit_enabled, spending_limit, spent
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(letter) DO UPDATE SET
                    name = excluded.name,
                    limit_enabled = excluded.limit_enabled,
                    spending_limit = excluded.spending_limit,
                    spent = excluded.spent
                """,
                (
                    letter,
                    name,
                    int(bool(bud.CatLim_Check.get(letter, False))),
                    float(bud.category_limits.get(letter, 0.0)),
                    float(bud.category_spent.get(letter, 0.0)),
                ),
            )

        conn.execute("DELETE FROM transactions")
        for amount, desc, date_value, letter, category in zip(
            bud.tra_spent,
            bud.tra_desc,
            bud.tra_date,
            bud.cat_letter,
            bud.tra_category,
        ):
            conn.execute(
                """
                INSERT INTO transactions (
                    amount, description, transaction_date,
                    category_letter, category_name, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    float(amount),
                    desc,
                    _parse_datetime(date_value).isoformat(),
                    letter,
                    category,
                    now,
                ),
            )

        conn.execute("DELETE FROM bills")
        bill_labels = getattr(bud, "bill_labels", [])
        for index, (amount, due_date) in enumerate(zip(bud.usr_bills, bud.bill_due)):
            label = bill_labels[index] if index < len(bill_labels) else ""
            conn.execute(
                """
                INSERT INTO bills (label, amount, due_date, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (label, float(amount), _parse_datetime(due_date).isoformat(), now),
            )

        conn.commit()
    _remove_legacy_file(DATA_FILE)


def load_data(bud):
    with _connect() as conn:
        _ensure_schema(conn)
        _migrate_json_data(conn)

        state = conn.execute("SELECT * FROM budget_state WHERE id = 1").fetchone()
        bud.iniBud = float(state["initial_budget"])
        bud.BudLimit = float(state["budget_limit"])
        bud.BudLim_Check = bool(state["budget_limit_enabled"])

        category_rows = conn.execute(
            "SELECT * FROM categories ORDER BY rowid"
        ).fetchall()
        bud.categories = {row["letter"]: row["name"] for row in category_rows}
        bud.CatLim_Check = {
            row["letter"]: bool(row["limit_enabled"]) for row in category_rows
        }
        bud.category_limits = {
            row["letter"]: float(row["spending_limit"]) for row in category_rows
        }
        bud.category_spent = {
            row["letter"]: float(row["spent"]) for row in category_rows
        }

        transaction_rows = conn.execute(
            """
            SELECT amount, description, transaction_date,
                   category_letter, category_name
            FROM transactions
            ORDER BY id
            """
        ).fetchall()
        bud.tra_spent = [float(row["amount"]) for row in transaction_rows]
        bud.tra_desc = [row["description"] for row in transaction_rows]
        bud.tra_date = [
            _parse_datetime(row["transaction_date"]) for row in transaction_rows
        ]
        bud.cat_letter = [row["category_letter"] for row in transaction_rows]
        bud.tra_category = [row["category_name"] for row in transaction_rows]

        bill_rows = conn.execute(
            "SELECT label, amount, due_date FROM bills ORDER BY id"
        ).fetchall()
        bud.bill_labels = [row["label"] or "" for row in bill_rows]
        bud.usr_bills = [float(row["amount"]) for row in bill_rows]
        bud.bill_due = [_parse_datetime(row["due_date"]) for row in bill_rows]

        _normalise_budget_totals(bud)


def reset_data(bud):
    bud.iniBud = 0.0
    bud.balance = 0.0
    bud.spent = 0.0
    bud.BudLimit = 0.0
    bud.BudLim_Check = False
    bud.categories = dict(DEFAULT_CATEGORIES)
    bud.CatLim_Check = {letter: False for letter in bud.categories}
    bud.category_limits = {letter: 0.0 for letter in bud.categories}
    bud.category_spent = {letter: 0.0 for letter in bud.categories}
    bud.usr_bills = []
    bud.bill_due = []
    bud.tra_spent = []
    bud.tra_desc = []
    bud.tra_date = []
    bud.cat_letter = []
    bud.tra_category = []
    bud.tra_overview = []
    bud.bill_labels = []

    with _connect() as conn:
        _ensure_schema(conn)
        conn.execute("DELETE FROM transactions")
        conn.execute("DELETE FROM bills")
        now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            """
            UPDATE budget_state
            SET initial_budget = 0, balance = 0, spent = 0,
                budget_limit = 0, budget_limit_enabled = 0, updated_at = ?
            WHERE id = 1
            """,
            (now,),
        )
        for letter, name in DEFAULT_CATEGORIES.items():
            conn.execute(
                """
                INSERT INTO categories (
                    letter, name, limit_enabled, spending_limit, spent
                )
                VALUES (?, ?, 0, 0, 0)
                ON CONFLICT(letter) DO UPDATE SET
                    name = excluded.name,
                    limit_enabled = 0,
                    spending_limit = 0,
                    spent = 0
                """,
                (letter, name),
            )
        conn.commit()
    _remove_legacy_file(DATA_FILE)


def save_settings(settings):
    with _connect() as conn:
        _ensure_schema(conn)
        for key, value in {**DEFAULT_SETTINGS, **settings}.items():
            conn.execute(
                """
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, json.dumps(value)),
            )
        conn.commit()
    _remove_legacy_file(SETTINGS_FILE)


def load_settings():
    with _connect() as conn:
        _ensure_schema(conn)
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
    settings = dict(DEFAULT_SETTINGS)
    for row in rows:
        try:
            settings[row["key"]] = json.loads(row["value"])
        except json.JSONDecodeError:
            settings[row["key"]] = row["value"]
    return settings


def reset_settings():
    with _connect() as conn:
        _ensure_schema(conn)
        conn.execute("DELETE FROM settings")
        for key, value in DEFAULT_SETTINGS.items():
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                (key, json.dumps(value)),
            )
        conn.commit()
    _remove_legacy_file(SETTINGS_FILE)
    return dict(DEFAULT_SETTINGS)


def get_theme_colors(theme_name):
    return DEFAULT_THEME.get(theme_name, DEFAULT_THEME["default"])
