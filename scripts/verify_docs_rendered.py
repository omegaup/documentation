#!/usr/bin/env python3
"""
After `zensical build`, verify every markdown source page has a matching index.html output.

Run from documentation/: python3 scripts/verify_docs_rendered.py
Requires site/<lang>/ to exist (run after build_all.py or zensical build).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = [
    ("docs/en", "site/en"),
    ("docs/es", "site/es"),
    ("docs/pt", "site/pt"),
    ("docs/pt-BR", "site/pt-BR"),
]


def expected_html(site_root: Path, md_rel: str) -> Path:
    """Map docs-relative path to output path (use_directory_urls)."""
    p = Path(md_rel)
    if md_rel == "index.md":
        return site_root / "index.html"
    if p.name == "index.md":
        return site_root.joinpath(*p.parent.parts, "index.html")
    return site_root.joinpath(*p.with_suffix("").parts, "index.html")


def main() -> int:
    failed = False
    for docs_sub, site_sub in LOCALES:
        docs_root = ROOT / docs_sub
        site_root = ROOT / site_sub
        if not site_root.is_dir():
            print(f"Missing output tree: {site_sub}/ (build the site first).")
            return 1

        md_files = sorted(docs_root.rglob("*.md"))
        for md in md_files:
            rel = md.relative_to(docs_root).as_posix()
            html = expected_html(site_root, rel)
            if not html.is_file():
                failed = True
                print(f"{docs_sub}/{rel} -> missing {html.relative_to(ROOT)}")

        # Count sanity (fast signal for partial builds)
        n_md = len(md_files)
        n_html = sum(
            1
            for h in site_root.rglob("index.html")
            if "assets" not in h.parts
        )
        if n_md != n_html:
            failed = True
            print(
                f"{docs_sub}: count mismatch — {n_md} markdown file(s) vs "
                f"{n_html} content index.html under {site_sub}/"
            )

    if failed:
        print("\nRebuild with a full clean build: python3 build_all.py")
        return 1
    print("Rendered output OK: every markdown page has a matching HTML file (all locales).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
