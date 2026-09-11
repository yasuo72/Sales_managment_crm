"""
app.py — Zudio Store Operations Dashboard Server

Thin HTTP server shell: routes requests, serves static files, and delegates
all business intelligence to the copilot module.

Responsibilities (only):
  - Serve index.html and static assets from web/ and output/
  - Expose /api/metrics  (GET)  → pre-computed analytics JSON
  - Expose /api/chat     (POST) → AI copilot answers via copilot.query_ai()
  - Cache metrics in-memory; auto-reload when sales_data.csv changes on disk
"""

import json
import logging
import os
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from typing import Optional

import pandas as pd

from copilot import build_system_prompt, query_ai
from insight_engine import AnalyticsEngine, DataValidator, DEFAULT_INPUT_PATH

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("WebServer")

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")


# ---------------------------------------------------------------------------
# Threaded HTTP server
# ---------------------------------------------------------------------------

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handles each request in its own thread for snappy browser responsiveness."""
    daemon_threads = True


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class StoreDashboardHandler(SimpleHTTPRequestHandler):
    """
    Routes HTTP requests to static assets or API handlers.
    All business logic is delegated to copilot.py and insight_engine.py.
    """

    # Class-level cache shared across all threads
    metrics_cache: Optional[dict] = None
    system_instruction: Optional[str] = None
    last_csv_mtime: Optional[float] = None

    # ------------------------------------------------------------------ #
    # Cache / warm-up                                                      #
    # ------------------------------------------------------------------ #

    @classmethod
    def load_metrics_and_context(cls, force: bool = False) -> None:
        """
        Loads and caches pre-computed sales metrics from CSV.
        Auto-generates sales_data.csv if missing.
        Refreshes only when the CSV file is modified on disk.
        """
        csv_path = os.path.join(BASE_DIR, DEFAULT_INPUT_PATH)

        if not os.path.exists(csv_path):
            from generate_data import generate_sales_dataset, write_csv
            logger.info("sales_data.csv not found — generating dataset now...")
            write_csv(generate_sales_dataset(), csv_path)

        current_mtime = os.path.getmtime(csv_path) if os.path.exists(csv_path) else None
        if not force and cls.metrics_cache is not None and current_mtime == cls.last_csv_mtime:
            return  # Cache is still fresh

        raw_df = pd.read_csv(csv_path)
        clean_df, _ = DataValidator.validate_and_clean(raw_df)
        analytics = AnalyticsEngine(clean_df)
        cls.metrics_cache = analytics.compute_all_metrics()
        cls.last_csv_mtime = current_mtime
        cls.system_instruction = build_system_prompt(cls.metrics_cache)

        logger.info("Store metrics and AI copilot context successfully loaded from CSV.")

    # ------------------------------------------------------------------ #
    # GET routing                                                          #
    # ------------------------------------------------------------------ #

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Root → index.html
        if path in ("/", "/index.html"):
            self.send_file_response(os.path.join(WEB_DIR, "index.html"), "text/html; charset=utf-8")
            return

        # /api/metrics → JSON analytics payload
        if path == "/api/metrics":
            self.load_metrics_and_context()
            self.send_json_response(self.metrics_cache or {})
            return

        # /web/* → static CSS / JS / HTML assets
        if path.startswith("/web/"):
            file_path = os.path.join(WEB_DIR, path[5:])
            if os.path.exists(file_path):
                if path.endswith(".css"):
                    mime = "text/css"
                elif path.endswith(".js"):
                    mime = "application/javascript"
                else:
                    mime = "text/html"
                self.send_file_response(file_path, mime)
                return

        # /output/* → chart PNG images
        if path.startswith("/output/"):
            file_path = os.path.join(BASE_DIR, "output", path[8:])
            if os.path.exists(file_path):
                self.send_file_response(file_path, "image/png")
                return

        self.send_error(404, "File Not Found")

    # ------------------------------------------------------------------ #
    # POST routing                                                         #
    # ------------------------------------------------------------------ #

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/chat":
            self.load_metrics_and_context()

            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")

            try:
                data = json.loads(body)
                user_msg = data.get("message", "").strip()
                if not user_msg:
                    self.send_json_response({"error": "Empty message"}, status=400)
                    return

                reply = query_ai(user_msg, self.system_instruction, self.metrics_cache or {})
                self.send_json_response({"reply": reply})

            except Exception as exc:
                logger.error(f"Chat endpoint error: {exc}")
                self.send_json_response({"reply": f"Error generating answer: {exc}"}, status=500)
            return

        self.send_error(404, "Endpoint Not Found")

    # ------------------------------------------------------------------ #
    # Response helpers                                                     #
    # ------------------------------------------------------------------ #

    def send_json_response(self, data: dict, status: int = 200) -> None:
        try:
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass  # Client disconnected mid-response — safe to ignore

    def send_file_response(self, filepath: str, content_type: str) -> None:
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass  # Client disconnected mid-response — safe to ignore


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def start_server(port: int = PORT) -> None:
    StoreDashboardHandler.load_metrics_and_context()
    httpd = ThreadedHTTPServer(("127.0.0.1", port), StoreDashboardHandler)
    logger.info("===========================================================")
    logger.info(" ZUDIO STORE OPERATIONS DASHBOARD & COPILOT")
    logger.info(f" Local URL: http://127.0.0.1:{port}")
    logger.info(" Press Ctrl+C to terminate server.")
    logger.info("===========================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nShutting down server.")
        httpd.server_close()


if __name__ == "__main__":
    start_server(PORT)
