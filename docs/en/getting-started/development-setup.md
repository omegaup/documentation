---
title: Development Environment Setup
description: Complete guide to setting up your local omegaUp development environment
icon: bootstrap/tools
---

# Development Environment Setup

This guide will walk you through setting up a local development environment for omegaUp using Docker.

!!! tip "Video Tutorial"
    We have a [video tutorial](http://www.youtube.com/watch?v=H1PG4Dvje88) that demonstrates the setup process visually.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Engine**: [Install Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
- **Docker Compose 2**: [Install Docker Compose](https://docs.docker.com/compose/install/linux/#install-the-plugin-manually)
- **Git**: For cloning the repository

!!! note "WSL Users"
    If you're using WSL (Windows Subsystem for Linux), follow the [official Docker Desktop WSL integration guide](https://docs.docker.com/desktop/features/wsl).

### Linux-Specific Setup

If you're running Linux, after installing Docker, add your user to the docker group:

```bash
sudo usermod -a -G docker $USER
```

Log out and log back in for the changes to take effect.

!!! warning "Git Knowledge"
    If you're not confident using Git, we recommend reading [this Git tutorial](https://github.com/shekhargulati/git-the-missing-tutorial) first.

## Step 1: Fork and Clone the Repository

1. **Fork the repository**: Visit [github.com/omegaup/omegaup](https://github.com/omegaup/omegaup) and click the "Fork" button

2. **Clone your fork**:
   ```bash
   git clone --recurse-submodules https://github.com/YOURUSERNAME/omegaup
   cd omegaup
   ```

3. **Initialize submodules** (if needed):
   ```bash
   git submodule update --init --recursive
   ```

## Step 2: Start Docker Containers

### First Time Setup

On your first run, pull the Docker images and start the containers:

```bash
docker-compose pull
docker-compose up --no-build
```

This will take 2-10 minutes. You'll know it's ready when you see output similar to:

```
frontend_1     | Child frontend:
frontend_1     |        1550 modules
frontend_1     |     Child HtmlWebpackCompiler:
frontend_1     |            1 module
...
```

### Subsequent Runs

After the first run, you can start containers faster with:

```bash
docker compose up --no-build
```

The `--no-build` flag avoids rebuilding everything, significantly speeding up startup.

!!! note "`docker compose` vs `docker-compose`"
    Docker Compose V2 uses the plugin command `docker compose` (with a space). Older installs may use the `docker-compose` binary; both are fine as long as your Docker installation provides one of them. The examples in this guide use `docker compose`.

## Step 3: Access Your Local Instance

Once the containers are running, access your local omegaUp instance at:

**http://localhost:8001**

## Step 4: Access Container Console

To run commands inside the container:

```bash
docker exec -it omegaup-frontend-1 /bin/bash
```

The codebase is located at `/opt/omegaup` inside the container.

## Development Accounts

Your local installation includes pre-configured accounts:

### Admin Account
- **Username**: `omegaup`
- **Password**: `omegaup`
- **Role**: Administrator (sysadmin privileges)

### Regular User Account
- **Username**: `user`
- **Password**: `user`
- **Role**: Regular user

### Test Accounts

For testing purposes, you can use these test accounts:

| Username | Password |
|----------|----------|
| `test_user_0` | `test_user_0` |
| `test_user_1` | `test_user_1` |
| ... | ... |
| `course_test_user_0` | `course_test_user_0` |

!!! info "Email Verification"
    In development mode, email verification is disabled. You can use dummy email addresses when creating new accounts.

## Running Tests Locally

If you want to run JavaScript/TypeScript tests outside of Docker:

### Prerequisites

1. **Node.js**: Version 16 or higher
2. **Yarn**: Package manager

### Setup Steps

1. **Initialize Git Submodules**:
   ```bash
   git submodule update --init --recursive
   ```
   
   This downloads required dependencies:
   - `pagedown` - Markdown editor
   - `iso-3166-2.js` - Country/region codes
   - `csv.js` - CSV parsing
   - `mathjax` - Math rendering

2. **Install Dependencies**:
   ```bash
   yarn install
   ```

3. **Run Tests**:
   ```bash
   yarn test
   ```

### Quick Start (Fresh Clone)

For a fresh clone, use this single command:

```bash
git clone --recurse-submodules https://github.com/YOURUSERNAME/omegaup
cd omegaup
yarn install
yarn test
```

## Codebase Structure

The omegaUp codebase is organized as follows:

```
omegaup/
├── frontend/
│   ├── server/
│   │   └── src/
│   │       ├── Controllers/    # Business logic & API endpoints
│   │       ├── DAO/            # Data Access Objects
│   │       └── libs/           # Libraries & utilities
│   ├── www/                    # Frontend assets (TypeScript, Vue.js)
│   ├── templates/              # Smarty templates & i18n files
│   ├── database/               # Database migrations
│   └── tests/                  # Test files
```

For more details, see the [Architecture Overview](../architecture/index.md) and [Frontend architecture](../architecture/frontend.md).

Contributing workflow (branches, PRs, remotes) is documented in [Contributing](contributing.md).

## Visual Studio Code with Docker

You can edit code from your host using [Visual Studio Code](https://code.visualstudio.com/) while the stack runs in Docker.

### Recommended extensions

- [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) or [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) to attach to a running container
- PHP, Vue, and ESLint extensions as needed for the files you touch

### Attach to the frontend container

1. Start the environment: `docker compose up --no-build` (or `docker compose up` on first run).
2. In VS Code, open the Docker extension (or Command Palette) and **Attach to Running Container**, then pick the container that runs the omegaUp frontend (often named like `omegaup-frontend-1`; exact name comes from `docker compose ps`).
3. In the attached window, use **File → Open Folder** and open **`/opt/omegaup`** — that is the bind-mounted project root inside the container.

You can also clone on the host and edit files normally: the same directory is mounted into `/opt/omegaup`, so hot reload and webpack inside the container pick up saves from the host.

!!! tip "Legacy Vagrant / SSH workflow"
    If you still use a VM provisioned with [omegaup/deploy](https://github.com/omegaup/deploy), you can connect with **Remote - SSH** using `vagrant ssh-config` output pasted into your SSH config, as described in the [VS Code Remote SSH documentation](https://code.visualstudio.com/docs/remote/ssh). Prefer Docker for new contributors when possible.

## GitHub OAuth (local “Sign in with GitHub”)

To enable GitHub login on **`http://localhost:8001/`**:

### 1. Create the OAuth App on GitHub

1. Open [GitHub Developer Settings](https://github.com/settings/developers).
2. **OAuth Apps → New OAuth App**.
3. Set:
   - **Application name**: e.g. `omegaUp local`
   - **Homepage URL**: `http://localhost:8001/`
   - **Authorization callback URL**: `http://localhost:8001/login?third_party_login=github`
4. Register the app and copy the **Client ID**; generate and copy the **Client Secret** (you will not see the secret again).

### 2. Configure omegaUp locally

1. Create or edit **`frontend/server/config.php`** (this file is for local overrides — do not put secrets in git).
2. Add:

```php
<?php
define('OMEGAUP_GITHUB_CLIENT_ID', 'your_real_client_id_here');
define('OMEGAUP_GITHUB_CLIENT_SECRET', 'your_real_client_secret_here');
```

3. A full Docker Compose restart is usually **not** required for PHP defines to be picked up in typical dev setups, but if the button stays disabled, restart the frontend container once.

!!! failure "Never commit OAuth secrets"
    Revert or exclude `config.php` before pushing. Do **not** put credentials in `config.default.php`. If `config.php` is recreated when containers are recreated, keep a copy of your Client ID/Secret in a password manager.

!!! tip "Button disabled?"
    If the GitHub login button stays inactive, the client ID is missing or wrong in `config.php`. If you change host or port, update the callback URL in the GitHub OAuth app to match.

See also [Security → OAuth](../architecture/security.md#oauth-integration) for how authentication fits into the platform.

## Common Issues

### The Web App Is Not Showing My Changes

Make sure Docker is running:

```bash
docker compose up --no-build
```

If the problem persists, ask for help in omegaUp's communication channels.

### Browser Redirects HTTP to HTTPS

If your browser keeps changing `http` to `https` for localhost, you can disable security policies for `localhost`. [See this guide](https://hmheng.medium.com/exclude-localhost-from-chrome-chromium-browsers-forced-https-redirection-642c8befa9b).

### MySQL Not Found Error

If you encounter this error when pushing to GitHub:

```
FileNotFoundError: [Errno 2] No such file or directory: '/usr/bin/mysql'
```

Install MySQL client outside the container:

```bash
sudo apt-get install mysql-client mysql-server
```

Then configure MySQL connection:

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

### MySQL Connection Error

If MySQL is installed but you get connection errors (for example `Can't connect to local MySQL server through socket`), the policy hooks that run on `git push` expect a **TCP** client config pointing at the Docker-exposed port (**13306**). Use the `~/.mysql.docker.cnf` + `.my.cnf` symlink pattern shown in the [Contributing guide](contributing.md) **Additional Settings** section.

### Git submodule / third-party JS errors

If tests or the build fail with missing modules under `frontend/www/third_party/js/`, initialize submodules:

```bash
git submodule update --init --recursive
```

### Rebuild the frontend image

If Node or Yarn errors appear after pulling large dependency changes, rebuild the frontend image:

```bash
docker compose build frontend
docker compose up
```

### Permission denied: `phpminiadmin`, `venv`, or developer-environment restart loop

**Symptoms**: Logs show `Permission denied` creating `phpminiadmin` or under `stuff/venv/`; `developer-environment` exits repeatedly; the site never serves on `http://localhost:8001`.

**Cause**: The repo was cloned or `docker compose` was run as **root**, or the project directory is owned by root. Bind mounts map your host directory to `/opt/omegaup`; root-owned trees block the container user from writing.

**Fix**: Do not try to “repair” a root-owned tree in place. As a normal user, clone again under your home directory, add your user to the `docker` group, and run **`docker compose` without `sudo`**. Never `sudo git clone`.

### Policy tool / `mysql` errors when pushing

If `git push` fails with Python tracebacks from `stuff/policy-tool.py` and `FileNotFoundError: ... 'mysql'`, install the MySQL client on the **host** (outside the container) and add the Docker TCP client config as in the MySQL sections above.

For deployment-environment issues, open an issue on [omegaup/deploy](https://github.com/omegaup/deploy/issues) with logs and steps.

## Next Steps

- **[Learn how to contribute](contributing.md)** - Create branches and submit pull requests
- **[Review coding guidelines](../development/coding-guidelines.md)** - Understand our coding standards
- **[Explore the architecture](../architecture/index.md)** - Understand how omegaUp works

## Getting Help

If you encounter issues not covered here:

1. Check the [Getting Help guide](getting-help.md)
2. Search existing [GitHub issues](https://github.com/omegaup/deploy/issues)
3. Ask in our [Discord server](https://discord.gg/gMEMX7Mrwe)

---

**Ready to start coding?** Head to the [Contributing Guide](contributing.md) to learn how to submit your first pull request!
