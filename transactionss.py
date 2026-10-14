
# CheckyoMoney - Transaction Management

from datetime import date
from storage import load_transactions, save_transactions

# Load previous records when this module is imported.
transactions = load_transactions()


def add_transaction(transaction_type, amount, category, description=""):
    """Record a transaction and save it."""

    if amount <= 0:
        print("Oi! Money amounts must be greater than zero.")
        return False

    if transaction_type not in ("income", "expense"):
        print("Invalid transaction type.")
        return False

    if not category.strip():
        print("Category cannot be empty.")
        return False

    transaction = {
        "type": transaction_type,
        "amount": round(amount, 2),
        "category": category.strip().title(),
        "description": description.strip(),
        "date": date.today().isoformat()
    }

    transactions.append(transaction)
    save_transactions(transactions)

    if transaction_type == "income":
        print(f"Cha-ching! +{amount:.2f} THB added!")
    else:
        print(f"Money escaped! -{amount:.2f} THB recorded.")

    return True


def calculate_totals():
    """Calculate lifetime income, expenses, and balance."""

    income = sum(
        item["amount"] for item in transactions
        if item["type"] == "income"
    )
    expenses = sum(
        item["amount"] for item in transactions
        if item["type"] == "expense"
    )

    return income, expenses, income - expenses


def show_summary():
    """Display the financial summary."""

    income, expenses, balance = calculate_totals()

    print("\n========== YOUR MONEY STATUS ==========")
    print(f"Income:   {income:,.2f} THB")
    print(f"Expenses: {expenses:,.2f} THB")
    print(f"Balance:  {balance:,.2f} THB")

    if balance < 0:
        print("WARNING: Your wallet is in the negatives. 💀")
    elif balance == 0:
        print("Perfectly balanced... and completely broke.")
    elif income > 0 and expenses >= income * 0.8:
        print("Careful! Your wallet is sweating.")
    else:
        print("Your wallet lives to fight another day!")

    print("=======================================")


def show_transactions():
    """Display transaction history."""

    if not transactions:
        print("\nNo transactions yet. Your wallet has no lore.")
        return

    print("\n========== TRANSACTION HISTORY ==========")

    for number, item in enumerate(transactions, start=1):
        print(
            f"{number}. [{item['date']}] "
            f"{item['type'].title()} | {item['category']} | "
            f"{item['amount']:.2f} THB"
        )

        if item["description"]:
            print(f"   Note: {item['description']}")

    print("=========================================")

def show_category_breakdown():
    """Show total expenses for each category."""

    spending = {}

    for item in transactions:
        if item["type"] == "expense":
            category = item["category"]
            spending[category] = (
                spending.get(category, 0) + item["amount"]
            )

    if not spending:
        print("\nNo expenses recorded. Your wallet is mysterious.")
        return

    print("\n========== WHERE DID IT GO? ==========")

    total_expenses = sum(spending.values())

    for category, amount in sorted(
        spending.items(),
        key=lambda entry: entry[1],
        reverse=True
    ):
        percentage = amount / total_expenses * 100
        bar = "#" * round(percentage / 5)

        print(
            f"{category:<15} {amount:>10,.2f} THB "
            f"({percentage:>5.1f}%)"
        )
        print(f"  {bar}")

    print("-" * 42)
    print(f"{'TOTAL':<15} {total_expenses:>10,.2f} THB")
    print("=======================================")

if __name__ == "__main__":
    print("Loaded transactions:", len(transactions))
    show_summary()