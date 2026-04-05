#!/usr/bin/env python3
"""
Build all language versions of the omegaUp documentation site.

This script builds the documentation for all configured languages
(English, Spanish, Portuguese, and Brazilian Portuguese).

Before building, runs scripts/verify_docs_nav.py (every .md is listed in nav).
After a successful build, runs scripts/verify_docs_rendered.py (every .md has HTML output).
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
VERIFY_NAV = ROOT / "scripts" / "verify_docs_nav.py"
VERIFY_RENDERED = ROOT / "scripts" / "verify_docs_rendered.py"
CONFIG_FILES = [
    "zensical.toml",       # English
    "zensical.es.toml",    # Spanish
    "zensical.pt.toml",    # Portuguese
    "zensical.pt-BR.toml", # Brazilian Portuguese
]

# Check for virtual environment
VENV_DIR = ROOT / ".venv"
if VENV_DIR.exists():
    PYTHON = str(VENV_DIR / "bin" / "python3")
    ZENSICAL = str(VENV_DIR / "bin" / "zensical")
else:
    PYTHON = "python3"
    ZENSICAL = "zensical"

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"🔨 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        return False

def main():
    print("🌍 Building omegaUp Documentation - All Languages")
    print(f"📂 Working directory: {ROOT}")

    if not VERIFY_NAV.is_file():
        print(f"❌ Missing {VERIFY_NAV.name}; cannot verify navigation coverage.")
        return 1
    if not run_command(
        [PYTHON, str(VERIFY_NAV)],
        "Verifying nav covers every markdown page (all locales)",
    ):
        print(
            "\nFix orphan pages in zensical*.toml, then rebuild. "
            "See scripts/verify_docs_nav.py for rules."
        )
        return 1

    # Clean the site directory first
    print("\n🧹 Cleaning site directory...")
    site_dir = ROOT / "site"
    if site_dir.exists():
        import shutil
        shutil.rmtree(site_dir)
        print("   Removed existing site/ directory")
    
    # Build each language
    failures = []
    for config in CONFIG_FILES:
        lang = config.replace("zensical.", "").replace(".toml", "")
        if lang == "toml":  # zensical.toml -> "en"
            lang = "en"
        
        config_path = ROOT / config
        if not config_path.exists():
            print(f"⚠️  Config file not found: {config}")
            failures.append(lang)
            continue
        
        success = run_command(
            [ZENSICAL, "build", "--clean", "--config-file", config],
            f"Building {lang.upper()} documentation"
        )
        
        if not success:
            failures.append(lang)
    
    # Create root redirect to /en/
    print("\n🔗 Creating root redirect...")
    redirect_html = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta http-equiv="refresh" content="0; url=./en/" />
    <link rel="icon" href="./en/assets/images/favicon-76x76.png" type="image/png" />
    <link rel="canonical" href="./en/" />
    <title>omegaUp Documentation</title>
    <script>
      (function() {
        location.replace('./en/');
      })();
    </script>
  </head>
  <body>
    <p>Redirecting to <a href="./en/">English documentation</a>…</p>
  </body>
</html>
"""
    
    index_file = ROOT / "site" / "index.html"
    index_file.write_text(redirect_html, encoding="utf-8")
    print("   Created site/index.html redirect")

    # Summary
    print("\n" + "="*60)
    if failures:
        print("⚠️  Build completed with errors")
        print(f"   Failed languages: {', '.join(failures)}")
        return 1

    if not VERIFY_RENDERED.is_file():
        print(f"❌ Missing {VERIFY_RENDERED.name}; cannot verify rendered HTML.")
        return 1
    if not run_command(
        [PYTHON, str(VERIFY_RENDERED)],
        "Verifying every markdown page produced HTML (all locales)",
    ):
        print(
            "\nSome source pages are missing from site/. "
            "See scripts/verify_docs_rendered.py."
        )
        return 1

    print("✅ All language versions built successfully!")
    print("\n📚 Available languages:")
    print("   • English:              site/en/")
    print("   • Español:              site/es/")
    print("   • Português:            site/pt/")
    print("   • Português (Brasil):   site/pt-BR/")
    print("\n🚀 To serve locally, run:")
    print("   python3 serve_multilang.py")
    print("   or")
    print("   cd site && python3 -m http.server 8000")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Build interrupted by user")
        sys.exit(130)
