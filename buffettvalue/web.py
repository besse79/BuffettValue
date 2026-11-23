"""Local-only DCF research UI. No network data acquisition and no trading."""
import json
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs
from .__main__ import evaluate

FIELDS = ("free_cash_flow", "growth", "discount", "terminal_growth", "years", "net_debt", "shares", "price")
EXAMPLE = dict(free_cash_flow=1000000000, growth=0.05, discount=0.10,
               terminal_growth=0.02, years=10, net_debt=2000000000,
               shares=500000000, price=25)

def page(result=None, error=None):
    fields = "".join(
        f'<label>{escape(k)} <input name="{escape(k)}" type="number" step="any" required value="{EXAMPLE[k]}"></label>'
        for k in FIELDS
    )
    output = ('<pre>' + escape(json.dumps(result, indent=2, ensure_ascii=False)) + '</pre>') if result else ''
    warning = ('<p role="alert">' + escape(str(error)) + '</p>') if error else ''
    return ("""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>BuffettValue — DCF</title><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font:16px system-ui;max-width:760px;margin:2rem auto;padding:0 1rem}
label{display:flex;justify-content:space-between;gap:1rem;margin:.7rem 0}
input{max-width:220px;padding:.4rem}button{padding:.7rem 1rem}
pre{overflow:auto;background:#eee;padding:1rem}p[role=alert]{color:#a00}</style></head><body>
<h1>BuffettValue — DCF</h1><p>Recherche uniquement. Hypothèses manuelles,
aucune donnée de marché certifiée, aucun ordre PAPER ou réel.</p>
<form method="post" action="/calculate">""" + fields +
            '<button type="submit">Calculer la valeur intrinsèque</button></form>' +
            warning + output + '</body></html>')

class Handler(BaseHTTPRequestHandler):
    def _respond(self, status, body, content_type="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            return self._respond(200, page())
        if self.path == "/health":
            return self._respond(200, '{"status":"ok","mode":"RESEARCH_ONLY"}', "application/json")
        return self._respond(404, "Not found", "text/plain")

    def do_POST(self):
        if self.path != "/calculate":
            return self._respond(404, "Not found", "text/plain")
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 8192:
                raise ValueError("invalid request size")
            raw = self.rfile.read(length).decode("utf-8")
            params = parse_qs(raw, strict_parsing=True)
            if set(params) != set(FIELDS) or any(len(v) != 1 for v in params.values()):
                raise ValueError("all eight assumptions are required exactly once")
            data = {k: int(params[k][0]) if k == "years" else float(params[k][0]) for k in FIELDS}
            result = evaluate(data)
            return self._respond(200, page(result=result))
        except (ValueError, UnicodeError, OverflowError, ZeroDivisionError) as exc:
            return self._respond(400, page(error=exc))

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("invalid port")
    print(f"BuffettValue DCF: http://127.0.0.1:{args.port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()

if __name__ == "__main__":
    main()
