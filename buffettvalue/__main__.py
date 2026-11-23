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
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        print(json.dumps(evaluate(payload), indent=2, sort_keys=True, allow_nan=False))
    except (OSError, ValueError, TypeError, json.JSONDecodeError, OverflowError, ZeroDivisionError) as exc:
        print(f"DCF_ERROR: {exc}", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
