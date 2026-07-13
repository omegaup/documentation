---
title: Docker Setup
description: Detailed Docker Compose configuration for local development
icon: bootstrap/tools
---

# Docker Setup

omegaUp is not one program — it is a PHP web application plus a handful of Go services plus
their datastores, and the only sane way to run all of it on your machine is the Docker
Compose stack in the repository's [`docker-compose.yml`](https://github.com/omegaup/omegaup/blob/main/docker-compose.yml).
This page explains what that stack actually starts and why, so that when something misbehaves
you know which container to look at.

If your goal is to *contribute* — clone, boot, log in, edit code — start with
[Development Setup](../getting-started/development-setup.md), which walks the happy path.
This page is the map underneath it.

## The services

Bringing the stack up (`docker-compose up`) starts these containers, each pinned to a
specific image so everyone runs the same versions:

| Service | Image | What it is |
| ------- | ----- | ---------- |
| `frontend` | `omegaup/dev-php` | The PHP 8.1 web application (php-fpm behind nginx) — the [MVC](../architecture/mvc-pattern.md) app that serves every page and the `/api/` endpoints. This is the container you exec into to run tests, webpack, and PHP tooling. |
| `mysql` | `mysql:8.0.34` | The database. Exposed to the host on port **13306** (not the default 3306, so it won't collide with a MySQL you already run). |
| `redis` | `redis` | Cache. |
| `rabbitmq` | `rabbitmq:3-management-alpine` | Message queue used for asynchronous work; the `-management` image also gives you its web console. |
| `gitserver` | `omegaup/gitserver:v1.9.13` | The Go service that stores each problem as a git repository. See [Gitserver](../architecture/gitserver.md). |
| `grader` | `omegaup/backend` | The Go grader — receives runs, queues them, dispatches to runners. The frontend reaches it over HTTP at `OMEGAUP_GRADER_URL` (default `https://localhost:21680`). |
| `runner` | `omegaup/runner` | The Go runner — compiles and executes submissions inside minijail. |
| `broadcaster` | `omegaup/backend` | The Go service that pushes scoreboard/verdict updates to the browser over WebSockets. |
| `init-omegaupdata` | `alpine` | A short-lived init container that seeds the shared problem-data volume before the long-running services start. |

The grader, runner, broadcaster, and gitserver are **prebuilt binaries** shipped as Docker
images — they are not built from this repository, which contains no Go source. They come
from the separate [omegaup/quark](https://github.com/omegaup/quark) and
[omegaup/gitserver](https://github.com/omegaup/gitserver) projects; see
[Infrastructure](../architecture/infrastructure.md) for how the pieces fit together in
production.

## Volumes

A few named volumes persist state across restarts so you don't re-seed everything each time:
`dbdata` (MySQL), `omegaupdata` (the shared problem data the frontend, grader, and gitserver
all read), plus `rabbitmq` and `redis`. If the stack ever gets into a genuinely wedged
state, removing these volumes and re-seeding is the big hammer — see
[Troubleshooting](troubleshooting.md).

## Production vs. development

`docker-compose.yml` is the development stack. Production runs the same services on
Kubernetes from [`docker-compose.k8s.yml`](https://github.com/omegaup/omegaup/blob/main/docker-compose.k8s.yml)
with the `omegaup/php` and `omegaup/nginx` images rather than the all-in-one `dev-php`
image. The service topology is the same; the packaging and scaling differ. See
[Deployment](deployment.md).
