---
title: Problem Format
description: ZIP file structure for manual problem creation
icon: bootstrap/file-document
---

# Problem format (manual ZIP)

For most authors, the [Problem Creator](https://omegaup.com/problem/creator) (CDP) or the in-site editor is enough. This page is for **manual** `.zip` packaging when you need full control (for example **Karel**, **interactive** tasks, or custom validators).

!!! tip "Video walkthroughs"
    Manual ZIP workflow: [part 1](https://www.youtube.com/watch?v=LfyRSsgrvNc), [part 2](https://www.youtube.com/watch?v=i2aqXXOW5ic). CDP tutorial: [YouTube](https://www.youtube.com/watch?v=cUUP9DqQ1Vg).

## ZIP layout (overview)

Use a **`.zip`** archive (not RAR/7z). The archive name is arbitrary.

```
problem.zip
├── cases/                 # Required: test inputs/outputs
├── statements/            # Required: at least statement markdown
├── solutions/             # Optional: editorial / official solution writeups
├── interactive/           # Optional: libinteractive bundle
├── validator.cpp          # Optional: custom validator (see naming below)
├── settings.json          # Optional: packaged settings (when used)
├── limits.json            # Optional: limits override
└── testplan               # Optional: per-case weights
```

Reference bundle in the repo: [`frontend/tests/resources/testproblem.zip`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/resources/testproblem.zip).

## Configurable settings (mental model)

Whether you set these in the UI or in packaged metadata, the problem has:

| Area | Meaning |
|------|---------|
| **Validator type** | How output is compared: token, token-caseless, numeric tolerance, “stdout as score” (interactive), or **custom** `validator.<lang>` |
| **Languages** | Allowed submission modes: normal languages, **Karel**, **output-only** (`.zip` of answers; single case may be `Main.in`/`Main.out` for plain text), **no submissions** (content-only) |
| **Time / memory / output limits** | Per-case CPU time, total wall time, validator time, memory (KiB), stdout/stderr size caps |
| **Input limit** | Max source size to discourage hard-coded solutions |
| **Public / tags / source** | Listing visibility and attribution |

## `cases/`

- Pairs of **`.in`** and **`.out`** files. Base names must match (`1.in` / `1.out`, `sample.in` / `sample.out`).
- **Grouped cases**: use a **dot** in the basename to separate group and case, e.g. `group1.case1.in` — contestant must solve the whole group for partial credit rules that depend on grouping.
- Avoid extra dots in names unless you intend grouping.
- Keep total case payload reasonable (very large zips slow grading in live contests).

## `statements/`

- Markdown files per locale, e.g. `es.markdown`, `en.markdown`, `pt.markdown`.
- You can preview Markdown/LaTeX on [omegaup.com/redaccion.php](https://omegaup.com/redaccion.php).
- Use `$n$`, `$x_i$`, etc. for math-style variables in the statement.

## `solutions/`

Optional official writeups, same locale naming as statements (`es.markdown`, …). See examples under [`frontend/tests/resources`](https://github.com/omegaup/omegaup/tree/main/frontend/tests/resources).

## `interactive/` and libinteractive

Interactive problems should be built with [libinteractive](https://omegaup.com/libinteractive/). Reference pack: [Cave (IOI 2013) sample](https://omegaup.com/resources/cave.zip).

## Custom validator (`validator.<lang>`)

Place **one** of `validator.c`, `validator.cpp`, `validator.java`, `validator.p`, or `validator.py` at the **root** of the zip.

Behavior (simplified):

- The grader runs equivalently to piping contestant stdout: `./contestant < data.in | ./validator casebasename`.
- The validator may read `data.in` (case input) and `data.out` (expected output).
- It **must** print a float in **[0, 1]** to stdout = score for the case. Empty output → **JE**; values are clamped to \[0,1\].

See the full manual on the wiki mirror in-repo: [`Manual-for-Zip-File-Creation-for-Problems.md`](https://github.com/omegaup/omegaup/blob/main/frontend/www/docs/Manual-for-Zip-File-Creation-for-Problems.md) for long examples (e.g. C++ validator sketch).

## `testplan` and weights

If present, defines normalized weights per case group; otherwise cases are weighted evenly. Sum of weights must be consistent with grader expectations (see wiki / examples in `testproblem.zip`).

## Related documentation

- **[Creating problems](creating-problems.md)** — authoring workflow and UI paths
- **[Verdicts](../verdicts.md)** — what outcomes mean
