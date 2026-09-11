"""
api/index.py — Vercel Serverless Function Entrypoint
Zudio Store Operations Intelligence Engine

Exposes serverless endpoints for Vercel deployment:
  - GET  /api/metrics -> Computed Pandas analytical dimensions (JSON)
  - POST /api/chat    -> AI Copilot (Gemini / OpenAI / Deterministic Safe Mode)
  - OPTIONS           -> CORS Pre-flight handling
"""

import json
import logging
import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler

# Ensure project root is in sys.path so modules like insight_engine, copilot, config are accessible
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import pandas as pd

# Set matplotlib to non-interactive Agg backend to avoid headless server issues
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
    Caches results in memory across warm serverless invocations for sub-10ms response times.
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
    """Vercel Python runtime handler."""

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.lower()

        # Handle /api/metrics (or any path routing containing "metrics")
        if "metrics" in path or path in ("/api", "/api/"):
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

        # 404 for unknown GET
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.lower()

        # Handle /api/chat
        if "chat" in path or path in ("/api", "/api/"):
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
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))


# Local testing convenience
if __name__ == "__main__":
    from http.server import HTTPServer
    server = HTTPServer(("127.0.0.1", 8080), handler)
    print("Test server running at http://127.0.0.1:8080")
    server.serve_forever()
