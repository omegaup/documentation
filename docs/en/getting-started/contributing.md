---
title: Contributing to omegaUp
description: Learn how to contribute code to omegaUp through pull requests
icon: bootstrap/code-tags
---

# Contributing to omegaUp

Thank you for your interest in contributing to omegaUp! This page walks you through the whole loop of a contribution: forking and cloning, keeping your local copy honest before you touch anything, branching, opening a good pull request, and fixing one after you have already pushed something you are not proud of. Nothing here is exotic git — it is the everyday workflow the maintainer team actually uses, with the reasoning attached so you can improvise safely when your situation does not match the happy path.

Before you write a line of code, we invite you to read the [Coding Guidelines](../development/coding-guidelines.md). Their north star is worth internalizing early: it is preferred to explain *why* things are done the way they are done rather than *what* the code does. Following them makes your change far easier for a reviewer to read and merge, so the effort pays you back the same week.

## Why you never commit to `main`

After you fork omegaUp, the `main` branch in your fork should always stay a byte-for-byte mirror of the `main` branch of `omegaup/omegaup`, which holds the latest changes the review team has already approved. That is the entire reason for the rule you will see repeated everywhere: **never commit directly to `main`**. Once your commits land on `main` and the upstream `main` moves on, it is genuinely painful to drag your `main` back to a clean state — you end up rebasing, resetting, or force-pushing your way out of a hole you dug for no reason. Instead, create a separate branch for every change you intend to submit as a Pull Request, and let `main` do nothing but track upstream.

## Prerequisites

Before you start:

1. [Set up your development environment](development-setup.md)
2. Read the [Coding Guidelines](../development/coding-guidelines.md)
3. Know [how to get help](getting-help.md) if you get stuck

## Every PR needs an assigned issue

!!! important "Required before opening a PR"
    Every Pull Request **must** be linked to an existing GitHub issue that is **assigned to you**. This is not bureaucracy for its own sake — it is how the team avoids two people silently building the same fix, and it is enforced by automation, so a PR with no assigned issue behind it cannot be merged no matter how good the code is.

### Getting an issue assigned

