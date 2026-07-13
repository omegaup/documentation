---
title: Useful Links
description: The repositories that make up omegaUp, where to start contributing, and a pointer to the API
icon: bootstrap/link
---

# Useful Links

omegaUp is not a single program — it's a handful of services that talk to each other over
HTTP, spread across several repositories. If you've only ever seen
[`omegaup/omegaup`](https://github.com/omegaup/omegaup) you've seen the PHP frontend and
the API, but not the Go grader that actually compiles and runs submissions, nor the git
server that stores problems as version-controlled repos. This page is the map: which repo
holds what, where to start if you want to contribute, and where the always-current API
reference lives. When a link points at code, it points at the repo that *owns* that code,
not the monorepo, so you land where the change actually has to be made.

## The repositories

There are three that matter for almost everything, plus a few satellites. The reason the
split exists at all is that the pieces are written in different languages and evolve on
different clocks: the frontend is PHP + Vue and ships on every merge to `main`, while the
grader is Go and ships as a versioned binary that the frontend calls over the network. Keep
that boundary in mind — it's why "fix the queue" and "fix the submission form" live in
different repos.

### omegaup/omegaup — the frontend and the API

[`github.com/omegaup/omegaup`](https://github.com/omegaup/omegaup) is the big one and the
one you'll spend most of your time in. It's the PHP 8.1 backend (php-fpm behind nginx, the
namespaced `\OmegaUp\...` code under
[`frontend/server/src`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src)),
the Vue 2.7 + TypeScript single-file components under
[`frontend/www/js/omegaup/components`](https://github.com/omegaup/omegaup/tree/main/frontend/www/js/omegaup/components),
and the entire public REST API. Every controller lives in
[`frontend/server/src/Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers),
and each `apiXxx` method on a controller is exactly one endpoint — so
[`Run.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Run.php)'s
`apiCreate` *is* `/api/run/create/`. What this repo does **not** contain is the grader, the
runner, or the sandbox: when a submission needs to be judged, the PHP class
[`\OmegaUp\Grader`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Grader.php)
just makes a curl call to `OMEGAUP_GRADER_URL` (default `https://localhost:21680`) and lets
the Go service do the real work.

### omegaup/quark — grader, runner, broadcaster

[`github.com/omegaup/quark`](https://github.com/omegaup/quark) is the backend proper, written
in Go, and its own README describes it in three pieces:

- **grader** — manages the run/submission queue. Notably, it *does not run anything itself*;
  it just holds the queue and hands work out. When you POST a submission, this is what
  `\OmegaUp\Grader` is talking to.
- **runner** — asks the grader for new submissions, then compiles and runs the code inside the
  [omegajail sandbox](https://github.com/omegaup/omegajail) against every input, compares the
  output to the expected answer (running a validator if the problem needs one), and assigns a
  score per case. It's basically a pretty, distributed frontend for the sandbox.
- **broadcaster** — pushes live notifications to everyone in a contest or course: runs getting
  graded, scoreboards shifting, new clarifications, and so on.

If you're chasing a bug about *why a verdict came back wrong* or *why the queue stalled*,
this is the repo, not the PHP one. The sandbox itself is one more repo down —
[`omegaup/omegajail`](https://github.com/omegaup/omegajail) — because isolating untrusted
contestant code is a hard enough problem to deserve its own project.

### omegaup/gitserver — problems as git repositories

[`github.com/omegaup/gitserver`](https://github.com/omegaup/gitserver) is the Go service that
stores every problem as its own git repository — statements, test cases, validators, settings,
all versioned. That's why editing a problem produces a real commit history you can roll back:
the "database" for problem *content* is git, not MySQL. The frontend talks to it whenever a
problem is created or edited, and the runner reads test cases from it when grading.

### The satellites

These come up less often but are worth knowing exist:

| Repository | What it's for |
|------------|---------------|
| [omegaup/libinteractive](https://github.com/omegaup/libinteractive) | Generates the boilerplate that lets a problem be *interactive* (contestant code and a judge process exchanging messages). Written up in the 2015 IOI-journal paper below. |
| [omegaup/omegajail](https://github.com/omegaup/omegajail) | The sandbox the runner shells out to. Isolates untrusted submissions at the syscall level. |
| [omegaup/deploy](https://github.com/omegaup/deploy) | Deployment scripts and production configuration. |
| [omegaup/problemsetter-toolkit](https://github.com/omegaup/omegaup/wiki) | Tooling around authoring problems (see the wiki for the current entry point). |

## Where to start contributing

The workflow lives in the main repo, and the single source of truth is
[`CONTRIBUTING.md`](https://github.com/omegaup/omegaup/blob/main/CONTRIBUTING.md) — read it
before your first PR, because the assignment rules are enforced by automation, not goodwill.
A few things it's worth knowing up front so you don't get surprised:

- **Claim an issue with `/assign`.** You may hold up to **2 active assignments** at a time,
  and `/assign` only works when the issue was opened by someone with repository association
  `OWNER`, `MEMBER`, or `COLLABORATOR` — that filter exists so the assignment bot doesn't hand
  out issues that random users filed. If you're a first-time contributor you can't self-assign
  until you have at least one merged PR here; until then, comment and a maintainer will help.
- **Set the environment up before anything else.** The full Docker walkthrough — bringing the
  containers up, running the tests, seeding test users, and the troubleshooting for when the
  container won't boot — lives in
  [`frontend/www/docs/Development-Environment-Setup-Process.md`](https://github.com/omegaup/omegaup/blob/main/frontend/www/docs/Development-Environment-Setup-Process.md),
  or in this site's own [Development Setup](../getting-started/development-setup.md) guide.
- **Follow the coding guidelines.** They're not style pedantry for its own sake; the meta-rule
  the whole codebase runs on is *explain why, not what*. See
  [Coding Guidelines](../development/coding-guidelines.md) here, or the canonical
  [wiki version](https://github.com/omegaup/omegaup/wiki/Coding-guidelines-(English-version)).

For the day-to-day, these are the pages the maintainers actually point new contributors at:

| Guide | What it covers |
|-------|----------------|
| [Contributing](../getting-started/contributing.md) | The fork → branch → PR loop and why you never commit to `main`. |
| [Getting Help](../getting-started/getting-help.md) | Where to ask when you're stuck (and the [wiki "How to Get Help"](https://github.com/omegaup/omegaup/wiki/How-to-Get-Help)). |
| [Useful Commands](../development/useful-commands.md) | The exact `docker-compose`, lint, and test invocations you'll run every day. |
| [Testing](../development/testing.md) | PHPUnit, Jest, and Cypress — how to run them and how to write one. |
| [Migration Guide](../development/migration-guide.md) | The live Vue 2.7 → Vue 3 migration (the old Smarty → Vue one is finished). |
| [Wiki home](https://github.com/omegaup/omegaup/wiki) | The original working-notes wiki, still the deepest source for setup edge cases. |

And the GitHub surfaces you'll live in:

| Resource | Link |
|----------|------|
| Issue tracker | [omegaup/omegaup/issues](https://github.com/omegaup/omegaup/issues) |
| Good first issues | [`Good first issue` label](https://github.com/omegaup/omegaup/labels/Good%20first%20issue) |
| Open pull requests | [omegaup/omegaup/pulls](https://github.com/omegaup/omegaup/pulls) |
| Code of Conduct | [`CODE_OF_CONDUCT.md`](https://github.com/omegaup/omegaup/blob/main/CODE_OF_CONDUCT.md) |
| Discord (main channel) | [discord.gg/gMEMX7Mrwe](https://discord.gg/gMEMX7Mrwe) |

## A pointer to the API

Everything the web frontend does, it does by calling the same public REST API you can call
yourself — every scoreboard refresh, every submission, every login is just an HTTP request to
`/api/...`. The rules are the same for all of them: plain HTTP GET or POST, JSON back, **HTTPS
only** (a plain-HTTP call gets a `301` redirect, not a silent success, because sniffing
contest traffic is a real cheating vector), every URL under `https://omegaup.com/api/`, and
authentication via a token you get from `user/login` and send back in a cookie named `ouat`.
One consequence worth remembering: you may only have **one active session at a time**, so
logging in programmatically will knock out your browser session and vice-versa.

!!! tip "Read this first"

    The full cross-cutting rules — transport, the `ouat` auth token, and the
    `status`/`errorcode`/`errorname`/`error` response envelope — are written up on the
    **[API Reference](api.md)** page, with a worked `curl` example.

The one thing we deliberately do **not** keep here is a hand-maintained list of endpoints,
because it would rot the moment someone edited a controller. The authoritative, always-current
surface is *generated from the source* by
[`frontend/server/cmd/APITool.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/cmd/APITool.php)
— the same tool that emits the typed frontend client
[`api.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/api.ts) and
[`api_types.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/api_types.ts).
To see exactly what a call accepts and returns, read the `apiXxx` method on its controller in
[`frontend/server/src/Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers)
rather than trusting any table.

## Official sites

| Resource | URL | What it is |
|----------|-----|------------|
| Platform | [omegaup.com](https://omegaup.com) | The live judge and contest system. |
| Organization | [omegaup.org](https://omegaup.org) | The nonprofit, our mission and impact. |
| Blog | [blog.omegaup.com](https://blog.omegaup.com) | Announcements, tutorials, release notes. |
| Status | [status.omegaup.com](https://status.omegaup.com) | Live system status and incident history. |

## Academic background

Two IOI-journal papers are the authoritative background on why the system is built the way it
is — worth reading if you want the design intent behind the architecture, not just the current
code:

- [omegaUp: Cloud-Based Contest Management System](http://www.ioinformatics.org/oi/pdf/v8_2014_169_178.pdf) (IOI Journal, 2014) — the original architecture paper.
- [libinteractive: A Better Way to Write Interactive Tasks](https://ioinformatics.org/journal/v9_2015_3_14.pdf) (IOI Journal, 2015) — the design behind [`omegaup/libinteractive`](https://github.com/omegaup/libinteractive).

The broader venue is the [IOI Journal at ioinformatics.org](https://ioinformatics.org/), and
omegaUp itself grew out of the [Mexican Olympiad in Informatics (OMI)](https://www.olimpiadadeinformatica.org.mx/).

## See also

- **[API Reference](api.md)** — the cross-cutting rules for calling any endpoint.
- **[System Internals](../architecture/internals.md)** — how a `run/create` call actually flows from `\OmegaUp\ApiCaller` through a controller and out to the Go grader.
- **[Grader Internals](../architecture/grader-internals.md)** and **[Runner Internals](../architecture/runner-internals.md)** — what happens inside quark once the frontend hands off a submission.

---

!!! tip "Missing a link?"
    If you know of a resource that belongs here, [open a PR](https://github.com/omegaup/omegaup/pulls) against the docs.
