# OsCorp Industries Budget App

A simple budgeting app for tracking a budget, spending categories, transaction history, and upcoming bills.

## What Is Integrated

- Kivy frontend screens from the frontend branch.
- Backend budget logic from `bud_app_class.py`.
- Local SQLite persistence through Python's built-in `sqlite3` module.
- INI-backed app settings and local login credentials.

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

Older JSON data files in `User Data/` are migrated automatically if they exist and the SQLite database is still empty.

## Local Settings

The Settings screen stores app preferences in:

```text
User Data/oscorp_settings.ini
```

The first launch opens a login screen. If no account exists yet, the login screen creates a local account and stores the username plus a salted password hash in the same INI file. Plain-text passwords are not stored.

## CSC 317 Requirement Checklist

- Python and Kivy are the primary implementation language and UI framework.
- The dashboard is the home page and includes more than three features: budget summary cards, spending chart, category limit shortcuts, and page navigation.
- The app includes four additional feature pages: New Transaction, Transaction History, Budget Breakdown, and Bills & Reminders.
- The Settings page manages theme, stored data reset, settings reset, and sign out.
- Settings are stored in `User Data/oscorp_settings.ini`.
- Critical budget data is stored long term in the local SQLite database at `User Data/oscorp_budget.db`.
- The implementation follows an MVC-style layout: `bud_app_class.py` and `persistence.py` act as the model/data layer, `Pages/*.kv` files define the views, and `Pages/*.py` screen classes coordinate user actions as controllers.

## Setup
(Optional venv Setup):


Step1: py -3.11 -m venv .venv - Use 3.11 for Kivy compatibility


Step2:  .venv\Scripts\Activate.ps1 - Most common in VS Code 

Install Python(3.11), then install the app dependency:
#kivy does not support python version 3.14 or later at the moment so it is recommended to install python ver 3.11
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
