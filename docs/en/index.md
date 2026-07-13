---
title: Welcome
description: Complete documentation for the omegaUp educational programming platform
icon: bootstrap/home
---

![omegaUp Logo](assets/images/omegaup.png){ width="300" style="max-width: 100%; height: auto; object-fit: contain;" }

# Welcome to omegaUp Documentation

omegaUp is a free, open-source educational platform built around an automatic online judge: you write a solution, submit it, and within seconds you get back a verdict — `AC`, `WA`, `TLE`, and the rest — because a sandboxed grader has actually compiled and run your code against every test case. Tens of thousands of students and teachers across Latin America use it every day to practice, teach, and compete, from national olympiad training all the way down to kids taking their first steps in **Karel**, the robot-on-a-grid language omegaUp supports specifically so a ten-year-old can learn to program before they know what a `for` loop is (alongside the languages you'd expect: C, C++, Java, Python, C#, Go, Haskell, Lua, Pascal, and Ruby).

These docs are for the people who **build and run** that platform — the contributor setting up their environment for the first time, the developer tracing how a submission actually flows through the code, and the operator keeping the site alive in production. If you just want to *use* omegaup.com to solve problems or run a contest for your school, you'll be happier on the site itself and on the [blog](https://blog.omegaup.com/), where the newest features get announced first. Everything below assumes you want to look under the hood.

!!! abstract "The one-paragraph mental model"

    omegaUp is **not** a single program. This repository — [`omegaup/omegaup`](https://github.com/omegaup/omegaup) — is the **PHP 8.1 frontend and API monorepo** (php-fpm behind nginx). It serves a thin Twig 3 HTML shell that boots a Vue 2.7 + TypeScript single-page app, and it exposes every feature as a REST endpoint under `/api/`. It does **not** compile or run your code. When you submit, the PHP backend hands the run over HTTP to a completely separate **Go grader service** (the [`omegaup/quark`](https://github.com/omegaup/quark) project — grader, runner, broadcaster, and the minijail sandbox), and problem data lives in git repositories managed by a third service, [`omegaup/gitserver`](https://github.com/omegaup/gitserver). Knowing which of these three repos a thing lives in saves you hours; most of this documentation is organized around that split.

## Quick Start

New to omegaUp? Start here:

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __[Getting Started](getting-started/index.md)__

    ---

    Stand up a full local omegaUp with `docker-compose`, create your test users, and make your first pull request. The environment is containerized precisely so you don't have to hand-install PHP, MySQL, Redis, and the Go grader yourself — the first `docker-compose up` can take a few minutes while images pull and the database seeds.

    [:octicons-arrow-right-24: Get Started](getting-started/index.md)

-   :material-code-tags:{ .lg .middle } __[Architecture](architecture/index.md)__

    ---

    Follow one real submission end to end — from `OmegaUp.submit` in the browser, through `ApiEntryPoint.php` → `bootstrap.php` → `\OmegaUp\ApiCaller`, into `\OmegaUp\Controllers\Run::apiCreate`, and out over HTTP to the Go grader. This is the map of how the three services fit together.

    [:octicons-arrow-right-24: Learn More](architecture/index.md)

-   :material-api:{ .lg .middle } __[API Reference](reference/api.md)__

    ---

    Every page the frontend renders is just an authenticated call to `/api/...`, so the API can do anything the UI can. Learn the cross-cutting rules — PASETO `auth_token` auth, JSON transport, and the `status`/`error`/`errorcode` response envelope — then follow the always-current, source-generated endpoint list.

    [:octicons-arrow-right-24: Browse API](reference/api.md)

-   :material-tools:{ .lg .middle } __[Development Guides](development/index.md)__

    ---

    The house rules that keep 257 Vue components and a large PHP codebase coherent: coding guidelines (yes, "Don't use jQuery!"), how to run Psalm, PHPUnit, Jest, and Cypress locally, and how the generated `api.ts` / `api_types.ts` clients keep the frontend and backend types in lockstep.

    [:octicons-arrow-right-24: Read Guides](development/index.md)

</div>

## What is omegaUp?

omegaUp exists to make deliberate programming practice free and automatic. Everything on the platform is built around the online judge — the machinery that decides, objectively and in seconds, whether a solution is correct and fast enough:

- **Problem solving** — a large library of programming problems, each with hidden test cases, a `time_limit` (commonly `1000` ms) and a `memory_limit` (commonly `32768` KiB), graded automatically so nobody has to hand-check submissions.
- **Contests** — run a timed programming competition for your school, university, or club, with a live scoreboard. All contest traffic is encrypted for a concrete reason: at a past programming contest someone sniffed the network to cheat, so *every* communication with omegaUp goes over TLS.
- **Courses** — structured learning paths that bundle problems into assignments, so a teacher can build a semester's worth of graded practice.
- **Training** — practice problems organized by topic and difficulty for anyone leveling up on their own.

## Documentation Sections

### :material-school:{ .lg } [Getting Started](getting-started/index.md)
Everything you need to go from a fresh clone to a running local site and a merged pull request: the `docker-compose` setup, seeded test accounts (the admin `omegaup`/`omegaup` and a normal `user`/`user`, plus the `test_user_0..9` fixtures), the fork-and-PR workflow, and where to get help when the container won't boot.

### :material-sitemap:{ .lg } [Architecture](architecture/index.md)
A deep dive into how the three services — the PHP frontend/API, the Go grader (quark), and gitserver — actually move a request through real code: the controller layer under `frontend/server/src/Controllers/`, the auto-generated DAO/VO data-access layer over MySQL 8.0, and the HTTP handoff to the grader at `OMEGAUP_GRADER_URL` (default `https://localhost:21680`).

### :material-api:{ .lg } [API Reference](reference/api.md)
The transport, authentication, and response-envelope rules that apply to every endpoint, plus the source-generated endpoint reference. Because the list is generated from the PHP controllers by `frontend/server/cmd/APITool.php`, it can't drift out of sync with what the server actually accepts.

### :material-code-braces:{ .lg } [Development](development/index.md)
Coding standards, the linting and static-analysis toolchain (Psalm for PHP, `prettier`/ESLint for TypeScript), testing across PHPUnit, Jest 26, and Cypress 15.7, database and migration patterns, and how to build Vue single-file components without fighting the existing conventions.

### :material-feature-search:{ .lg } [Features](features/index.md)
Feature-by-feature internals: how the [Arena](features/arena.md) serves contests, how the [grader and runner](features/sandbox.md) compile and execute a submission inside minijail, what each [verdict](features/verdicts.md) means, how [problem versioning](features/problem-versioning.md) uses git, and how [badges](features/badges.md) and [real-time updates](features/realtime.md) work.

### :material-server:{ .lg } [Operations](operations/index.md)
Running omegaUp in production: nginx and php-fpm configuration, the Redis and RabbitMQ 3 infrastructure the app depends on, observability through Prometheus and Monolog, and the troubleshooting playbooks for when something breaks.

### :material-account-group:{ .lg } [Community](community/index.md)
How to become a regular contributor, including omegaUp's long-running participation in [Google Summer of Code](community/gsoc/index.md).

## Key Facts

!!! tip "Educational by design"
    omegaUp is built for classrooms and competitions, not just solo practice — courses, assignments, and contest scoreboards exist so a teacher can run an entire program on it. That's why it supports Karel: the platform meets students where they are, including the ones who haven't written real code yet.

!!! success "Open source, three repositories"
    Contributions are welcome across all three: the PHP frontend/API in [`omegaup/omegaup`](https://github.com/omegaup/omegaup), the Go grader stack in [`omegaup/quark`](https://github.com/omegaup/quark), and problem storage in [`omegaup/gitserver`](https://github.com/omegaup/gitserver). Check which repo a subsystem lives in before you go looking for its code — the grader and the sandbox are **not** in the PHP monorepo.

!!! info "Multi-language grading"
    Submissions can be written in C, C++, Java, Python, C#, Go, Haskell, Lua, Pascal, Ruby, and Karel. The grader compiles each one in an isolated sandbox and runs it against every test case, then scores it.

!!! warning "Everything is encrypted"
    All communication with omegaUp and its subsystems goes over TLS. This isn't box-ticking security theater: encrypting everything minimizes the chance of cheating in contests (traffic *has* been sniffed at a real competition), and with tooling like Firesheep around, doing it right is cheap and non-negotiable.

## Get Involved

- **Contribute code** — start with the [Contributing Guide](getting-started/contributing.md); the maintainer team reviews every PR against the [Coding Guidelines](development/index.md).
- **Report issues** — open one at [github.com/omegaup/omegaup/issues](https://github.com/omegaup/omegaup/issues).
- **Google Summer of Code** — omegaUp mentors students each year; see the [GSoC program](community/gsoc/index.md).

## Resources

- **Website**: [omegaup.com](https://omegaup.com)
- **Blog**: [blog.omegaup.com](https://blog.omegaup.com)
- **Organization**: [omegaup.org](https://omegaup.org)
- **GitHub**: [github.com/omegaup/omegaup](https://github.com/omegaup/omegaup)

---

**Ready to start?** Head to [Getting Started](getting-started/index.md) to bring up a local omegaUp with `docker-compose` and make your first change.
