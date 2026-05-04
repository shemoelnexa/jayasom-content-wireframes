#!/usr/bin/env python3
"""Tiny dev server with live-reload for the Jayasom wireframe deck.

Usage:  python dev-server.py [port]    (default 8765)

- Serves files from this folder
- Injects a tiny polling script into every served .html response
- The script polls /_livereload/mtime once a second; if any *.html in the
  folder has been modified, the page reloads (cache-busted)
- Disables HTTP caching so manual reloads also pick up changes
"""
import http.server
import json
import os
import socketserver
import sys
import urllib.parse
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
ROOT = Path(__file__).parent.resolve()

LIVERELOAD_JS = (
    b"(function(){\n"
    b"  var last = null;\n"
    b"  function poll(){\n"
    b"    fetch('/_livereload/mtime', {cache:'no-store'})\n"
    b"      .then(function(r){return r.json();})\n"
    b"      .then(function(d){\n"
    b"        if (last === null) { last = d.mtime; return; }\n"
    b"        if (d.mtime > last) { window.location.reload(); }\n"
    b"      })\n"
    b"      .catch(function(){});\n"
    b"  }\n"
    b"  setInterval(poll, 1000);\n"
    b"  poll();\n"
    b"})();\n"
)

INJECT_TAG = b'<script src="/_livereload.js"></script>\n'


class Handler(http.server.SimpleHTTPRequestHandler):
    def _send_bytes(self, body: bytes, content_type: str, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/_livereload.js':
            self._send_bytes(LIVERELOAD_JS, 'application/javascript')
            return

        if path == '/_livereload/mtime':
            try:
                mtime = max(
                    (p.stat().st_mtime for p in ROOT.glob('*.html')),
                    default=0.0,
                )
            except OSError:
                mtime = 0.0
            body = json.dumps({'mtime': mtime}).encode()
            self._send_bytes(body, 'application/json')
            return

        # Inject the live-reload script into served HTML
        rel = path.lstrip('/')
        if rel == '' or rel.endswith('/'):
            rel += 'index.html'
        if rel.endswith('.html'):
            target = (ROOT / rel).resolve()
            try:
                target.relative_to(ROOT)
            except ValueError:
                self.send_error(403)
                return
            if target.is_file():
                content = target.read_bytes()
                if INJECT_TAG not in content:
                    if b'</body>' in content:
                        content = content.replace(b'</body>', INJECT_TAG + b'</body>', 1)
                    else:
                        content += INJECT_TAG
                self._send_bytes(content, 'text/html; charset=utf-8')
                return

        return super().do_GET()

    def end_headers(self):
        # No-cache for everything else (CSS, JS, images, etc.) so refreshes never serve stale
        if self.path not in ('/_livereload.js', '/_livereload/mtime'):
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, fmt, *args):
        if '/_livereload' in self.path:
            return
        super().log_message(fmt, *args)


class ReusableTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    os.chdir(ROOT)
    with ReusableTCPServer(('', PORT), Handler) as httpd:
        print(f'Serving {ROOT} on http://localhost:{PORT}/  (live-reload enabled)')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nbye')


if __name__ == '__main__':
    main()
