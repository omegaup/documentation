---
title: Testing Guide
description: Comprehensive testing guide for omegaUp
icon: bootstrap/flask
---

# Testing Guide

omegaUp is tested at three layers, and each one lives somewhere different for a
reason. The PHP controllers and API are covered by **PHPUnit 9** tests that run
_inside_ the Docker `frontend` container (they need a real MySQL 8.0, a real
gitserver, and the whole `\OmegaUp\` autoload chain). The Vue 2.7 components and
the TypeScript under `frontend/www/js` are covered by **Jest 26** unit tests,
which also run inside the container but only need jsdom. And the full
click-through user journeys — register, log in, create a contest, submit a run —
are covered by **Cypress 15.7** end-to-end tests that run _on your host_,
driving a real Chrome against the container over `http://127.0.0.1:8001`.

The rule we hold everyone to: tests must be green before you open a pull
request, and any new behavior ships with a test that exercises it. CI will run
all three suites again on your PR, so a suite that only passes on your machine
is not passing.

| Layer | Framework | Where it lives | Where it runs |
|-------|-----------|----------------|---------------|
| PHP controllers + API | PHPUnit 9 | `frontend/tests/controllers/`, `frontend/tests/badges/` | Inside the `frontend` container |
| TypeScript / Vue units | Jest 26 (jsdom) | `frontend/www/js/**/*.test.ts` | Inside the `frontend` container |
| End-to-end journeys | Cypress 15.7 | `cypress/e2e/*.cy.ts` | On your host, against `127.0.0.1:8001` |

## PHP unit tests (PHPUnit)

### The one command: `./stuff/runtests.sh`

The script we actually run before pushing is
[`stuff/runtests.sh`](https://github.com/omegaup/omegaup/blob/main/stuff/runtests.sh),
and it is deliberately more than "just PHPUnit." It first decides whether it is
inside Docker by checking whether the repo root is `/opt/omegaup` (that is where
the container mounts the source); if so it runs directly, otherwise it shells
into the container with `docker compose exec -T frontend`. From there it, in
order:

1. Validates the schema migrations with `stuff/db-migrate.py validate` and the
   authorization policies with `stuff/policy-tool.py validate`, because a test
   run against a stale schema or policy tells you nothing useful.
2. Runs [`stuff/mysql_types.sh`](https://github.com/omegaup/omegaup/blob/main/stuff/mysql_types.sh),
   which is the interesting part — see below.
3. Runs Psalm across the whole tree with `vendor/bin/psalm --show-info=false`
   (we suppress info-level noise so only real type errors fail the run).
4. Verifies the pinned GitHub Action hashes are consistent via
   `hack/gha-reversemap.sh verify-mapusage`, but only if `yq` and `jq` are
   installed — otherwise it prints a skip notice rather than failing.

When you run it inside the container it finishes by reminding you to run
`./stuff/lint.sh` and the Python UI tests (`python3 -m pytest ./frontend/tests/ui/ -s`)
_outside_ the container, because those need tools the container doesn't carry.

### Why `mysql_types.sh` exists (the clever bit)

`mysql_types.sh` doesn't just run the PHPUnit suite — it runs it with MySQL's
**general query log** turned on (`SET GLOBAL general_log = 'ON'` writing to a
`TABLE`), captures every query the tests actually issued, and then feeds them to
`stuff/process_mysql_return_types.py`. The point is to verify that the
`@psalm-type` annotations we hand-write on the DAO layer match what MySQL
_really_ returns for those columns. If you add a query whose result shape
doesn't match its declared Psalm type, this is the step that catches it — long
before it becomes a runtime surprise in a controller. It also runs
`process_mysql_explain_logs.py` to sanity-check the query plans. So "the type
check" the older docs mention is not a static guess; it is grounded in the
queries your tests genuinely ran.

### Running the suite (or one test)

Under the hood, [`stuff/run-php-tests.sh`](https://github.com/omegaup/omegaup/blob/main/stuff/run-php-tests.sh)
is what actually invokes PHPUnit. With no arguments it runs everything under
`frontend/tests/`; with arguments it passes them straight through to `phpunit`,
so you get PHPUnit's filtering for free. To iterate on a single controller test:

```bash
# From inside the container (or via docker compose exec -T frontend ...)
./stuff/run-php-tests.sh frontend/tests/controllers/UserRankTest.php \
    --filter testUserRankingClassName
```

It always wires up the same three things: `--bootstrap frontend/tests/bootstrap.php`,
`--configuration frontend/tests/phpunit.xml`, and
`--coverage-clover coverage.xml` (that Clover file is what Codecov later reads).

The suites themselves are declared in
[`frontend/tests/phpunit.xml`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/phpunit.xml):
a **Controllers** suite over `frontend/tests/controllers/` (currently ~129 test
files — this is the bulk of the coverage) and a **Badges** suite over
`frontend/tests/badges/`. Coverage is measured over `../server/` but deliberately
excludes generated code (`server/libs/dao/base/`), the config, the `cmd/`
scripts, and the Psalm plugin sources, because measuring auto-generated files
would only dilute the number.

!!! note "Tests need a gitserver, and the listener provides it"
    `phpunit.xml` registers `\OmegaUp\Test\GitServerTestSuiteListener`
    ([`GitServerTestSuiteListener.php`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/GitServerTestSuiteListener.php)).
    Problem-creation and submission tests need a real git backend for problem
    storage, so the listener stands one up for the test run. This is why you
    can't meaningfully run these tests outside the container — the moving parts
    they touch (MySQL 8.0, gitserver) are container services, not mocks.

Helpers you'll lean on when writing new tests live alongside the suites:
`frontend/tests/Utils.php`, the `frontend/tests/Factories/` directory for
building users/contests/problems, and `ControllerTestCase.php` /
`BadgesTestCase.php` as base classes. There's also an `ApiCallerMock.php` for
driving the API layer without going over HTTP.

## TypeScript / Vue unit tests (Jest)

The Jest suite covers the ~180 `*.test.ts` files under `frontend/www/js`,
ranging from pure logic (`omegaup.test.ts`, `markdown.test.ts`, `csv.test.ts`)
to Vue single-file components mounted with `@vue/test-utils`. The npm scripts in
[`package.json`](https://github.com/omegaup/omegaup/blob/main/package.json) all
force `TZ=UTC` via `cross-env`, because otherwise date-formatting assertions
pass on a machine in one timezone and fail in CI — pinning UTC keeps everyone's
results identical:

```bash
yarn test            # cross-env TZ=UTC jest 'frontend/www/js/.*test\.ts$'
yarn test:watch      # same, but --watchAll --notify — reruns on save
yarn test:coverage   # same, with --coverage=true
```

To run a single file while iterating, skip the wrapper and hit the binary
directly:

```bash
./node_modules/.bin/jest frontend/www/js/omegaup/components/RadioSwitch.test.ts
```

Component tests read like this — mount the SFC with props, then assert on
rendered text or emitted events. Note the convention of importing translations
(`T`) rather than hard-coding UI strings, so a test survives a copy change:

```typescript
import { shallowMount } from '@vue/test-utils';
import T from '../lang';
import omegaup_RadioSwitch from './RadioSwitch.vue';

describe('RadioSwitch.vue', () => {
  it('Should render a simple radio switch with default descriptions', () => {
    const wrapper = shallowMount(omegaup_RadioSwitch, {
      propsData: { selectedValue: true },
    });
    expect(wrapper.text()).toContain(T.wordsYes);
    expect(wrapper.text()).toContain(T.wordsNo);
  });
});
```

Prefer `shallowMount` over `mount` unless you specifically need child components
to render — it stubs the children, which keeps the test fast and stops an
unrelated child's bug from failing your test. The Jest config
([`jest.config.js`](https://github.com/omegaup/omegaup/blob/main/jest.config.js))
does the plumbing you'd otherwise trip over: `testEnvironment: 'jsdom'`, a
`testURL` of `http://localhost:8001/` so code that reads `window.location`
behaves, `vue-jest` for `.vue` files, and `moduleNameMapper` entries that mock
out the heavy or browser-only dependencies — `monaco-editor`, CSS/LESS imports,
and `sugar` all resolve to stubs under
`frontend/www/js/omegaup/__mocks__/`, and `@/` maps to `frontend/www/`. Shared
setup runs from `frontend/www/js/omegaup/test.setup.ts` via
`setupFilesAfterEnv`.

## Cypress end-to-end tests

The 10 specs under
[`cypress/e2e/`](https://github.com/omegaup/omegaup/tree/main/cypress/e2e) —
`basic_commands`, `certificate`, `contest`, `course`, `course_2Part`, `group`,
`ide`, `navigation`, `problem_collection`, and `problem_creator`, all named
`*.cy.ts` — drive a real browser through the whole product. Unlike PHPUnit and
Jest, **Cypress runs on your host, not inside the Docker container.** The
container serves the app at `http://127.0.0.1:8001`, and Cypress
(`baseUrl` in [`cypress.config.ts`](https://github.com/omegaup/omegaup/blob/main/cypress.config.ts))
points Chrome at that address. So you need Node, your Yarn dependencies
installed, and — on Linux — several system libraries that the Electron/Chrome
runner links against.

### Getting Cypress installed

After a `yarn install`, if the browser binary itself is missing you'll see
something like:

```text
No version of Cypress is installed in: ~/.cache/Cypress/15.7.0/Cypress

Please reinstall Cypress by running: cypress install
```

That is not a dependency problem — the npm package is there, but the actual
Cypress binary that lives under `~/.cache/Cypress/<version>/` didn't download.
Fix it with:

```bash
./node_modules/.bin/cypress install
```

The pinned version is `cypress` in `package.json` (currently **15.7.0**); the
path in any error message tells you which version's binary Cypress is looking
for, which is the fastest way to spot a version/cache mismatch after an upgrade.

### Linux system libraries

Cypress fails fast — before running a single test — if a shared library it
needs is missing, and the error names the exact `.so`. Two show up constantly.
If you see:

```text
~/.cache/Cypress/15.7.0/Cypress/Cypress: error while loading shared libraries:
libnss3.so: cannot open shared object file: No such file or directory
```

that's the NSS crypto library. And:

```text
error while loading shared libraries: libasound.so.2: cannot open shared object
file: No such file or directory
```

is ALSA (audio). Install the whole set Cypress documents as
[required dependencies](https://on.cypress.io/required-dependencies):

```bash
sudo apt update
sudo apt install -y libgtk-3-0 libgbm-dev libnss3 libatk1.0-0 \
    libatk-bridge2.0-0 libgdk-pixbuf2.0-0 libxss-dev libasound2
```

On **Ubuntu 24.04+** ALSA was renamed for the 64-bit time_t transition, so
`libasound2` won't be found — install `libasound2t64` instead. If a library
error persists after installing, run `sudo apt update` and retry; a stale
package index is the usual culprit.

### Running the tests

The GUI is the pleasant way to develop a spec — it shows every command as it
runs and lets you hover any step to see a DOM snapshot of the page at that exact
moment, plus a selector tool that writes the `cy.get(...)` for whatever element
you click:

```bash
npx cypress open
# or
./node_modules/.bin/cypress open
```

Headless is what CI does, and what `yarn test:e2e` maps to:

```bash
yarn test:e2e        # cypress run --browser chrome
```

We pin `--browser chrome` on purpose rather than letting it default to the
bundled Electron, so local runs match CI. A run records a video into
`cypress/videos/` and, on failure, a screenshot into `cypress/screenshots/`, so
you can watch what the test saw even for a headless failure.

A couple of settings in `cypress.config.ts` are worth knowing because they
change how tests behave: `chromeWebSecurity: false` (so cross-origin things like
OAuth iframes don't get blocked in local dev), `experimentalStudio: true`
(enables Studio, below), and `experimentalMemoryManagement: true` with
`numTestsKeptInMemory: 0` — we keep zero prior tests in memory because these
journeys are long and Chrome would otherwise balloon and crash mid-run.

### Custom commands

The single most useful Cypress feature here is **custom commands**: a reusable
Cypress function so you don't rewrite login (or contest creation, or problem
creation) in every spec. They're declared in
[`cypress/support/commands.ts`](https://github.com/omegaup/omegaup/blob/main/cypress/support/commands.ts).
`login` logs a user in by POSTing to the API directly instead of driving the
form, which is faster and less flaky:

```typescript
Cypress.Commands.add('login', ({ username, password }: LoginOptions) => {
  cy.request({
    method: 'POST',
    url: '/api/user/login/',
    form: true,
    body: { usernameOrEmail: username, password },
  }).then((response) => {
    expect(response.status).to.equal(200);
    cy.reload();
  });
});
```

There's a sibling `loginAdmin` that hard-codes the seeded admin account
(`omegaup` / `omegaup`), plus `register`, `logout`, `logoutUsingApi`,
`createProblem`, `createCourse`, `createRun`, `createContest`,
`addProblemsToContest`, `createGroup`, and more — the full contest/course setup
vocabulary, so a spec reads like a story instead of a wall of clicks.

Because we're on TypeScript, adding a command is two steps, and skipping the
second is the classic mistake: **declare its type**, or TypeScript won't know
`cy.myCommand()` exists. The `Chainable` interface lives in
[`cypress/support/cypress.d.ts`](https://github.com/omegaup/omegaup/blob/main/cypress/support/cypress.d.ts),
and the option types (`LoginOptions`, `CourseOptions`, `ProblemOptions`, …) in
`cypress/support/types.d.ts`:

```typescript
declare global {
  namespace Cypress {
    interface Chainable {
      login(loginOptions: LoginOptions): void;
      loginAdmin(): void;
      register(loginOptions: LoginOptions): void;
      createProblem(problemOptions: ProblemOptions): void;
      // ...add your new command's signature here
    }
  }
}
```

### Events: don't let a third-party exception kill the run

Sometimes you want a test to keep going even when an uncaught exception fires
from code you don't control. The concrete case that forced this: when running
Cypress, Google Sign-In's API refused to recognize `127.0.0.1` (the Docker IP)
as a permitted host and threw `idpiframe_initialization_failed`, which by default
aborts the whole test. The fix is a global `uncaught:exception` handler in
[`cypress/support/e2e.ts`](https://github.com/omegaup/omegaup/blob/main/cypress/support/e2e.ts)
that returns `false` for exactly those known-harmless errors so the test
continues:

```typescript
import './commands';

Cypress.on('uncaught:exception', (err, runnable) => {
  if (
    (err as any).message?.includes('idpiframe_initialization_failed') ||
    (err as any).error?.includes('idpiframe_initialization_failed') ||
    (err as any).message?.includes(
      'ResizeObserver loop completed with undelivered notifications',
    )
  ) {
    // Google API sign-in error, and a benign ResizeObserver warning
    return false;
  }
});
```

Note it also swallows the `ResizeObserver loop completed with undelivered
notifications` warning — a benign browser noise that would otherwise flake your
tests. Put handlers you only want for one spec inside that spec file rather than
here; `e2e.ts` is global and applies to every test.

### Cypress Studio and the plugins

Because `experimentalStudio` is on, opening a spec in the GUI gives you a button
to **record** your interactions straight into the spec as commands — click
through the flow and Studio writes the `cy.*` calls for you, either extending an
existing test or scaffolding a brand-new one. One nice property: Studio does
_not_ record the time between actions, so you don't have to rush; take as long
as you like between clicks.

Two plugins are wired in and imported at the top of `commands.ts`:
**cypress-wait-until** (`cy.waitUntil(...)`, for polling until a condition holds
— used e.g. in `logout` to wait for the URL to settle) and
**cypress-file-upload** (for `.attachFile(...)` on the problem-upload flows).
The `setupNodeEvents` hook in `cypress.config.ts` loads
`cypress/plugins/index.js`, which registers a `log` task so a test can print to
the terminal running Cypress.

### When it passes locally but fails in CI

CI runs the specs sharded across a matrix (see the `cypress` job in
[`.github/workflows/ci.yml`](https://github.com/omegaup/omegaup/blob/main/.github/workflows/ci.yml)),
each shard running `./node_modules/.bin/cypress run --browser chrome --spec '<specs>'`.
When a test is green on your machine but red on the PR, don't guess — watch what
the CI browser saw. Open the PR's **Checks** tab, select the failing **cypress**
job, and download the run's artifacts:

- `cypress-videos-shard-<shard>-<run_attempt>` — the video of the actual run.
- `cypress-screenshots-shard-<shard>-<run_attempt>` — screenshots at the moment
  of failure.
- `frontend-test-logs-<run_attempt>` — container-side logs, when the failure is
  really the backend misbehaving rather than the test.

The `<run_attempt>` suffix is the attempt number from the workflow run (visible
in the run URL, e.g. `/attempts/3`), so if you re-ran a flaky job make sure you
grab the artifacts from the attempt that actually failed.

## Python UI tests

There's a smaller Selenium-style UI suite under `frontend/tests/ui/` run with
`python3 -m pytest ./frontend/tests/ui/ -s`. As `runtests.sh` reminds you, it
runs **outside** the container, which is why it isn't part of the in-container
PHPUnit flow.

## Test coverage

We push coverage to **Codecov**. PHP coverage comes from the Clover report
(`coverage.xml`) that `run-php-tests.sh` emits, and TypeScript coverage from
`yarn test:coverage`. Cypress runs are **not** wired into coverage yet — they
prove the journeys work end to end, but they don't count toward the coverage
number, so don't rely on an e2e test to "cover" a unit of logic that a Jest or
PHPUnit test should own.

## A few habits worth keeping

Keep unit tests genuinely fast and genuinely isolated — each PHPUnit test builds
its own fixtures through the `Factories/` helpers and each Jest test mounts its
own component, so tests never depend on each other's leftover state or on
execution order. Reach for the layer that matches what you're testing: pure
functions and single components belong in Jest, controller/permission/API
behavior belongs in PHPUnit against a real MySQL, and only the full
cross-page user journey earns a Cypress spec (they're the slowest and the
flakiest, so spend them deliberately). And when you touch behavior, write or
update the test in the same change — a PR that changes what the code does but
not what the tests assert is the one reviewers will send back.

## Related documentation

- **[Coding Guidelines](coding-guidelines.md)** — the standards the linters and Psalm enforce
- **[Useful Commands](useful-commands.md)** — the day-to-day command cheat sheet
- **[Development setup](../getting-started/development-setup.md)** — get Node, Yarn, and Docker in place before running any of this
