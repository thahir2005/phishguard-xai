"""
PhishGuard-XAI REST API & Web Dashboard Server
High-performance HTTP server with zero external dependencies.
Provides real-time URL scanning, TreeSHAP explainability, benchmark metrics,
and serves the Web Security Operations Dashboard.
"""

import json
import mimetypes
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add parent path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml_engine.model_core import PhishGuardEngine
from ml_engine.evaluate_benchmark import get_comparison_table
from ml_engine.feature_extractor import FEATURE_COLUMNS

PORT = 8000
DASHBOARD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web_dashboard"))

# Initialize engine singleton
engine = PhishGuardEngine.get_instance()


class PhishGuardRequestHandler(BaseHTTPRequestHandler):

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def _send_json_response(self, status_code: int, data: dict):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # --- API ENDPOINTS ---
        if path == "/api/health":
            self._send_json_response(200, {
                "status": "healthy",
                "service": "PhishGuard-XAI Detection Engine",
                "version": "2.0.0",
                "algorithm": "Gradient Boosted Decision Ensemble (GBDT + TreeSHAP)",
                "test_metrics": engine.test_metrics
            })
            return

        elif path == "/api/benchmark":
            comparison = get_comparison_table()
            self._send_json_response(200, {
                "paper_reference": "Dirchaoui et al. (Procedia Computer Science 2026)",
                "table_1_comparison": comparison
            })
            return

        elif path == "/api/features":
            self._send_json_response(200, {
                "feature_count": len(FEATURE_COLUMNS),
                "features": FEATURE_COLUMNS
            })
            return

        # --- SERVE STATIC DASHBOARD ---
        if path == "/" or path == "":
            file_name = "index.html"
        else:
            file_name = path.lstrip("/")

        file_path = os.path.join(DASHBOARD_DIR, file_name)

        # Basic path traversal protection
        if not os.path.abspath(file_path).startswith(DASHBOARD_DIR):
            self.send_error(403, "Access Denied")
            return

        if os.path.exists(file_path) and os.path.isfile(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self._send_cors_headers()
                self.send_header("Content-Type", mime_type)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(500, f"Error reading file: {str(e)}")
        else:
            self._send_json_response(404, {"error": "Not Found", "path": path})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            raw_body = self.rfile.read(content_length).decode("utf-8")
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}
        else:
            body = {}

        if path == "/api/scan":
            url = body.get("url", "").strip()
            if not url:
                self._send_json_response(400, {"error": "Missing 'url' field in JSON request body."})
                return

            try:
                scan_result = engine.scan_url(url)
                self._send_json_response(200, scan_result)
            except Exception as e:
                self._send_json_response(500, {"error": f"Scan failed: {str(e)}"})

        elif path == "/api/batch-scan":
            urls = body.get("urls", [])
            if not isinstance(urls, list) or len(urls) == 0:
                self._send_json_response(400, {"error": "Expected non-empty list 'urls'."})
                return

            results = []
            for u in urls[:50]:  # limit to 50 per batch
                if isinstance(u, str) and u.strip():
                    results.append(engine.scan_url(u.strip()))

            self._send_json_response(200, {
                "batch_count": len(results),
                "results": results
            })

        else:
            self._send_json_response(404, {"error": "Invalid API endpoint."})

    def log_message(self, format, *args):
        # Clean console output
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def run_server(port=PORT):
    server_address = ("", port)
    httpd = HTTPServer(server_address, PhishGuardRequestHandler)
    print("=" * 70)
    print(f" PhishGuard-XAI Server running at: http://localhost:{port}")
    print(f" - Web Dashboard UI  : http://localhost:{port}/")
    print(f" - Single URL Scan   : POST http://localhost:{port}/api/scan")
    print(f" - Benchmark Metrics : GET  http://localhost:{port}/api/benchmark")
    print(f" - Health & Status   : GET  http://localhost:{port}/api/health")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
