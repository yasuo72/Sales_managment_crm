"""
api/index.py — Vercel Serverless Function & Full-Stack Web Handler
Zudio Store Operations Intelligence Engine

Unified Serverless Handler for Vercel:
  - GET  /             -> Serves web/index.html (Executive Dashboard)
  - GET  /web/*        -> Serves static assets (style.css, app.js)
  - GET  /api/metrics  -> Pre-computed Pandas analytics JSON
  - POST /api/chat     -> AI Copilot (Gemini / OpenAI / Safe Mode)
  - GET  /output/*     -> Matplotlib visual charts
  - GET  /assets/*     -> Project screenshots & assets
  - OPTIONS            -> CORS Pre-flight handling
"""

import json
import logging
import mimetypes
import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler

# Ensure project root is in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import pandas as pd

# Headless matplotlib safety
try:
    import matplotlib
    matplotlib.use("Agg")
except Exception:
    pass

from copilot import build_system_prompt, query_ai
from insight_engine import AnalyticsEngine, DataValidator, DEFAULT_INPUT_PATH

# ---------------------------------------------------------------------------
# Global In-Memory Warm-Start Cache
# ---------------------------------------------------------------------------
_metrics_cache = None
_system_instruction = None


def get_metrics_and_context():
    """
    Computes or retrieves cached ground-truth metrics from sales_data.csv.
    Caches in memory across warm serverless invocations for sub-10ms response times.
    """
    global _metrics_cache, _system_instruction
    if _metrics_cache is not None:
        return _metrics_cache, _system_instruction

    csv_path = os.path.join(ROOT_DIR, DEFAULT_INPUT_PATH)
    if not os.path.exists(csv_path):
        from generate_data import generate_sales_dataset, write_csv
        write_csv(generate_sales_dataset(), csv_path)

    raw_df = pd.read_csv(csv_path)
    clean_df, _ = DataValidator.validate_and_clean(raw_df)
    analytics = AnalyticsEngine(clean_df)
    _metrics_cache = analytics.compute_all_metrics()
    _system_instruction = build_system_prompt(_metrics_cache)
    return _metrics_cache, _system_instruction


# ---------------------------------------------------------------------------
# Vercel Serverless Request Handler
# ---------------------------------------------------------------------------

class handler(BaseHTTPRequestHandler):
    """Full-stack Vercel serverless request handler."""

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _resolve_path(self) -> str:
        """Resolves the real requested URL from Vercel rewrite headers or query parameters."""
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)

        # 1. Injected by vercel.json rewrite: ?route_path=...
        if "route_path" in qs and qs["route_path"][0]:
            return "/" + qs["route_path"][0].lstrip("/")

        # 2. Vercel edge rewrite headers
        for h in ("x-matched-path", "x-invoke-path", "x-forwarded-uri"):
            val = self.headers.get(h)
            if val and val != "/api/index.py":
                return val

        # 3. Direct path fallback
        p = parsed.path.rstrip("/")
        if not p or p == "/api/index.py":
            return "/"
        return p

    def _serve_file(self, file_path: str, default_content_type: str = "text/plain"):
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self.send_response(404)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"File not found: {os.path.basename(file_path)}"}).encode("utf-8"))
            return

        mime, _ = mimetypes.guess_type(file_path)
        content_type = mime or default_content_type
        if "text/" in content_type or "javascript" in content_type:
            content_type += "; charset=utf-8"

        with open(file_path, "rb") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self._set_cors_headers()
        self.send_header("Content-Length", str(len(content)))
        if any(file_path.endswith(ext) for ext in (".css", ".js", ".png", ".jpg", ".svg", ".ico")):
            self.send_header("Cache-Control", "public, max-age=86400")
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        path = self._resolve_path()

        # 1. Root / UI Dashboard → web/index.html
        if path in ("/", "/index.html", "/web", "/web/index.html", "/api/index.py"):
            index_file = os.path.join(ROOT_DIR, "web", "index.html")
            self._serve_file(index_file, "text/html; charset=utf-8")
            return

        # 2. Metrics API → pre-computed analytics JSON
        if path.endswith("/api/metrics") or path == "/api/metrics" or "metrics" in path:
            try:
                metrics, _ = get_metrics_and_context()
                body = json.dumps(metrics, default=str).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self._set_cors_headers()
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                err_body = json.dumps({"error": str(e)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self._set_cors_headers()
                self.send_header("Content-Length", str(len(err_body)))
                self.end_headers()
                self.wfile.write(err_body)
            return

        # 3. Static assets from web/ (e.g. /web/style.css, /web/app.js)
        if path.startswith("/web/"):
            rel_path = path[5:]
            file_path = os.path.join(ROOT_DIR, "web", rel_path)
            self._serve_file(file_path)
            return

        # Direct asset fallback (e.g. /style.css or /app.js)
        if path in ("/style.css", "/app.js"):
            file_path = os.path.join(ROOT_DIR, "web", path.lstrip("/"))
            self._serve_file(file_path)
            return

        # 4. Output chart images (/output/top_products.png)
        if path.startswith("/output/"):
            rel_path = path[8:]
            file_path = os.path.join(ROOT_DIR, "output", rel_path)
            self._serve_file(file_path, "image/png")
            return

        # 5. Assets (/assets/*)
        if path.startswith("/assets/"):
            rel_path = urllib.parse.unquote(path[8:])
            file_path = os.path.join(ROOT_DIR, "assets", rel_path)
            self._serve_file(file_path, "image/png")
            return

        # 6. Any other GET that is not an API -> fallback to index.html (SPA routing safety)
        if not path.startswith("/api/"):
            index_file = os.path.join(ROOT_DIR, "web", "index.html")
            self._serve_file(index_file, "text/html; charset=utf-8")
            return

        # 404 for unknown API GET
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({"error": f"Endpoint '{path}' not found"}).encode("utf-8"))

    def do_POST(self):
        path = self._resolve_path().lower()

        # All POST traffic to chat API
        if "chat" in path or path in ("/api", "/api/", "/", "/api/index.py"):
            try:
                metrics, sys_prompt = get_metrics_and_context()
                content_len = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                data = json.loads(raw_body) if raw_body else {}
                user_msg = data.get("message", "").strip()

                if not user_msg:
                    reply = "Please provide a question about store sales, stockouts, or product performance."
                else:
                    reply = query_ai(user_msg, sys_prompt, metrics)

                resp_data = json.dumps({"reply": reply, "status": "ok"}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self._set_cors_headers()
                self.send_header("Content-Length", str(len(resp_data)))
                self.end_headers()
                self.wfile.write(resp_data)
            except Exception as e:
                err_body = json.dumps({"error": str(e), "reply": f"Error: {e}"}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self._set_cors_headers()
                self.send_header("Content-Length", str(len(err_body)))
                self.end_headers()
                self.wfile.write(err_body)
            return

        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({"error": f"Endpoint '{path}' not found"}).encode("utf-8"))


if __name__ == "__main__":
    from http.server import HTTPServer
    server = HTTPServer(("127.0.0.1", 8080), handler)
    print("Vercel dev test server running at http://127.0.0.1:8080")
    server.serve_forever()
