#!/usr/bin/env python3
"""Simple HTTP server for BIOTICA reports"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 8000
DIRECTORY = "reports"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

print(f"\n🌐 BIOTICA Report Server")
print(f"📁 Serving reports from: {DIRECTORY}/")
print(f"📍 Visit: http://localhost:{PORT}")
print(" Press Ctrl+C to stop\n")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
