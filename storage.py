import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "transactions.json"


def load_transactions():
    """Load saved transactions, or return an empty list."""

    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        print("Save file format is invalid. Starting with empty records.")
        return []

    except (json.JSONDecodeError, OSError):
        print("Could not read saved data. Starting with empty records.")
        return []


def save_transactions(transactions):
    """Save transactions to a JSON file."""

    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(transactions, file, indent=4, ensure_ascii=False)

    except OSError:
        print("Warning: Could not save your transactions.")
