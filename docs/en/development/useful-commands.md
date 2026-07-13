---
title: Useful Development Commands
description: Common commands and shortcuts for omegaUp development
icon: bootstrap/terminal
---

# Useful Development Commands

This is the working set of commands you'll reach for day to day: linting, the PHP and Vue test suites, the Webpack build, and the database scripts that keep your local schema and seed data honest. Every command below is reproduced exactly as you should type it — the flags are load-bearing, so don't paraphrase them.

The single most important thing to get right before anything else is **where** you run each command. omegaUp development happens across a boundary: some tooling runs on your host machine (it needs your Docker socket, your Node install, or a browser), and some runs *inside* the `frontend` container (it needs the PHP runtime, the MySQL connection on port `13306`, and the code mounted at `/opt/omegaup`). Running a command on the wrong side of that boundary is the most common early stumble, so each section calls out its execution location, and several scripts actively refuse to run in the wrong place rather than fail cryptically.

To get inside the container in the first place:

```bash
docker exec -it omegaup-frontend-1 /bin/bash
```

This opens a bash shell inside the frontend container, dropping you at `/opt/omegaup` (the repo, bind-mounted from your host). The container is named `omegaup-frontend-1` under Docker Compose V2 (the `<project>-<service>-<n>` scheme, where the project name defaults to your `omegaup` directory). On older Compose V1 installs the same container is named `omegaup_frontend_1` with underscores — if `docker exec` complains that the container doesn't exist, run `docker compose ps` to see the exact name your setup produced.

!!! tip "How to tell which side you're on"
    Inside the container your prompt sits at `/opt/omegaup`; on the host it's wherever you cloned the repo (e.g. `~/dev/omegaup`). Several scripts key off this: `git rev-parse --show-toplevel` returning `/opt/omegaup` is exactly how `lint.sh` and `runtests.sh` detect that they're inside the container.

## Linting and Validation

### Run all omegaUp linters

```bash
./stuff/lint.sh
```

Run this from the **project root on your host**, outside the container — it spins up its own Docker image (`omegaup/hook_tools:v1.0.9`) to run the linters in a pinned, reproducible environment, so it needs your Docker socket. Because of that, `lint.sh` explicitly refuses to run inside the container: if `git rev-parse --show-toplevel` comes back as `/opt/omegaup`, it prints *"Running ./stuff/lint.sh inside a container is not supported"* and exits, and if it can't find a `docker` binary it tells you to install Docker or move outside the container. Both messages are the script protecting you from a run that would silently do the wrong thing.

With no arguments, `lint.sh` doesn't lint the whole tree — it guesses the set of files you actually changed by diffing against the merge-base of your branch and `upstream/main` (falling back to `origin/main` if you haven't added the `upstream` remote), which is why a first run after cloning without an upstream can behave differently than you expect. You rarely need to invoke it by hand, though: it's wired into the `pre-push` git hook, so it runs automatically on every `git push` and blocks the push if anything is unclean.

### Validate style without fixing

```bash
./stuff/lint.sh validate
```

The default mode *fixes* what it can (it delegates to `yapf`, `prettier`, `phpcbf`, and friends inside the hook-tools image); `validate` instead only checks and reports, changing nothing on disk. Reach for this in CI-like situations or when you want to see what's wrong before letting the autofixer rewrite your files.

### Generate `.lang` translation files

```bash
./stuff/lint.sh --linters=i18n fix --all
```

This runs only the `i18n` linter and regenerates the `*.lang` files across all locales from the three source-of-truth files `es.lang`, `en.lang`, and `pt.lang`. Run it whenever you add or change a user-facing string so the generated per-language files stay in sync — the i18n linter will fail the push otherwise. It also runs outside the container, from the project root.

## Testing

### Run all PHP tests and validations

```bash
./stuff/runtests.sh
```

This is the full backend gate, and it's meant to run **inside the container**. It bundles four distinct checks that you'd otherwise run separately: `stuff/db-migrate.py validate` (confirms your migrations are consistent), `stuff/policy-tool.py validate`, and `stuff/mysql_types.sh` — which is the heavy one, running the controllers and badges PHPUnit suites *plus* the MySQL return-type check that verifies your DAO methods actually match the shapes their queries return — and finally Psalm with `--show-info=false`.

`runtests.sh` is location-aware: run it inside the container and it invokes those tools directly; run it on the host and it transparently shells into the container with `docker compose exec -T frontend` for each step. Either way, when the in-container portion finishes it reminds you to run the two host-side checks it *can't* do from inside — `./stuff/lint.sh` and the Selenium/UI tests via `python3 -m pytest ./frontend/tests/ui/ -s` — because those need Docker and a browser respectively. Don't skip that reminder; a green `runtests.sh` alone is not a green build.

### Run PHP unit tests for a specific file

```bash
./stuff/run-php-tests.sh frontend/tests/controllers/$MY_FILE.php
```

