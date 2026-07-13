---
title: Verdicts & Scoring
description: Understanding submission verdicts and scoring models
icon: bootstrap/check-circle
---

# Verdicts & Scoring

Every submission you make ends its life as a **verdict**: a short code that says what
happened when the grader ran your program against the problem's test cases. The verdict
you see in the Arena is the *worst* thing that happened across all the cases the grader
ran — omegaUp reports the most severe failure, because a program that gets one case wrong
is wrong no matter how many others it got right.

The verdict is stored on every run in the `verdict` column of the `Runs` and `Submissions`
tables, and it is one of exactly twelve values. They are, roughly from best to worst:

| Code | Name | What it means |
| ---- | ---- | ------------- |
| `AC` | Accepted | Every case in the run passed. Full marks. |
| `PA` | Partially Accepted | Some case groups passed, or a custom validator awarded fractional credit. Your score is strictly between 0 and the maximum. |
| `PE` | Presentation Error | The answer is essentially right but its formatting is off. A legacy verdict — most problems now use token validators that ignore whitespace, so you will rarely see it. |
| `WA` | Wrong Answer | The program ran to completion but produced output the validator rejected. |
| `TLE` | Time Limit Exceeded | The program did not finish within the problem's `time_limit` (e.g. 1000 ms). Also what a deadlock or an infinite wait on input becomes. |
| `OLE` | Output Limit Exceeded | The program wrote more output than allowed — usually an infinite loop with a `print` inside it. |
| `MLE` | Memory Limit Exceeded | The program tried to use more than the `memory_limit` (e.g. 32768 KiB). |
| `RTE` | Runtime Error | The program crashed — a non-zero exit code, an uncaught exception, a segfault, a signal. |
| `RFE` | Restricted Function Error | The program tried a system call the sandbox forbids (a socket, a fork, an unexpected file). Minijail caught it and killed the program. See [Sandbox](sandbox.md). |
| `CE` | Compilation Error | The code did not compile. The compiler's `stderr` is returned so you can see why — the one verdict decided before any case runs. |
| `JE` | Judge Error | Something went wrong *on omegaUp's side*, not yours: a runner died mid-evaluation, a case file was missing, an internal error surfaced. Re-submitting usually clears it; if it doesn't, tell us. |
| `VE` | Validator Error | The problem's own custom validator crashed or returned nonsense. A problem-setter bug, not a contestant bug. |

## Why the verdict is a group decision, not a case decision

A single run is really a batch of many executions — one per `.in` file — and each execution
gets its own per-case verdict inside the grader (`AC`, `WA`, `TLE`, …). The verdict you
finally see is the aggregate, and the aggregation rule is where the interesting behaviour
lives, because it is tied directly to **scoring**.

omegaUp groups test cases: everything before the first `.` in a case's filename is its
**group** (so `3.foo.in` and `3.bar.in` both belong to group `3`; a case with no dot, like
`5.in`, forms its own group `5`). A group awards its points only if **every** case in it
came back `AC` or `PA` — the "all-or-nothing per subtask" model competitive problems rely
on, where a partially-correct solution to a subtask earns nothing for that subtask.

Case weights come from the problem's `testplan` file if it has one (normalized so they sum
to 1); otherwise every case is worth `1 / number-of-cases`. The run's score is the sum of
the weights of the groups that fully passed, multiplied by the points the problem is worth
in the current contest (or scaled to 100% in practice mode). So `PA` — a fractional score —
is what you get when some groups pass and others don't, or when a custom validator hands
back a partial score for a case.

For the full path a submission takes from `/api/run/create/` through the queues, the
runner, the validators, and back to the scoreboard, see [System Internals](../architecture/internals.md)
and [Grader Internals](../architecture/grader-internals.md).

## Validators: how a case becomes AC or WA

The grader decides each case's verdict with a **validator**. The built-in validators
tokenize the expected output and the contestant output on whitespace and then compare:

- **`token`** — compare token by token; the first mismatch (or one stream ending before the
  other) is a `WA`. The default for most problems.
- **`token-caseless`** — the same, but case-insensitive.
- **`token-numeric`** — ignore non-numeric tokens, parse the rest as floating point, and
  compare with a tolerance. This is what lets a problem accept `3.14159` where the key says
  `3.14160`.
- **`literal`** — an exact match, no tokenization.
- **`custom`** — the problem ships its own validator program that reads the contestant's
  output (and, for some problems, the input) and decides the verdict itself, optionally
  awarding a partial score. A crash here is what produces `VE`.

!!! note "The reported verdict is the most severe one"
    When you debug a submission, remember the verdict is the worst case across the whole
    run. A run showing `TLE` may be solving most cases correctly and timing out on one large
    one — open the run details to see the per-case breakdown before concluding your whole
    approach is wrong.
