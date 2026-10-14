# CheckyoMoney

A small desktop money tracker made with **Python** and **Tkinter**.
It records income and expenses, sets budgets, warns you when you overspend, and shows where your money went.

## Run it

Keep all files in one folder and run:

```
python main.py
```

No `pip install` needed. The app writes to `transactions.json` and `budgets.json`, so don't overwrite them with older copies.

## How it is built (3 layers)

| Layer | File | Job |
|---|---|---|
| Screen | `main.py` | Window, buttons, tables |
| Logic | `transactionss.py`, `budgets.py` | Rules and maths |
| Storage | `storage.py` | Load and save JSON |

**Flow:** click a button -> `main.py` checks input -> logic file does the work → `storage.py` saves -> screen refreshes.

**Why split?** Each file has a job of their own, so it is easier to read and fix.

## Data Files

- **transactions.json**: a list of records. Each has `type` (income/expense), `amount`, `category`, `description`, `date`.
- **budgets.json**: `weekly` limit, `monthly` limit, and `categories` (per-category limits). All can be set within the app
- **.pyc files**: automatic cache made by Python (version 3.14). Safe to delete.

## storage.py

Loads and saves transactions.

- `DATA_FILE`: path to `transactions.json`, always next to the code.
- `load_transactions()`: returns the saved list. If the file is missing or broken, it returns an empty list instead of crashing (`try/except`).
- `save_transactions()`: writes the whole list to the file as readable JSON.

## transactionss.py

Handles transaction records.

- `transactions = load_transactions()`: runs once on import. This list is **shared** with `main.py`, so new items show up on screen.
- `add_transaction()`: checks the amount is above 0, the type is valid, and the category is not empty. Then it builds the record (category in Title Case, date set to today), adds it to the list, and saves it. Returns `True` or `False`.
- `calculate_totals()`: returns income, expenses, and balance (income minus expenses).
- `show_summary()`, `show_transactions()`, `show_category_breakdown()`: console printouts from the old text version. The GUI doesn't use them.

## budgets.py

Handles budget limits and spending checks.

- `load_budgets()` / `save_budgets()`: read and write `budgets.json`, with safe defaults if something is missing.
- `set_budget()`: sets the weekly or monthly limit (must be above 0). Pattern: load, change, save.
- `set_category_budget()`: sets a monthly limit for one category.
- `get_spending()`: adds up expenses for this week (from Monday) or this month (from the 1st).
- `get_category_spending()`: same, but for one category this month.
- `show_budgets()`: console report. Alert if over the limit, warning if 20% or less remains. The GUI has its own version.

## main.py

The window. It does no saving or maths itself. It asks the other files.

- **Setup:** `__init__` sets the window, then calls `configure_styles()` (colors and fonts), `build_interface()` (creates 4 tabs), and `refresh_all()` (fills in data).
- **Tabs:** Dashboard (3 cards, status banner, recent table), Transactions (full history), Budgets (limit inputs and status text), Spending breakdown (table with bars).
- **Helpers:** `make_card()` builds one info box. `create_transaction_tree()` builds a table (income green, expense red). `fill_transaction_tree()` clears and refills it, newest first.
- **`open_add_transaction()`:** popup form (type, amount, category, note). Its `save()` checks the input, calls `add_transaction()`, then closes the popup and refreshes. Enter key also saves.
- **`save_period_budgets()` / `save_category_budget()`:** check the input, call the budget functions, refresh, and show a message.
- **`refresh_all()`:** the key method. Updates the cards, banner message, tables, budget report, and breakdown. Runs at startup and after every change.
- **`main()`:** creates the window and starts `mainloop()`, which waits for clicks.

## Limits

- Money uses `float` (`Decimal` is more exact).
- Date is always today.
- No edit or delete for transactions.
- The whole file is rewritten on every save.

## 30-second summary

> CheckyoMoney is a desktop money tracker in Python and Tkinter. `main.py` is the interface, `transactionss.py` and `budgets.py` hold the logic, and `storage.py` saves to JSON files. When you add a transaction, the GUI checks it, the backend saves it, and the screen refreshes.
