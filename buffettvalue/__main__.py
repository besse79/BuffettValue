"""Local research-only DCF CLI. No trades, no network, no credentials."""
import argparse
import json
import sys
from pathlib import Path
from .valuation import dcf

REQUIRED = {"free_cash_flow", "growth", "discount", "terminal_growth", "years", "net_debt", "shares", "price"}

def evaluate(payload):
    if not isinstance(payload, dict) or set(payload) != REQUIRED:
        raise ValueError("DCF JSON must contain exactly: " + ", ".join(sorted(REQUIRED)))
    if any(type(payload[k]) not in (int, float) for k in REQUIRED):
        raise ValueError("all DCF fields must be numeric")
    if type(payload["years"]) is not int:
        raise ValueError("years must be an integer")
    result = dcf(**payload)
    return {"mode": "RESEARCH_ONLY", "assumptions": payload, **result}

def main(argv=None):
    parser = argparse.ArgumentParser(description="BuffettValue V1 offline DCF research (no PAPER orders)")
    parser.add_argument("--input", required=True, type=Path, help="JSON file containing DCF assumptions")
    parser.add_argument("--mkd-instrument")
    parser.add_argument("--currency", choices=["EUR","USD"])
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        if args.mkd_instrument:
            from datetime import datetime, timezone, timedelta
            from .mkd_observations import observed_history
            now = datetime.now(timezone.utc)
            if not args.currency:
                raise ValueError("DCF assumptions must use the specified price currency")
            doc = observed_history(args.mkd_instrument,currency=args.currency,start=now.date()-timedelta(days=4),end=now.date()-timedelta(days=1),as_of=now)
            if not doc["items"]:
                raise ValueError("no recent MKD observations")
            row = doc["items"][-1]
            payload["price"] = float(row["close"])
            result = {**evaluate(payload),"price_source":"MKD_OBSERVED","price_date":row["date"],"currency":args.currency}
        else:
            result = evaluate(payload)
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    except (OSError, ValueError, TypeError, json.JSONDecodeError, OverflowError, ZeroDivisionError) as exc:
        print(f"DCF_ERROR: {exc}", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
