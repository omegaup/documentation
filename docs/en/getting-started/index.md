---
title: Getting Started
description: Start your journey contributing to omegaUp
icon: bootstrap/rocket-launch
---

# Getting Started with omegaUp Development

Welcome! This guide will help you get started with contributing to omegaUp, a free educational platform that helps improve programming skills.

## What is omegaUp?

omegaUp is an educational programming platform used by tens of thousands of students and teachers in Latin America. It provides:

- **Problem Solving**: Thousands of programming problems with automatic evaluation
- **Contests**: Organize programming competitions
- **Courses**: Structured learning paths
- **Training**: Practice problems organized by topic and difficulty

## Before You Begin

If you're new to omegaUp, we recommend:

1. **Experience the Platform**: Visit [omegaUp.com](https://omegaup.com/), create an account, and solve a few problems
2. **Learn About Us**: Explore [omegaup.org](https://omegaup.org/) to learn more about our organization
3. **Understand the Codebase**: Review the [Architecture Overview](../architecture/index.md) to understand how omegaUp works

## Quick Start Path

<div class="grid cards" markdown>

-   :material-docker:{ .lg .middle } __[Development Setup](development-setup.md)__

    ---

    Set up your local development environment using Docker. This is the first step to start contributing.

    [:octicons-arrow-right-24: Setup Guide](development-setup.md)

-   :material-source-branch:{ .lg .middle } __[Contributing Guide](contributing.md)__

    ---

    Learn how to fork the repository, create branches, and submit pull requests.

    [:octicons-arrow-right-24: Contribute](contributing.md)

-   :material-help-circle:{ .lg .middle } __[Getting Help](getting-help.md)__

    ---

    Stuck? Learn how to ask questions effectively and get help from the community.

    [:octicons-arrow-right-24: Get Help](getting-help.md)

</div>

## Development environment overview

omegaUp uses Docker for local development. At a high level:

- **Web + API**: PHP controllers and DAOs over **MySQL** (classic MVC; JSON APIs)
- **Judge**: **Go** grader, runners, and **minijail** sandbox
- **Browser UI**: **Vue.js**, **TypeScript**, **Bootstrap 4** (ongoing migration away from legacy templates)
- **Problem storage**: **gitserver** and zip/case layout as documented under [Features → Problems](../features/problems/index.md)

### Where things live in the repo (quick map)

| Area | Path (in the main repository) |
|------|--------------------------------|
| HTTP API / business rules | `frontend/server/src/Controllers/` |
| Database access | `frontend/server/src/DAO/` |
| Migrations | `frontend/database/` |
| TypeScript / Vue | `frontend/www/js/` |
| Legacy templates / i18n | `frontend/templates/` |
| PHPUnit API tests | `frontend/tests/controllers/` |
| Cypress E2E | `cypress/e2e/` |

### Papers (architecture context)

- [omegaUp: Cloud-Based Contest Management System](http://www.ioinformatics.org/oi/pdf/v8_2014_169_178.pdf) (IOI Journal, 2014)
- [libinteractive](https://ioinformatics.org/journal/v9_2015_3_14.pdf) — interactive tasks

## Supported browsers (contributors and contestants)

Use a **current evergreen** browser (**Chrome**, **Firefox**, **Safari**, or **Edge**). The site is **HTTPS-only**. Very old Internet Explorer versions are **not** supported.

## Development Accounts

When you set up your local environment, you'll have access to two pre-configured accounts:

| Username | Password | Role |
|----------|----------|------|
| `omegaup` | `omegaup` | Administrator |
| `user` | `user` | Regular user |

## Next Steps

1. **[Set up your development environment](development-setup.md)** - Get Docker running and clone the repository
2. **[Read the contributing guide](contributing.md)** - Learn the workflow for submitting changes
3. **[Explore the architecture](../architecture/index.md)** - Understand how omegaUp is structured
4. **[Review coding guidelines](../development/coding-guidelines.md)** - Learn our coding standards

## Resources

- **Website**: [omegaup.com](https://omegaup.com)
- **GitHub**: [github.com/omegaup/omegaup](https://github.com/omegaup/omegaup)
- **Discord**: [Join our Discord server](https://discord.gg/gMEMX7Mrwe) for community support
- **Issues**: [Report bugs or request features](https://github.com/omegaup/omegaup/issues)

---

Ready to start? Head to [Development Setup](development-setup.md) to begin!
