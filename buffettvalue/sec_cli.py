"""Read a downloaded SEC companyfacts JSON; never place orders."""
import argparse
import json
import sys
from pathlib import Path
from .sec import summarize

def main(argv=None):
    parser = argparse.ArgumentParser(description="Point-in-time SEC Company Facts summary")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--as-of", required=True, help="YYYY-MM-DD")
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
        result = summarize(document, args.as_of)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError, OverflowError) as exc:
        print(f"SEC_ERROR: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
