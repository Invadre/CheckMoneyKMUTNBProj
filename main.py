import tkinter as tk
from tkinter import ttk, messagebox

from transactionss import transactions, add_transaction, calculate_totals
from budgets import (
    load_budgets,
    set_budget,
    set_category_budget,
    get_spending,
    get_category_spending,
)


BG = "#f3f5f8"
CARD = "#ffffff"
INK = "#202938"
MUTED = "#687386"
GREEN = "#16835d"
RED = "#c44747"
ACCENT = "#485bd6"


class CheckyoMoneyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CheckyoMoney")
        self.root.geometry("1000x720")
        self.root.minsize(820, 600)
        self.root.configure(bg=BG)

        self.configure_styles()
        self.build_interface()
        self.refresh_all()

    def configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("TLabel", background=BG, foreground=INK, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground=INK, background=BG)
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground=MUTED, background=BG)
        style.configure("CardTitle.TLabel", font=("Segoe UI", 10, "bold"), foreground=MUTED, background=CARD)
        style.configure("CardValue.TLabel", font=("Segoe UI", 19, "bold"), foreground=INK, background=CARD)
        style.configure("TButton", font=("Segoe UI", 10), padding=(10, 7))
        style.configure("Accent.TButton", background=ACCENT, foreground="white")
        style.map("Accent.TButton", background=[("active", "#3548c2")])
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(14, 9), font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=29, font=("Segoe UI", 10), background=CARD, fieldbackground=CARD)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def build_interface(self):
        header = ttk.Frame(self.root, padding=(24, 20, 24, 10))
        header.pack(fill="x")
        ttk.Label(header, text="CheckyoMoney", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Take care of yo Money",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(4, 20))

        self.dashboard_tab = ttk.Frame(self.notebook, padding=18)
        self.transactions_tab = ttk.Frame(self.notebook, padding=18)
        self.budgets_tab = ttk.Frame(self.notebook, padding=18)
        self.categories_tab = ttk.Frame(self.notebook, padding=18)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.notebook.add(self.budgets_tab, text="Budgets")
        self.notebook.add(self.categories_tab, text="Spending breakdown")

        self.build_dashboard()
        self.build_transactions()
        self.build_budgets()
        self.build_categories()

    def make_card(self, parent, title, value, color=INK):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=16)
        ttk.Label(frame, text=title, style="CardTitle.TLabel").pack(anchor="w")
        value_label = ttk.Label(frame, text=value, style="CardValue.TLabel", foreground=color)
        value_label.pack(anchor="w", pady=(8, 0))
        return frame, value_label

    def build_dashboard(self):
        cards = ttk.Frame(self.dashboard_tab)
        cards.pack(fill="x")
        for column in range(3):
            cards.columnconfigure(column, weight=1, uniform="cards")

        income_card, self.income_value = self.make_card(cards, "TOTAL INCOME", "฿0.00", GREEN)
        expense_card, self.expense_value = self.make_card(cards, "TOTAL EXPENSES", "฿0.00", RED)
        balance_card, self.balance_value = self.make_card(cards, "BALANCE", "฿0.00", ACCENT)
        income_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        expense_card.grid(row=0, column=1, sticky="nsew", padx=4)
        balance_card.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        self.wallet_message = tk.Label(
            self.dashboard_tab,
            text="Almost Cooked",
            bg="#e9edff", fg="#303f9f", anchor="w", padx=14, pady=12,
            font=("Segoe UI", 10, "bold"), wraplength=850,
        )
        self.wallet_message.pack(fill="x", pady=16)

        section = ttk.Frame(self.dashboard_tab)
        section.pack(fill="both", expand=True)
        ttk.Label(section, text="Recent transactions", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))
        self.recent_tree = self.create_transaction_tree(section, height=8)
        self.recent_tree.pack(fill="both", expand=True)

        actions = ttk.Frame(self.dashboard_tab)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Button(actions, text="＋ Add transaction", style="Accent.TButton", command=self.open_add_transaction).pack(side="left")
        ttk.Button(actions, text="Refresh", command=self.refresh_all).pack(side="left", padx=8)

    def create_transaction_tree(self, parent, height=12):
        columns = ("date", "type", "category", "amount", "description")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=height)
        headings = {
            "date": ("Date", 105),
            "type": ("Type", 95),
            "category": ("Category", 135),
            "amount": ("Amount (THB)", 125),
            "description": ("Note", 260),
        }
        for key, (label, width) in headings.items():
            tree.heading(key, text=label)
            tree.column(key, width=width, minwidth=70, anchor="w" if key in ("category", "description", "type") else "center")
        tree.tag_configure("income", foreground=GREEN)
        tree.tag_configure("expense", foreground=RED)
        return tree

    def fill_transaction_tree(self, tree, rows):
        tree.delete(*tree.get_children())
        for item in reversed(rows):
            kind = item.get("type", "").title()
            tree.insert(
                "", "end",
                values=(
                    item.get("date", ""), kind, item.get("category", ""),
                    f"{float(item.get('amount', 0)):.2f}", item.get("description", ""),
                ),
                tags=(item.get("type", ""),),
            )

    def build_transactions(self):
        toolbar = ttk.Frame(self.transactions_tab)
        toolbar.pack(fill="x", pady=(0, 12))
        ttk.Label(toolbar, text="Your financial history", font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Button(toolbar, text="＋ Add transaction", style="Accent.TButton", command=self.open_add_transaction).pack(side="right")
        self.transactions_tree = self.create_transaction_tree(self.transactions_tab, height=16)
        self.transactions_tree.pack(fill="both", expand=True)

    def build_budgets(self):
        intro = ttk.Label(self.budgets_tab, text="Set the limit of your spendings.", style="Subtitle.TLabel")
        intro.pack(anchor="w", pady=(0, 14))

        limits = ttk.LabelFrame(self.budgets_tab, text="Weekly and monthly budgets", padding=14)
        limits.pack(fill="x")
        limits.columnconfigure(1, weight=1)
        ttk.Label(limits, text="Weekly limit (THB)").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=6)
        self.weekly_entry = ttk.Entry(limits, width=20)
        self.weekly_entry.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Label(limits, text="Monthly limit (THB)").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=6)
        self.monthly_entry = ttk.Entry(limits, width=20)
        self.monthly_entry.grid(row=1, column=1, sticky="ew", pady=6)
        ttk.Button(limits, text="Save weekly and monthly limits", style="Accent.TButton", command=self.save_period_budgets).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        category_frame = ttk.LabelFrame(self.budgets_tab, text="Monthly category limit", padding=14)
        category_frame.pack(fill="x", pady=14)
        ttk.Label(category_frame, text="Category").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        self.budget_category_entry = ttk.Entry(category_frame, width=22)
        self.budget_category_entry.grid(row=0, column=1, sticky="ew", pady=5)
        ttk.Label(category_frame, text="Limit (THB)").grid(row=0, column=2, sticky="w", padx=(16, 10), pady=5)
        self.category_limit_entry = ttk.Entry(category_frame, width=16)
        self.category_limit_entry.grid(row=0, column=3, sticky="ew", pady=5)
        ttk.Button(category_frame, text="Save category limit", command=self.save_category_budget).grid(row=1, column=0, columnspan=4, sticky="w", pady=(8, 0))
        category_frame.columnconfigure(1, weight=1)

        ttk.Label(self.budgets_tab, text="Current budget status", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(2, 8))
        self.budget_status = tk.Text(self.budgets_tab, height=11, wrap="word", font=("Segoe UI", 10), bg=CARD, fg=INK, relief="flat", padx=12, pady=10, state="disabled")
        self.budget_status.pack(fill="both", expand=True)

    def build_categories(self):
        ttk.Label(self.categories_tab, text="Where did it go?", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(self.categories_tab, text="All recorded expenses, grouped by category.", style="Subtitle.TLabel").pack(anchor="w", pady=(2, 12))
        columns = ("category", "spent", "share", "bar")
        self.category_tree = ttk.Treeview(self.categories_tab, columns=columns, show="headings", height=15)
        for col, title, width in [
            ("category", "Category", 190), ("spent", "Spent (THB)", 150),
            ("share", "Share of spending", 150), ("bar", "Spending bar", 300),
        ]:
            self.category_tree.heading(col, text=title)
            self.category_tree.column(col, width=width, anchor="w" if col in ("category", "bar") else "center")
        self.category_tree.pack(fill="both", expand=True, pady=(0, 12))
        self.category_total = ttk.Label(self.categories_tab, text="Total expenses: ฿0.00", font=("Segoe UI", 11, "bold"))
        self.category_total.pack(anchor="e")

    def open_add_transaction(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add transaction")
        dialog.configure(bg=BG)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Add a transaction", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

        ttk.Label(frame, text="Type").grid(row=1, column=0, sticky="w", padx=(0, 14), pady=7)
        kind_var = tk.StringVar(value="expense")
        kind_box = ttk.Combobox(frame, textvariable=kind_var, values=("income", "expense"), state="readonly", width=27)
        kind_box.grid(row=1, column=1, sticky="ew", pady=7)

        ttk.Label(frame, text="Amount (THB)").grid(row=2, column=0, sticky="w", padx=(0, 14), pady=7)
        amount_entry = ttk.Entry(frame, width=30)
        amount_entry.grid(row=2, column=1, sticky="ew", pady=7)

        ttk.Label(frame, text="Category").grid(row=3, column=0, sticky="w", padx=(0, 14), pady=7)
        category_entry = ttk.Entry(frame, width=30)
        category_entry.grid(row=3, column=1, sticky="ew", pady=7)

        ttk.Label(frame, text="Description (optional)").grid(row=4, column=0, sticky="w", padx=(0, 14), pady=7)
        description_entry = ttk.Entry(frame, width=30)
        description_entry.grid(row=4, column=1, sticky="ew", pady=7)

        def save():
            try:
                amount = float(amount_entry.get().strip())
            except ValueError:
                messagebox.showerror("Invalid amount", "Please enter a valid number, such as 120 or 120.50.", parent=dialog)
                return
            if amount <= 0:
                messagebox.showerror("Invalid amount", "Amount must be greater than zero.", parent=dialog)
                return
            category = category_entry.get().strip()
            if not category:
                messagebox.showerror("Missing category", "Please enter a category.", parent=dialog)
                return

            # The existing backend validates and saves the transaction to JSON.
            success = add_transaction(kind_var.get(), amount, category, description_entry.get().strip())
            if success:
                dialog.destroy()
                self.refresh_all()
                message = "Got that BREAD" if kind_var.get() == "income" else "Money OUT"
                messagebox.showinfo("Transaction saved", message, parent=self.root)

        buttons = ttk.Frame(frame)
        buttons.grid(row=5, column=0, columnspan=2, sticky="e", pady=(16, 0))
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(buttons, text="Save transaction", style="Accent.TButton", command=save).pack(side="right")
        amount_entry.focus_set()
        dialog.bind("<Return>", lambda event: save())
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def save_period_budgets(self):
        weekly_text = self.weekly_entry.get().strip()
        monthly_text = self.monthly_entry.get().strip()

        if not weekly_text and not monthly_text:
            messagebox.showerror("Missing budget", "Enter a weekly or monthly limit first.", parent=self.root)
            return

        try:
            weekly = float(weekly_text) if weekly_text else None
            monthly = float(monthly_text) if monthly_text else None
        except ValueError:
            messagebox.showerror("Invalid budget", "Use numbers only, such as 500 or 2500.50.", parent=self.root)
            return

        if (weekly is not None and weekly <= 0) or (monthly is not None and monthly <= 0):
            messagebox.showerror("Invalid budget", "Any budget you enter must be greater than zero.", parent=self.root)
            return

        if weekly is not None:
            set_budget("weekly", weekly)
        if monthly is not None:
            set_budget("monthly", monthly)

        self.refresh_all()
        messagebox.showinfo("Budgets saved", "Your limits are saved. Try not Overspend.", parent=self.root)

    def save_category_budget(self):
        category = self.budget_category_entry.get().strip()
        try:
            amount = float(self.category_limit_entry.get().strip())
        except ValueError:
            messagebox.showerror("Invalid budget", "Enter a valid category limit amount.", parent=self.root)
            return
        if not category:
            messagebox.showerror("Missing category", "Please enter a category name.", parent=self.root)
            return
        if amount <= 0:
            messagebox.showerror("Invalid budget", "Category limit must be greater than zero.", parent=self.root)
            return
        set_category_budget(category, amount)
        self.budget_category_entry.delete(0, "end")
        self.category_limit_entry.delete(0, "end")
        self.refresh_all()
        messagebox.showinfo("Category limit saved", f"Monthly limit for {category.title()} saved.", parent=self.root)

    def refresh_all(self):
        income, expenses, balance = calculate_totals()
        self.income_value.configure(text=f"฿{income:,.2f}")
        self.expense_value.configure(text=f"฿{expenses:,.2f}")
        self.balance_value.configure(text=f"฿{balance:,.2f}", foreground=GREEN if balance >= 0 else RED)

        if balance < 0:
            message = "Your balance is negative. BROKE AHH"
        elif income > 0 and expenses >= income * 0.8:
            message = "Warning: Money getting low, limit your spendings."
        elif income == 0 and expenses == 0:
            message = "Almost cooked"
        else:
            message = "Good wallet health"
        self.wallet_message.configure(text=message)

        self.fill_transaction_tree(self.recent_tree, transactions[-8:])
        self.fill_transaction_tree(self.transactions_tree, transactions)
        self.refresh_budgets()
        self.refresh_categories()

    def refresh_budgets(self):
        budgets = load_budgets()
        weekly_spent = get_spending(transactions, "weekly")
        monthly_spent = get_spending(transactions, "monthly")
        lines = []

        for label, key, spent in [
            ("Weekly", "weekly", weekly_spent),
            ("Monthly", "monthly", monthly_spent),
        ]:
            limit = float(budgets.get(key, 0) or 0)
            if limit <= 0:
                lines.append(f"{label}: Not set yet")
                lines.append("")
                continue
            remaining = limit - spent
            lines.append(f"{label} budget: ฿{limit:,.2f}")
            lines.append(f"  Spent: ฿{spent:,.2f} | Remaining: ฿{remaining:,.2f}")
            if remaining < 0:
                lines.append("  ALERT: Budget exceeded. Your wallet might be cooked")
            elif remaining <= limit * 0.2:
                lines.append("  WARNING: Less than 20% remains.")
            else:
                lines.append("  Status: Looking good.")
            lines.append("")

        lines.append("MONTHLY CATEGORY LIMITS")
        lines.append("------------------------")
        categories = budgets.get("categories", {})
        if not categories:
            lines.append("No category limits set yet.")
        else:
            for category, limit in categories.items():
                spent = get_category_spending(transactions, category)
                remaining = float(limit) - spent
                lines.append(f"{category}: ฿{spent:,.2f} / ฿{float(limit):,.2f} (remaining ฿{remaining:,.2f})")
                if remaining < 0:
                    lines.append("  ALERT: Category budget exceeded!")
                elif remaining <= float(limit) * 0.2:
                    lines.append("  WARNING: Category budget is nearly gone.")

        self.budget_status.configure(state="normal")
        self.budget_status.delete("1.0", "end")
        self.budget_status.insert("1.0", "\n".join(lines))
        self.budget_status.configure(state="disabled")

        # Fill the settings fields with currently saved limits.
        self.weekly_entry.delete(0, "end")
        self.weekly_entry.insert(0, str(budgets.get("weekly", 0) or ""))
        self.monthly_entry.delete(0, "end")
        self.monthly_entry.insert(0, str(budgets.get("monthly", 0) or ""))

    def refresh_categories(self):
        self.category_tree.delete(*self.category_tree.get_children())
        spending = {}
        for item in transactions:
            if item.get("type") == "expense":
                category = item.get("category", "Other")
                spending[category] = spending.get(category, 0) + float(item.get("amount", 0))

        total = sum(spending.values())
        for category, amount in sorted(spending.items(), key=lambda entry: entry[1], reverse=True):
            share = amount / total * 100 if total else 0
            bar = "█" * round(share / 5)
            self.category_tree.insert("", "end", values=(category, f"฿{amount:,.2f}", f"{share:.1f}%", bar))
        self.category_total.configure(text=f"Total expenses: ฿{total:,.2f}")


def main():
    root = tk.Tk()
    CheckyoMoneyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
