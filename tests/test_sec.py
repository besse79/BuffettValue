import unittest
from buffettvalue.sec import summarize

def fact(value, filed, end="2025-12-31", start="2025-01-01", form="10-K"):
    return {"val": value, "filed": filed, "start": start, "end": end, "form": form}

def document():
    return {"cik": 1234, "entityName": "Example Corp", "facts": {
        "us-gaap": {
            "NetCashProvidedByUsedInOperatingActivities": {"units": {"USD": [
                fact(100, "2026-02-15"), fact(999, "2026-08-15")]}},
            "PaymentsToAcquirePropertyPlantAndEquipment": {"units": {"USD": [
                fact(20, "2026-02-15"), fact(99, "2026-08-15")]}},
        },
        "dei": {"EntityCommonStockSharesOutstanding": {"units": {"shares": [
            {"val": 10, "filed": "2026-02-15", "end": "2025-12-31"},
            {"val": 20, "filed": "2026-08-15", "end": "2025-12-31"}]}}}
    }}

class SecTests(unittest.TestCase):
    def test_no_lookahead(self):
        r = summarize(document(), "2026-03-01")
        self.assertEqual(r["annual_fcf"][0]["free_cash_flow_usd"], 80)
        self.assertEqual(r["shares"]["value"], 10)
        self.assertFalse(r["paper_eligible"])

    def test_later_amendments_visible_only_later(self):
        r = summarize(document(), "2026-09-01")
        self.assertEqual(r["annual_fcf"][0]["free_cash_flow_usd"], 900)

    def test_before_publication(self):
        r = summarize(document(), "2026-01-01")
        self.assertEqual(r["annual_fcf"], [])
        self.assertIsNone(r["shares"])

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            summarize(document(), "2026-99-99")

    def test_short_quarter_rejected(self):
        d = document()
        d["facts"]["us-gaap"]["NetCashProvidedByUsedInOperatingActivities"]["units"]["USD"] = [
            fact(100, "2026-02-15", start="2025-10-01")]
        self.assertEqual(summarize(d, "2026-03-01")["annual_fcf"], [])
