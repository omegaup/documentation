#!/usr/bin/env python3
"""
Multi-language development server for omegaUp documentation.

This server properly serves all language versions from the site/ directory,
allowing language switching to work correctly during local development.
"""

import http.server
import re
import socketserver
import os
import sys
from pathlib import Path

# Change to the site directory
ROOT = Path(__file__).parent
SITE_DIR = ROOT / "site"


def _warn_if_favicon_href_mismatch():
    """Partial single-language rebuilds leave other site/<lang>/ trees stale (wrong favicon, assets)."""
    hrefs = {}
    for lang in ("en", "es", "pt", "pt-BR"):
        idx = SITE_DIR / lang / "index.html"
        if not idx.is_file():
            continue
        text = idx.read_text(encoding="utf-8", errors="replace")
        for tag in re.finditer(r"<link\b[^>]*>", text, re.IGNORECASE):
            t = tag.group(0)
            if not re.search(r'rel\s*=\s*["\']icon["\']', t, re.IGNORECASE):
                continue
            hm = re.search(r'href\s*=\s*(["\'])([^"\']+)\1', t, re.IGNORECASE)
            if hm:
                hrefs[lang] = hm.group(2)
            break
    unique = set(hrefs.values())
    if len(unique) > 1:
        print(
            "Warning: <link rel=\"icon\"> href differs between languages (stale site/ output).\n"
            "  Run: python3 build_all.py\n"
            f"  Seen: {hrefs}"
        )


if not SITE_DIR.exists():
    print(f"Error: {SITE_DIR} does not exist.")
    print("Please build the site first using: zensical build")
    sys.exit(1)

_warn_if_favicon_href_mismatch()

os.chdir(SITE_DIR)

PORT = 8000

class MultiLangHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler that redirects root to /en/"""
    
    def do_GET(self):
        # Redirect root to /en/
        if self.path == "/" or self.path == "":
            self.send_response(302)
            self.send_header("Location", "/en/")
            self.end_headers()
            return
        
        return super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MultiLangHTTPRequestHandler) as httpd:
        print(f"🌍 Multi-language documentation server running at http://localhost:{PORT}/")
        print(f"📂 Serving from: {SITE_DIR}")
        print(f"\n Available languages:")
        print(f"   • English:              http://localhost:{PORT}/en/")
        print(f"   • Español:              http://localhost:{PORT}/es/")
        print(f"   • Português:            http://localhost:{PORT}/pt/")
        print(f"   • Português (Brasil):   http://localhost:{PORT}/pt-BR/")
        print(f"\nPress Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped")
            sys.exit(0)
