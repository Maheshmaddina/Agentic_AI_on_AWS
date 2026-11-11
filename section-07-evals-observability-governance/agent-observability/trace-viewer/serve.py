"""Agent trace viewer: a friendlier look at the traces Jaeger collected.

Jaeger's query API doesn't send CORS headers, so a page served from another port
can't read it. This small server (standard library only) serves the viewer page
and forwards its /api/... requests to Jaeger.

Run (Jaeger must be running; see 02_jaeger_tracing_groq.ipynb):
    python serve.py            # then open http://localhost:8090

Settings (environment variables):
    JAEGER_URL   where Jaeger's UI and API listen (default http://localhost:16686)
    PORT         port for this viewer (default 8090)
"""

import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

JAEGER_URL = os.getenv("JAEGER_URL", "http://localhost:16686").rstrip("/")
PORT = int(os.getenv("PORT", "8090"))
PAGE = Path(__file__).with_name("index.html")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/"):
            self._proxy()
        elif self.path.split("?")[0] in ("/", "/index.html"):
            self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        else:
            self._send(404, b"Not found", "text/plain; charset=utf-8")

    def _proxy(self):
        try:
            with urllib.request.urlopen(JAEGER_URL + self.path, timeout=15) as resp:
                self._send(resp.status, resp.read(), resp.headers.get("Content-Type", "application/json"))
        except urllib.error.HTTPError as e:
            self._send(e.code, e.read(), e.headers.get("Content-Type", "application/json"))
        except (urllib.error.URLError, OSError) as e:
            reason = getattr(e, "reason", e)
            body = json.dumps({"error": f"Can't reach Jaeger at {JAEGER_URL} ({reason})"}).encode()
            self._send(502, body, "application/json")

    def _send(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):  # keep the terminal quiet
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Agent trace viewer: http://localhost:{PORT}  (reading Jaeger at {JAEGER_URL})")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
