---
title: Contributing to omegaUp
description: Learn how to contribute code to omegaUp through pull requests
icon: bootstrap/code-tags
---

# Contributing to omegaUp

Thank you for your interest in contributing to omegaUp! This guide will walk you through the process of submitting your first contribution.

## Development Process Overview

The `main` branch in your fork should always be kept up to date with the `main` branch of the omegaUp repository. **Never commit directly to `main`**. Instead, create a separate branch for each change you plan to submit via a Pull Request.

## Prerequisites

Before you start:

1. ✅ [Set up your development environment](development-setup.md)
2. ✅ Read the [Coding Guidelines](../development/coding-guidelines.md)
3. ✅ Understand [how to get help](getting-help.md) if you get stuck

## Issue Assignment Requirement

!!! important "Required Before Opening PR"
    Every Pull Request **must** be linked to an existing GitHub issue that is **assigned to you**.

### Steps to Get Issue Assigned

1. **Find or create an issue**:
   - Browse [existing issues](https://github.com/omegaup/omegaup/issues)
   - Or [create a new issue](https://github.com/omegaup/omegaup/issues/new) describing your bug fix or feature

2. **Express interest**:
   - Comment on the issue expressing your interest in working on it
   - Wait for a maintainer to assign it to you

3. **Start working**:
   - Once assigned, you can create your branch and start coding
   - Reference the issue in your PR description using: `Fixes #1234` or `Closes #1234`

!!! failure "PR Will Fail Without Issue Assignment"
    If your PR is not linked to an assigned issue, automated checks will fail and your PR cannot be merged.

### Self-service assignment (bot)

This repository uses [`takanome-dev/assign-issue-action`](https://github.com/takanome-dev/assign-issue-action) so contributors can claim work without waiting for a manual assign click on every issue.

**Commands** (comment on the GitHub issue):

- `/assign` — assign the issue to yourself.
- `/unassign` — remove yourself from the issue.

The bot may also suggest assignment when your comment shows you want to work on the issue.

**Limits and deadlines**

- You can have at most **5** issues assigned to you at the same time (across the repo).
- After you are assigned, you must **open a pull request** (a **draft** PR is enough) within **7 days**.
- A reminder is posted about halfway through that window (~3.5 days).
- If no PR is opened by day 7, you are **automatically unassigned** and **blocked from self-assigning again** on that issue; ask a maintainer if you still need it.

**Experienced issue authors**

- If **you created the issue** and you have at least **10 merged PRs** in this repository, you may self-assign **without** counting against the “5 active assignments” limit for issues you authored.
- The **7-day rule** (open a PR after assignment) still applies.
- For issues **created by someone else**, the usual limit of **5** concurrent assignments still applies.

**Tips**

- Comment `/assign`, then open a draft PR early so you do not lose the assignment.
- Use `/unassign` if you cannot continue, so someone else can take the issue.
- If you need more time, ask a maintainer to add the **`📌 Pinned`** label on the issue.

## Setting Up Your Fork and Remotes

You only need to do this once. The names below match the **usual GitHub fork workflow** so tutorials and tooling stay familiar:

- **`origin`** — your fork (`https://github.com/YOURUSERNAME/omegaup.git`): where you **push** branches and open pull requests from.
- **`upstream`** — the canonical repository (`https://github.com/omegaup/omegaup.git`): where you **pull** official changes from.

Some older omegaUp wiki pages used the opposite names; this documentation site uses the convention above.

### 1. Fork the Repository

Visit [github.com/omegaup/omegaup](https://github.com/omegaup/omegaup) and click the "Fork" button.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOURUSERNAME/omegaup.git
cd omegaup
```

### 3. Add `upstream` and verify remotes

Your clone already has **`origin`** pointing at your fork. Add **`upstream`** once:

```bash
git remote add upstream https://github.com/omegaup/omegaup.git
git remote -v
```

You should see:

```
origin     https://github.com/YOURUSERNAME/omegaup.git (fetch)
origin     https://github.com/YOURUSERNAME/omegaup.git (push)
upstream   https://github.com/omegaup/omegaup.git (fetch)
upstream   https://github.com/omegaup/omegaup.git (push)
```

If `origin` is wrong (for example you cloned the wrong URL), fix it with:

```bash
git remote set-url origin https://github.com/YOURUSERNAME/omegaup.git
```

## Updating Your main Branch

Keep your local `main` and your **fork’s** `main` aligned with **omegaUp’s** `main`:

```bash
git checkout main
git fetch upstream
git pull --rebase upstream main
git push origin main
```

!!! warning "If push to main is rejected"
    If `git push origin main` fails because you committed directly on `main`, prefer resetting to a clean state with maintainer help, or use `git push origin main --force-with-lease` only when you understand the risk. In general, **never commit on `main`**; use a feature branch instead.

## Starting a New Change

### 1. Create a Feature Branch

Create a new branch from the latest official `main`:

```bash
git fetch upstream
git checkout -b feature-name upstream/main
git push -u origin feature-name
```

!!! tip "Branch Naming"
    Use descriptive branch names like `fix-login-bug` or `add-dark-mode-toggle`.

### 2. Make Your Changes

- Write your code following the [coding guidelines](../development/coding-guidelines.md)
- Write tests for your changes
- Ensure all tests pass

### 3. Commit Your Changes

```bash
git add .
git commit -m "Write a clear description of your changes"
```

!!! tip "Commit Messages"
    Write clear, descriptive commit messages. See [Conventional Commits](https://www.conventionalcommits.org/) for best practices.

### 4. Run Validators

Before pushing, run the linting script:

```bash
./stuff/lint.sh
```

This command:
- Aligns code elements
- Removes unnecessary lines
- Performs validations for all languages used in omegaUp

!!! note "Pre-push Hooks"
    This script is also run automatically via pre-push hooks, but running it manually ensures your changes meet standards.

### 5. Configure Git User (First Time Only)

If you haven't configured Git user information:

```bash
git config --global user.email "your-email@domain.com"
git config --global user.name "Your Name"
```

## Creating a Pull Request

### 1. Push Your Changes

```bash
git push -u origin feature-name
```

The `-u` flag sets up tracking between your local branch and **`origin`** (your fork).

### 2. Open Pull Request on GitHub

1. Go to [github.com/YOURUSERNAME/omegaup](https://github.com/YOURUSERNAME/omegaup)
2. Click "Branch" and select your branch
3. Click "Pull request"
4. Fill in the PR description

### 3. PR Description Template

Your PR description should include:

```markdown
## Description
Brief description of what this PR does.

## Related Issue
Fixes #1234  <!-- Replace with your issue number -->

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
Describe how you tested your changes.

## Screenshots (if applicable)
Add screenshots if your changes affect the UI.
```

!!! important "Issue Reference Required"
    Always include `Fixes #1234` or `Closes #1234` in your PR description. This automatically closes the issue when the PR is merged.

## Updating Your Pull Request

If you need to make changes after creating the PR:

```bash
git add .
git commit -m "Description of additional changes"
git push  # No -u flag needed after first push
```

The PR will automatically update with your new commits.

## What Happens After Submission

1. **Automated Checks**: GitHub Actions will run tests and validations
2. **Code Review**: A maintainer will review your code
3. **Address Feedback**: Make requested changes and push updates
4. **Merge**: Once approved, your PR will be merged
5. **Deployment**: Changes are deployed on weekends

!!! info "Weekend Deployments"
    Merged PRs are deployed to production during weekend deployments. You'll see your changes live after the next deployment.

## Deleting Branches

After your PR is merged:

### Delete Local Branch

```bash
git branch -D feature-name
```

### Delete Remote Branch

1. Go to GitHub and click "Branches"
2. Find your branch and click the delete icon

Or use Git:

```bash
git push origin --delete feature-name
```

### Clean Up Remote References

Remove stale remote-tracking branches (for example after a branch was deleted on GitHub):

```bash
git remote prune origin --dry-run  # Preview what will be removed
git remote prune origin             # Actually remove them
```

## Fixing a pull request (bad commits or history)

If you already pushed commits to your fork and need to **squash**, **drop**, or **edit** recent commits, use an interactive rebase, then push with lease.

### Squash or fixup the last `n` commits

```bash
git rebase -i HEAD~n
```

Replace `n` with how many commits to edit. In the editor, keep the top commit as `pick` and change the rest to `fixup` (or `f`) to fold them into the first without keeping their messages. Save and close.

Prefer **force-with-lease** so you do not overwrite someone else’s work by mistake:

```bash
git push --force-with-lease
```

### Change the last commit message only

If the bad commit is the **latest** and you have **not** pushed yet, or you are OK rewriting that commit on the branch:

```bash
git commit --amend
```

If you already pushed that commit:

```bash
git commit --amend
git push --force-with-lease
```

!!! warning "Rewriting public history"
    Only rewrite history on **your** feature branch. Never force-push to `main` on the canonical repo.

## Additional Settings

### Locale Configuration

The virtual machine may not have `en_US.UTF-8` as the default locale. To fix this, follow [this guide](https://askubuntu.com/questions/881742/locale-cannot-set-lc-ctype-to-default-locale-no-such-file-or-directory-locale/893586#893586).

### Composer Dependencies

On first setup, install PHP dependencies:

```bash
composer install
```

### MySQL Configuration

If you encounter MySQL errors when pushing, install and configure MySQL:

```bash
sudo apt install mysql-client mysql-server

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

## Resources

- **[Coding Guidelines](../development/coding-guidelines.md)** - Our coding standards
- **[Useful Commands](../development/useful-commands.md)** - Development commands reference
- **[Testing Guide](../development/testing.md)** - How to write and run tests
- **[How to Get Help](getting-help.md)** - Where to ask questions

## Next Steps

- Review the [Architecture Overview](../architecture/index.md) to understand the codebase
- Check out [Development Guides](../development/index.md) for detailed guides
- Join our [Discord server](https://discord.gg/gMEMX7Mrwe) to connect with the community

---

**Ready to make your first contribution?** Pick an issue, create a branch, and submit your PR!
