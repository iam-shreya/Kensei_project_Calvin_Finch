"""
Pytest checks for Calvin race gear buy-check output.
These tests assume the model output CSV is saved at the task root as:
calvin_race_gear_buy_check.csv
"""
from pathlib import Path
import csv
import math

OUTPUT = Path("calvin_race_gear_buy_check.csv")
REQUIRED_COLUMNS = {
    "cart_item_id",
    "item_name",
    "decision",
    "final_quantity",
    "line_total",
    "reason",
}

def read_rows():
    assert OUTPUT.exists(), "Missing calvin_race_gear_buy_check.csv"
    with OUTPUT.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows, "CSV has no rows"
    return rows

def by_id(rows, cart_item_id):
    for row in rows:
        if row.get("cart_item_id") == cart_item_id:
            return row
    raise AssertionError(f"Missing row for {cart_item_id}")

def money(value):
    return float(str(value).replace("$", "").strip())

def test_required_filename_and_columns():
    rows = read_rows()
    assert REQUIRED_COLUMNS.issubset(set(rows[0].keys()))

def test_keep_remove_decisions():
    rows = read_rows()
    expected = {
        "C01": "keep",
        "C02": "remove",
        "C03": "remove",
        "C04": "remove",
        "C05": "keep",
        "C06": "remove",
        "C07": "keep",
        "C08": "keep",
    }
    for cart_item_id, decision in expected.items():
        assert by_id(rows, cart_item_id)["decision"].strip().lower() == decision

def test_final_quantities():
    rows = read_rows()
    expected = {
        "C01": "1",
        "C02": "0",
        "C03": "0",
        "C04": "0",
        "C05": "1",
        "C06": "0",
        "C07": "1",
        "C08": "1",
    }
    for cart_item_id, qty in expected.items():
        assert str(by_id(rows, cart_item_id)["final_quantity"]).strip() == qty

def test_final_total_before_fees():
    rows = read_rows()
    total = sum(money(row["line_total"]) for row in rows if row["cart_item_id"].startswith("C"))
    assert math.isclose(total, 191.49, rel_tol=0, abs_tol=0.01)

def test_removed_item_reasons():
    rows = read_rows()
    assert "86.4" in by_id(rows, "C02")["reason"]
    assert "wide" in by_id(rows, "C03")["reason"].lower()
    assert "deliver" in by_id(rows, "C04")["reason"].lower()
    assert "wool" in by_id(rows, "C06")["reason"].lower()

def test_no_purchase_claimed():
    text = OUTPUT.read_text(encoding="utf-8").lower()
    forbidden = ["purchased", "ordered", "order placed", "bought"]
    assert not any(term in text for term in forbidden)
