---
title: GSoC documentation data files
description: How omegaUp generates GSoC year pages from JSON data
icon: bootstrap/code
---

# GSoC documentation data files {#gsoc-documentation-data-files}

Every year omegaUp runs a Google Summer of Code campaign, and every year the docs need one page per year: a "current" page full of project ideas and the application funnel while the campaign is live, and a lean "past" page listing what got shipped once it's over. Rather than hand-write those pages and let their headings drift apart, we keep the year-specific content in a single JSON data file and stamp out the Markdown from it with a small Python generator. Think of `scripts/generate-gsoc-pages.py` as a tiny template compiler whose only template language is Python f-strings and whose only input is `_data/gsoc-data.json` — no Jinja, no Zensical plugin, nothing but the standard library, so it runs on a bare `python3` with zero `pip install`.

The whole thing is deliberately small (about 180 lines) because it's a **scaffolding tool, not a live renderer**. It doesn't run at build time — `build_all.py` never calls it (grep it and you'll find no reference). You run it by hand when you add or roll over a year, review the Markdown it spits out, hand-polish it, and commit the result. That distinction matters, and we come back to it below, because the pages currently committed under `docs/en/community/gsoc/` are considerably richer than anything the generator emits today.

## The one-line mental model {#the-one-line-mental-model}

`gsoc-data.json` is the source of truth for the *skeleton* of each year page; the generator walks `data["years"]` and, for each year, dispatches on its `type` field to one of two functions that build the Markdown line by line. `type: "current"` gets the full treatment (project ideas + a four-phase application process + communications + FAQ + related docs); anything else gets the stripped-down "past" layout (completed projects with results + related docs).

## What the generator actually does, end to end {#what-the-generator-actually-does-end-to-end}

The entry point is `main()` at the bottom of `scripts/generate-gsoc-pages.py`. In order:

1. **It resolves paths relative to the script itself**, not your shell's working directory. `PROJECT_ROOT = Path(__file__).parent.parent` (the repo root, one level up from `scripts/`), and then it hardcodes `DATA_FILE = PROJECT_ROOT / "docs" / "community" / "gsoc" / "_data" / "gsoc-data.json"` and `OUTPUT_DIR = PROJECT_ROOT / "docs" / "community" / "gsoc"`. **Read those two paths carefully** — they no longer match the repo, and that's the first thing that will bite you. More on that in [The stale path gotcha](#the-stale-path-gotcha-read-this-before-you-run-it).

2. **It fails loudly if the data file is missing.** Before doing anything, `main()` checks `DATA_FILE.exists()`; if not, it prints `Error: Data file not found: <path>` plus `Please create the data file first.` and calls `sys.exit(1)`. So a missing or misplaced data file is a hard stop, not a silent no-op.

3. **It parses JSON, and only JSON.** `load_data()` does a plain `json.load()` on `DATA_FILE`. If the JSON is malformed, `main()` catches the `json.JSONDecodeError` and prints `Error: Invalid JSON in data file: <message>` before exiting `1`, so a stray trailing comma gives you a real diagnostic instead of a traceback. Note what it *doesn't* read: the sibling `gsoc-data.yaml`. That YAML file is a human-friendly mirror we keep for editing convenience (it's commented, it's diffable), but the generator never touches it — there's no `import yaml` anywhere in the script, precisely so the tool stays standard-library-only. If you edit the YAML and forget the JSON, nothing changes. **The JSON is the input; the YAML is a courtesy copy.**

4. **It generates newest-year-first.** `main()` iterates `sorted(data["years"].keys(), reverse=True)`, so `"2025"`, then `"2024"`, then `"2023"`. This is a string sort over the year keys, which happens to be correct for four-digit years; it only affects console ordering, not the output files themselves.

5. **For each year, `generate_page()` dispatches on `type`.** It pulls `year_data = data["years"][year]` and branches: `if year_data["type"] == "current"` it calls `generate_current_year_page()`, `else` it calls `generate_past_year_page()`. Note the `else` — the dispatch is "current versus *everything that isn't current*". So `"type": "past"` and a typo like `"type": "pastt"` both land on the past layout. There's no validation that catches a mistyped type; you just silently get a past page. It writes the result to `OUTPUT_DIR / f"{year}.md"` and prints `✓ Generated <path>`.

When it finishes it prints `✓ All GSoC pages generated successfully!` and a reminder to review and commit the files. Nothing is staged in git for you — that's on you.

## The two layouts, field by field {#the-two-layouts-field-by-field}

The genuine teaching value is knowing exactly which JSON key becomes which piece of Markdown, because that's what you're editing blind when you touch the data file.

### Current-year page — `generate_current_year_page()` {#current-year-page-generate_current_year_page}

Given a `type: "current"` year, the function emits, in this fixed order:

- **Frontmatter** built from three keys: `title`, `description`, and a hardcoded `icon: material/school`. (Watch that icon — see [Icon drift](#icon-drift) below; the committed pages don't use `material/school`.)
- **`# {title}`** as the H1, then a blank line, then the raw `intro` string verbatim. The `intro` is Markdown-passthrough, so links and emphasis inside it survive.
- **`## Project Ideas`** — always emitted, even if there are no ideas. The ideas themselves come from `year_data.get("project_ideas", [])`, so a missing key gives you an empty section rather than a crash. Each idea object becomes:
    ```
    ### {name}
    {description}

    **Skills**: {skills}
    **Size**: {size}
    **Level**: {level}
    ```
    A subtle rendering gotcha lives here: `**Skills**`, `**Size**`, and `**Level**` are emitted on three consecutive lines with **no blank line between them**, so Markdown collapses them into one soft-wrapped paragraph. That's why the source data keeps each of those values short — `"350 hours"`, `"Advanced"`, `"Vue.js, TypeScript, PHP"` — rather than trying to make them separate visual rows.
- **`## Application Process`** — built from `year_data.get("application_process", {})`. The function loops over the literal fixed list `["phase1", "phase2", "phase3", "phase4"]` and emits only the phases that are present, in that order. Two consequences worth internalizing: a `phase5` key would be **silently ignored** (the loop never looks for it), and the phases render in `phase1..phase4` order regardless of the order they appear in the JSON. Within each phase it emits `### {title}`, then — if the phase has a `steps` array — a numbered list (`enumerate(..., 1)`), and/or — if it has a `description` string — that description as a paragraph. Both can coexist; a phase with neither just contributes its title. This is why phases 1–3 in the live data use `steps` (concrete checklists) while `phase4` uses a single `description` (the interview blurb).
- **`## Communications`** — emitted only `if "communications" in year_data`, as a bullet list where each array entry is printed verbatim after `- `. The entries are already Markdown (`"**Discord**: [Join our Discord server](...)"`), so the bolding and links are yours to write in the data.
- **`## FAQ`** — emitted only `if "faq" in year_data`. Each item becomes `**{question}**` on one line and `{answer}` on the next — again with no blank line between, so question and answer render as one paragraph, question bold-leading.
- **`## Related Documentation`** — emitted only `if "related_docs" in year_data`, each entry as `- **{doc}**`. Because the whole `doc` string is wrapped in `**...**`, the *entire* entry (link text *and* the trailing " - description") comes out bold. That's a quirk of the current template, not a design choice worth defending.

### Past-year page — `generate_past_year_page()` {#past-year-page-generate_past_year_page}

Anything not `current` gets the lean layout: the same three-key frontmatter and `# {title}` / `intro` header, then **`## Projects`** built from `year_data.get("projects", [])`. Each project object is just:

```
### {name}
{description}

**Result**: {result}
```

Then the same optional **`## Related Documentation`** block. That's the whole past template — no skills, no phases, no FAQ. The mental split is: a *current* page is a recruiting funnel, a *past* page is a résumé.

## The data schema {#the-data-schema}

Everything hangs off a top-level `years` object keyed by four-digit year strings. Each year is one of two shapes.

A **current** year (see `2025` in the live data):

```json
"2025": {
  "type": "current",
  "title": "GSoC 2025",
  "description": "Google Summer of Code 2025 program at omegaUp",
  "intro": "omegaUp is participating in Google Summer of Code 2025! ...",
  "project_ideas": [
    {
      "name": "AI Teaching Assistant",
      "description": "Create a bot that can answer clarifications ...",
      "skills": "Python, PHP, MySQL, LLM Prompt Engineering, REST APIs",
      "size": "350 hours",          // free text; GSoC sizes are 90 / 175 / 350 hours
      "level": "Advanced"           // free text; e.g. "Medium", "High", "Medium to Advanced"
    }
  ],
  "application_process": {
    "phase1": { "title": "...", "steps": ["...", "..."] },   // steps -> numbered list
    "phase4": { "title": "...", "description": "..." }         // description -> paragraph
  },
  "communications": ["**Discord**: [...](...)"],   // verbatim Markdown bullets, optional
  "faq": [ { "question": "...", "answer": "..." } ], // optional
  "related_docs": ["[Getting Started](../getting-started/index.md) - Development setup"]
}
```

A **past** year (see `2023` / `2024`):

```json
"2024": {
  "type": "past",
  "title": "GSoC 2024",
  "description": "Google Summer of Code 2024 projects",
  "intro": "Projects completed during GSoC 2024.",
  "projects": [
    {
      "name": "Migrate Problem Creator to Vue.js + TypeScript",
      "description": "Migrated the Problem Creator ...",
      "result": "Problem Creator can now be used directly on omegaUp.com ..."
    }
  ],
  "related_docs": ["[GSoC 2025](../community/gsoc/2025.md) - Current year program"]
}
```

`type`, `title`, `description`, and `intro` are the only keys the generator dereferences directly (`year_data['title']`, etc.), so those four are effectively **required** — omit one and you get a `KeyError`. Everything else (`project_ideas`, `application_process`, `communications`, `faq`, `related_docs`, `projects`) is read through `.get(...)` or guarded by an `if ... in year_data`, so it's all optional and degrades to an empty (or absent) section.

One thing the schema does *not* encode: the relative links inside `related_docs`, `application_process` steps, and `communications` are written from the perspective of the year page's own directory (`../getting-started/...`, `../index.md`, and sibling `2025.md`). If you move where the pages are generated, those links move with them and can break — verify them with `scripts/verify_docs_nav.py` after regenerating.

## Adding a new year {#adding-a-new-year}

When a new campaign opens, you do two edits and roll one year over:

1. **Add the new current year** to `gsoc-data.json`. Give it `"type": "current"`, fill in `title`/`description`/`intro`, and populate `project_ideas`, `application_process` (phases `phase1`–`phase4`), `communications`, `faq`, and `related_docs`. Keep the `skills`/`size`/`level` values short (they glue together on render).
2. **Demote last year's page to past.** Flip the previous year's `"type"` from `"current"` to `"past"`, and swap its `project_ideas` for a `projects` array where each object carries `name` / `description` / `result` describing what actually shipped. The past template ignores `project_ideas` entirely, so leaving the old array in place just makes it dead data — delete it.
3. **Mirror the change into `gsoc-data.yaml`** so the human-editable copy doesn't rot. This is a manual courtesy — the generator won't do it and won't read it — but the next person to edit will reach for the YAML first.
4. **Regenerate**, then review the diff. See the path caveat immediately below before you run anything.
5. **Hand-polish and commit the `YYYY.md` files.** The generator output is a starting skeleton; the committed pages carry extra sections (statistics tables, achievement lists, benefit comparisons) that don't exist in the data file. Don't expect regeneration to reproduce them.

Because omegaUp maintains four locales (`docs/en`, `docs/es`, `docs/pt`, `docs/pt-BR`), each with its own `_data/gsoc-data.json`, "add a year" means repeating steps 1–5 per locale you maintain — the generator has no notion of locale, it just runs against whatever single JSON its `DATA_FILE` points at. `scripts/translate_docs.py` handles the bulk translation of prose, but the structured year data is edited per-locale by hand.

## The stale path gotcha — read this before you run it {#the-stale-path-gotcha-read-this-before-you-run-it}

Here's the sharp edge. The script's `DATA_FILE` is hardcoded to:

```
docs/community/gsoc/_data/gsoc-data.json
```

But the docs tree was reorganized into per-locale roots (`docs/en/…`, `docs/es/…`, `docs/pt/…`, `docs/pt-BR/…`), and `docs/community/` **no longer exists**. So running the script as committed, from anywhere, gives you:

```
$ python3 scripts/generate-gsoc-pages.py
Error: Data file not found: /…/ou-documentation/docs/community/gsoc/_data/gsoc-data.json
Please create the data file first.
```

That error is not "you forgot to create the file" — it's "the generator was written before the docs were split by language and its two path constants were never updated." The real files live at `docs/<lang>/community/gsoc/_data/gsoc-data.json`. To actually use the generator today you have to repoint both `DATA_FILE` and `OUTPUT_DIR` at a specific locale, e.g.:

```python
DATA_FILE  = PROJECT_ROOT / "docs" / "en" / "community" / "gsoc" / "_data" / "gsoc-data.json"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "en" / "community" / "gsoc"
```

and run it once per locale. A proper fix would take the locale as an argument and loop, but as of this writing the script is still single-path and locale-blind. Treat the committed constants as a bug to work around, not a layout to trust.

## Two more drifts to know about {#two-more-drifts-to-know-about}

### Icon drift {#icon-drift}

The generator hardcodes `icon: material/school` into the frontmatter of every page it emits. The pages actually committed under `docs/en/community/gsoc/` use `icon: bootstrap/school` — the whole docs site standardized on the `bootstrap/…` icon set (see any sibling under `docs/en/development/`, e.g. `icon: bootstrap/terminal`). So freshly generated pages come out with the wrong icon namespace and need a one-line fixup, or the generator's frontmatter string needs updating to `bootstrap/school`. Until someone does the latter, expect to hand-correct it every regeneration.

### The committed pages are richer than the generator {#the-committed-pages-are-richer-than-the-generator}

If you diff a committed page against what the generator would produce, they don't match — and that's expected. Take `docs/en/community/gsoc/2023.md`: the generator's past layout would give you two `### {name}` blocks with a one-line description and a `**Result**:` each. The committed page instead has a **COPPA Compliance** deep-dive, "Key Achievements" and "Technical Implementation" bullet lists, a Selenium-vs-Cypress benefit table, a "Project Ideas (2023)" section, and a Statistics table — none of which exist anywhere in `gsoc-data.json`. Likewise `2026.md` is committed and live even though the data file's newest year is still `2025`.

The takeaway: the generator is a **bootstrap tool for the initial skeleton of a year page**, not the authoritative renderer of the pages you see on the site. Regenerating will *overwrite* those hand-crafted sections with the bare template. So before you rerun it against a year that's already been hand-enriched, make sure you're prepared to re-apply (or git-restore) the richer content — or, better, only regenerate genuinely new years.

## File layout {#file-layout}

```
docs/<lang>/community/gsoc/
├── _data/
│   ├── gsoc-data.json   # the generator's input (JSON only)
│   └── gsoc-data.yaml   # human-editable mirror; NOT read by the generator
├── index.md             # public hub (cards + links) — hand-written, not generated
├── 2023.md              # generated skeleton, then hand-enriched
├── 2024.md
├── 2025.md
├── 2026.md
└── …
```

A standing rule for this folder: **never drop a `README.md` next to `index.md`.** Zensical treats `README.md` as the section index, so it would claim the `/community/gsoc/` URL and shadow the real `index.md` hub. If the landing page ever "disappears," a stray `README.md` is the first thing to check.

## Notes {#notes}

- The generator is pure standard library (`json`, `sys`, `pathlib`) — no dependencies, no virtualenv needed. That constraint is why it reads JSON and not the friendlier YAML mirror.
- It does not run during `build_all.py`; regeneration is always a deliberate, manual step you review before committing.
- Commit the generated (and hand-polished) `YYYY.md` files alongside the data change so the site and its source stay in sync.
</content>
</invoke>
