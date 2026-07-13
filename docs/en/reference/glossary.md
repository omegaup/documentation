---
title: Glossary
description: Terminology and definitions used in omegaUp
icon: bootstrap/book
---

# Glossary {#glossary}

This is the vocabulary the maintainers actually use in code review, in the issue tracker, and when something breaks at 2am. It is deliberately not an alphabetical dictionary of MVC buzzwords: the entries are grouped by where they sit in the life of a submission, because that is how the system is built and how you will end up debugging it. Almost every term links to the exact symbol, file, or config key that implements it, so you can go read the truth instead of trusting this page.

Two things worth internalizing before you read on. First, omegaUp is **two repositories that talk over HTTP**, not one: the PHP monorepo ([`omegaup/omegaup`](https://github.com/omegaup/omegaup)) is the frontend, API, and web app; the actual judging machinery — Grader, Runner, Broadcaster, and the sandbox — lives in the Go repo [`omegaup/quark`](https://github.com/omegaup/quark), with problem storage in [`omegaup/gitserver`](https://github.com/omegaup/gitserver). When this page says the PHP side "calls the Grader," it means a literal `curl` over `OMEGAUP_GRADER_URL`. Second, a lot of old wiki lore (HHVM, Smarty, an 8-named-queue Grader) is dead; where a term's implementation has moved, the entry says so.

---

## The submission pipeline {#the-submission-pipeline}

These are the components a single submission passes through, in roughly the order it touches them. If you only read one section, read this one — it is the spine everything else hangs off.

### Arena {#arena}

The Arena is the contest and practice UI — the split-pane screen where a contestant reads a problem, writes code in the embedded editor, submits, and watches the scoreboard and clarifications update live. It is **not** a separate service (it was floated as one for a hypothetical "v2" years ago and never split out); today it is plain Vue 2.7 running in the browser, with one TypeScript entrypoint per mode under `frontend/www/js/omegaup/arena/` — `contest_contestant.ts` for a live contest, `contest_practice.ts` for [practice mode](#practice-mode), and `contest_virtual.ts` for a [virtual contest](#virtual-contest). Everything it does is an ordinary API call: it POSTs code to `/api/run/create/`, polls `/api/contest/scoreboard/`, and opens a [Broadcaster](#broadcaster) socket for push updates so it does not have to poll for every verdict. See [Arena](../features/arena.md) for the user-facing tour and [Frontend architecture](../architecture/frontend.md) for how the Vue entrypoints are wired.

### Run / Submission {#run-submission}

A **submission** is what the contestant sends (source code + language + which problem, and if applicable which contest); a **run** is the graded artifact that comes back. In the database these really are two tables — `Submissions` holds the code and metadata, `Runs` holds the [verdict](#verdict), score, runtime, and memory — because a single submission can be graded more than once (a [rejudge](#rejudge) produces a new run for the same submission). The whole thing is created by `\OmegaUp\Controllers\Run::apiCreate` (`frontend/server/src/Controllers/Run.php`, around line 415), which is the single most instructive function in the backend to read: in one pass it validates that all required fields are present, that the problem belongs to the contest, that the [time limit](#time-limit) hasn't expired, that the user isn't exceeding the submission rate (`Run::$defaultSubmissionGap = 60` seconds between submissions to the same problem by default), and that the contest is public or the user was explicitly invited. Only after all of that does it hand off to the Grader at line ~573 via `\OmegaUp\Grader::getInstance()->grade($run, trim($source))`. Each run is identified by an opaque `guid` — that is the id you see in URLs and pass to `/api/run/status/`.

A field you will trip over: `submit_delay` is *the number of minutes from when the problem was opened (or the contest started) until the submission was sent*, and it is exactly what the scoreboard turns into [penalty](#penalty). It is `0` for [practice](#practice-mode) and for public-problem submissions outside any contest; `submission_deadline` is likewise `0` when you are not inside a contest.

### Grader {#grader}

The Grader is the brain of the judging half: a Go service in [`omegaup/quark`](https://github.com/omegaup/quark) (`cmd/omegaup-grader/`) that owns the queue of pending runs and hands them out to [Runners](#runner). The PHP backend never touches the queue directly — it only speaks HTTP to it through `\OmegaUp\Grader` (`frontend/server/src/Grader.php`), hitting `OMEGAUP_GRADER_URL` (default `https://localhost:21680`) at `/run/new/{run_id}/` to enqueue a fresh run, `/run/grade/` to force a [rejudge](#rejudge), `/broadcast/` to fan a message out through the [Broadcaster](#broadcaster), and `/grader/status/` to read queue health. That status payload (`run_queue_length`, `runner_queue_length`, `runners`, `broadcaster_sockets`, `embedded_runner`) is what `\OmegaUp\Controllers\Grader::apiStatus` surfaces on the admin dashboard.

Two implementation facts that matter and contradict the old wiki. First, the queue model is **four priority levels, not eight named queues**: `grader/queue.go` defines `QueuePriorityHigh (0)`, `QueuePriorityNormal (1)`, `QueuePriorityLow (2)`, and `QueuePriorityEphemeral (3)` with `QueueCount = 4`; a normal contest submission enters at `QueuePriorityNormal`, and the ephemeral tier is special because it deliberately does *not* persist results to the filesystem (it backs the "run this snippet" playground). Second, the Grader assumes Runners can die: the `InflightMonitor` in `grader/queue.go` arms a `connectTimeout` and `readyTimeout` of **10 minutes each**, and if a Runner picks up a run and then goes silent past that deadline it is presumed dead and the run is re-queued, retried up to `Config.Grader.MaxGradeRetries` times before being abandoned. See [Grader internals](../architecture/grader-internals.md) for the full state machine.

### Runner {#runner}

A Runner is a Go worker (also in `omegaup/quark`, `cmd/omegaup-runner/`) that does the actual compiling and executing. It **pulls** work rather than being pushed to: it long-polls the Grader's `/run/request/` endpoint, and when it gets a run it compiles the source and runs it against each [test case](#test-case) inside the [sandbox](#minijail-omegajail), streaming results back. The single best mental model, straight from the original design notes, is that the Runner *knows how to compile, execute, and feed input to a program, and check whether it's right — it is basically a pretty, distributed frontend for the sandbox.* Many Runners register with one Grader and are dispatched round-robin (there is no affinity today, though it existed at one point and would not be hard to add back). If a Runner is handed a run but doesn't have the problem's input set cached locally, it says so and the Grader re-sends the input `.zip`; if compilation fails it deletes the temp files and returns the compiler's stderr as a [CE](#verdict). See [Runner internals](../architecture/runner-internals.md).

### Minijail / omegajail {#minijail-omegajail}

This is the sandbox that makes it safe to run a stranger's C++ on your server. The lineage: **minijail** is the low-level process jailer (the binary shipped in `Dockerfile.minijail` as `minijail-xenial-distrib`), and **omegajail** is omegaUp's wrapper around it — in the Runner it is `OmegajailSandbox` (`runner/sandbox.go`), which shells out to `bin/omegajail` under an `omegajailRoot` with flags like `--root`. It enforces the [time](#time-limit) and [memory limits](#time-limit), blocks network access, and confines the filesystem, so a submission that tries to open a socket, fork-bomb, or read `/etc/passwd` simply can't. When a program attempts a forbidden syscall the sandbox kills it and the run comes back [RFE](#verdict) (restricted-function error). Note it lives entirely in `omegaup/quark`, not in the PHP repo — grepping the monorepo for `minijail` returns zero hits by design, because the frontend never invokes it and only ever sees the verdict. See [Sandbox](../features/sandbox.md).

### Broadcaster {#broadcaster}

The Broadcaster is the real-time fan-out service (Go, `omegaup/quark`, `broadcaster/`). When something a contestant should see happens — a [verdict](#verdict) lands, a [clarification](#clarification) is answered, the [scoreboard](#scoreboard) shifts — the PHP side calls `\OmegaUp\Broadcaster` which POSTs to the Grader's `/broadcast/`, and the Broadcaster pushes that message to every relevant connected client so the [Arena](#arena) updates without polling. "Relevant" is decided by filters in `broadcaster/filter.go`: a `UserFilter`, `ProblemFilter`, `ProblemsetFilter`, `ContestFilter`, and a catch-all `AllEventsFilter`, so a message for contest X only reaches sockets subscribed to contest X. It speaks two transports (`broadcaster/transport.go`): `WebSocketTransport` and an `SSETransport` fallback. See [Broadcaster architecture](../architecture/broadcaster.md) and [Real-time updates](../features/realtime.md).

### GitServer {#gitserver}

Problems are stored as **git repositories**, one repo per problem, and the GitServer ([`omegaup/gitserver`](https://github.com/omegaup/gitserver), Go) is what serves and versions them. Every edit to a statement, test case, or [validator](#validator) is a commit, which is why a problem has a full history and why a contest can be pinned to a specific problem version even after the author keeps editing (see [Problem versioning](../features/problem-versioning.md)). The PHP side reaches it at `OMEGAUP_GITSERVER_URL` (default `http://localhost:33861`, from `OMEGAUP_GITSERVER_PORT`) authenticated with `OMEGAUP_GITSERVER_SECRET_TOKEN`. See [GitServer architecture](../architecture/gitserver.md).

---

## Verdicts {#verdicts}

### Verdict {#verdict}

The one-word outcome of a run. The canonical, authoritative list is `VerdictList` in `common/problemsettings.go` in `omegaup/quark`, and it is stored **sorted from worst to best** — this ordering is load-bearing, because when a submission is judged case by case the final verdict is the *worst* case's verdict, so "worse sorts first" is how the Runner picks it:

`JE` → `CE` → `RFE` → `VE` → `MLE` → `RTE` → `TLE` → `OLE` → `WA` → `PA` → `AC` → `OK`

Each one:

- **`AC` (Accepted)** — every case correct within limits. The one you want.
- **`PA` (Partially Accepted)** — some cases/[groups](#test-group) passed, some didn't, and the [score mode](#score-mode) awards partial credit.
- **`WA` (Wrong Answer)** — output was well-formed but wrong on at least one case.
- **`OLE` (Output Limit Exceeded)** — the program printed more than the allowed [output limit](#time-limit); the Runner also raises this if a program in an interactive setup causes its parent to overflow.
- **`TLE` (Time Limit Exceeded)** — exceeded the per-case [time limit](#time-limit).
- **`RTE` (Runtime Error)** — crashed: segfault, uncaught exception, nonzero exit, division by zero.
- **`MLE` (Memory Limit Exceeded)** — blew past the [memory limit](#time-limit).
- **`VE` (Validator Error)** — the problem's custom [validator](#validator) itself failed to produce a usable score (a problem-author bug, not a contestant bug).
- **`RFE` (Restricted Function Error)** — the [sandbox](#minijail-omegajail) killed the program for attempting a forbidden syscall, e.g. trying to open a network socket.
- **`CE` (Compilation Error)** — didn't compile; the compiler's stderr is returned so the contestant can see why.
- **`JE` (Judge Error)** — omegaUp's own fault: bad test data, a broken validator, or infrastructure trouble. If you see this, check the Grader logs, don't blame the contestant.
- **`OK`** — an internal, per-case "this case ran fine" marker used inside the Runner, not a user-facing final verdict.

The verdict lands on `Runs.verdict` and rides the [Broadcaster](#broadcaster) to the [Arena](#arena). See [Verdicts](../features/verdicts.md) for worked examples of each.

---

## Contests, courses, and their shared plumbing {#contests-courses-and-their-shared-plumbing}

### Contest {#contest}

A timed competition over a set of [problems](#problem), owned by `\OmegaUp\Controllers\Contest`. A contest has a hard `start_time`/`finish_time`, a [scoreboard](#scoreboard), a [score mode](#score-mode) and [penalty](#penalty) policy, an `admission_mode` (public vs invite-only), and an optional `window_length` — the per-contestant clock for "you get N minutes from when *you* start," which returns `null` when the contest wasn't configured that way. Note a contest doesn't store its problems directly; it points at a [problemset](#problemset).

### Course {#course}

A structured, class-oriented container: a sequence of assignments, each of which is itself a [problemset](#problemset), plus students, deadlines, progress tracking, and optional teaching assistants. Owned by `\OmegaUp\Controllers\Course`. The mental split is that a **contest is a one-shot event** and a **course is an ongoing class** — but because both ultimately group problems into problemsets, they share almost all of the run-submission, scoreboard, and clarification machinery underneath.

### Problemset {#problemset}

The abstraction that lets contests and course assignments reuse the same code. A **problemset** is just "a set of problems people submit against," identified by `problemset_id`; a contest *has* a problemset, and each course assignment *is* a problemset (`\OmegaUp\Controllers\Problemset`). This is why a [run](#run-submission) carries a `problemset_id` rather than a `contest_id` — the run doesn't care whether it's being submitted into a contest or a homework assignment, only which problemset governs it. If you're ever confused about why contest and course logic look so similar, this is the answer: they're the same problemset plumbing with different lids.

### Clarification {#clarification}

The in-contest Q&A channel. A contestant asks a question about a problem via `\OmegaUp\Controllers\Clarification::apiCreate` (`frontend/server/src/Controllers/Clarification.php`); it's stored in the `Clarifications` table with a `public` flag. When an organizer answers, or marks it public, the controller pushes it through the static `\OmegaUp\Broadcaster` so it appears live in the askers' (or everyone's, if public) [Arena](#arena) without a refresh. The `public` flag is the important nuance: a private clarification goes only to the one asker, a public one broadcasts to the whole contest so everybody sees the same ruling.

### Scoreboard {#scoreboard}

The live ranking. Built in `frontend/server/src/Scoreboard.php`, and — this is the part people forget — it is **heavily cached** in Redis under distinct keys for the two audiences: `CONTESTANT_SCOREBOARD_PREFIX` (what players see, respecting [freeze](#scoreboard-freeze)) and `ADMIN_SCOREBOARD_PREFIX` (the unfrozen truth for organizers), each with a parallel `..._EVENTS_PREFIX` for the animated timeline. Ranking sorts by total points then total [penalty](#penalty), and how penalty aggregates across problems depends on `penalty_calc_policy` (`sum` adds every problem's penalty; `max` takes only the largest). Because it's expensive to recompute, the Arena listens for [Broadcaster](#broadcaster) nudges rather than re-fetching constantly.

### Penalty {#penalty}

The tiebreaker time in ICPC-style scoring: with equal points, whoever accumulated less penalty ranks higher. **When** penalty starts counting is set by `penalty_type`, an enum with exactly four values (`Contest.php`): `contest_start` (minutes counted from the contest's start), `problem_open` (from when *that contestant* first opened *that problem*), `runtime` (use the solution's actual execution time), and `none` (no penalty at all — pure score race). **How** it aggregates across problems is the separate `penalty_calc_policy` (`sum` vs `max`) described under [Scoreboard](#scoreboard). The per-submission raw value is the run's `submit_delay`; wrong submissions before the accepted one add fixed penalty on top (conventionally 20 minutes each in ICPC rules).

### Score mode {#score-mode}

How a problem's per-case results roll up into a number, set by `score_mode` with three values (`Contest.php`): `all_or_nothing` (you score full marks only if every case is [AC](#verdict) — classic ICPC), `partial` (sum the weights of the cases/[groups](#test-group) you passed — classic IOI), and `max_per_group` (take the best result per group and sum those). This is what decides whether a half-right solution earns [PA](#verdict) and some points or just [WA](#verdict) and zero.

### Scoreboard freeze {#scoreboard-freeze}

The suspense mechanism: near the end of a contest the public [scoreboard](#scoreboard) stops updating for contestants while organizers keep seeing live standings — implemented as the split between the `CONTESTANT_SCOREBOARD_PREFIX` and `ADMIN_SCOREBOARD_PREFIX` caches. Submissions are still judged normally; only the public *view* is held, so the final reveal is dramatic and nobody can reverse-engineer their exact standing to game the last minutes.

### Practice mode {#practice-mode}

After a contest ends (or on any public problem), you can keep submitting for learning with no stakes. In `Run::apiCreate` this is the `isPractice` branch: `submit_delay` is forced to `0` and no [penalty](#penalty) accrues, and access is gated by `Problems::getPracticeDeadline` rather than the contest clock — submit past that deadline and it's rejected. The Arena entrypoint is `contest_practice.ts`. The point is to let people grind old problems without polluting any live ranking.

### Virtual contest {#virtual-contest}

Re-running a finished contest against its *original* clock so you can experience it as if you were competing — same problems, same duration, but shifted to now, and scored on a private scoreboard that doesn't touch the real historical results. Entrypoint `contest_virtual.ts`. It's the honest way to "take" a past contest for practice under real time pressure.

### Lockdown {#lockdown}

A **global, site-wide read-only switch**, not a per-contest anti-cheat feature. When `OMEGAUP_LOCKDOWN` is on, `\OmegaUp\Controllers\Controller::ensureNotInLockdown()` throws `ForbiddenAccessException('lockdown')` from every mutating endpoint, so the site keeps serving reads but refuses writes — used during migrations or incidents. It has a companion `OMEGAUP_LOCKDOWN_DOMAIN` (default `localhost-lockdown`). Don't confuse it with contest exam-security features; this one is an operator's kill switch for writes.

---

## Problem anatomy {#problem-anatomy}

### Problem {#problem}

The atomic unit of content: a statement, input/output spec, constraints, [test cases](#test-case), limits, and an optional [validator](#validator), stored as a git repo in the [GitServer](#gitserver) and owned on the PHP side by `\OmegaUp\Controllers\Problem`. Everything else — contests, courses, runs — exists to get people submitting against problems.

### Test case {#test-case}

One input file paired with its expected output. A submission is [AC](#verdict) only if it satisfies every test case within [limits](#time-limit); the worst case's [verdict](#verdict) becomes the run's verdict.

### Test group {#test-group}

A named bundle of test cases that scores together, used for subtask-style grading. The naming convention is mechanical and worth knowing: a case's group is *everything before the first `.` in its name* (so `2.a`, `2.b`, `2.c` all belong to group `2`), and under `all_or_nothing`/`max_per_group` [scoring](#score-mode) a group awards its points only if the whole group is satisfied. Weights are normalized so they sum to 1, or default to 1/(number of cases) when unspecified.

### Validator {#validator}

For problems with more than one correct answer (any ordering, floating-point tolerance, "print any shortest path"), a plain text-diff won't do, so the author ships a **validator** program that reads the contestant's output and decides the score. The comparison strategy is the [validator type](#validator-type). If the validator itself blows up, the run is [VE](#verdict), not [WA](#verdict) — that distinction tells you whose bug it is.

### Validator type {#validator-type}

How output is checked. `token` / `token-caseless` compare token by token (optionally ignoring case), `token-numeric` compares numbers within an epsilon (so `1.0000001` matches `1.0`), `literal` demands an exact byte match, and `custom` hands the decision to the author's [validator](#validator) program.

### Time limit / Memory limit / Output limit {#time-limit}

The three resource ceilings the [sandbox](#minijail-omegajail) enforces per case. **Time limit** is wall/CPU time (breaching it yields [TLE](#verdict)); **memory limit** is the address-space cap in KiB (breaching it yields [MLE](#verdict)); **output limit** caps how many bytes a program may print (breaching it yields [OLE](#verdict)), which exists so an infinite `while(true) printf(...)` can't fill a disk. These are per-problem settings; the actual enforcement is omegajail flags in `runner/sandbox.go`, not PHP.

---

## Backend building blocks {#backend-building-blocks}

### Controller {#controller}

The PHP classes that implement the API and hold the business logic, in `frontend/server/src/Controllers/` under the `\OmegaUp\Controllers` namespace. A convention that bites newcomers: the class names **drop the `Controller` suffix** — the run endpoint lives in class `Run` (fully qualified `\OmegaUp\Controllers\Run`), not `RunController`; likewise `Contest`, `Problem`, `Clarification`, `Grader`. Public API methods are prefixed `api…` (`apiCreate`, `apiStatus`).

### ApiCaller / entrypoint {#apicaller-entrypoint}

Every `/api/...` request lands at `frontend/www/api/ApiEntryPoint.php`, which `require`s `frontend/server/bootstrap.php` and then calls `\OmegaUp\ApiCaller::httpEntryPoint()`. `ApiCaller` (`frontend/server/src/ApiCaller.php`) is the dispatcher: it parses the route, checks the [auth token](#authentication-token), and invokes the right controller's `api…` method. That chain — entry file → bootstrap → ApiCaller → `Controller::apiXxx` — is the front door for the entire backend. See [Backend architecture](../architecture/backend.md).

### DAO (Data Access Object) {#dao-data-access-object}

The generated data-access layer. Each table gets an auto-generated abstract base in `frontend/server/src/DAO/Base/` (e.g. `Base/Runs.php`, holding the raw `INSERT`/`UPDATE` SQL) plus a hand-editable public wrapper in `frontend/server/src/DAO/` where custom queries live. The split exists so regenerating the boilerplate never clobbers your bespoke queries. Access is via `mysqli` against MySQL 8.0 (`MySQLConnection.php`). See [Database patterns](../development/database-patterns.md).

### VO (Value Object) {#vo-value-object}

The typed row objects the DAOs move around, in `frontend/server/src/DAO/VO/` (e.g. `VO/Runs.php`). A VO is one record with typed properties and a `FIELD_NAMES` map — you fetch VOs from a DAO, mutate them, and hand them back to the DAO to persist. Together **DAO + VO** are how the codebase avoids hand-writing SQL string-slinging in controllers; the [MVC pattern](../architecture/mvc-pattern.md) page has the full picture.

### Authentication token {#authentication-token}

The credential that identifies a user on API calls, carried in the `ouat` cookie and validated by [`ApiCaller`](#apicaller-entrypoint). Under the hood these are PASETO tokens (`paragonie/paseto`), not the ad-hoc strings the old wiki described. An unauthenticated call to a protected endpoint comes back with a permission error, not a redirect, because the API is meant to be consumed programmatically.

### Rejudge {#rejudge}

Re-running an existing [submission](#run-submission) to produce a fresh [run](#run-submission) — after a bad [test case](#test-case) is fixed, a [validator](#validator) is corrected, or limits change. The PHP side triggers it by calling the Grader's `/run/grade/` endpoint; in the [queue](#grader) a rejudge enters at a lower priority so it can't starve live contest submissions.

---

## Related documentation {#related-documentation}

- **[Grader internals](../architecture/grader-internals.md)** — the queue, dispatch, and retry state machine
- **[Runner internals](../architecture/runner-internals.md)** — compile/run pipeline and the sandbox call
- **[Broadcaster](../architecture/broadcaster.md)** and **[Real-time updates](../features/realtime.md)** — how live updates reach the Arena
- **[GitServer](../architecture/gitserver.md)** — problems as git repositories
- **[Backend architecture](../architecture/backend.md)** and **[MVC pattern](../architecture/mvc-pattern.md)** — controllers, DAO/VO, the API entrypoint
- **[Verdicts](../features/verdicts.md)** — every verdict with examples
- **[Sandbox](../features/sandbox.md)** — minijail/omegajail isolation
- **[Languages](languages.md)** — supported compilers and language keys
