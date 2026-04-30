# OsCorp Industries Budget App

A simple budgeting app for tracking a budget, spending categories, transaction history, and upcoming bills.

## What Is Integrated

- Kivy frontend screens from the frontend branch.
- Backend budget logic from `bud_app_class.py`.
- Local SQLite persistence through Python's built-in `sqlite3` module.

## Local Database

The app stores data in:

```text
User Data/oscorp_budget.db
```

The database is created automatically the first time the app runs. It uses structured tables for:

- `budget_state`
- `categories`
- `transactions`
- `bills`
- `settings`

Older JSON data files in `User Data/` are migrated automatically if they exist and the SQLite database is still empty.

## Setup

Install Python, then install the app dependency:

```bash
python -m pip install -r requirements.txt
```

## Run

From this project folder:

```bash
python budget_app_main.py
```

## Reset Data

Use the Settings screen inside the app to reset budget data or settings. Resetting budget data clears the SQLite transaction and bill records while keeping the database structure ready for future use.
