---
title: Development Guides
description: Developer guides, coding standards, and best practices
icon: bootstrap/code-tags
---

# I Want to Develop in omegaUp

Thanks for your interest in contributing to omegaUp. This page is the front door to the codebase: it tells you what the system is actually made of, which repository each piece lives in, where in the tree your change probably belongs, and which guide to read next once you have picked a path in.

If you are not yet familiar with omegaUp as a *user*, do that first. Go to [omegaup.com](https://omegaup.com/), make an account, and solve a problem or two so you have felt the submit-and-get-a-verdict loop from the outside before you go read the code that runs it. Then [omegaup.org](https://omegaup.org/) will orient you on the organization and the areas we work on. It is a lot easier to reason about `apiCreate` once you have watched your own submission turn green.

## The 30-second mental model

omegaUp is not one program, it is a small constellation of services, and the single most useful thing to internalize before you clone anything is **which repo owns what**, because a change to how a verdict is computed and a change to how a contest page renders live in completely different codebases and different languages.

- **[omegaup/omegaup](https://github.com/omegaup/omegaup)** is the big one, the PHP + Vue **frontend and API monorepo**. This is where you almost certainly want to start. It renders every page, exposes the whole `/api/` surface, owns the MySQL schema, and talks to everything else over the network. When people say "the omegaUp codebase" without qualification, they mean this repo.
- **[omegaup/quark](https://github.com/omegaup/quark)** is the **evaluation backend**, written in Go: the *grader* (owns the submission queue and computes verdicts), the *runner* (compiles and executes user code), the *broadcaster* (pushes live scoreboard/verdict updates over WebSockets), and *minijail* (the sandbox that actually confines a running submission). None of this is in the PHP repo. The PHP side only ever *calls* the grader over HTTP.
- **[omegaup/gitserver](https://github.com/omegaup/gitserver)** is a Go service that stores each problem as its own git repository, which is how problem versioning works, so that a contest can be pinned to an exact revision of a problem's statement and test cases.

A one-line version to keep in your head: **the PHP monorepo is a pretty distributed web app that delegates the dangerous work — running untrusted code — to the Go grader in quark, and stores problems as git repos in gitserver.** Everything below is a consequence of that split.

!!! note "A correction the old wiki will trip you on"
    Older documentation describes the frontend running on HHVM and rendering with Smarty templates, and describes a Smarty→Vue migration in progress. All three are stale. The backend is standard **PHP 8.1** (php-fpm behind nginx), the server-side shell is **Twig 3**, and the Smarty→Vue migration is *done* — the app is currently **257 Vue 2.7 single-file components** and **414 TypeScript files** against exactly **one** application template (a Twig layout shell). The only migration still live is Vue 2 → Vue 3. If you read "HHVM" or "Smarty" anywhere, treat the surrounding claim as suspect.

## Architecture at a glance

These are the components and how they connect. Temporary internal codenames are written in *italics*.

| Component | What it is | Repo / language |
| --- | --- | --- |
| *Frontend* | The controllers and the whole `/api/` surface: contests, problems, users, rankings, the scoreboard. Renders the site and calls the *Backend* to compile and run code. | [omegaup/omegaup](https://github.com/omegaup/omegaup) — PHP 8.1 + MySQL 8.0 |
| *UX* | Every page's interface — Vue 2.7 single-file components in TypeScript, bundled by Webpack 5 and mounted into the Twig shell. | [omegaup/omegaup](https://github.com/omegaup/omegaup) — Vue 2.7 + TS 4.4 |
| *Grader* | Owns the submission queue, dispatches runs to *Runners*, collects their results, computes the verdict. | [omegaup/quark](https://github.com/omegaup/quark) — Go |
| *Runner* | Knows how to compile, execute, and feed input to a submission and check whether it is correct. Essentially a pretty, distributed frontend for *Minijail*. | [omegaup/quark](https://github.com/omegaup/quark) — Go |
| *Broadcaster* | Pushes live updates (new verdicts, scoreboard changes) to connected browsers over WebSockets. | [omegaup/quark](https://github.com/omegaup/quark) — Go |
| *Minijail* | The sandbox that confines a running submission — a fork of the Linux sandbox used in Chrome OS, hardened for judging untrusted C/C++/Python/Java/Karel and more. | [omegaup/quark](https://github.com/omegaup/quark) — C |
| *Gitserver* | Stores each problem as a git repo so contests can pin an exact problem revision. | [omegaup/gitserver](https://github.com/omegaup/gitserver) — Go |

If you want the authoritative long-form background, two papers were published in the IOI journal and are still the best deep reading on *why* the system is shaped this way: [omegaUp: Cloud-Based Contest Management System and Training Platform in the Mexican Olympiad in Informatics](http://ioinformatics.org/oi/pdf/v8_2014_169_178.pdf) (Chávez, González, Ponce, 2014) and [libinteractive: A Better Way to Write Interactive Tasks](https://ioinformatics.org/journal/v9_2015_3_14.pdf) (Chávez, 2015). For the in-repo version, read [Architecture Overview](../architecture/index.md) and, when you are ready to follow a submission end to end, [System Internals](../architecture/internals.md).

## Follow one real request before you touch anything

The fastest way to build a map of this codebase is to trace a single submission, because that one path touches almost every layer you will ever edit. When you hit "submit" in the Arena, the code is POSTed to `/api/run/create/`, and here is where it goes:

1. **`frontend/www/api/ApiEntryPoint.php`** is the literal entrypoint. It does `require_once('../../server/bootstrap.php')` and then `echo \OmegaUp\ApiCaller::httpEntryPoint()`. Every API request the browser makes lands here first.
2. **`frontend/server/bootstrap.php`** wires up the world — config, autoloading, DB, logging — and hands off to **`\OmegaUp\ApiCaller`** (`frontend/server/src/ApiCaller.php`), which parses the URL, resolves it to a controller, and dispatches to the matching `apiXxx` method.
3. For a submission that method is **`\OmegaUp\Controllers\Run::apiCreate`**, in [`frontend/server/src/Controllers/Run.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Run.php) (currently around line 415). Note the class is **`Run`**, not `RunController` — omegaUp controllers drop the `Controller` suffix (`Contest`, `Problem`, `Grader`, `Submission`, …). Inside, `apiCreate` runs the full gate of checks in order: that every required field is present (problem, contest, language, source), that the problem actually belongs to the contest, that the contest's time limit has not expired, that the user is not exceeding the submission rate limit, and that the contest is public or the user was explicitly invited — *before* it will accept the run. This is the pattern to imitate anywhere you add an endpoint: validate first, in one readable sweep.
4. Once the run is accepted, `apiCreate` calls **`\OmegaUp\Grader::getInstance()->grade($run, trim($source))`** (currently around line 573). That is the border of this repo. **`\OmegaUp\Grader`** (`frontend/server/src/Grader.php`) is a thin HTTP/curl client — it does *not* run any code itself. It POSTs the run to the Go grader at `OMEGAUP_GRADER_URL`, which defaults to `https://localhost:21680` (set in `frontend/server/config.default.php`).
5. From there the queue, the runners, and minijail all live in **quark**, over in Go, and are not in this repo at all. When you want to understand *that* half — the queue disciplines, how a runner is dispatched, how minijail fakes the absence of a network — read [Grader Internals](../architecture/grader-internals.md) and [Runner Internals](../architecture/runner-internals.md).

Understanding that boundary — PHP validates and enqueues, Go grades and sandboxes — tells you immediately which repo a given bug belongs to.

## The code, and the accounts you get

In the running dev container everything is under **`/opt/omegaup`**. The install ships two pre-configured accounts so you are not stuck at a login wall on first boot: **`omegaup` / `omegaup`** (administrator) and **`user` / `user`** (a normal user). Feel free to create as many more as you need for testing.

These are the directories we are actively working in, and *why* each matters:

- **[`frontend/database`](https://github.com/omegaup/omegaup/tree/main/frontend/database)** — the base SQL that builds the schema, plus every migration added since. If your change touches the shape of the data, it lands here as a new SQL file, not as a hand-edited base file.
- **[`frontend/server/src`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src)** — all the PHP, namespaced under `\OmegaUp\` (PSR-4). This is the server. Inside it:
    - **[`Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers)** — the business logic and the `/api/` surface. Every `apiXxx` method here is a public endpoint. If you are adding or changing behavior a client can call, you are working here.
    - **[`DAO/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/DAO)** — the data-access layer, split deliberately. **`DAO/Base/`** holds the auto-generated base classes with the raw create/update/delete/get SQL for each table, and **`DAO/VO/`** holds the auto-generated Value Objects (one per row shape). *You do not hand-edit either of those* — they are generated. When you need custom queries, you add them to the public DAO wrapper in `DAO/` itself, so the generated code can be regenerated without clobbering your work.
    - **[`Template/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Template)** — the custom Twig 3 extensions (`EntrypointNode`, `JsIncludeNode`, `VersionHashNode`, and the `Loader`) that let the single Twig shell inject Vue entrypoints and cache-busting version hashes.
- **[`frontend/www`](https://github.com/omegaup/omegaup/tree/main/frontend/www)** — the frontend. The TypeScript files call the controllers and massage the responses; the Vue single-file components render it all with HTML/CSS. Every `.vue` file lives under `frontend/www/js/omegaup/`, and the bulk of them (currently 248 of 257) under `frontend/www/js/omegaup/components/`. Two files here are special and **must not be hand-edited** — `frontend/www/js/omegaup/api.ts` and `api_types.ts` both open with `// generated by frontend/server/cmd/APITool.php. DO NOT EDIT.` They are the typed bridge between PHP and TypeScript: `APITool.php` reads the controllers' Psalm types and emits the matching TS, so the frontend calls the API in a fully type-checked way. Change a controller's shape, rerun `APITool.php`, and the types follow.
- **[`frontend/tests`](https://github.com/omegaup/omegaup/tree/main/frontend/tests)** — the PHPUnit controller tests. There are also Jest unit tests colocated with components and Cypress end-to-end specs under `cypress/e2e/`.
- **[`frontend/templates`](https://github.com/omegaup/omegaup/tree/main/frontend/templates)** — the internationalization files (English, Spanish, Portuguese) and `template.tpl`, the one Twig shell that wraps every page.

## Pick a path in

Where you go from here depends on what you want to change.

- **Frontend / UI work** — a page, a component, a form. You are living in `frontend/www/js/omegaup/components/` writing Vue 2.7 SFCs in TypeScript, styled with Bootstrap 4.6 + bootstrap-vue 2.21. Read [Components](components.md), and if you want to build a component in isolation, Storybook is set up (`yarn storybook`, on port 6006). One hard rule up front: **don't reach for jQuery** — this is a Vue app, do it the Vue way.
- **Backend / API work** — a new endpoint, a permission check, a query. You are in `frontend/server/src/Controllers/` and the DAO layer. Read the [Backend Architecture](../architecture/backend.md), the [MVC pattern](../architecture/mvc-pattern.md) we follow, and [Database Patterns](database-patterns.md) so you use the DAO/VO split correctly instead of writing raw SQL in a controller.
- **The evaluation pipeline** — how code is compiled, sandboxed, or scored. That work is in the **quark** and **gitserver** Go repos, not here. Start with [Grader Internals](../architecture/grader-internals.md), [Runner Internals](../architecture/runner-internals.md), and [Sandbox](../features/sandbox.md).
- **Verdicts, contests, problems as domain concepts** — read the [Features](../features/index.md) section and the [Verdicts reference](../features/verdicts.md) so you know what `AC`, `TLE`, `MLE` and friends actually mean before you touch code that emits them.

## Before you write a line: setup, tests, and the rules

Three things are non-negotiable and each has its own guide:

1. **[Set up your environment](../getting-started/development-setup.md)** — we develop in Docker. Windows and Ubuntu are the well-trodden paths; macOS works but needs extra configuration. Your checkout mounts into the container at `/opt/omegaup`, MySQL 8.0 listens on port `13306`, and the grader on `21680`.
2. **[Read the coding guidelines](coding-guidelines.md)** — these are reasoned engineering judgment, not arbitrary style. The load-bearing meta-rule: comments should explain *why*, not *what*. A representative one to give you the flavor — each `undefined`/`null` parameter doubles the combinations a function can be called with, and that grows exponentially, so keep the count of nullable parameters **under 10**. We delegate the mechanical enforcement to tools (Psalm, PHP_CodeSniffer, Prettier, ESLint, yapf/flake8/mypy on the Python side); run `./stuff/lint.sh validate` before you push and it will tell you what to fix.
3. **[Write tests](testing.md)** — every functionality change ships with tests, and they must be 100% green before you commit. PHPUnit for controllers, Jest for components, Cypress for end-to-end flows. Run the suite with `stuff/runtests.sh`.

When your change is ready, follow [How to make a pull request](../getting-started/contributing.md). One thing worth internalizing early, because it is the mistake new contributors hit first: after you fork, keep your `main` in sync with omegaUp's `main` and **never commit directly to it** — `main` mirrors the review-approved upstream, so if `git push upstream` ever fails, it means you committed to `main` by accident. (The recovery is `git push upstream -f`, but the real fix is to branch for every change.)

## Design decisions worth knowing

A few principles thread through the whole system, and knowing the reasoning keeps you from "fixing" something that is deliberate:

- **Encrypt everything.** *All* communication with omegaUp and between its subsystems is encrypted, client-to-server and component-to-component. This is not abstract security dogma — at an actual programming contest, someone sat down and sniffed the traffic, and between that and Firesheep-style attacks the bar for doing this is low enough that there is no excuse not to. The grader is spoken to over HTTPS for the same reason.
- **Minimize passwords; federate identity.** We lean on OAuth2 / OpenID (Facebook, GitHub) because every password you *don't* store is one you can't leak, and a user should be able to link multiple identities — a student who signed up as `user@email.com` should be able to prove they also own `a0001@school.mx` and merge the two accounts.
- **Keep components decoupled.** Some *Frontend* responsibility is expected to migrate toward *Arena* over time, so parts are kept as independent as possible rather than tightly welded together. When you are tempted to reach across a component boundary, remember it may not stay a single component.

## You might also want

- [Getting Started](../getting-started/index.md) — the top of the contributor funnel.
- [Useful Commands](useful-commands.md) — the day-to-day incantations for the dev container.
- [Migration Guide](migration-guide.md) — the current Vue 2 → Vue 3 upgrade work.
- [Architecture Overview](../architecture/index.md) and [System Internals](../architecture/internals.md) — the full end-to-end story of a submission.
- [API Reference](../reference/api.md) — the endpoint surface and the request/response envelope.
