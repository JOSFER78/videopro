#!/usr/bin/env python3
"""
VideoPro Development Server on Port 7001
Serves the web application from workspace or static web dir with reverse proxy to FastAPI backend (8080).
"""

import os
import sys
import urllib.request
import urllib.error
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 7001

# Determine web directory to serve
CANDIDATE_DIRS = [
    "/home/ubuntu/workspace/pro/webs/11-videopro",
    "/var/www/pro/videopro",
    "/home/ubuntu/.hermes/skills/creative/videopro"
]
WEB_DIR = next((d for d in CANDIDATE_DIRS if os.path.exists(os.path.join(d, "index.html"))), CANDIDATE_DIRS[0])
API_BACKEND = "http://127.0.0.1:8080"

class DevProxyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        # Proxy API calls
        if self.path.startswith("/pro/videopro/api/") or self.path.startswith("/api/"):
            self._proxy_request("GET")
        elif self.path in ["/", "/pro/videopro", "/pro/videopro/"]:
            self.path = "/index.html"
            return super().do_GET()
        else:
            return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/pro/videopro/api/") or self.path.startswith("/api/"):
            self._proxy_request("POST")
        else:
            self.send_error(405, "Method Not Allowed")

    def _proxy_request(self, method):
        # Normalize target URL
        rel_path = self.path
        if rel_path.startswith("/pro/videopro/api/"):
            target_path = rel_path[len("/pro/videopro/api"):]
        else:
            target_path = rel_path
        
        target_url = f"{API_BACKEND}{target_path}"
        
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None
        
        headers = {}
        for k, v in self.headers.items():
            if k.lower() not in ["host", "content-length"]:
                headers[k] = v
        
        req = urllib.request.Request(target_url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                self.send_response(resp.status)
                for header, value in resp.getheaders():
                    if header.lower() not in ["transfer-encoding", "content-length"]:
                        self.send_header(header, value)
                resp_body = resp.read()
                self.send_header("Content-Length", str(len(resp_body)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for header, value in e.headers.items():
                if header.lower() not in ["transfer-encoding", "content-length"]:
                    self.send_header(header, value)
            err_body = e.read()
            self.send_header("Content-Length", str(len(err_body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(err_body)
        except Exception as e:
            self.send_error(502, f"Bad Gateway: {str(e)}")

    def log_message(self, format, *args):
        sys.stderr.write(f"[DevServer:7001] {self.address_string()} - {format % args}\n")

if __name__ == "__main__":
    server_address = ("0.0.0.0", PORT)
    httpd = HTTPServer(server_address, DevProxyHandler)
    print(f"==================================================")
    print(f"🚀 VideoPro Development Server running on port {PORT}")
    print(f"   Local URL:    http://127.0.0.1:{PORT}/")
    print(f"   Network URL:  http://0.0.0.0:{PORT}/")
    print(f"   Proxying API: {API_BACKEND}")
    print(f"   Root Dir:     {WEB_DIR}")
    print(f"==================================================")
    sys.stdout.flush()
    httpd.serve_forever()
