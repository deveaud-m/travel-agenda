from __future__ import annotations

import tempfile
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from . import parser, renderer


def serve(yaml_path: Path, port: int = 5173) -> None:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            if self.path == "/":
                self._serve_html()
            elif self.path == "/mtime":
                self._serve_mtime()
            else:
                self.send_error(404)

        def do_POST(self):
            if self.path == "/save":
                self._save()
            else:
                self.send_error(404)

        def _serve_html(self):
            try:
                trip = parser.load(str(yaml_path))
                tmp = Path(tempfile.mktemp(suffix=".html"))
                renderer.render(trip, tmp, yaml_path=yaml_path)
                html = tmp.read_bytes()
                tmp.unlink(missing_ok=True)
            except Exception as e:
                html = f"<pre style='padding:2rem;color:red'>Error: {e}</pre>".encode()

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html)

        def _serve_mtime(self):
            mtime = str(yaml_path.stat().st_mtime)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(mtime.encode())

        def _save(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                tmp = Path(tempfile.mktemp(suffix=".yaml"))
                tmp.write_bytes(body)
                parser.load(str(tmp))  # validate before saving
                tmp.unlink(missing_ok=True)
                yaml_path.write_bytes(body)
                self.send_response(200)
                self.end_headers()
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(str(e).encode())

    url = f"http://localhost:{port}"
    webbrowser.open(url)
    print(f"Serving at {url}  (Ctrl+C to stop)")
    httpd = HTTPServer(("localhost", port), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
