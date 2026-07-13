---
title: Troubleshooting
description: Common issues and solutions
icon: bootstrap/tools
---

# Troubleshooting

This page collects the operational failures people actually hit running omegaUp — the stack won't boot, the API can't reach MySQL, your frontend edits don't show up, or the grader is unreachable and submissions hang. For each one we lead with the **raw error you'll see**, then explain **what it actually means**, then give the **fix** — because a symptom you can't interpret is a symptom you can't resolve, and the error text is what lets us match your problem to a known cause.

A lot of the *development-time* stumbles (root-owned checkout, `git push` MySQL tracebacks, forced-HTTPS redirects, missing submodules) already have detailed write-ups in [Development Environment Setup](../getting-started/development-setup.md#troubleshooting). This page is the operations-side companion: it assumes the stack was standing at some point and is now misbehaving, and it cross-links back to the setup page wherever the root cause is really a setup mistake.

Before you dig in, one mental model that saves a lot of time: **the local stack is not one process, it's a graph of containers with a strict boot order.** In `docker-compose.yml` the `frontend` container `depends_on` `mysql`, `gitserver`, `grader`, and `redis`; the `grader` waits on `mysql:13306` (`wait-for-it mysql:13306`) before it starts; the `runner` waits on `grader:11302`; and `gitserver` waits on `mysql:13306` too. So when something "won't come up," the first question is always *which container*, and the second is *what was it waiting for*. `docker compose ps` answers the first; `docker compose logs <service>` answers the second.

---

## The Stack Won't Boot

**Symptom**: `docker compose up --no-build` never reaches the ready state, or a container shows up as `Restarting` / `Exited` in `docker compose ps` instead of `Up`.

Start by asking Compose what it thinks is running, then read the log of whichever service is unhealthy:

```bash
docker compose ps               # which container is Restarting / Exited?
docker compose logs frontend    # then read that specific service's log
docker compose logs grader
```

The normal, healthy signal for a first boot is **not instant** — a cold start takes **2–10 minutes** because the `frontend` container compiles the entire Vue 2.7 + TypeScript app with Webpack, MySQL initializes its data directory, and the grader blocks on the database. What tells you it's genuinely ready is a Webpack module dump ending with something like `Child grader: 1131 modules` (the exact counts drift as the codebase grows). If you've never seen a successful boot on this machine, don't treat a long wait as a hang — see the [full ready-state output in the setup guide](../getting-started/development-setup.md#step-2-bring-up-the-containers) and give it the full ten minutes first.

Once you've isolated the failing container, the usual culprits, in rough order of how often we see them:

**The `frontend` container restarts on a loop with `Permission denied`.** If the logs show `Permission denied` while creating `phpminiadmin` or writing under `stuff/venv/`, the project tree was cloned as **root** or `docker compose` was run with `sudo`, so the bind mount at `/opt/omegaup` is root-owned and the container's non-root user can't write to it. This is common enough that it has its own section — [My Dev Environment Won't Come Up](../getting-started/development-setup.md#my-dev-environment-wont-come-up) — and the fix is to re-clone as a normal user under your home directory, add yourself to the `docker` group (`sudo usermod -a -G docker $USER`, then log out and back in), and never `sudo git clone`. Trying to `chown` the root-owned tree back in place is not worth the fight.

**A dependent container starts before the thing it needs.** Because `grader` and `gitserver` both gate on `wait-for-it mysql:13306`, a MySQL that never becomes reachable will leave *them* stuck waiting, which in turn leaves `frontend` waiting on `grader`. If `docker compose ps` shows `grader` or `gitserver` sitting in a wait state, don't debug them — debug MySQL first (next section). The order matters: fixing the leaf rarely fixes the root.

**Port already in use.** If a container dies immediately with a bind error like `Error starting userland proxy: listen tcp4 0.0.0.0:8001: bind: address already in use`, something else on your host already owns that port. The stack publishes a specific, memorable set: **`8001`** (frontend HTTP), **`13306`** (MySQL), **`21680`** (grader HTTP API), **`33861`** (gitserver), and **`5672`/`15672`** (RabbitMQ). Find and free the offender:

```bash
lsof -i :8001        # or :13306, :21680, :33861
kill -9 <PID>        # or stop whatever service owns it
```

**You're out of disk, or the images are stale.** A wedged build or an OOM-during-init often traces back to a full Docker data root. Check and reclaim:

```bash
docker system df           # how much is images / containers / volumes eating?
docker system prune        # remove stopped containers, dangling images, unused networks
```

If the failure is instead "image not found" or a mismatch after a big pull, the pinned images (currently `omegaup/dev-php:20231008`, `omegaup/backend:v1.9.35`, `omegaup/runner:v1.9.35`, `omegaup/gitserver:v1.9.13`, `mysql:8.0.34`) need refreshing — `docker compose pull` grabs the current set, and you only need it on first setup or when `up` complains an image is missing or stale.

As a last resort — and only when you're willing to lose local state — you can wipe and rebuild from a clean slate. Note the `-v` drops your **volumes** (including the MySQL data and the problems git storage), so you'll re-run the environment bootstrap afterward:

```bash
docker compose down -v      # careful: this deletes the MySQL and omegaupdata volumes
docker compose up --no-build
```

---

## MySQL Is Not Reachable

**Symptom**: the API returns 500s, and the PHP log or the browser shows a connection error like `SQLSTATE[HY000] [2002]` or `Can't connect to MySQL server`. Nothing that touches the database works, which is basically everything.

The load-bearing fact here is **where MySQL actually lives and how the PHP talks to it.** The database runs in the `mysql` container (`mysql:8.0.34`), and the frontend connects over TCP — `OMEGAUP_DB_HOST` defaults to **`mysql:13306`** (see `frontend/server/config.default.php`), and `\OmegaUp\MySQLConnection` uses the **mysqli** driver (`mysqli_init()` / `real_connect()`), not PDO. So a "can't connect" almost always means one of three things: the container isn't up, it's up but still initializing, or something is aiming the client at the wrong place.

First, confirm the container is actually running and has finished initializing. MySQL 8.0 does real work on first boot, and the API will get connection refused until it prints its ready line:

```bash
docker compose ps mysql
docker compose logs mysql | tail -50
docker compose logs mysql | grep "ready for connections"
```

If you don't see `ready for connections` yet, that's the whole answer — **wait for it**, don't restart it, because a restart just re-runs the same slow init. This is also why `grader` and `gitserver` gate on `wait-for-it mysql:13306`: everything downstream is written to assume MySQL comes up first.

If MySQL *is* ready but the API still can't reach it, prove the connection from inside the frontend container, which is the environment the PHP actually runs in:

```bash
docker compose exec frontend /bin/bash
mysql --host=mysql --port=13306 --user=omegaup --password=omegaup omegaup -e "SELECT 1"
```

The default local credentials are `omegaup` / `omegaup` against the `omegaup` database, matching the `MYSQL_USER` / `MYSQL_PASSWORD` / `MYSQL_DATABASE` in the `mysql` service. If that `SELECT 1` succeeds from inside the container but your tool fails from the **host**, you've hit the single most common confusion: **the host has no path to MySQL except TCP on `13306`.** A host-side `mysql` client defaulting to a Unix socket will fail with `Can't connect to local MySQL server through socket '/var/run/mysqld/mysqld.sock'` — because there is no local server, it's in Docker. That exact case (it bites the `git push` policy hook, which runs on the host) has a copy-pasteable TCP-config fix in [git push Fails with "Can't connect to local MySQL server"](../getting-started/development-setup.md#git-push-fails-with-cant-connect-to-local-mysql-server).

Two more MySQL error signatures worth interpreting, because they look like connectivity but aren't:

- **`ERROR 3024 ... Query execution was interrupted, maximum statement execution time exceeded`.** The `mysql` container is started with `--max_execution_time=30000` (30 seconds), so a genuinely slow query gets killed rather than hanging forever. Read this as "your query is too slow," not "MySQL is down" — `EXPLAIN` it and look for a missing index.
- **`Lock wait timeout exceeded`.** The container also sets `--lock_wait_timeout=10` and `--wait_timeout=20`, so a transaction blocked on a row lock for more than ~10 seconds is aborted deliberately, to stop one stuck writer from wedging everyone. Find the holder with `SHOW PROCESSLIST` and let it finish or kill it, rather than raising the timeout.

If the data itself is corrupt after a hard crash — not just unreachable — the nuclear option is to drop the MySQL volume and re-bootstrap. You lose all local data, so only do this on a dev box:

```bash
docker compose down -v
docker compose up -d
```

---

## The Web App Is Not Showing My Changes

**Symptom**: you edited a `.vue` or `.ts` file, saved, hard-reloaded the browser — and it still shows the old UI.

This one confuses people because it *looks* like a caching bug, but it usually isn't. **The browser is served a Webpack build, not your source files**, so an edit you haven't rebuilt is invisible no matter how many times you refresh. Every page's UI is a Vue 2.7 single-file component under `frontend/www/js/omegaup/components/`, compiled by Webpack 5 into the bundle the Twig shell (`frontend/templates/template.tpl`) loads via its `{% entrypoint %}` / `{% jsInclude %}` tags. Nothing you type reaches the browser until Webpack recompiles.

So the fix is to rebuild, from inside the container where the toolchain lives:

```bash
docker compose exec frontend /bin/bash
cd /opt/omegaup && yarn run dev
```

`yarn run dev` runs Webpack **once** over the frontend. If you're iterating and don't want to re-run it after every save, use `yarn dev:watch` instead, which watches the tree and rebuilds on change. This is the same guidance as the setup guide's [The Web App Is Not Showing My Changes!](../getting-started/development-setup.md#the-web-app-is-not-showing-my-changes) — worth reading there for the Windows-specific twist.

Speaking of which: **on Windows, the watcher silently misses file-change events if your checkout lives under `/mnt/c/...`.** Docker bind mounts across the Windows↔Linux boundary don't reliably deliver inotify events, so `yarn dev:watch` sees nothing, never rebuilds, and you stare at stale output with no error to explain it. The fix isn't a Webpack flag — it's to keep the repo inside the WSL2 Linux filesystem (e.g. `~/omegaup`), as covered in the setup guide.

If you've rebuilt successfully and it's *still* stale, work down this short list before blaming the tooling: confirm the containers are actually up (`docker compose up --no-build`); do a real hard refresh (`Ctrl+Shift+R`, or `Cmd+Shift+R` on macOS) or open DevTools → Network → **Disable cache** so the browser stops serving its own cached bundle; and if you touched a PHP controller's signature, remember that the typed API client (`api.ts` / `api_types.ts`) is **generated** — it won't reflect controller changes until it's regenerated by `frontend/server/cmd/APITool.php`, not by Webpack. Don't hand-edit those two files; regenerate them.

---

## The Grader Is Unreachable

**Symptom**: submissions sit forever with no verdict, or an admin action that touches grading returns a 500. In the PHP log you'll see a `Grader` channel error — `curl failed` with a URL under `https://localhost:21680`, or the terminal message `Maximum retry attempts exceeded`.

Here's the architecture you have to hold to debug this, because it's the thing the old wiki got wrong: **the grader is not part of the PHP codebase.** The grader, runner, broadcaster, and minijail sandbox are separate **Go** services from [github.com/omegaup/quark](https://github.com/omegaup/quark) (problem storage is [github.com/omegaup/gitserver](https://github.com/omegaup/gitserver)), shipped as prebuilt Docker images. The PHP side is only a thin HTTP client: `\OmegaUp\Grader` (in [`frontend/server/src/Grader.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Grader.php)) sends curl requests to **`OMEGAUP_GRADER_URL`**, which defaults to **`https://localhost:21680`** (`frontend/server/config.default.php`). When you submit, `\OmegaUp\Controllers\Run::apiCreate` eventually calls `\OmegaUp\Grader::getInstance()->grade($run, $source)`, which POSTs to the grader's `/run/new/{run_id}/`. If that HTTP call can't complete, the submission never gets graded — so "unreachable grader" is really "the PHP can't complete an HTTP request to `21680`."

That connection is **mutually authenticated over TLS**, and this is where local setups most often break. The curl call in `\OmegaUp\Grader::curlRequestSingle` presents a client certificate (`CURLOPT_SSLCERT => /etc/omegaup/frontend/certificate.pem`, `CURLOPT_SSLKEY => /etc/omegaup/frontend/key.pem`), pins the CA to that same cert (`CURLOPT_CAINFO`), and — importantly — verifies the peer strictly (`CURLOPT_SSL_VERIFYPEER => true`, `CURLOPT_SSL_VERIFYHOST => 2`, TLS 1.2). So a self-signed or mismatched cert doesn't silently pass; it fails the handshake. If the grader `curl failed` error mentions an SSL/certificate problem rather than a refused connection, suspect the certs under `/etc/omegaup/frontend/`, not the grader being down.

Diagnose it in the order the request actually travels. First, is the grader container even up and did it get past its own dependency wait?

```bash
docker compose ps grader
docker compose logs grader | tail -50
```

Remember the grader `wait-for-it mysql:13306` gate — a grader stuck waiting is really a MySQL problem, so check that first if the log shows it never started. The runner is a separate container that registers with the grader on the **internal** port `11302` (`wait-for-it grader:11302`), which is distinct from the `21680` HTTP API the PHP talks to; a grader that's up but has **no runners** will accept submissions and never finish them, so check `docker compose logs runner` for registration and errors too.

Next, ask the grader directly what it thinks its queue looks like. There's a first-class endpoint for this: **`GET /api/grader/status/`**, served by `\OmegaUp\Controllers\Grader::apiStatus`, which requires a **system-admin** session (`\OmegaUp\Authorization::isSystemAdmin`, else `ForbiddenAccessException`) and returns `\OmegaUp\Grader::getInstance()->status()` — a proxy to the grader's own `/grader/status/`. The payload (`GraderStatus`) tells you exactly where a backlog lives:

```json
{
  "grader": {
    "status": "ok",
    "broadcaster_sockets": 0,       // live WebSocket clients on the broadcaster
    "embedded_runner": false,       // is a runner running in-process?
    "queue": {
      "running": [],                // runs currently being judged: [{name, id}]
      "run_queue_length": 0,        // runs waiting to be dispatched
      "runner_queue_length": 0,     // runners idle and waiting for work
      "runners": []                 // names of registered runners
    }
  }
}
```

Read it like this: a growing `run_queue_length` with an empty `runners` list means **no runner is registered** — the grader has work but nobody to do it, so look at the runner container. A healthy but slow system shows runs moving through `running`. An empty `runners` *and* zero everything usually means you're talking to a grader that just came up (or a faked one — see below).

When the PHP genuinely can't reach `21680`, the client doesn't give up on the first failure. `\OmegaUp\Grader::curlRequest` **retries up to 3 times** with exponential backoff (`sleep(2^(n-1))`, capped at 5 seconds), but *only* for errors it classifies as transient — the current list in `isRetryableError` is `SSL connection timeout`, `HTTP/2 stream`, `SSL routines::unexpected eof`, `INTERNAL_ERROR`, `Connection timed out`, and `Operation timed out`. A flat `Connection refused` (grader not listening) is **not** retryable and fails immediately, whereas a flaky TLS handshake gets three shots before you finally see `Maximum retry attempts exceeded`. The per-attempt budget is also bounded: `CURLOPT_CONNECTTIMEOUT => 5` and `CURLOPT_TIMEOUT => 30`, so a single hung call can't block a page for more than ~30 seconds. If you see `Maximum retry attempts exceeded` in logs, that's three failed transient attempts — an intermittently unhealthy grader — not a config typo, which would fail on the first try.

One escape hatch worth knowing for frontend-only work: you don't actually need a live grader to develop most of the site. Setting **`OMEGAUP_GRADER_FAKE`** (default `false`) makes `\OmegaUp\Grader` short-circuit every call — `grade()` just writes the source to `/tmp/{guid}` and returns, and `status()` returns an empty-but-well-formed `GraderStatus`. If submissions "succeed" but never produce a real verdict and the queue always reads as empty, check whether you're running in fake-grader mode before you go hunting for a networking bug that isn't there.

---

## Quick Error Reference

These are the signatures you'll actually see, mapped to the section above that explains them. When you file an issue, paste the exact text — the error string is what lets us match your symptom to a known cause.

| Error you see | What it really means | Where to look |
|---|---|---|
| `bind: address already in use` (`:8001`, `:13306`, `:21680`) | Another process already owns a published port | [The Stack Won't Boot](#the-stack-wont-boot) |
| `Permission denied` creating `phpminiadmin` / under `stuff/venv/`, container restart loop | Repo cloned as root or `sudo docker compose` — bind mount is root-owned | [Won't Come Up (setup)](../getting-started/development-setup.md#my-dev-environment-wont-come-up) |
| `SQLSTATE[HY000] [2002]` / `Can't connect to MySQL server` | MySQL container down, still initializing, or wrong host | [MySQL Is Not Reachable](#mysql-is-not-reachable) |
| `Can't connect ... through socket '/var/run/mysqld/mysqld.sock'` | Host client using a Unix socket; MySQL is TCP-only on `13306` | [git push MySQL socket fix (setup)](../getting-started/development-setup.md#git-push-fails-with-cant-connect-to-local-mysql-server) |
| `maximum statement execution time exceeded` | Query exceeded the container's `--max_execution_time=30000` (30s) | [MySQL Is Not Reachable](#mysql-is-not-reachable) |
| `Lock wait timeout exceeded` | Row lock held past `--lock_wait_timeout=10` (10s), aborted on purpose | [MySQL Is Not Reachable](#mysql-is-not-reachable) |
| Edits invisible after reload | Browser serves the Webpack build, not your source — needs a rebuild | [Changes Not Showing](#the-web-app-is-not-showing-my-changes) |
| `Grader` channel `curl failed` @ `https://localhost:21680` | PHP can't complete the HTTPS call to the Go grader | [The Grader Is Unreachable](#the-grader-is-unreachable) |
| `Maximum retry attempts exceeded` | 3 transient grader retries all failed — intermittently unhealthy grader | [The Grader Is Unreachable](#the-grader-is-unreachable) |

---

## Getting More Help

If none of this resolves it:

1. **Search existing issues** on [GitHub](https://github.com/omegaup/omegaup/issues) — someone may have hit the exact signature already.
2. **Ask on [Discord](https://discord.gg/gMEMX7Mrwe)**, and always include the relevant log output; a symptom without its error text is hard to place.
3. **File a bug** with your reproduction steps and the verbatim error — see [Getting Help](../getting-started/getting-help.md) for what makes a good report.

## Related Documentation

- **[Development Environment Setup](../getting-started/development-setup.md)** — standing up the stack, and the setup-time troubleshooting this page defers to.
- **[Getting Help](../getting-started/getting-help.md)** — where to ask when you're stuck.
- **[Monitoring](monitoring.md)** — watching the stack in production.
- **[Docker Setup](docker-setup.md)** — how the containers are wired together.
