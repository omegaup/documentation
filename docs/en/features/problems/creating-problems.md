---
title: Creating Problems
description: Step-by-step guide to creating programming problems
icon: bootstrap/plus-circle
---

# Creating Problems

Thanks for wanting to add content to omegaUp. A problem is four things glued together: a **statement** the contestant reads, a set of **cases** (`.in`/`.out` pairs) that define what "correct" means, a set of **limits** that decide when a submission is killed, and a **validator** that decides how strictly output is compared. This page walks through all four and explains *why* each knob exists, so you can pick sensible values instead of copying defaults blindly.

There are two ways to author a problem, and you should reach for them in this order:

- **The Problem Creator (CDP)** at [omegaup.com/problem/creator](https://omegaup.com/problem/creator) is a visual editor that covers the common case intuitively. It has a few limitations — most notably it does **not** support Karel problems — so if it can't express what you need, drop down to the manual option below. There's a [video walkthrough](https://www.youtube.com/watch?v=cUUP9DqQ1Vg) if you'd rather watch first.
- **Hand-building the `.zip`** gives you full control and is the right call for Karel, interactive tasks, or custom validators. The raw archive layout lives in [Problem format (manual ZIP)](problem-format.md); this page explains the *content decisions* that go into that archive. Manual-mode video: [part 1](https://www.youtube.com/watch?v=LfyRSsgrvNc), [part 2](https://www.youtube.com/watch?v=i2aqXXOW5ic).

Either way, when you hit **Create**, the request lands on `\OmegaUp\Controllers\Problem::apiCreate` ([`frontend/server/src/Controllers/Problem.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L460)), which validates your metadata, builds a `ProblemSettings` object, and hands the whole bundle to `\OmegaUp\ProblemDeployer`. The deployer doesn't store your files in MySQL — it commits them as a **git repository** into the separate [omegaup-gitserver](https://github.com/omegaup/gitserver) service ([`ProblemDeployer.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/ProblemDeployer.php#L91)), which is why every edit you make becomes a new revision you can publish or roll back.

## The statement

The statement is Markdown, and it lives under `statements/` in the archive, one file per language: `es.markdown`, `en.markdown`, `pt.markdown` — those three (`en`, `es`, `pt`) are the only locales omegaUp recognizes (`\OmegaUp\Controllers\Problem::VALID_LANGUAGES`). Spanish is the historical default, so most legacy problems ship `es.markdown` and nothing else.

A few things that make statements read well, and the reasoning behind each:

- **Wrap every variable in math delimiters** — write `$n$`, `$x$`, `$x_i$` (subscripts use `_`) rather than a bare `n`. This isn't decoration: during a live contest a variable set apart from the prose is far easier to spot and impossible to confuse with an English word, which cuts down on clarifications.
- **LaTeX is fully supported**, so formulas, summations, and matrices render properly. Preview both the LaTeX *and* the sample input/output table before you publish at [omegaup.com/redaccion.php](https://omegaup.com/redaccion.php) — what you see there is what the contestant sees.
- **Images go inside `statements/`** next to the Markdown, and you reference them with plain Markdown image syntax, `![alt text](imagen.jpg)`. Supported formats are **jpg, gif, and png**. There's no rescaling in Markdown, so size the image before you add it — keep it under **650 pixels wide** or it'll overflow the statement column.

If you have an official write-up or editorial, drop it under `solutions/` using the same per-locale naming (`es.markdown`, `en.markdown`, `pt.markdown`). The repo ships worked examples under [`frontend/tests/resources`](https://github.com/omegaup/omegaup/tree/main/frontend/tests/resources) — [`testproblem.zip`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/resources/testproblem.zip) in particular includes a solution.

## Cases

Every case is a pair of files under `cases/`: an input `.in` and its expected output `.out`. The **base names must match** and be paired correctly — `1.in`/`1.out`, `hola.in`/`hola.out` — but the specific name is otherwise irrelevant. omegaUp runs on Linux, so casing is load-bearing: a folder named `Cases` or a file ending in `.In` **will not be found**. There's no hard cap on the number of cases, but keep the total case payload under **~100 MB**: every extra case is more work per submission, and in a live contest a slow solution that `TLE`s on a hundred cases can back up the grading queue and sour everyone's experience.

### Grouped cases

By default each case scores independently. If instead you want **all-or-nothing** scoring — the contestant only earns the group's points when *every* case in it passes — use **grouped cases**. You group by putting a `.` (dot) in the file name to separate the group name from the case name; the group name is everything before the first dot. So `grupo1.caso1.in`, `grupo1.caso1.out`, `grupo1.caso2.in`, `grupo1.caso2.out` is a **single group with two cases**. There's no limit on the number of groups, and groups can hold different numbers of cases.

This is the right tool when the space of plausible answers is tiny — say, a yes/no problem — where a contestant could otherwise farm partial credit by guessing on individual cases. Note the flip side: **the dot is reserved for grouping**, so don't put stray dots in a case name unless you actually mean to group it.

### Weights (`testplan`)

By default every case is worth `1 / number-of-cases`, so the scores sum to 100%. To weight cases differently, add a file literally named **`testplan`** (no extension) at the root of the zip, one line per case, each line being the case base name (no extension) followed by its points:

```
caso1 5
grupo2.caso1 10
grupo2.caso2 0
```

Make sure no file has spaces in its name. To assign points to a *group* as a whole rather than splitting them across its cases, the convention is to put the group's full point value on its **first** case and `0` on every other case in the group.

## Limits

Limits are what the grader enforces per case. Every problem starts from a defaults block in `\OmegaUp\Controllers\Problem::getDefaultProblemSettings` ([`Problem.php#L4549`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L4549)):

| Setting | Default | What it does |
|---|---|---|
| **Time limit** (`TimeLimit`) | `1s` (1000 ms) | Max **CPU** time the contestant's process may run *per case* before the OS kills it with `TLE`. |
| **Memory limit** (`MemoryLimit`) | `64MiB` | Max RAM (heap + stack) in [kibibytes](https://en.wikipedia.org/wiki/Kibibyte); exceeding it is `MLE`. |
| **Overall wall-time limit** (`OverallWallTimeLimit`) | `30s` | Max **real** time the grader waits for the *whole* problem (all cases) to finish, else `TLE`. |
| **Extra wall time** (`ExtraWallTime`) | `0s` | Extra real-time grace, used mainly for `libinteractive` problems where the evaluator process also needs to finish. |
| **Output limit** (`OutputLimit`) | `10240KiB` | Max bytes the process may write to stdout/stderr before it's killed with `OLE`. |
| **Input limit** (`inputLimit`) | `10240` bytes | Max size of the contestant's *source code* — a lever to stop precomputed/hard-coded solutions. |

Two subtleties worth internalizing. First, **time limit is CPU time, but overall wall-time limit is real time** — they measure different clocks on purpose. A submission can blow the overall wall limit even if no single case exceeds its CPU limit. When that happens, any case that didn't get to run isn't scored, and to keep results reproducible the grader evaluates cases in **lexicographic order** — so which cases "make it" under a tight overall limit is deterministic, not a coin flip.

Second, the **output limit is normally auto-detected**: omegaUp takes the size of the largest `.out` file and adds **10 KiB** of headroom. You only need to set it by hand when you use a custom validator, because then omegaUp can't infer the expected output size — so for custom-validator problems, provide `OutputLimit` explicitly.

## Validators

The validator decides *how* the contestant's output is compared against your `.out`. omegaUp ships five types; the string constants live in [`\OmegaUp\ProblemParams`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/ProblemParams.php#L28):

- **`token`** — reads all *tokens* (runs of up to **4,194,304** contiguous printable characters separated by whitespace) from both files and requires the two token sequences to be **identical**. This is the everyday default and what `getDefaultProblemSettings` starts you on. It ignores how much whitespace separates tokens, which is what you almost always want.
- **`token-caseless`** — same as `token`, but lowercases every token first, so `Yes` and `yes` match. Use it when the answer is a word and you don't want casing to matter.
- **`token-numeric`** — reads numeric tokens, interprets them as numbers, and requires the two sequences to have the same length *and* each corresponding number to match within an **absolute OR relative error of 1e-9** (that's the `Tolerance`, [`Problem.php#L4562`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L4562)). This is the one for floating-point answers, where an exact string match would wrongly reject `0.5000000001`.
- **`literal`** — exact byte-for-byte match, no tokenization. Reach for it only when whitespace itself is part of the answer.
- **`custom`** — you ship a validator program. See below.

### Custom validators (`validator.<lang>`)

When "compare these tokens" isn't expressive enough — for example when a problem has **many correct answers** — you write a validator. Put a single file named `validator.<lang>` at the **root** of the zip, where `<lang>` is one of `c`, `cpp`, `java`, `p` (Pascal), or `py`. You only need one validator regardless of what language the contestant submits in.

Here's the mental model for what the grader hands your validator:

- The contestant's output arrives on the validator's **standard input** — read it normally with `scanf`/`cin`/`input()`. It behaves as if the grader ran `./contestant < data.in | ./validator casename`, where `casename` is the current case's `.in` name without the extension.
- You can `open("data.in")` to read the *original case input*, and `open("data.out")` to read the *expected output* for that case, if you need either to judge.
- Your validator **must print one floating-point number in `[0, 1]`** to stdout — the fraction of the case the contestant earned. **Print nothing and you get `JE`.** A value below `0` is clamped to `0`; above `1` is clamped to `1`. Anything you write to *stderr* is ignored by scoring but handy for debugging.

Two gotchas that bite people: the validator **runs inside the same sandbox** as contestant code, so if *it* crashes or misbehaves (`WA`, `RFE`, `RTE`, …) the whole submission is judged `JE`, not the contestant's fault — test your validator hard. And even though your `.out` files are never compared when you use a custom validator, **you must still ship an `.out` for every case** (they can be empty files) so the pairing is complete.

A validator for a "print the sum of `a` and `b`" problem, accepting either the literal sum or the recomputed value, in C++17:

```cpp
#include <iostream>
#include <fstream>

int main() {
  // Read "data.in" to recover the original case input.
  int64_t a, b;
  {
    std::ifstream original_input("data.in", std::ifstream::in);
    original_input >> a >> b;
  }
  // "data.out" holds the expected output for this case.
  int64_t expected;
  {
    std::ifstream original_output("data.out", std::ifstream::in);
    original_output >> expected;
  }

  // Standard input carries the contestant's output.
  int64_t contestant;
  if (!(std::cin >> contestant)) {
    // stderr is ignored by scoring but useful while debugging.
    std::cerr << "Could not read contestant output\n";
    std::cout << 0.0 << '\n';
    return 0;
  }

  if (expected != contestant && contestant != a + b) {
    std::cerr << "Wrong answer\n";
    std::cout << 0.0 << '\n';
    return 0;
  }

  std::cout << 1.0 << '\n';  // full credit for this case
  return 0;
}
```

Custom-validator problems also get their **own** limits block, separate from the contestant's, because your judging program has different resource needs. When the validator type is `custom` and you don't override them, omegaUp fills in `TimeLimit` `30s`, `MemoryLimit` `256MiB`, `OverallWallTimeLimit` `5s`, `OutputLimit` `10KiB`, `ExtraWallTime` `0s` ([`Problem.php#L4605`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L4605)). The separate **validator time limit** (`validatorTimeLimit`) is the real-time budget the grader gives your validator to emit a verdict per case before giving up with `JE`.

### "Standard output as score"

There's a sixth mode worth knowing: interpreting the contestant's stdout directly as the score. The grader reads stdout, parses it as a float, clamps it to `[0.0, 1.0]`, and uses that as the final score. This is used almost exclusively with **interactive** problems, where letting the *interactor* (rather than the contestant) declare the score prevents the contestant from simply printing `1.0` to cheat.

## Languages and submission modes

"Languages" controls not just which programming languages are allowed but the whole *mode* of submission:

- **Normal languages** — C, C++ (multiple standards), Java, Kotlin, Python 2/3, Ruby, C#, Pascal, and more. The contestant submits source, omegaUp compiles and runs it.
- **Karel** — the block/robot language, submitted as Karel-Java (`kj`) or Karel-Pascal (`kp`). Karel problems can only be built via the manual ZIP path; the CDP doesn't support them.
- **Output-only** (`cat`) — the contestant uploads a `.zip` of answers for all cases instead of code. If you want to also allow submitting a single case's answer as plain text (no zip), there must be exactly one case named `Main.in`/`Main.out`.
- **No submissions** — disables submitting entirely. This exists only so a "problem" can display content inside a course without being solvable.

## Publishing knobs

A handful of metadata fields shape how the problem is discovered and administered:

- **Appears in the public listing** (visibility) — whether the problem can show up publicly and be reused in third-party contests and courses. New problems default to **private** (`VISIBILITY_PRIVATE`), so nothing you're still drafting leaks.
- **Email clarifications** — whether omegaUp emails you the clarifications contestants ask about this problem, so you can answer without camping on the site.
- **Source** — attribution for where the problem came from (e.g. `OMI 2020`).
- **Tags** — classification labels; you can also choose whether users are allowed to add tags of their own.

## Common mistakes

The two failures that trip up nearly every first-time manual author:

- **`cases/` and `statements/` must sit at the *root* of the zip**, with no wrapping folder — this is a long-standing packaging gotcha ([issue #310](https://github.com/omegaup/omegaup/issues/310)). From the problem directory on Linux/macOS, `zip -r myproblem.zip *` produces a correctly-rooted archive; zipping the *containing folder* does not.
- **It must be a `.zip`** — not `.rar`, `.tar.bz2`, `.7z`, or `.zx`. The archive's own name doesn't matter.

## Related documentation

- **[Problem format (manual ZIP)](problem-format.md)** — the exact archive layout, file-by-file
- **[Verdicts](../verdicts.md)** — what `AC`, `PA`, `WA`, `TLE`, `MLE`, `OLE`, `RTE`, `JE`, and the rest actually mean
- **[Problems API](../../reference/api.md)** — the endpoints behind `apiCreate` and friends
- **[Long-form manual (GitHub)](https://github.com/omegaup/omegaup/blob/main/frontend/www/docs/Manual-for-Zip-File-Creation-for-Problems.md)** — supplementary detail in the main repo
