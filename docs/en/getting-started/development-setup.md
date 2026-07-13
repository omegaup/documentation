---
title: Development Environment Setup
description: Complete guide to setting up your local omegaUp development environment
icon: bootstrap/tools
---

# Development Environment Setup

This page walks you through standing up a full local omegaUp — frontend, PHP API, MySQL, and the Go grader/runner/gitserver — on your own machine with Docker. The whole stack lives in a handful of containers described by `docker-compose.yml`, so you don't install PHP 8.1, MySQL 8.0, Redis, or RabbitMQ by hand; you pull prebuilt images and bring them up. We prefer Docker for everyone now — the old Vagrant/VirtualBox VM provisioned from [omegaup/deploy](https://github.com/omegaup/deploy) is deprecated and no longer the supported path, so if you find a wiki page telling you to `vagrant up`, skip it.

!!! tip "Video Tutorial"
    If you'd rather watch than read, we keep a [video tutorial](http://www.youtube.com/watch?v=H1PG4Dvje88) that walks through the same setup end to end.

## Prerequisites

Before anything else, install the two pieces of Docker tooling and Git:

- **Docker Engine** — [install it](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository). This is what actually runs the containers.
- **Docker Compose v2** — [install the plugin](https://docs.docker.com/compose/install/linux/#install-the-plugin-manually). Compose is what reads `docker-compose.yml` and brings the whole stack up together. If you're still on Compose v1, you can [migrate to v2](https://docs.docker.com/compose/install/linux/#install-using-the-repository); both the `docker compose` (space) and `docker-compose` (hyphen) spellings work, and this guide uses them interchangeably.
- **Git** — for cloning the repository, and because the whole contribution workflow is built on it.

!!! warning "New to Git?"
    If you're not confident with Git yet, read [this Git tutorial](https://github.com/shekhargulati/git-the-missing-tutorial) before you start. Everything after the clone — branches, pull requests, keeping `main` in sync — assumes you can move around in Git comfortably.

### Linux: add yourself to the `docker` group

On Linux, run this once so you can invoke `docker` without `sudo`:

```bash
sudo usermod -a -G docker $USER
```

Then **log out and log back in** for the new group membership to take effect. This matters more than it looks: if you skip it and start reaching for `sudo docker compose up` instead, the bind-mounted project tree ends up owned by `root`, and the container's non-root user can no longer write to it — which surfaces later as a baffling restart loop (see [My Dev Environment Won't Come Up](#my-dev-environment-wont-come-up)). Do it the right way once and you avoid the whole class of problem.

!!! note "Windows: develop inside WSL2"
    On Windows, run everything through [WSL2](https://docs.docker.com/desktop/features/wsl) with Docker Desktop's WSL integration enabled, and — this is the load-bearing part — **clone the repo into the Linux filesystem** (somewhere under your WSL home, e.g. `~/omegaup`), *not* under `/mnt/c/...`. Docker bind mounts that cross the Windows↔Linux boundary are slow, and worse, `webpack --watch` inside the container silently misses file-change events on `/mnt/c`, so your edits never trigger a rebuild and you're left staring at stale output. Keeping the checkout on the Linux side is the modern replacement for the old WinSCP/Xming file-sync dance from the Vagrant era.

## Step 1: Fork and Clone

Fork [omegaup/omegaup](https://github.com/omegaup/omegaup) on GitHub first — you push to your fork, not to the main repo — then clone your fork into an empty directory. The `--recurse-submodules` flag matters: several third-party frontend dependencies (`pagedown` for the Markdown editor, `iso-3166-2.js` for country codes, `mathjax` for math rendering, and more) live in Git submodules, and the build breaks without them.

```bash
git clone --recurse-submodules https://github.com/YOURUSERNAME/omegaup
cd omegaup
```

If you cloned without `--recurse-submodules`, or a submodule looks empty, pull them in explicitly from the repo root:

```bash
git submodule update --init --recursive
```

## Step 2: Bring Up the Containers

From the repository root (`omegaup/`), pull the images and start the stack:

```bash
docker-compose pull       # only needed the first time, or when the next command complains
docker-compose up --no-build
```

The `pull` grabs the prebuilt images Compose needs — the PHP/nginx frontend, MySQL 8.0, Redis, RabbitMQ, and the separate Go services (`omegaup/backend`, `omegaup/runner`, `omegaup/gitserver`) that provide the grader, runner, and problem storage. You only need to re-pull when you first set up or when `docker-compose up` complains that an image is missing or stale. The `--no-build` flag tells Compose to run those prebuilt images as-is instead of rebuilding them from scratch, which is what keeps startup down to minutes instead of a very long coffee break.

**The first boot takes 2–10 minutes.** Behind that wait, the frontend container is running Webpack to compile the entire Vue 2.7 + TypeScript frontend, MySQL is initializing, and the grader is waiting on the database (`wait-for-it mysql:13306`). What signals that it's actually ready is a Webpack module dump that looks similar to this:

```
frontend_1     | Child frontend:
frontend_1     |        1550 modules
frontend_1     |     Child HtmlWebpackCompiler:
frontend_1     |            1 module
frontend_1     | Child style:
frontend_1     |        1 module
frontend_1     |     Child extract-text-webpack-plugin node_modules/extract-text-webpack-plugin/dist node_modules/css-loader/dist/cjs.js!node_modules/sass-loader/dist/cjs.js!frontend/www/sass/main.scss:
frontend_1     |            2 modules
frontend_1     | Child grader:
frontend_1     |        1131 modules
frontend_1     |     Child vs/editor/editor:
frontend_1     |            36 modules
frontend_1     |     Child vs/language/typescript/tsWorker:
frontend_1     |            41 modules
```

Once you see that, the frontend has finished its build and the site is up. The exact module counts drift as the frontend grows — treat them as a "we're done compiling" signal, not a checksum.

On later runs you can skip the `pull` and just start the stack:

```bash
docker compose up --no-build
```

## Step 3: Open Your Local Instance

With the containers running, your local omegaUp is at:

**[http://localhost:8001](http://localhost:8001)**

That's port `8001`, published from the frontend container in `docker-compose.yml`. Note it's plain `http` — see [the browser HTTPS-redirect fix](#my-browser-keeps-forcing-https) if your browser insists on rewriting it.

## Step 4: Get a Shell Inside the Container

Almost every dev command — running tests, invoking `stuff/` scripts, poking at the database — runs *inside* the frontend container, because that's where PHP 8.1, Node, Yarn, and the tooling actually live. Open a shell with either of these (they're equivalent):

```bash
docker compose exec frontend /bin/bash
# or, by container name:
docker exec -it omegaup-frontend-1 /bin/bash
```

The exact container name depends on your Compose version — v2 names it `omegaup-frontend-1` (hyphens), older `docker-compose` used `omegaup_frontend_1` (underscores). If you're unsure which you've got, `docker compose ps` lists the real names. Inside the container, the codebase is bind-mounted at **`/opt/omegaup`** — the very same files you edit on your host, so a save on your machine is instantly visible in the container.

## Development Accounts

Your fresh install ships with two accounts already seeded, so you can log in immediately without registering anything:

- **`omegaup`** / password **`omegaup`** — a user with sysadmin privileges. Use this when you need to touch admin-only UI.
- **`user`** / password **`user`** — a plain regular user, for testing the normal-user experience.

On top of those, the test suite seeds a stable roster of accounts you can log in as. The password is always identical to the username, which makes them trivial to remember:

| Username | Password |
| -- | -- |
| `test_user_0` | `test_user_0` |
| `test_user_1` | `test_user_1` |
| `test_user_2` | `test_user_2` |
| `test_user_3` | `test_user_3` |
| `test_user_4` | `test_user_4` |
| `test_user_5` | `test_user_5` |
| `test_user_6` | `test_user_6` |
| `test_user_7` | `test_user_7` |
| `test_user_8` | `test_user_8` |
| `test_user_9` | `test_user_9` |
| `course_test_user_0` | `course_test_user_0` |
| `course_test_user_1` | `course_test_user_1` |
| `course_test_user_2` | `course_test_user_2` |

**Feel free to create as many users as you need** to test your changes. In development mode email verification is disabled, so any dummy address works — you never have to check an inbox to activate an account.

## Codebase Structure

omegaUp code lives at `/opt/omegaup` inside the container (and in your clone on the host — it's the same bind-mounted tree). These are the directories we actively work in day to day:

- **[`frontend/server/src/Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers)** — the controllers, namespaced `\OmegaUp\Controllers`, which hold the business logic and expose the server API. Each `apiXxx` static method is one API endpoint; for example `\OmegaUp\Controllers\Run::apiCreate` (in [`Run.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Run.php)) is what handles a submission. Note the class is `Run`, not `RunController` — omegaUp controllers drop the `Controller` suffix.
- **[`frontend/server/src/DAO/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/DAO)** — the data-access layer. It's split on purpose: auto-generated abstract base classes under `DAO/Base/` carry the raw SQL, plain Value Objects under `DAO/VO/` mirror the database rows, and hand-written wrappers directly under `DAO/` add the queries controllers actually call. You edit the wrappers and the VOs, not the generated bases.
- **[`frontend/server/src/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src)** — the rest of the server libraries and utilities, including `ApiCaller.php` (the request dispatcher) and `Grader.php` (the thin HTTP client that talks to the Go grader).
- **[`frontend/templates/`](https://github.com/omegaup/omegaup/tree/main/frontend/templates)** — the server-rendered HTML shell plus the internationalization files for English, Spanish, and Portuguese. There is a single template here, `template.tpl`, and despite the `.tpl` extension it's **Twig 3**, not Smarty — Smarty is gone. Its custom tags (`{% entrypoint %}`, `{% jsInclude %}`) are implemented by our own Twig extensions in `frontend/server/src/Template/`, and all they do is bootstrap a Vue app and hand it a JSON payload.
- **[`frontend/www/`](https://github.com/omegaup/omegaup/tree/main/frontend/www)** — the entire browser-facing app. Every page's UI is a Vue 2.7 single-file component; the components live under `frontend/www/js/omegaup/components/`, and the typed API client (`api.ts`, `api_types.ts`) is generated from the PHP controllers by `frontend/server/cmd/APITool.php` — don't hand-edit those two, regenerate them.

One thing that trips people up: the **grader, runner, broadcaster, and minijail sandbox are not in this repository**. They're separate Go services in [github.com/omegaup/quark](https://github.com/omegaup/quark) (and problem storage lives in [github.com/omegaup/gitserver](https://github.com/omegaup/gitserver)). Docker runs them as prebuilt binaries, and the PHP backend only *talks* to the grader over HTTP through `\OmegaUp\Grader`, at `OMEGAUP_GRADER_URL` (default `https://localhost:21680`). If you're chasing a grading bug, that's the repo to point your editor at — not this one.

For a deeper tour, see the [Architecture Overview](../architecture/index.md) and the [Frontend architecture](../architecture/frontend.md). The branch-and-pull-request workflow lives in [Contributing](contributing.md).

## Editing with Visual Studio Code

You can edit on your host with [Visual Studio Code](https://code.visualstudio.com/) while the stack keeps running in Docker. Because your clone is bind-mounted into `/opt/omegaup`, a save on the host is a save in the container — hot reload and Webpack inside the container pick it up with no copy step, which is exactly the friction the old Vagrant-plus-WinSCP setup existed to work around and no longer needs to.

Two ways to work, depending on how much you want VS Code's own tooling (PHP IntelliSense, the integrated terminal, extensions) running against the container's filesystem:

1. **Edit on the host, run in Docker.** Just open your clone as a folder and edit normally. Simplest path; your saves flow into the container through the bind mount.
2. **Attach VS Code to the running container.** Install the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension (or the [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) extension). With the stack up (`docker compose up --no-build`), open the Command Palette and pick **Attach to Running Container**, choose the frontend container (named like `omegaup-frontend-1`; confirm with `docker compose ps`), then **File → Open Folder** on **`/opt/omegaup`**. Now VS Code's terminal and language servers run *inside* the container, against the same PHP 8.1 and Node the app uses.

Add the PHP, Vue, and ESLint extensions as the files you touch require them.

## GitHub OAuth (local "Sign in with GitHub")

To make the **Sign in with GitHub** button work on **`http://localhost:8001/`**, you register an OAuth app with GitHub and hand its credentials to your local config.

### 1. Create the OAuth App on GitHub

Open [GitHub Developer Settings](https://github.com/settings/developers), go to **OAuth Apps → New OAuth App**, and set:

- **Application name**: anything, e.g. `omegaUp local`
- **Homepage URL**: `http://localhost:8001/`
- **Authorization callback URL**: `http://localhost:8001/login?third_party_login=github`

Register it, copy the **Client ID**, then generate and copy the **Client Secret** — GitHub only shows the secret once, so grab it now.

### 2. Configure omegaUp locally

Put the credentials in **`frontend/server/config.php`**, the local-overrides file (create it if it doesn't exist). This file is for *your* machine only — never commit it, and never put secrets in the version-controlled `config.default.php`.

```php
<?php
define('OMEGAUP_GITHUB_CLIENT_ID', 'your_real_client_id_here');
define('OMEGAUP_GITHUB_CLIENT_SECRET', 'your_real_client_secret_here');
```

A full Compose restart usually isn't needed for a new PHP `define` to take effect, but if the button stays greyed out, restart the frontend container once.

!!! failure "Never commit OAuth secrets"
    Revert or exclude `config.php` before pushing, and keep your Client ID/Secret in a password manager — if the container is recreated and takes `config.php` with it, you'll want them handy. If the login button stays inactive, the Client ID is missing or wrong in `config.php`; if you change host or port, update the callback URL on the GitHub OAuth app to match, or the redirect will fail.

See [Security → OAuth](../architecture/security.md#oauth-integration) for how third-party login fits into the platform.

## Troubleshooting

Here are the problems people actually hit, in roughly the order they hit them — the raw error first, then what it means, then the fix.

### The Web App Is Not Showing My Changes!

You edited a `.vue` or `.ts` file, saved, reloaded — and the browser shows the old thing. The frontend is served from a Webpack *build*, so an unbuilt edit is invisible no matter how many times you refresh. Rebuild it from inside the container:

```bash
docker compose exec frontend /bin/bash
cd /opt/omegaup && yarn run dev
```

`yarn run dev` runs Webpack once over the frontend; if you're iterating and don't want to re-run it by hand after every save, use `yarn dev:watch` instead, which watches the tree and rebuilds on change. (On Windows this is exactly why your checkout must live in the WSL2 Linux filesystem and not under `/mnt/c` — the watcher misses change events across that boundary.) If it's still not updating after a successful build, make sure the containers are actually running (`docker compose up --no-build`) and, failing that, ask in our [communication channels](getting-help.md).

### My Dev Environment Won't Come Up :(

**Symptoms**: the logs show `Permission denied` while creating `phpminiadmin` or writing under `stuff/venv/`, the `developer-environment` container exits and restarts on a loop, and the site never serves on `http://localhost:8001`.

**Cause**: the repo was cloned as **root**, or `docker compose` was run with `sudo`, so the project directory is owned by `root`. The bind mount maps your host directory onto `/opt/omegaup`, and a root-owned tree blocks the container's non-root user from writing to it — so it fails, dies, and Compose restarts it forever.

**Fix**: don't try to "repair" the root-owned tree in place; it's not worth the fight. As a normal user, clone again under your home directory, make sure you've added yourself to the `docker` group (`sudo usermod -a -G docker $USER`, then log out and back in), and run **`docker compose` without `sudo`**. Never `sudo git clone`.

### My Browser Keeps Forcing HTTPS

If your browser rewrites `http://localhost:8001` to `https://` and then can't connect, that's the browser's HSTS/forced-HTTPS behavior, not omegaUp — the local instance only speaks plain HTTP. Disable the forced-HTTPS policy for `localhost` following [this guide](https://hmheng.medium.com/exclude-localhost-from-chrome-chromium-browsers-forced-https-redirection-642c8befa9b).

---

### `git push` Fails with a MySQL Traceback

When you push, omegaUp's policy hooks run `stuff/policy-tool.py`, which needs to query the database. On many machines the first push blows up with a long Python traceback ending in:

```
Traceback (most recent call last):
  File "/home/ubuntu/dev/omegaup/stuff/policy-tool.py", line 124, in <module>
    main()
  ...
  File "/home/ubuntu/dev/omegaup/stuff/database_utils.py", line 75, in mysql
    return subprocess.check_output(args, universal_newlines=True)
  ...
FileNotFoundError: [Errno 2] No such file or directory: '/usr/bin/mysql'
error: failed to push some refs to 'https://github.com/user/omegaup'
```

That `FileNotFoundError: ... '/usr/bin/mysql'` means there's no `mysql` client binary on the machine running the hook. The catch: `git push` runs on your **host**, outside the container, so even though MySQL 8.0 is happily running *in* Docker, the host has no client to talk to it. Install the client **outside the container**:

```bash
sudo apt-get install mysql-client
```

### `git push` Fails with "Can't connect to local MySQL server"

Sometimes the client is installed but the push still fails, this time with a socket error before the same traceback:

```
mysql: [Warning] Using a password on the command line interface can be insecure.
ERROR 2002 (HY000): Can't connect to local MySQL server through socket '/var/run/mysqld/mysqld.sock' (2)
Traceback (most recent call last):
  File "/home/ubuntu/dev/omegaup/stuff/policy-tool.py", line 124, in <module>
    main()
  ...
subprocess.CalledProcessError: Command '['/usr/bin/mysql', '--user=root', '--password=omegaup', 'omegaup', '-NBe', 'SELECT COUNT(*) FROM `PrivacyStatements` WHERE ...']' returned non-zero exit status 1.
error: failed to push some refs to 'https://github.com/user/omegaup'
```

`Can't connect ... through socket '/var/run/mysqld/mysqld.sock'` is the giveaway: the client is defaulting to a **local Unix socket**, but your MySQL isn't local — it's in a container, reachable only over **TCP on port 13306** (published from the container in `docker-compose.yml`). The fix is to hand the host client a TCP config pointing at that port, then symlink it as the default `.my.cnf` the hook reads:

```bash
cat > ~/.mysql.docker.cnf <<EOF
[client]
port=13306
host=127.0.0.1
protocol=tcp
user=root
password=omegaup
EOF
ln -sf ~/.mysql.docker.cnf .my.cnf
```

After this, the policy tool connects over TCP to the Dockerized MySQL and the push goes through. This is the same TCP-config pattern documented in the [Contributing guide](contributing.md).

---

### A `stuff/` Script Errors Out

If you run one of the `stuff/` scripts directly on your host and get the same `/usr/bin/mysql` traceback shown above, the usual cause is that **you ran it outside the container**. Most of those scripts assume the tooling and database access that only exist inside the frontend container. Open a shell in the container (`docker compose exec frontend /bin/bash`) and run it there instead. (The `git push` hooks above are the deliberate exception — those *do* run on the host, which is why they need the host-side MySQL client and TCP config.)

### Missing Third-Party Modules

If the build or tests fail complaining about missing modules under `frontend/www/third_party/js/`, your submodules aren't checked out. Pull them in:

```bash
git submodule update --init --recursive
```

### Node / Yarn Errors After Pulling Big Changes

If Node or Yarn start throwing errors right after you pull a large dependency bump, the prebuilt frontend image can be out of step with the new `package.json`. Rebuild it:

```bash
docker compose build frontend
docker compose up
```

---

If you hit something not covered here, file an issue at [omegaup/deploy/issues](https://github.com/omegaup/deploy/issues) with your reproduction steps and the exact error message — the error text is what lets us match your symptom to a known one.

## Next Steps

- **[Learn how to contribute](contributing.md)** — branches, remotes, and submitting a pull request.
- **[Review the coding guidelines](../development/coding-guidelines.md)** — the conventions we hold code to.
- **[Explore the architecture](../architecture/index.md)** — how the pieces you just booted fit together.

## Getting Help

If you're stuck on something this page doesn't cover:

1. Check the [Getting Help guide](getting-help.md).
2. Search the existing [GitHub issues](https://github.com/omegaup/deploy/issues).
3. Ask in our [Discord server](https://discord.gg/gMEMX7Mrwe).

---

**Ready to start coding?** Head to the [Contributing Guide](contributing.md) to send your first pull request.
