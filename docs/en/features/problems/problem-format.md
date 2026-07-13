---
title: Problem Format
description: ZIP file structure for manual problem creation
icon: bootstrap/file-document
---

# Problem format (manual ZIP) {#problem-format-manual-zip}

This page is for the experienced problemsetter who needs to hand-build a problem
`.zip` — or edit one omegaUp already deployed — because they need something the
point-and-click tools do not expose: **Karel** problems, **interactive** tasks,
a **custom validator**, or precise control over grouping and weights. If you are
just getting started, or your problem is a plain "read input, print output" task,
use the [Problem Creator (CDP)](https://omegaup.com/problem/creator) instead and
save yourself the packaging — there is a [CDP walkthrough on YouTube](https://www.youtube.com/watch?v=cUUP9DqQ1Vg).

!!! tip "Video walkthroughs"
    If you do go the manual route, it helps to watch someone do it first:
    [part 1](https://www.youtube.com/watch?v=LfyRSsgrvNc) and
    [part 2](https://www.youtube.com/watch?v=i2aqXXOW5ic) of the manual
    problem-creation tutorial.

The single most important thing to internalize before you build anything: the
`.zip` you upload is **not** what omegaUp stores. When you upload, omegaUp's
gitserver (the Go service in [`omegaup/gitserver`](https://github.com/omegaup/gitserver)
that keeps every problem as its own git repository) unpacks the archive, reads
your `cases/`, your optional `testplan`, and any `settings.json` you included,
and **compiles all of it down into one canonical `settings.json`** that the
grader actually consumes. `testplan` and any partial `settings.json` you shipped
are deleted after they are folded in, precisely because they are now redundant
with the generated file (see
[`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L463-L492)).
So think of the `.zip` as *source* and `settings.json` as the *compiled artifact* —
which is exactly why the directory names and file extensions below have to be
letter-perfect.

## The configurable settings (mental model) {#the-configurable-settings-mental-model}

Whether you set these through the web UI or ship them in packaged metadata, every
problem carries the same handful of knobs. Understanding what each one *means* —
and what verdict you get when it is exceeded — is what lets you package correctly.

### Validator: how the contestant's output is judged {#validator-how-the-contestants-output-is-judged}

The validator decides whether an output is right, and gives a per-case score in
`[0.0, 1.0]`. omegaUp ships five, whose canonical names live in
[`ProblemParams.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/ProblemParams.php#L28-L40)
(PHP side) and
[`common/problemsettings.go`](https://github.com/omegaup/quark/blob/main/common/problemsettings.go#L30-L48)
(grader side):

- **`token`** — token-by-token. It reads every token (a run of up to
  **4,194,304** contiguous printable characters — 4 MiB, the `MaxTokenLength` in
  the runner's [`tokenizer.go`](https://github.com/omegaup/quark/blob/main/runner/tokenizer.go#L13) —
  separated by whitespace) from both the expected `.out` and the contestant's
  output, and requires the two token sequences to be **identical**. This is the
  default and what you want for almost everything.
- **`token-caseless`** — same as `token`, but it lowercases every token first, so
  `Yes` and `yes` match. Reach for this when capitalization is not part of the
  answer.
- **`token-numeric`** — reads numeric tokens only, interprets them as numbers,
  and accepts them when the contestant's value is within an **absolute *or*
  relative error of 1e-9** of the expected value (the default `Tolerance`, also
  `1e-9`, set in
  [`Problem.php`'s default settings](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L4560)).
  The two sequences must still have the same length. Use it for floating-point
  answers where the last digits are allowed to wobble.
- **`literal`** (shown in the UI as "interpret standard output as score") — reads
  the contestant's stdout, parses it as a single float, and **clamps it to
  `[0.0, 1.0]` to use directly as the case score**. It is almost exclusively for
  **interactive** problems: the interactor process, not the contestant, prints the
  score, which stops the contestant from simply printing `1.0` to cheat.
- **`custom`** (`validator.<lang>`) — you ship a program that reads the
  contestant's stdout (and, if it wants, the case's input and expected output) and
  prints the score itself. Full details and worked examples are in
  [Custom validator](#custom-validator-validatorlang) below.

### Languages: what the contestant may submit {#languages-what-the-contestant-may-submit}

- **C, C++, Java, Python, …** — the contestant submits source in one of omegaUp's
  supported languages.
- **Karel** — the contestant submits a Karel program. See the
  [Karel problems](#karel-problems) section for how to build the cases.
- **Output only** — the contestant uploads a `.zip` of answers for every case
  instead of a program. If you want to *also* let them paste a single case's
  answer as plain text rather than a zip, the problem must have exactly **one**
  case named `Main.in`/`Main.out`.
- **No submissions** — the contestant cannot submit at all. This exists purely to
  display content (a reading, a lesson) inside a course.

### Time, memory, and output limits {#time-memory-and-output-limits}

Each of these maps to a specific verdict when the contestant's program crosses it,
and each has a real default. The problem-creation form currently pre-fills these
values (see
[`Problem.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L5952-L5961)),
and the grader's own `DefaultLimits`
([`common/problemsettings.go`](https://github.com/omegaup/quark/blob/main/common/problemsettings.go#L193))
agree with them, so a package that omits limits still runs sensibly:

- **Time limit — `TimeLimit` (ms), default `1000`** — the maximum **CPU** time the
  OS lets the contestant's process run *for each case* before it is killed with
  **`TLE`**. This is CPU time, not wall-clock, so time spent asleep or blocked
  does not count against it.
- **Total (overall wall) time limit — `OverallWallTimeLimit` (ms), default
  `60000`** — the maximum **real** time the grader waits for the *whole* problem
  to finish before stopping it with **`TLE`**. Any case that did not get to run
  before this deadline is simply **not evaluated**. To keep results at least
  somewhat consistent when this fires, cases are evaluated in **lexicographic
  order**, so which cases get skipped is deterministic rather than random.
- **Memory limit — `MemoryLimit` (KiB), default `32768`** (i.e. 32 MiB) — the
  maximum RAM (heap + stack) the OS lets the program use before killing it with
  **`MLE`**. It is expressed in
  [kibibytes](https://en.wikipedia.org/wiki/Kibibyte), so `32768` KiB = 32 MiB.
- **Output limit — `OutputLimit` (bytes), default `10240`** — the most the program
  may write to stdout *or* stderr before it is killed with **`OLE`**. For ordinary
  token problems omegaUp normally **auto-detects** this from your `.out` files —
  it takes the largest one and adds 10 KiB of headroom — so you rarely set it by
  hand. **But if you use a custom validator you must set it explicitly**, because
  there is no plain `.out` to size against.
- **Input limit — `inputLimit` (bytes), default `10240`** — the maximum length of
  the contestant's **source code**. Turn this down when you want to stop people
  from pasting in a precomputed answer table instead of actually solving the
  problem.
- **Validator time limit — `validatorTimeLimit` (ms), default `1000`** — how long
  the grader waits for a *custom validator* to emit a verdict for each case before
  giving up with **`JE`**.
- **Extra wall time for libinteractive — `ExtraWallTime` (ms), default `0`** — how
  long the grader waits for the *interactor* program to finish each case (beyond
  the normal limits) before stopping it with **`TLE`**. Only relevant to
  interactive problems.

!!! note "Custom validators get their own, more generous limits"
    The moment you switch the validator to `custom`, omegaUp seeds a separate set
    of limits for the *validator* process — currently **256 MiB** memory, a **30 s**
    CPU time limit, **5 s** overall wall time, and **10 KiB** output
    ([`Problem.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L4606-L4611)).
    The idea is that judging can afford to be slower and hungrier than the
    contestant's solution.

### Everything else {#everything-else}

- **Source** — attribution/origin for the statement, shown to contestants.
- **Appears in the public listing** — whether the problem can be shown publicly and
  used in *other people's* contests and courses.
- **Send clarifications by email** — whether omegaUp emails you (the author) when a
  user asks a clarification about this problem.
- **Tags** — classification labels.

## The ZIP layout {#the-zip-layout}

Save everything into a **`.zip`** archive — not `.rar`, `.tar.bz2`, `.7z`, or
`.zx`. The name of the zip itself does not matter. A minimal language problem
looks like this:

```
problem.zip
├── cases/                 # Required: the .in/.out test data
│   ├── 1.in
│   ├── 1.out
│   └── …
├── statements/            # Required: at least one <locale>.markdown
│   └── es.markdown
├── solutions/             # Optional: editorial / official write-up
├── interactive/           # Optional: libinteractive bundle
├── validator.cpp          # Optional: custom validator (one of validator.<lang>)
├── settings.json          # Optional: pre-baked settings (usually generated for you)
└── testplan               # Optional: per-case weights
```

A real, working reference bundle lives in the repo at
[`frontend/tests/resources/testproblem.zip`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/resources/testproblem.zip),
and there are many more under
[`frontend/tests/resources`](https://github.com/omegaup/omegaup/tree/main/frontend/tests/resources).

!!! warning "`cases/` and `statements/` must sit at the very root"
    It is *critically* important that `cases/` and `statements/` are directly at
    the root of the `.zip`, with **no** intermediate folder wrapping them — this
    has bitten enough people to earn its own bug,
    [omegaup#310](https://github.com/omegaup/omegaup/issues/310). On Linux/Mac the
    reliable way to get this right is to `cd` into the problem directory and run
    `zip -r myproblem.zip *`, which zips the *contents* rather than the containing
    folder. And because omegaUp runs on **Linux, names are case-sensitive**: a
    folder called `Cases` will not be found, and neither will an input file ending
    in `.In` instead of `.in`.

### `cases/` {#cases}

This folder holds every test case as paired `.in`/`.out` files. The **base names
must match** — `1.in` with `1.out`, `hola.in` with `hola.out` — but the base name
itself is arbitrary. Internally the deployer only accepts files matching the
regexp `^cases/([^/]+)\.in$`
([`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L130)),
and if the folder is missing or empty the upload fails outright with
`cases/ directory missing or empty`
([`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L1095)).
Every `.in` that expects submissions must have a matching `.out`, or the deploy
errors with `failed to find the output file for cases/<name>`.

**The `.` (dot) in a case name is reserved for grouping.** Do not put a dot in a
case name unless you mean to group — the text *before the first dot* becomes the
**group name** (`strings.SplitN(caseName, ".", 2)[0]` in
[`common/problemsettings.go`](https://github.com/omegaup/quark/blob/main/common/problemsettings.go#L336-L342)).
So `grupo1.caso1.in`, `grupo1.caso1.out`, `grupo1.caso2.in`, `grupo1.caso2.out`
form **one group** (`grupo1`) with **two cases**.

**Grouped cases** exist because sometimes the set of plausible answers is tiny and
you do not want a contestant scoring partial credit on a lucky guess: to earn a
group's points you must solve **every case in that group**. There is no limit on
the number of groups, and groups may have different numbers of cases.

There is no hard limit on the number of cases either, but **keep the total case
payload under ~100 MB**. More cases means every submission takes longer to grade,
and in a live contest that translates directly into queue wait times — especially
painful when a slow, `TLE`-bound solution is sitting ahead of everyone else in the
queue.

### `statements/` {#statements}

This holds the problem statement in Markdown (the same flavor Wikipedia uses), one
file per locale: `es.markdown`, `en.markdown`, `pt.markdown`. At least one is
required. You can preview exactly how your Markdown and LaTeX will render at
[omegaup.com/redaccion.php](https://omegaup.com/redaccion.php) — please actually do
this and confirm the input/output tables look right, because a garbled statement
is a miserable experience mid-contest.

LaTeX is fully supported. Wrap variable names in `$…$` — write `$n$`, `$x$`,
`$x_i$` for a subscript — so they stand out from prose and contestants can find
them at a glance. It reads better and it avoids ambiguity.

### `solutions/` {#solutions}

Structurally identical to `statements/`: the official solution write-up in
Markdown, named per locale (`es.markdown`, and translations `en.markdown`,
`pt.markdown`). The bundle at
[`testproblem.zip`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/resources/testproblem.zip)
includes a solutions example.

### `interactive/` (optional) {#interactive-optional}

Interactive problems — where the contestant's program talks back and forth with a
judge process rather than reading a fixed input — must be built with
[libinteractive](https://omegaup.com/libinteractive/); that page documents the
`.idl` interface format and how the shims are generated. For a complete, real
reference of how an interactive problem's zip is structured, use
[Cave from IOI 2013](https://omegaup.com/resources/cave.zip) as a template.

One convenience the deployer handles for you: libinteractive sample cases under
`interactive/examples/` **do not need an `.out`** — gitserver generates an empty
one automatically
([`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L495-L514)).

### Custom validator (`validator.<lang>`) {#custom-validator-validatorlang}

When token comparison is not enough — multiple correct answers, special-judge
scoring, partial credit — ship exactly **one** file named `validator.<lang>` at
the **root** of the zip, where `<lang>` is one of `c`, `cpp`, `java`, `p` (Pascal),
or `py`. You only need one validator, and it is **independent of the contestant's
language**.

Here is the exact contract, and it pays to get it right:

- Your validator reads the **contestant's output on its own stdin** — plain `scanf`
  / `cin` / `input()`. Mentally, the grader runs the equivalent of
  `./contestant < data.in | ./validator <casename>`, where `<casename>` is the
  current case's `.in` name **without the extension**.
- It may open a file literally named **`data.in`** — the same input that was fed to
  the contestant — and a file named **`data.out`** — the expected output paired
  with that `data.in`. Read either, both, or neither.
- It **must print a single float in `[0.0, 1.0]` to stdout** — the fraction of the
  case the contestant got right. **Print nothing → `JE`.** Print less than 0 → the
  score is clamped to 0; print more than 1 → clamped to 1.
- The validator runs **inside the same sandbox** as contestant programs. If *the
  validator itself* misbehaves (`WA`, `RFE`, `RTE`, …), the submission is judged
  **`JE`** — so a buggy validator fails loudly rather than silently mis-scoring.
- **You must still ship `.out` files even though they will not be used** for
  comparison. Empty files are fine; they just have to exist so the case pairing
  succeeds.

A validator for [sumas](https://omegaup.com/arena/problem/sumas) (read two
integers, print their sum) in C++17 — note how it reads the original `a` and `b`
from `data.in`, the expected sum from `data.out`, the contestant's answer from
stdin, and prints `1.0` or `0.0`:

```c++
#include <iostream>
#include <fstream>

int main() {
  // read "data.in" to get the original input.
  int64_t a, b;
  {
    std::ifstream original_input("data.in", std::ifstream::in);
    original_input >> a >> b;
  }
  // you can store anything that helps you evaluate in "data.out".
  int64_t sum;
  {
    std::ifstream original_output("data.out", std::ifstream::in);
    original_output >> sum;
  }

  // read standard input to get the contestant's output.
  int64_t contestant_sum;
  if (!(std::cin >> contestant_sum)) {
    // anything you print to cerr is ignored, but it's useful for debugging.
    std::cerr << "Error reading the contestant's output\n";
    std::cout << 0.0 << '\n';
    return 0;
  }

  // determine whether the answer is incorrect.
  if (sum != contestant_sum && sum != a + b) {
    std::cerr << "Incorrect output\n";
    std::cout << 0.0 << '\n';
    return 0;
  }

  // If execution reaches here, the contestant's output is correct.
  std::cout << 1.0 << '\n';
  return 0;
}
```

The same validator in Python 3:

```python
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import sys

def _main():
  # read "data.in" to get the original input.
  with open('data.in', 'r') as f:
    a, b = [int(x) for x in f.read().strip().split()]
  # you can store anything that helps you evaluate in "data.out".
  with open('data.out', 'r') as f:
    expected_sum = int(f.read().strip())

  score = 0
  try:
    # Read the contestant's output.
    contestant_sum = int(input().strip())

    # Determine whether the output is incorrect.
    if contestant_sum not in (expected_sum, a + b):
      # Anything printed to sys.stderr is ignored, but useful for debugging.
      print('Incorrect output', file=sys.stderr)
      return

    # If execution reaches here, the contestant's output is correct.
    score = 1
  except:
    logging.exception("Error reading the contestant's output")
  finally:
    print(score)

if __name__ == '__main__':
  _main()
```

### `testplan` (optional) {#testplan-optional}

By default **every case is worth `1/number-of-cases`** — the deployer assigns each
case a weight of `1/1` and the grader normalizes all weights so they sum to 1
(`AddCaseName(caseName, big.NewRat(1, 1), false)` in
[`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L453-L461),
weights divided by the total in
[`common/literalinput.go`](https://github.com/omegaup/quark/blob/main/common/literalinput.go#L317-L333)).
When you want cases weighted unequally, drop a file named **`testplan`** (no
extension) at the root of the zip, one line per case: the case's file name
**without the extension**, whitespace, then the number of points. For a problem
with cases `cases/caso1.in`, `cases/grupo2.caso1.in`, `cases/grupo2.caso2.in`:

```
caso1 5
grupo2.caso1 10
grupo2.caso2 0
```

A few things the parser
([`NewCaseWeightMappingFromTestplan`](https://github.com/omegaup/quark/blob/main/common/problemsettings.go#L305-L334))
actually enforces, matching each line against
`^\s*([^#[:space:]]+)\s+([0-9.]+)\s*$`:

- **No spaces in case file names** — the case name token cannot contain
  whitespace.
- **`#` starts a comment** — a line whose first non-space character is `#` (and any
  line that does not match the pattern) is skipped, so you can annotate your
  testplan.
- The `testplan` and the `.zip` must **agree on the set of cases**. gitserver runs
  a *symmetric difference* both ways
  ([`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L463-L488)):
  a case in the testplan but missing from `cases/` fails with
  `testplan missing case "<name>"`, and a case in `cases/` but absent from the
  testplan fails with `.zip missing case "<name>"`. You cannot half-specify.

**To score a whole group** without splitting the points across its cases, the
convention is to put the group's full score on the **first** case and **0** on all
the others — as `grupo2.caso1 10` / `grupo2.caso2 0` does above.

This interacts with the group's **score policy**, one of two values in
[`ProblemParams.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/ProblemParams.php#L48-L49):
`sum-if-not-zero` (the default — a group scores the **sum** of its cases' scores,
but only if they are *all* non-zero) or `min` (the group scores the **minimum** of
its cases' scores times the group weight). The default is why the
"points-on-the-first-case, zero-on-the-rest" convention works: solve the whole
group and you collect the full weight; miss any case and the group collapses to
zero.

### `settings.json` (usually generated, occasionally hand-written) {#settingsjson-usually-generated-occasionally-hand-written}

You will most often *never* write this file — it is the compiled artifact gitserver
produces from your `cases/`, `testplan`, and limits, marshaled out in
[`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L580-L597).
Its shape is the `ProblemSettings` struct
([`common/problemsettings.go`](https://github.com/omegaup/quark/blob/main/common/problemsettings.go#L174-L182)):
a `Limits` block, a `Validator` block (`Name`, `Tolerance`, optional
`GroupScorePolicy`, optional custom-validator `Limits`), a `Cases` array of groups
each with their weighted cases, and — for interactive problems — an `Interactive`
block. If you *do* ship your own `settings.json`, gitserver reads it, then still
lets a `testplan` override the case weights on top of it. Either way, only the
generated `settings.json` survives into the deployed problem repository.

## Images {#images}

omegaUp has native image support :). To embed an image in a statement, add the
image file to your zip **inside `statements/`** and reference it from your
`es.markdown` with ordinary Markdown:

```markdown
![Alt text](image.jpg)
```

Supported formats are **jpg, gif, png**. Mind the size — Markdown will **not**
rescale it — so keep images at or under **650 pixels wide**.

## Example zips {#example-zips}

The zips omegaUp uses in its own tests are the best templates to copy from:
[`frontend/tests/resources`](https://github.com/omegaup/omegaup/tree/main/frontend/tests/resources).

## Karel problems {#karel-problems}

First, just try [karel.js](https://omegaup.com/karel.js/) — it converts cases for
you and is far less trouble than what follows.

If you already have your cases and would rather not re-make them in karel.js, the
steps below are for **Windows** and assume you have **Python 2.7** installed and on
your `PATH` (the default install path is typically `C:\Python27`); verify you can
run `python` from the DOS console before starting.

1. Have these files on hand:
   [the Karel toolkit](https://docs.google.com/file/d/0B6Rb3__ksbxDRC1VSDV0amRYNmc/edit?usp=sharing) —
   `karel.exe` (runs a solution against a world), `kcl.exe` (the solution
   compiler), the Python script `karel_mdo_convert.py`, and the wrapper
   `karel-to-omegaup.bat` that ties them together.
2. Put your MDO and KEC cases in one folder. To generate them you can use the
   case-making Karel from [KarelOMI.zip](http://www.cimat.mx/~amor/Omi/Utilerias/KarelOMI.zip).
3. You also need your **solution**. If you program in Java, give the solution a
   `.JS` extension (so `kcl.exe` interprets it as karel-java); for Pascal, use
   `.PAS` (karel-pascal).
4. Put the exes, the Python script, and the `.bat` all in that same folder.
5. Run `karel-to-omegaup.bat` with no arguments and it will prompt for the
   solution path and the cases path, or pass them on the command line —
   quote paths that contain spaces:

   ```
   karel-to-omegaup.bat "karel vs chuzpa\solucion.js" "karel vs chuzpa\casos"
   ```

6. With everything in place, the script first compiles the solution with `kcl.exe`
   (producing a `.KX`), then builds the `.IN` worlds from every `.MDO` in the cases
   folder. Note the Python converter needs the matching `.KEC` to exist: for
   `caso1.MDO` you must also have `caso1.KEC`. From those it extracts beepers,
   orientation, and position into each `.IN`.
7. It then runs `karel.exe` with each generated `.IN` and the compiled `.KX`
   solution to produce the matching `.OUT` — so a *correct* solution is essential,
   since the outputs are only as right as it is.
8. The `.bat` drops a `cases` folder (with the `.IN`/`.OUT` pairs) inside your
   cases directory.
9. Finally, add a `statements` folder with `es.markdown` and zip it up exactly as
   you would a language problem.

## How it all comes together {#how-it-all-comes-together}

To close the loop: when you upload, gitserver's
[`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go)
unpacks the archive, validates that `cases/` exists and every submitting case has
its `.out`, folds `testplan`/`settings.json` into one canonical `settings.json`,
commits the whole thing as a new revision of the problem's git repository, and
deletes the now-redundant `testplan`. At grade time the PHP frontend
(`\OmegaUp\Controllers\Run::apiCreate` →
[`\OmegaUp\Grader::grade`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Grader.php))
hands the submission to the Go grader over HTTP, which reads that `settings.json`,
normalizes the case weights to sum to 1, runs each case under the sandbox against
your limits, applies the validator, and rolls the per-case scores up through the
group score policy. Every path and extension in this document exists to make that
pipeline resolve correctly — which is why getting them exactly right matters.

## Related documentation {#related-documentation}

- **[Creating problems](creating-problems.md)** — the authoring workflow and UI paths
- **[Verdicts](../verdicts.md)** — what `AC`, `TLE`, `MLE`, `OLE`, `JE`, and the rest mean