First, **find or create an issue**. Browse the [existing issues](https://github.com/omegaup/omegaup/issues), or, if you are fixing something nobody has filed yet, [open a new issue](https://github.com/omegaup/omegaup/issues/new) describing the bug or feature so there is something to point your PR at.

Then **claim it**. omegaUp runs the [`takanome-dev/assign-issue-action`](https://github.com/takanome-dev/assign-issue-action) bot precisely so you do not have to wait for a maintainer to click "assign" on every ticket. Comment on the issue with:

- `/assign` — assign the issue to yourself.
- `/unassign` — remove yourself from the issue when you cannot continue, so someone else can pick it up.

The bot may also offer to assign the issue when your comment makes it obvious you want to work on it.

Finally, reference the issue in your PR description with `Fixes #1234` or `Closes #1234` (using your real issue number). GitHub reads that line and closes the issue automatically the moment your PR merges, so the tracker stays honest without anyone tidying it by hand.

!!! failure "A PR with no assigned issue will fail its checks"
    If your PR is not linked to an issue that is assigned to you, the automated checks fail and the PR cannot be merged. Claim the issue first.

### The assignment limits, and why they exist

The bot enforces a few deadlines so that claimed-but-abandoned issues do not rot indefinitely and block other contributors:

- You may hold at most **5** issues assigned to you at once across the whole repository. The cap keeps any one person from hoarding the backlog.
- After you are assigned, you must **open a pull request** — a **draft** PR counts — within **7 days**. The window is what turns "I'll get to it" into either real progress or a freed-up issue.
- A reminder is posted about halfway through, at roughly **3.5 days**, so a busy week does not cost you the issue by surprise.
- If no PR exists by day 7, you are **automatically unassigned** and **blocked from self-assigning that same issue again**; if you still want it after that, ask a maintainer.

There is one deliberate exception: if **you authored the issue** and you already have at least **10 merged PRs** in this repository, you can self-assign your own issues **without** them counting against the 5-active-assignments limit — you have earned the trust, and it is your issue. The 7-day-to-a-PR rule still applies even then, and issues authored by *other* people still count against your limit of 5.

!!! tip "Don't lose an assignment you meant to keep"
    Comment `/assign`, then open a **draft** PR the same day — that satisfies the 7-day rule immediately and buys you all the time you need to finish. If you genuinely need longer, ask a maintainer to add the **`📌 Pinned`** label, which exempts the issue from the auto-unassign sweep.

## Set up your fork and remotes (once)

You only do this once per clone. omegaUp uses the same two remote names as the standard GitHub fork workflow, so every git tutorial and tool you already know keeps working:

- **`origin`** — your fork, `https://github.com/YOURUSERNAME/omegaup.git`: where you **push** branches and open pull requests from.
- **`upstream`** — the canonical repository, `https://github.com/omegaup/omegaup.git`: where you **pull** the review team's approved changes from.

!!! note "Older wiki pages swapped these names"
    Some of omegaUp's older wiki pages used `origin` for the canonical repo and a second remote for the fork — the opposite of the convention here. This site follows the standard convention above (`origin` = your fork, `upstream` = canonical). If you are cross-referencing an old page and a command reads backwards, that is why.

### 1. Fork the repository

Visit [github.com/omegaup/omegaup](https://github.com/omegaup/omegaup) and click the **Fork** button to create your own copy of `omegaup/omegaup`.

### 2. Clone your fork

```bash
git clone https://github.com/YOURUSERNAME/omegaup.git
cd omegaup
```

### 3. Add `upstream` and verify

Your fresh clone already has `origin` pointing at your fork. Add `upstream` so you can fetch the canonical repo's changes:

```bash
git remote add upstream https://github.com/omegaup/omegaup.git
git remote -v
```

You should see exactly this — two lines for each remote, `origin` on your fork and `upstream` on the canonical repo:

```
origin     https://github.com/YOURUSERNAME/omegaup.git (fetch)
origin     https://github.com/YOURUSERNAME/omegaup.git (push)
upstream   https://github.com/omegaup/omegaup.git (fetch)
upstream   https://github.com/omegaup/omegaup.git (push)
```

If `origin` points somewhere wrong — most commonly because you cloned the canonical URL instead of your fork — repoint it without re-cloning:

```bash
git remote set-url origin https://github.com/YOURUSERNAME/omegaup.git
```

## Keep your `main` up to date before you start

It bears repeating: you should not make changes on `main`, because it is very hard to return it to a decent state once your changes have merged. But it is a good idea to sync it from time to time — always right before you branch off a new change — so your work starts from the same commit the review team is looking at:

```bash
git checkout main               # Switch back to main if you were on a feature branch
git fetch upstream              # Download the latest omegaup/main
git pull --rebase upstream main # Replay upstream's commits under yours, keeping main linear
git push origin main            # Update your fork's main to match
```

!!! warning "If `git push origin main` is rejected"
    A rejected push to `main` means you broke the rule and committed something directly on `main` — your `main` and upstream's `main` have now diverged. The clean fix is to move those commits onto a feature branch and reset `main` back to `upstream/main`; ask a maintainer if you are unsure how. Only if you understand exactly what you are discarding should you overwrite your fork's `main` with `git push origin main --force-with-lease`. The real lesson is the one from the top of this page: don't commit on `main` in the first place — branch instead.

## Start a new change

### 1. Branch off the latest upstream `main`

Create your branch directly from `upstream/main` so it starts from the review-approved code, then push it to your fork right away so there is a home for it on GitHub:

```bash
git fetch upstream
git checkout -b feature-name upstream/main   # New branch, synced with omegaUp's main
git push -u origin feature-name              # Publish it to your fork; -u sets up tracking
```

!!! tip "Name the branch after the change"
    Descriptive names like `fix-login-bug` or `add-dark-mode-toggle` tell reviewers what the branch is for at a glance and keep your own branch list navigable months later.

### 2. Make your changes

Write your code following the [coding guidelines](../development/coding-guidelines.md), add tests for what you changed, and make sure the existing suite still passes. A change with tests is a change a reviewer can trust.

### 3. Set your git identity (first time only)

If you have never configured git on this machine, do it once so your commits are attributed correctly:

```bash
git config --global user.email "your-email@domain.com"
git config --global user.name "your-username"
```

### 4. Commit

```bash
git add .
git commit -m "Write a clear description of what changed and why"
```

A commit message that explains *why* the change was made — not just *what* file moved — is the same courtesy the coding guidelines ask of your code comments, and it is what a reviewer reads first.

### 5. Run the validators before you push

Run the linter from **outside** the container, at the repository root:

```bash
./stuff/lint.sh
```

With no arguments, `stuff/lint.sh` figures out which files you changed (it diffs against `upstream/main`, or `origin/main` if you have no `upstream` remote) and runs the `fix` pass over just those files, spinning up the pinned `omegaup/hook_tools` container to do the actual formatting and static checks for every language omegaUp uses. It aligns code, strips dead lines, and validates. If you only want to *check* without rewriting files, pass `validate` explicitly: `./stuff/lint.sh validate`.

!!! note "It must run outside the container"
    `stuff/lint.sh` refuses to run when its working directory is `/opt/omegaup` (the path the code lives at *inside* the dev container) and prints `Running ./stuff/lint.sh inside a container is not supported.` It needs your host's Docker to launch the hook-tools image, so run it from the host shell, not from inside `docker exec`.

!!! note "The pre-push hook runs this for you"
    omegaUp installs a `pre-push` git hook that runs `stuff/lint.sh ... validate` automatically, so a push with lint errors is stopped before it leaves your machine. Running the linter yourself first just means you find and fix problems on your own schedule instead of having the push bounce.

## Open the pull request

### 1. Push your branch

```bash
git push -u origin feature-name
```

The `-u` flag links your local branch to the branch on your fork (`origin`), so every later push is just `git push` with no arguments — the tracking is already set.

### 2. Open the PR on GitHub

Go to your fork at `https://github.com/YOURUSERNAME/omegaup`, use the branch selector to switch to `feature-name`, and click **Pull request**. GitHub will offer to open the PR against `omegaup/omegaup`'s `main` — that is exactly where you want it.

### 3. Write the description

A good description is what gets your PR reviewed quickly. Include what the change does, the issue it closes, what actually changed, and how you know it works:

```markdown
## Description
Brief description of what this PR does.

## Related Issue
Fixes #1234  <!-- Replace with your real issue number -->

## Changes Made
- Change 1
- Change 2

## Testing
How you tested the change.

## Screenshots (if applicable)
Before/after images for any UI change.
```

!!! important "Always reference the issue"
    The `Fixes #1234` / `Closes #1234` line is not optional decoration — it is what links the PR to your assigned issue (satisfying the automated check) and what closes the issue automatically when the PR merges.

## Update a PR after review

Reviewers will leave comments. Address them the same way you made the original change — commit on the same branch and push. There is no `-u` this time because the branch is already tracking `origin`:

```bash
git add .
git commit -m "Address review: <what you changed>"
git push
```

The open PR updates itself with the new commits automatically, and the reviewer sees them the next time they look.

## Fix a PR you already pushed

Sometimes you push and only then notice the branch carries three "wip", "oops", and "typo" commits, or the top commit has a message you would rather not immortalize. Because this is *your* feature branch and not shared history, you are free to rewrite it and force-push. The one hard rule is the same as everywhere else on this page: **only rewrite history on your own feature branch — never force-push to `main` on the canonical repo.**

### Change just the last commit's message

If the message on your most recent commit is wrong, amend it — this opens your editor on the existing message:

```bash
git commit --amend
```

You will see the current message followed by git's helper text:

```
Old commit message

# Please enter the commit message for your changes. Lines starting
# with '#' will be ignored, and an empty message aborts the commit.
```

Edit the top line, save, and close. Confirm it took with `git log`, which should now show your new message against that commit. If you had already pushed the commit, the remote still has the old version, so update it:

```bash
git push --force-with-lease
```

`--force-with-lease` is the safe form of `--force`: it refuses to overwrite the remote branch if someone else pushed to it since you last fetched, so a force-push can never silently clobber a collaborator's work.

### Squash away the throwaway commits

To fold a run of messy commits into one clean commit, interactively rebase the last `n` of them:

```bash
git rebase -i HEAD~n
```

Replace `n` with how many commits you want to collapse. Git opens an editor listing them oldest-first:

```
pick commit-1
pick commit-2
pick commit-3
...
pick commit-n
```

Keep the top one as `pick` — that is the commit whose message survives — and change every line below it from `pick` to `fixup` (or just `f`), which folds that commit's changes into the one above it and throws its message away:

```
pick  commit-1
f     commit-2
f     commit-3
...
f     commit-n
```

Save and close. Then publish the rewritten branch:

```bash
git push --force-with-lease
```

The PR now shows a single tidy commit instead of the fixup trail, and none of the discarded messages appear in the history.

## After you submit

Once the PR is open, a predictable sequence plays out. GitHub Actions runs the full battery of tests and validations — make sure they all go green, since a red check is the first thing a reviewer will bounce the PR on. Then a member of the omegaUp team reviews your code; address whatever they raise by pushing more commits to the same branch. Once it is approved and merged, there is one more wait: merged PRs go to production on the **weekend deployment**, so your change goes live after the next weekend rather than the instant it merges.

## Clean up after a merge

Once your PR is merged, the branch has done its job. Delete it locally:

```bash
git branch -D feature-name
```

Delete it on GitHub too — either from the **Branches** page, from the merged PR itself (GitHub offers a delete button), or from the command line:

```bash
git push origin --delete feature-name
```

Even after deleting the remote branch, your local repo keeps a stale remote-tracking reference to it, which you can see with `git branch -a`. Prune those dead references so `git branch -a` stops listing branches that no longer exist:

```bash
git remote prune origin --dry-run  # Preview what would be pruned
git remote prune origin            # Actually remove the stale references
```

## Environment gotchas you may hit on first push

These are the setup snags first-time contributors most often trip over. Each shows the symptom so you can match your own, then the fix.

### The VM's locale is not `en_US.UTF-8`

The development VM does not ship with `en_US.UTF-8` as its default locale, which some tools complain about. Fix it by following [this askubuntu guide](https://askubuntu.com/questions/881742/locale-cannot-set-lc-ctype-to-default-locale-no-such-file-or-directory-locale/893586#893586).

### Missing PHP dependencies

A fresh checkout has no `vendor/` directory, so PHP dependencies are missing until you install them:

```bash
composer install
```

### `FileNotFoundError: ... 'mysql'` when pushing

If your push aborts with something like this:

```
FileNotFoundError: [Errno 2] No such file or directory: 'mysql'
error: failed to push some refs to 'https://github.com/YOURUSERNAME/omegaup.git'
```

what it is telling you is that the pre-push hook tried to run the `mysql` client and could not find it — MySQL is not installed on your host. The MySQL **server** runs inside the dev container, but the client the hook invokes must live on the host, **outside** the container. Install both packages there:

```bash
sudo apt install mysql-client mysql-server
```

Then point the client at the container's MySQL, which is published on port **13306** (not the default 3306, so it does not collide with any MySQL you already run):

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

With `.my.cnf` linked, the client reads that config automatically and the pre-push hook can reach the database.

## Where to go next

- **[Coding Guidelines](../development/coding-guidelines.md)** — the standards that make your PR easy to review.
- **[Useful Commands](../development/useful-commands.md)** — the day-to-day development command reference.
- **[Testing Guide](../development/testing.md)** — how to write and run the tests your PR needs.
- **[How to Get Help](getting-help.md)** — where to ask when you are stuck.
- **[Architecture Overview](../architecture/index.md)** — how the pieces you are changing fit together.
- Join the [Discord server](https://discord.gg/gMEMX7Mrwe) to talk to the community.

---

**Ready to make your first contribution?** Claim an issue, branch off `upstream/main`, and open your PR.
