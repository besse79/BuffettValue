"""SEC companyfacts download with SEC-compliant identification and local cache."""
import argparse
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from .sec import summarize

SEC_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"

def fetch_companyfacts(cik, user_agent, cache_dir, opener=urlopen):
    if not isinstance(cik, int) or isinstance(cik, bool) or not 1 <= cik <= 9999999999:
        raise ValueError("CIK must be an integer between 1 and 9999999999")
    if not user_agent or "@" not in user_agent or len(user_agent.strip()) < 12:
        raise ValueError("SEC_USER_AGENT must identify the requester with a contact email")
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    target = cache_dir / f"CIK{cik:010d}.json"
    req = Request(SEC_URL.format(cik=cik), headers={
        "User-Agent": user_agent.strip(), "Accept": "application/json"})
    with opener(req, timeout=25) as response:
        payload = response.read(20_000_001)
    if len(payload) > 20_000_000:
        raise ValueError("SEC response exceeds size limit")
    document = json.loads(payload)
    if not isinstance(document, dict) or type(document.get("cik")) is not int or document["cik"] != cik:
        raise ValueError("SEC response CIK mismatch")
    if not isinstance(document.get("facts"), dict):
        raise ValueError("SEC response missing facts")
    temporary = target.with_suffix(".json.tmp")
    temporary.write_bytes(payload)
    temporary.replace(target)
    return document, target

def main(argv=None):
    parser = argparse.ArgumentParser(description="Download SEC Company Facts and summarize filed FCF")
    parser.add_argument("--cik", type=int, required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--cache-dir", default="data/sec")
    args = parser.parse_args(argv)
    try:
        document, path = fetch_companyfacts(args.cik, os.getenv("SEC_USER_AGENT"), args.cache_dir)
        result = summarize(document, args.as_of)
        result["cache_file"] = str(path)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError, TimeoutError) as exc:
        print(f"SEC_DOWNLOAD_ERROR: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