When you're iterating on one controller you don't want the whole suite. This wrapper runs PHPUnit against just the file you name (omit the filename entirely to run everything under `frontend/tests/`). It wires up the suite's real configuration for you — `--bootstrap frontend/tests/bootstrap.php`, `--configuration frontend/tests/phpunit.xml`, and coverage written to `coverage.xml` — and then passes any *extra* arguments straight through to `phpunit`. That passthrough is the useful part: to run a single test method you can append PHPUnit's own filter, e.g.

```bash
./stuff/run-php-tests.sh frontend/tests/controllers/UserRankTest.php --filter testUserRankingClassName
```

Run this inside the container, since PHPUnit needs the live MySQL connection.

### Run Cypress end-to-end tests (interactive)

```bash
npx cypress open
```

This opens the Cypress Test Runner, the GUI where you pick a spec, watch it drive a real Chrome, and inspect failures step-by-step with time-travel snapshots — the fastest way to debug a flaky e2e test. It runs on the **host**, outside the container (it needs a real browser and, on Linux, may need `libasound2` and other X dependencies installed before it'll launch). The specs themselves live in `cypress/e2e/*.cy.ts` — currently about ten of them, covering courses, groups, the IDE, navigation, certificates, contests, and the problem creator/collection flows.

### Run Cypress headlessly

```bash
yarn test:e2e
```

The same specs without the GUI: this expands to `cypress run --browser chrome`, running every spec headless and printing results to the terminal. This is what CI uses and what you want for a quick "did I break any e2e flow" pass, since it doesn't wait for you to click anything.

### Run Vue unit tests in watch mode

```bash
yarn run test:watch
```

This runs the Jest (Jest 26 via `ts-jest`) unit tests for the Vue/TypeScript frontend in watch mode — under the hood it's `cross-env TZ=UTC jest --watchAll --notify` scoped to files matching `frontend/www/js/.*test\.ts$`. Watch mode keeps Jest resident and reruns the affected tests every time you save a component or its test, so you get a continuous red/green signal while you work instead of manually re-triggering. The `TZ=UTC` pin matters: it forces a deterministic timezone so date-sensitive tests don't pass on your machine and fail in CI. For a one-shot run use `yarn test`; for coverage use `yarn test:coverage`.

### Run a specific Vue unit test file

```bash
./node_modules/.bin/jest frontend/www/js/omegaup/components/$MY_FILE.test.ts
```

When watch mode is rerunning too much, invoke Jest directly against a single test file. All the Vue single-file components live under `frontend/www/js/omegaup/components/`, so their `.test.ts` neighbors do too. This one is happy to run either inside or outside the container — it's pure Node with no MySQL dependency.

## Building the Frontend

The site is a Twig 3 shell wrapping Vue 2.7 + TypeScript single-file components, bundled by Webpack 5. During development you almost always want a watcher rebuilding bundles as you edit, rather than rebuilding by hand.

```bash
yarn dev:watch
```

This is the everyday loop: it runs Webpack against the `frontend` config in development mode with `--watch`, so every save re-bundles just the frontend entrypoints. Related scripts trade scope for speed — `yarn dev` is the same build once without watching; `yarn dev-all` / `yarn dev-all:watch` build *all* Webpack configs (the frontend, plus the style and secondary bundles) when a change touches more than the app code.

For a shippable bundle, `yarn build` runs Webpack in `--mode=production` (minified, no source maps), while `yarn build-development` produces an unminified development build. And to browse components in isolation:

```bash
yarn storybook
```

This launches Storybook (7.6) on port `6006` via `storybook dev -p 6006`, giving you a sandbox to render and poke at individual Vue components without booting the whole app. Story coverage is currently thin — roughly ten `.stories` files against 250-plus components — so not every component has an entry yet.

!!! note "The web app isn't showing my changes"
    If you edit a `.vue` or `.ts` file and the page looks unchanged, the usual cause is that no watcher is running to rebuild the bundle. Make sure `yarn dev:watch` (or `yarn dev-all:watch`) is running, then hard-reload the page at **http://localhost:8001**. PHP changes, by contrast, are picked up directly from the bind mount with no rebuild.

## Database

### Reset the database to its initial state

```bash
./stuff/bootstrap-environment.py --purge
```

Run this inside the container when your local data has drifted into an unusable state, or when you just want a clean slate to test against. The `--purge` flag drops and re-creates the database from scratch; the script then replays a series of real API requests to populate it, standing up contests, courses, problems, and the test users you need for manual testing. The definition of what gets created lives in `stuff/bootstrap.json`, so if you want extra fixtures, that's the file to edit. Feel free to run it as often as you need — a fresh bootstrap is the fastest way out of "my local DB is broken."

### Apply database migrations locally

```bash
./stuff/db-migrate.py migrate --databases=omegaup,omegaup-test
```

After you add a new `.sql` migration file, this applies the pending schema changes to your local databases. Naming **both** `omegaup` and `omegaup-test` is deliberate and important: the second is the database the PHPUnit suite runs against, so if you migrate only `omegaup` your app will work but `runtests.sh` will fail against a stale test schema (and its own `db-migrate.py validate` step will flag the mismatch). Run it inside the container.

### Regenerate `schema.sql` and the DAOs from your migration

```bash
./stuff/update-dao.sh
```

Migrations describe *changes*; `schema.sql` and the generated DAO/VO classes describe the *current* shape of the database, and they don't update themselves. This script copies `frontend/database/schema.sql` over to `frontend/database/dao_schema.sql` to trigger regeneration, then runs `stuff/update-dao.py` to rewrite the auto-generated DAO base classes and value objects to match your new columns. Run it inside the container after adding a migration — and note the ordering wrinkle: it regenerates against the committed schema, so it does its job once the migration file is in place.

## PHP Type Validation

### Run Psalm across the PHP source

```bash
find frontend/ \
    -name *.php \
    -and -not -wholename 'frontend/server/libs/third_party/*' \
    -and -not -wholename 'frontend/tests/badges/*' \
    -and -not -wholename 'frontend/tests/controllers/*' \
    -and -not -wholename 'frontend/tests/runfiles/*' \
    -and -not -wholename 'frontend/www/preguntas/*' \
  | xargs ./vendor/bin/psalm \
    --long-progress \
    --show-info=false
```

This runs Psalm (the static type checker configured by `psalm.xml`) over the first-party PHP, using `find` to hand it every `.php` file *except* the excluded paths — third-party libraries under `frontend/server/libs/third_party/`, several test-fixture directories, and the legacy `frontend/www/preguntas/` tree — because those either aren't ours to type-check or would drown the run in noise. `--long-progress` gives you a live progress bar for what is a slow, whole-tree pass, and `--show-info=false` suppresses informational notices so only genuine type errors surface. Run it inside the container. If you just want the same check the CI gate runs, `runtests.sh` already invokes `./vendor/bin/psalm --show-info=false` for you.

## Docker

### Start the development environment

```bash
docker compose up --no-build
```

This is how you bring the whole stack up: the `frontend` container (php-fpm behind nginx, serving on **http://localhost:8001**), MySQL 8.0 on port `13306`, Redis, and the prebuilt Go services — `gitserver`, `grader`, `broadcaster`, and `runner` — pulled from the `omegaup/*` images. `--no-build` skips rebuilding the images and just runs what you already have, which is what you want on a normal day; drop it (`docker compose up`) on a first run or after image changes so Compose builds/pulls first. The frontend PHP backend talks to the Go `grader` over HTTP at `OMEGAUP_GRADER_URL` (default `https://localhost:21680`), while the grader hands work to runners internally on port `11302` — those services live in the separate `omegaup/quark` and `omegaup/gitserver` repos, not in this one.

!!! note "`docker compose` vs `docker-compose`"
    Docker Compose V2 is the plugin form `docker compose` (with a space); older setups have the standalone `docker-compose` binary. Either works as long as your install provides one of them; the examples here use the V2 form.

### Restart the Docker service

```bash
systemctl restart docker.service
```

Run this on your **host** (Linux) when Docker itself gets into a bad state — specifically, if `docker exec` starts failing with:

```bash
OCI runtime exec failed: exec failed: unable to start container process: open /dev/pts/0: operation not permitted: unknown
```

That error isn't a problem with omegaUp; it's the Docker daemon's runtime having lost the ability to allocate a pseudo-terminal for your `exec`. Restarting the `docker.service` daemon clears it, after which `docker exec -it omegaup-frontend-1 /bin/bash` works again. (On macOS or Windows the equivalent is restarting Docker Desktop.)

## Quick Reference

Every command, with the side of the container boundary it belongs on:

| Task | Command | Where to run |
|------|---------|--------------|
| Run all linters (autofix) | `./stuff/lint.sh` | Host, project root |
| Check style without fixing | `./stuff/lint.sh validate` | Host, project root |
| Regenerate `.lang` files | `./stuff/lint.sh --linters=i18n fix --all` | Host, project root |
| Full PHP test + validation gate | `./stuff/runtests.sh` | Inside container |
| One PHP test file | `./stuff/run-php-tests.sh frontend/tests/controllers/$MY_FILE.php` | Inside container |
| Cypress GUI | `npx cypress open` | Host |
| Cypress headless | `yarn test:e2e` | Host |
| Vue unit tests (watch) | `yarn run test:watch` | Either side |
| One Vue test file | `./node_modules/.bin/jest frontend/www/js/omegaup/components/$MY_FILE.test.ts` | Either side |
| Frontend build watcher | `yarn dev:watch` | Host |
| Production bundle | `yarn build` | Host |
| Component sandbox | `yarn storybook` (port 6006) | Host |
| Reset & seed the database | `./stuff/bootstrap-environment.py --purge` | Inside container |
| Apply migrations | `./stuff/db-migrate.py migrate --databases=omegaup,omegaup-test` | Inside container |
| Regenerate schema + DAOs | `./stuff/update-dao.sh` | Inside container |
| Open a container shell | `docker exec -it omegaup-frontend-1 /bin/bash` | Host |
| Start the stack | `docker compose up --no-build` | Host |

## Related Documentation

- **[Testing Guide](testing.md)** — the full picture on PHPUnit, Jest, and Cypress
- **[Coding Guidelines](coding-guidelines.md)** — the standards the linters enforce
- **[Development Setup](../getting-started/development-setup.md)** — getting the environment running in the first place
