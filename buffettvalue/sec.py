"""SEC Company Facts parser: only filed facts known by the requested as-of date."""
from datetime import date
from math import isfinite

CASH_TAGS = ("NetCashProvidedByUsedInOperatingActivities",)
CAPEX_TAGS = ("PaymentsToAcquirePropertyPlantAndEquipment",)
SHARES_TAGS = ("CommonStockSharesOutstanding",)

def _facts(document, taxonomy, tag, unit, as_of):
    entries = document.get("facts", {}).get(taxonomy, {}).get(tag, {}).get("units", {}).get(unit, [])
    valid = []
    for row in entries:
        try:
            filed = date.fromisoformat(row["filed"])
            end = date.fromisoformat(row["end"])
            value = row["val"]
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value):
                continue
            if filed > as_of or end > filed:
                continue
            valid.append((row, filed, end))
        except (KeyError, TypeError, ValueError):
            continue
    return valid

def _annual(document, tag, as_of):
    result = {}
    ambiguous = set()
    for row, filed, end in _facts(document, "us-gaap", tag, "USD", as_of):
        try:
            start = date.fromisoformat(row["start"])
        except (KeyError, ValueError, TypeError):
            continue
        days = (end - start).days
        if not 330 <= days <= 380:
            continue
        if row.get("form") not in ("10-K", "10-K/A"):
            continue
        if tag in CAPEX_TAGS and row['val'] < 0:
            continue
        year = (start, end)
        previous = result.get(year)
        if previous is None or (filed, end) > (previous["filed"], previous["end"]):
            result[year] = {"value": float(row["val"]), "filed": filed, "end": end}
            ambiguous.discard(year)
        elif filed == previous["filed"] and float(row["val"]) != previous["value"]:
            ambiguous.add(year)
    return {period: value for period, value in result.items() if period not in ambiguous}

def _shares(document, as_of):
    rows = _facts(document, "dei", "EntityCommonStockSharesOutstanding", "shares", as_of)
    rows += _facts(document, "us-gaap", "CommonStockSharesOutstanding", "shares", as_of)
    rows = [r for r in rows if r[0]["val"] > 0]
    if not rows:
        return None
    row, filed, end = max(rows, key=lambda r: (r[2], r[1]))
    return {"value": float(row["val"]), "filed": filed.isoformat(), "end": end.isoformat()}

def summarize(document, as_of):
    if not isinstance(document, dict):
        raise ValueError("invalid SEC document")
    as_of = date.fromisoformat(as_of) if isinstance(as_of, str) else as_of
    if not isinstance(as_of, date):
        raise ValueError("invalid as_of")
    operating = _annual(document, CASH_TAGS[0], as_of)
    capex = _annual(document, CAPEX_TAGS[0], as_of)
    years = sorted(set(operating) & set(capex))
    annual = []
    for period in years:
        op, cap = operating[period], capex[period]
        year = period[1].year
        annual.append({"year": year, "operating_cash_flow_usd": op["value"],
                       "capex_usd": cap["value"], "free_cash_flow_usd": op["value"] - cap["value"],
                       "operating_filed": op["filed"].isoformat(), "capex_filed": cap["filed"].isoformat()})
    return {"cik": str(document.get("cik", "")), "entity_name": str(document.get("entityName", "")),
            "as_of": as_of.isoformat(), "annual_fcf": annual[-10:],
            "shares": _shares(document, as_of), "source": "SEC_COMPANYFACTS",
            "paper_eligible": False, "reason": "SEC_FINANCIALS_ONLY_NO_PRICE_OR_FULL_PIT_VALIDATION"}
