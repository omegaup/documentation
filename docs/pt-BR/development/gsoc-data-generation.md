---
title: GSoC documentation data files
description: How omegaUp generates GSoC year pages from JSON data
---

# GSoC documentation data files

The `community/gsoc/` section uses a data-driven setup so year pages stay consistent.

## How it works

1. **Data**: Year-specific content lives in `community/gsoc/_data/gsoc-data.json` (and mirrored YAML where present).
2. **Generator**: From the `documentation/` directory, run `python3 scripts/generate-gsoc-pages.py` to refresh the `YYYY.md` files.
3. **Hub page**: `community/gsoc/index.md` is the public landing page (do not add a `README.md` in that folder — Zensical treats `README.md` as the section index and it will replace `index.md`).

## Adding a new year

### Current year (with project ideas)

1. Edit `docs/<lang>/community/gsoc/_data/gsoc-data.json` for each locale you maintain.
2. Add a `years["YYYY"]` object with `type`, `title`, `description`, `intro`, `project_ideas`, `application_process`, `communications`, `faq`, `related_docs`, etc.
3. Set the previous year to `"type": "past"` and use a `projects` array instead of `project_ideas` where applicable.
4. Run `python3 scripts/generate-gsoc-pages.py` from `documentation/`.
5. Run `python3 build_all.py` and commit the updated markdown.

### Past year (completed projects)

Use `"type": "past"` and a `projects` array with `name`, `description`, and `result` per project, then regenerate as above.

## File layout

```
documentation/docs/<lang>/community/gsoc/
├── _data/
│   └── gsoc-data.json
├── index.md          # Public hub (cards + links)
├── 2023.md           # Generated
├── 2024.md           # Generated
└── ...
```

## Notes

- The generator uses only the Python standard library.
- Commit generated `YYYY.md` files after changing the data file.
- Never place a `README.md` next to `index.md` in `community/gsoc/` — it becomes the URL `/community/gsoc/` and hides the real hub page.
