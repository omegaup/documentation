---
title: Recruitment
description: How to join the omegaUp engineering team
icon: bootstrap/briefcase
---

# Joining the omegaUp Team

omegaUp is run by volunteers, and the whole platform — the PHP 8.1 frontend, the Vue 2.7 UI, the Go grader in [omegaup/quark](https://github.com/omegaup/quark), the problem-storage [gitserver](https://github.com/omegaup/gitserver), the thousands of problems and courses — exists because people who started exactly where you are decided to stick around. This page is about that second step: not how to open your first pull request (the [Contributing guide](../getting-started/contributing.md) covers that end to end), but how to go from one-off contributor to someone the maintainer team knows by name and formally invites onto the engineering team. There is no interview and no résumé screen. The only currency is merged work, and the path to it is completely open.

## There is nothing to apply for

The training process is open to anyone who wants it — you do not email a maintainer, fill out a form, or wait to be let in. You clone the repo, claim an issue, and start. The reason it works this way is the same reason the whole project is on GitHub in the open: the people who become team members are the ones who were going to contribute whether or not anyone was watching, so the process just gets out of their way and measures the output.

What that means in practice is that "getting recruited" is a side effect of doing the work, not a separate track you switch onto. Everything below is the work.

## The roles you can grow into

Writing backend and frontend code is the most visible way in, but it is far from the only one, and the team genuinely runs on all of these:

- **Developers** carry the code — controllers under `frontend/server/src/Controllers/`, Vue single-file components under `frontend/www/js/omegaup/components/`, plus reviewing other people's pull requests, which is itself one of the fastest ways to earn the team's trust because a good review saves a maintainer's scarcest resource, their time.
- **Problem setters** author the competitive-programming problems and their test cases — the educational content the judge actually runs. You do not need to touch the codebase at all to be indispensable here.
- **Translators** keep omegaUp usable in more than one language; the platform serves a Spanish-first community that spans many countries, and the error envelope itself is localized "en el idioma que se tenga configurada la cuenta," so translation is load-bearing, not cosmetic.
- **Educators** run omegaUp in real classrooms and competitions, and the feedback loop from an actual teacher using courses under load is worth more than most feature requests.
- **Mentors** help the next wave of newcomers get unstuck in **#dev_training**, and this is quietly one of the highest-leverage roles: the searchable Discord archive that will save the next contributor an afternoon only exists because someone answered publicly.

If you are not sure which of these is you, that is fine — most regulars end up doing two or three. Start with whichever one you can act on today.

## How to get involved beyond a single PR

The mechanics of the issue tracker are deliberately built to reward *sustained* involvement over a single drive-by fix, and understanding them tells you exactly how to become a regular:

Every pull request must be linked to a GitHub issue that is **assigned to you** — this is enforced by automation, so a PR with no assigned issue behind it cannot merge no matter how good the code is. You claim an issue by commenting `/assign` on it (the [`takanome-dev/assign-issue-action`](https://github.com/takanome-dev/assign-issue-action) bot handles it so you never wait on a human), and you can hold at most **5** issues at once. That cap is the first nudge toward consistency: you are meant to finish and ship, not hoard the backlog. After you claim an issue you have **7 days** to open a pull request — a **draft** PR counts — or the bot automatically unassigns you (a reminder lands at roughly the halfway mark, **3.5 days**, so a busy week does not cost you the issue by surprise). The rhythm this builds — claim, ship within the week, claim again — *is* what being a regular contributor looks like.

The system also has a built-in trust milestone you can aim at. Once you have **10 merged PRs** in the repository, issues *you* authored can be self-assigned without counting against your limit of 5 active assignments — a small but real signal that the project now treats you differently than it did on day one. Getting to ten merged PRs is a concrete, countable goal, and it is roughly the point at which the maintainers stop thinking of you as a newcomer.

Two more feedback loops are worth knowing about because they are how the team actually notices you. First, **helping peers in #dev_training counts.** We take it into account when selecting GSoC candidates — a contributor who reliably answers other people's questions demonstrates exactly the collaboration the project runs on, and you rarely need to be an expert to do it (pointing someone at the right doc page, or confirming "yes, that 2–10 minute first boot is normal, wait it out," is often the whole answer). Second, remember that merged PRs go to production on the **weekend deployment**, not the instant they merge — so the satisfying part, seeing your change live on omegaup.com, arrives after the next weekend, and watching it happen is part of what hooks people into coming back.

## What a formal invitation takes

There is a concrete bar for being formally invited onto the engineering team, and it is exactly the kind of countable target the project prefers over a subjective judgment call:

1. Read the documentation — this site, plus the older [omegaUp Wiki](https://github.com/omegaup/omegaup/wiki), so you know the system before you change it.
2. Resolve **5** issues labeled [**Good first issue**](https://github.com/omegaup/omegaup/issues?q=is%3Aissue+is%3Aopen+label%3A%22Good+first+issue%22) — the curated on-ramp for your first patches.
3. Resolve **5** issues labeled [**Good second issue**](https://github.com/omegaup/omegaup/issues?q=is%3Aissue+is%3Aopen+label%3A%22Good+second+issue%22) — the deliberately harder next tier, meant to prove you can navigate the codebase without hand-holding.

Clear those ten, and you are **formally invited to join the engineering team** and **offered an `@omegaup.com` email account** if you want one. The two-tier structure is intentional: five *first* issues show you can land a change through the whole pipeline (fork, branch, lint with `./stuff/lint.sh`, PR, review, merge, weekend deploy), and five *second* issues show you can do it on problems nobody has pre-chewed for you.

!!! note "Some people skip the ten-issue path"
    The requirement exists to build and demonstrate trust, so people who have already established it through another channel are not made to grind it out again. Two standing exceptions: **interns with a signed contract**, and **former volunteers with a recognized contribution record** who are returning. If you think you fall into one of these, raise it in **#dev_training** rather than assuming.

## Where to start today

The quickest concrete first step is the setup video and a good first issue, in that order:

- Watch the [development environment setup walkthrough](https://www.youtube.com/watch?v=H1PG4Dvje88), then follow the written [Development Setup](../getting-started/development-setup.md) guide — the dev stack can take **2–10 minutes** to come fully up the first time, so do not panic if it looks stuck.
- Join the [Discord server](https://discord.com/invite/K3JFd9d3wk) and say hello in **#dev_training**; this is where the whole contributor community coordinates, and where you will get unstuck fastest.
- Pick a [**Good first issue**](https://github.com/omegaup/omegaup/issues?q=is%3Aissue+is%3Aopen+label%3A%22Good+first+issue%22), comment `/assign`, and open a draft PR the same day to lock in your 7-day window.

## Related Documentation

- **[Contributing to omegaUp](../getting-started/contributing.md)** — the full pull-request workflow, from fork to weekend deploy.
- **[Development Setup](../getting-started/development-setup.md)** — get the stack running locally.
- **[Getting Help](../getting-started/getting-help.md)** — how to ask in #dev_training so you actually get answered.
- **[Community](index.md)** — the wider picture: GSoC, communication channels, and every way to get involved.
