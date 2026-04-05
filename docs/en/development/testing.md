---
title: Testing Guide
description: Comprehensive testing guide for omegaUp
icon: bootstrap/flask
---

# Testing Guide

omegaUp uses multiple testing frameworks to ensure code quality across different layers.

## Testing Stack

| Layer | Framework | Location |
|-------|-----------|----------|
| PHP Unit Tests | PHPUnit | `frontend/tests/controllers/` |
| TypeScript/Vue Tests | Jest | `frontend/www/js/` |
| E2E Tests | Cypress | `cypress/e2e/` |
| Python Tests | pytest | `stuff/` |

## PHP Unit Tests

### Running All PHP Tests

```bash
./stuff/runtests.sh
```

Runs PHPUnit tests, MySQL type validation, and Psalm.

**Location**: Inside Docker container

### Running Specific Test File

```bash
./stuff/run-php-tests.sh frontend/tests/controllers/MyControllerTest.php
```

Omit filename to run all tests.

### Test Requirements

- All tests must pass 100% before committing
- New functionality requires new/modified tests
- Tests located in `frontend/tests/controllers/`

## TypeScript/Vue Tests

### Running Vue Tests (Watch Mode)

```bash
yarn run test:watch
```

Automatically reruns tests when code changes.

**Location**: Inside Docker container

### Running Specific Test File

```bash
./node_modules/.bin/jest frontend/www/js/omegaup/components/MyComponent.test.ts
```

### Test Structure

Vue component tests check:
- Component visibility
- Event emission
- Expected behavior
- Props and state

## Cypress E2E Tests

End-to-end tests live under [`cypress/`](https://github.com/omegaup/omegaup/tree/main/cypress) at the repository root. **Cypress is normally run on your host** (not inside the omegaUp Docker frontend container), so you need Node, Yarn dependencies, and on Linux several system libraries for the Electron-based runner.

The pinned version is in the root [`package.json`](https://github.com/omegaup/omegaup/blob/main/package.json) (`cypress` field). After pulling upgrades, run `yarn install` and, if the binary is missing:

```bash
./node_modules/.bin/cypress install
```

### Install and open Cypress

```bash
npx cypress open
# or
./node_modules/.bin/cypress open
```

Headless run (same as CI driver in many workflows):

```bash
npx cypress run
# or
yarn test:e2e
```

`yarn test:e2e` runs `cypress run --browser chrome` (see `package.json` scripts).

### Linux system dependencies (Ubuntu / Debian)

Cypress fails fast if shared libraries are missing. Official list: [required dependencies](https://on.cypress.io/required-dependencies).

Typical fixes on Ubuntu:

```bash
sudo apt update
sudo apt install -y libatk1.0-0 libatk-bridge2.0-0 libgdk-pixbuf2.0-0 libgtk-3-0 libgbm-dev libnss3 libxss-dev
```

**`libnss3.so` / NSS errors** — install `libnss3` (package name may be `libnss3` or `libnss3-dev` depending on release).

**`libasound.so.2` errors**:

```bash
sudo apt-get install libasound2
```

On **Ubuntu 24.04+** the package may be named:

```bash
sudo apt install libasound2t64
```

If errors persist, run `sudo apt update` and retry; compare your Cypress version with the error output path under `~/.cache/Cypress/<version>/`.

### Layout and writing tests

- Specs: `cypress/e2e/`, naming pattern `*.cy.ts` (subfolders allowed).
- Custom commands: `cypress/support/commands.js` (and types in `cypress/support/cypress.d.ts`).
- Global hooks / `uncaught:exception` handlers: `cypress/support/e2e.ts`.
- [Cypress custom commands](https://docs.cypress.io/api/cypress-api/custom-commands) and [events](https://docs.cypress.io/api/events/catalog-of-events) — use these when sharing login flows or ignoring known third-party errors (for example OAuth iframes in local dev).
- **Cypress Studio** (in the Cypress app) can record interactions into a spec; see [Cypress Studio](https://docs.cypress.io/guides/core-concepts/cypress-studio).

Plugins used in this repo include **cypress-wait-until** and **cypress-file-upload** (see `package.json`).

### Debugging CI failures

When tests pass locally but fail in GitHub Actions, open the PR **Checks** tab → **CI**, then download artifacts named like `cypress-screenshots-<attempt>` and `cypress-videos-<attempt>` (the attempt number appears in the workflow run URL, e.g. `/attempts/3`).

## Python Tests

Python tests use pytest and are located in `stuff/` directory.

## Test Coverage

We use **Codecov** to measure coverage:

- **PHP**: Coverage measured ✅
- **TypeScript**: Coverage measured ✅
- **Cypress**: Coverage not yet measured ⚠️

## Best Practices

### Write Tests First
When possible, write tests before implementation (TDD).

### Test Critical Paths
Focus on:
- User authentication flows
- Problem submission and evaluation
- Contest management
- API endpoints

### Keep Tests Fast
- Unit tests should be fast (< 1 second)
- E2E tests can be slower but should complete in reasonable time

### Test Isolation
- Each test should be independent
- Clean up test data after tests
- Use test fixtures for consistent data

## Related Documentation

- **[Coding Guidelines](coding-guidelines.md)** — Code standards
- **[Useful Commands](useful-commands.md)** — Testing commands
- **[Development setup](../getting-started/development-setup.md)** — Node, Yarn, and Docker layout before running Cypress
