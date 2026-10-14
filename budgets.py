
# CheckyoMoney - Budget Management

import json
from datetime import date, timedelta
from pathlib import Path

BUDGET_FILE = Path(__file__).parent / "budgets.json"


def load_budgets():
    """Load budget settings from the JSON file."""

    if not BUDGET_FILE.exists():
        return {
            "weekly": 0,
            "monthly": 0,
            "categories": {}
        }

    try:
        with BUDGET_FILE.open("r", encoding="utf-8") as file:
            budgets = json.load(file)

        # Ensure the expected settings exist.
        budgets.setdefault("weekly", 0)
        budgets.setdefault("monthly", 0)
        budgets.setdefault("categories", {})
        return budgets

    except (json.JSONDecodeError, OSError):
        print("Could not load budgets. Using empty settings.")
        return {
            "weekly": 0,
            "monthly": 0,
            "categories": {}
        }


def save_budgets(budgets):
    """Save budget settings."""

    try:
        with BUDGET_FILE.open("w", encoding="utf-8") as file:
            json.dump(budgets, file, indent=4, ensure_ascii=False)
    except OSError:
        print("Warning: Could not save your budgets.")


def set_budget(period, amount):
    """Set a weekly or monthly budget."""

    if period not in ("weekly", "monthly"):
        print("Invalid budget period.")
        return

    if amount <= 0:
        print("Budget must be greater than zero.")
        return

    budgets = load_budgets()
    budgets[period] = round(amount, 2)
    save_budgets(budgets)

    print(f"{period.title()} budget set to {amount:.2f} THB.")


def set_category_budget(category, amount):
    """Set a monthly spending limit for one category."""

    if not category.strip():
        print("Category cannot be empty.")
        return

    if amount <= 0:
        print("Budget must be greater than zero.")
        return

    budgets = load_budgets()
    budgets["categories"][category.strip().title()] = round(amount, 2)
    save_budgets(budgets)

    print(
        f"{category.strip().title()} limit set to "
        f"{amount:.2f} THB per month."
    )


def get_spending(transactions, period):
    """Calculate expenses for the current week or month."""

    today = date.today()

    if period == "weekly":
        start_date = today - timedelta(days=today.weekday())
    elif period == "monthly":
        start_date = today.replace(day=1)
    else:
        return 0.0

    total = 0.0

    for item in transactions:
        if item["type"] != "expense":
            continue

        try:
            transaction_date = date.fromisoformat(item["date"])
        except (KeyError, ValueError):
            continue

        if start_date <= transaction_date <= today:
            total += item["amount"]

    return total


def get_category_spending(transactions, category):
    """Calculate this month's expenses in a category."""

    today = date.today()
    start_date = today.replace(day=1)
    total = 0.0

    for item in transactions:
        if item["type"] != "expense":
            continue

        if item["category"].title() != category.title():
            continue

        try:
            transaction_date = date.fromisoformat(item["date"])
        except (KeyError, ValueError):
            continue

        if start_date <= transaction_date <= today:
            total += item["amount"]

    return total


def show_budgets(transactions):
    """Display limits and warn when spending gets too high."""

    budgets = load_budgets()

    print("\n========== BUDGET CHECK ==========")

    for period in ("weekly", "monthly"):
        limit = budgets[period]

        if limit <= 0:
            print(f"{period.title()}: Not set")
            continue

        spent = get_spending(transactions, period)
        remaining = limit - spent

        print(f"{period.title()} limit: {limit:.2f} THB")
        print(f"  Spent: {spent:.2f} THB")
        print(f"  Remaining: {remaining:.2f} THB")

        if remaining < 0:
            print("  ALERT: Budget exceeded! Your wallet needs backup.")
        elif remaining <= limit * 0.2:
            print("  WARNING: Almost out of budget!")
        else:
            print("  Looking good. Stay disciplined!")

    print("\nMonthly category limits:")

    if not budgets["categories"]:
        print("No category limits set yet.")
    else:
        for category, limit in budgets["categories"].items():
            spent = get_category_spending(transactions, category)
            remaining = limit - spent

            print(
                f"{category}: {spent:.2f} / {limit:.2f} THB "
                f"(remaining {remaining:.2f} THB)"
            )

            if remaining < 0:
                print(f"  ALERT: {category} budget exceeded!")
            elif remaining <= limit * 0.2:
                print(f"  WARNING: {category} budget is nearly gone.")

    print("==================================")
