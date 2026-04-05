#!/usr/bin/env python3
"""
Fail if any markdown page under docs/<lang>/ is not referenced in that language's zensical config.

Run from documentation/:
  python3 scripts/verify_docs_nav.py

Also runs automatically at the start of build_all.py so full builds cannot succeed with orphan pages.
"""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIGS = [
    ("zensical.toml", "docs/en"),
    ("zensical.es.toml", "docs/es"),
    ("zensical.pt.toml", "docs/pt"),
    ("zensical.pt-BR.toml", "docs/pt-BR"),
]


def extract_nav_urls(obj) -> list[str]:
    if isinstance(obj, str):
        return [obj.strip()]
    if isinstance(obj, dict):
        acc: list[str] = []
        for v in obj.values():
            acc.extend(extract_nav_urls(v))
        return acc
    if isinstance(obj, list):
        acc = []
        for item in obj:
            acc.extend(extract_nav_urls(item))
        return acc
    return []


def main() -> int:
    failed = False
    for cfg_name, docs_sub in CONFIGS:
        cfg_path = ROOT / cfg_name
        data = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
        nav = data.get("project", {}).get("nav", [])
        urls = [u for u in extract_nav_urls(nav) if not u.startswith(("http://", "https://"))]

        sections = {u[:-1] for u in urls if u.endswith("/")}
        explicit_md = {u for u in urls if u.endswith(".md")}

        docs_root = ROOT / docs_sub
        md_files = sorted(p.relative_to(docs_root).as_posix() for p in docs_root.rglob("*.md"))

        def covered(path: str) -> bool:
            if path == "index.md":
                return True
            if path in explicit_md:
                return True
            if path.endswith("/index.md"):
                sec = path[: -len("index.md")].rstrip("/")
                return sec in sections
            return False

        orphans = [p for p in md_files if not covered(p)]
        if orphans:
            failed = True
            print(f"{cfg_name}: {len(orphans)} markdown file(s) not reachable from nav:")
            for o in orphans:
                print(f"  - {docs_sub}/{o}")

    if failed:
        print(
            "\nFix: add each file to [[project.nav]] in the matching zensical*.toml, "
            "or add a parent section URL ending with / (covers only that folder's index.md)."
        )
        return 1
    print("Nav coverage OK for all locales.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
