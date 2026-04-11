from __future__ import annotations

import tempfile
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import yaml

from . import parser, renderer


def _load_github_repo() -> str | None:
    settings_file = Path("settings.yaml")
    if settings_file.exists():
        settings = yaml.safe_load(settings_file.read_text()) or {}
        return settings.get("github_repo")
    return None


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
                renderer.render(trip, tmp, yaml_path=yaml_path, github_repo=_load_github_repo())
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


def serve_all(trips_dir: Path, port: int = 5173) -> None:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _yaml_files(self):
            return sorted(trips_dir.glob("*.yaml"))

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self._serve_index()
            elif self.path.endswith(".html"):
                slug = self.path.lstrip("/")[:-5]
                yaml_path = trips_dir / f"{slug}.yaml"
                if yaml_path.exists():
                    self._serve_trip(yaml_path)
                else:
                    self.send_error(404)
            elif self.path == "/mtime":
                self._serve_mtime()
            else:
                self.send_error(404)

        def _serve_index(self):
            trips = []
            for yaml_file in self._yaml_files():
                try:
                    trip = parser.load(str(yaml_file))
                    trips.append((yaml_file.stem, trip))
                except Exception:
                    pass
            try:
                tmp = Path(tempfile.mktemp(suffix=".html"))
                renderer.render_index(trips, tmp)
                html = tmp.read_bytes()
                tmp.unlink(missing_ok=True)
            except Exception as e:
                html = f"<pre style='padding:2rem;color:red'>Error: {e}</pre>".encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html)

        def _serve_trip(self, yaml_path: Path):
            try:
                trip = parser.load(str(yaml_path))
                tmp = Path(tempfile.mktemp(suffix=".html"))
                renderer.render(trip, tmp, yaml_path=yaml_path, github_repo=_load_github_repo())
                html = tmp.read_bytes()
                tmp.unlink(missing_ok=True)
            except Exception as e:
                html = f"<pre style='padding:2rem;color:red'>Error: {e}</pre>".encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html)

        def _serve_mtime(self):
            mtimes = [f.stat().st_mtime for f in self._yaml_files() if f.exists()]
            mtime = str(max(mtimes)) if mtimes else "0"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(mtime.encode())

    url = f"http://localhost:{port}"
    webbrowser.open(url)
    print(f"Serving all trips at {url}  (Ctrl+C to stop)")
    httpd = HTTPServer(("localhost", port), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
