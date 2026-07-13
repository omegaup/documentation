---
title: Managing Contests
description: Guide to creating and managing programming contests
icon: bootstrap/cog
---

# Managing Contests

This page walks through everything you do as the person *running* a contest — the teacher setting up a weekly practice for a class, the club organizer hosting a regional selection, the coach reproducing last year's IOI as a training session. We trace the real flow: creating the contest, hanging problems on it, deciding who gets in, tuning the scoreboard, and picking the mode that fits your room. Every knob here maps to a field on `\OmegaUp\DAO\VO\Contests` and an endpoint on `\OmegaUp\Controllers\Contest` (`frontend/server/src/Controllers/Contest.php`), so when the UI hides something you'll know exactly which parameter to reach for.

## Creating a Contest

The contest form you fill in on the site is the Vue component `frontend/www/js/omegaup/components/contest/Form.vue`; when you submit it, it POSTs to `Contest::apiCreate` (`Contest.php:2941`). Two gates fire before anything is written: `Controller::ensureNotInLockdown()` (you cannot author contests from the `arena.omegaup.com` lockdown host — more on that below), and `ensureMainUserIdentityIsOver13()`, because contest creation is tied to a full account and omegaUp does not let under-13 identities own one.

The single most surprising thing about `apiCreate` is that **every contest is born private**, no matter what you ask for. The controller hard-codes `'admission_mode' => 'private'`, and if you pass any `admission_mode` other than `'private'` it throws `contestMustBeCreatedInPrivateMode` rather than silently honoring it. This is deliberate: you build the contest in a quiet room — add problems, sanity-check the clock, invite a co-admin — and only *then* flip it public through `apiUpdate`. Nobody stumbles onto a half-finished contest.

### The basic fields

These four are the identity of the contest and are required:

- **`title`** — the human name shown in listings (e.g. "Selectivo Regional 2026").
- **`alias`** — the short slug that lives in the URL. The contest is reachable at `/arena/<alias>`, so keep it lowercase and URL-safe; `Validators::alias` enforces that.
- **`description`** — free text shown on the contest's intro page before a contestant enters.
- **`start_time` / `finish_time`** — both are timestamps. `finish_time` must be *strictly* greater than `start_time` or `validateCommonCreateOrUpdate` throws `contestNewInvalidStartTime`. The two together define the contest length, and that length is capped: `MAX_CONTEST_LENGTH_SECONDS` is `60 * 60 * 24 * 31`, i.e. **31 days** for a normal organizer; system admins get `MAX_CONTEST_LENGTH_SYSADMIN_SECONDS` = **60 days**. Ask for a 40-day contest as a teacher and you'll get `contestLengthTooLong` back with the `max_days` you're allowed.

### The tuning knobs (and what they actually do)

Everything past the basics has a sensible default, so you can leave them alone for a first contest and come back once you know what you want. The defaults below are the ones written on `VO/Contests`:

- **`window_length`** (`int` minutes, default `null`) — this is the USACO-style personal timer. `null` means "you may submit for the entire span between `start_time` and `finish_time`" — one shared clock for everybody. Set it to, say, `180`, and each contestant instead gets their own 180-minute window that starts ticking the moment *they* open the contest. That's what lets a class of 30 sit down at staggered times and still each get the same three hours. Note `apiCreate` stores `$r['window_length'] ?: null`, so a `0` collapses back to "no window."
- **`submissions_gap`** (`int` seconds, default `60`) — the minimum wait a contestant must serve between two submissions on any problem. The default 60 exists to blunt brute-force "submit-and-see" behavior and to keep one person from flooding the judge queue; drop it for a relaxed practice, raise it for a high-stakes selection.
- **`scoreboard`** (`int` 0–100, default `1`) — read this as *the percentage of the contest's elapsed time during which the live scoreboard is visible to contestants*. `100` means the board is live the whole way through; `0` means it's dark for the entire contest. This is your scoreboard **freeze**: set it to `80` and the standings quietly stop updating for the final 20% of the contest, so the last-hour drama stays secret. (See the [Scoreboard](#the-scoreboard) section for how this composes with `show_scoreboard_after`.)
- **`points_decay_factor`** (`float`, default `0.00`) — how much a problem's value bleeds away as the clock runs, rewarding early solves. `0` means no decay: a problem is worth the same in minute 1 and minute 179. For calibration, **TopCoder uses `0.7`**. Most school contests leave this at 0.
- **`penalty`** (`int` minutes, default `1`) and **`penalty_type`** (enum `'contest_start' | 'problem_open' | 'runtime' | 'none'`) — the tie-breaker machinery. `penalty` is how many minutes each *rejected* submission adds to your time; `penalty_type` decides what the clock even measures — minutes since the contest began (`contest_start`, the ICPC convention), minutes since *you personally opened* that problem (`problem_open`, which pairs naturally with `window_length`), the program's actual runtime in milliseconds (`runtime`), or nothing at all (`none`). **`penalty_calc_policy`** (enum `'sum' | 'max'`) then says whether a contestant's penalty is the sum across problems or just the worst one.
- **`score_mode`** (enum `'partial' | 'all_or_nothing' | 'max_per_group'`, validated by `ensureOptionalEnum`) — how a partially-correct solution scores. `partial` gives credit proportional to the test cases passed; `all_or_nothing` gives a problem full marks only when *every* case is AC and zero otherwise (classic olympiad style); `max_per_group` takes the best score you achieved on each test group. There's an older boolean `partial_score` (default `true`) that predates this enum and expresses the same partial-vs-all-or-nothing intent.
- **`feedback`** (enum `'none' | 'summary' | 'detailed'`, default `'none'`) — how much the contestant learns from a submission. `none` hides the verdict entirely (they submit into the dark, IOI-final style); `summary` shows the percentage of cases passed plus the worst-case verdict; `detailed` reveals the verdict case by case. Practice sessions want `detailed`; a real selection usually wants `none` or `summary`.
- **`show_scoreboard_after`** (`bool`, default `true`) — whether the full scoreboard is revealed to everyone once the contest ends, regardless of what `scoreboard` did during the run.
- **`languages`** (optional filter) — restrict which programming languages are allowed. Leave it `null` to permit all of omegaUp's supported languages; set it to lock a beginners' contest to, say, Python only.
- **`contest_for_teams`** (`bool`, default `false`) plus **`teams_group_alias`** — turn the contest into a team event whose participants come from a teams group rather than individual invitations. This flag changes how you add participants (see below), so decide it up front.
- **`check_plagiarism`** (`bool`, default `false`) — run omegaUp's plagiarism detector across submissions after the contest.

## Managing Problems

A contest starts empty; you hang problems on it with `Contest::apiAddProblem` (`Contest.php:3461`), which the `contest/AddProblem.vue` component drives. Only a contest admin may do this — `validateContestAdmin` runs first — and it's **forbidden on a virtual contest** (`forbiddenInVirtual`), since a virtual contest is a frozen replay of an existing problem set, not a fresh one you edit.

Two parameters shape each addition. **`points`** is `ensureFloat('points', 0, INF)` — any non-negative weight, so you can make the hard problem worth 300 and the warm-up worth 50. **`order_in_contest`** (default `1`) fixes where the problem appears in the list. There's a hard ceiling: `MAX_PROBLEMS_IN_CONTEST` is **30** (defined in `frontend/server/config.default.php:176`), and the 31st `apiAddProblem` throws `contestAddproblemTooManyProblems`.

A subtlety worth internalizing: adding a problem pins it to a **specific git commit** of that problem (via `Problem::resolveCommit`, which resolves the optional `commit` parameter or the problem's master commit). This freezes the exact test data and statement your contestants will see, so that an author editing the problem's live version mid-contest can't shift the ground under a running event. After the write, `apiAddProblem` invalidates two caches — `Cache::CONTEST_INFO` for the alias and the scoreboard cache via `Scoreboard::invalidateScoreboardCache` — so the change shows up immediately instead of serving a stale contest page. To pull a problem back out, `apiRemoveProblem` is the mirror image.

## Managing Participants

Because every contest is private until you say otherwise, the participant list *is* the access-control list. How you populate it depends on `admission_mode`, which you set through `apiUpdate` (the enum is `'private' | 'public' | 'registration'`):

- **`private`** — only the identities you explicitly invite can enter. This is the default and the right choice for a classroom.
- **`public`** — anyone on omegaUp may join without an invitation. `is_invited` is what distinguishes someone you deliberately added from someone who simply walked into a public contest, which matters when you later read the participant list.
- **`registration`** — contestants *request* access and you approve them. Their requests surface through `apiRequests`, and you accept or reject each with `apiArbitrateRequest`. This is the middle ground for an open-but-vetted event.

For a private contest you invite people one at a time with `Contest::apiAddUser` (`Contest.php:3859`), passing a `usernameOrEmail`. It writes a `ProblemsetIdentities` row with `is_invited => true` (and `score`/`time` zeroed, `end_time` null so their personal window hasn't started). One gotcha lives right here: if the contest was created with `contest_for_teams`, `apiAddUser` refuses with `usersCanNotBeAddedInContestForTeams` — a team contest draws its roster from a group, so you use `apiAddGroup` (or `apiReplaceTeamsGroup`) instead of adding individuals. And a convenience: if the contest is in `registration` mode, inviting someone through `apiAddUser` also **pre-accepts** their access request via `preAcceptAccessRequest`, so they skip the request queue entirely.

Inviting a whole class one username at a time gets old fast, which is why `apiAddGroup` exists: build a group once (your "Period 3 CS" roster), and add the entire group to any contest in a single call. To hand off co-organizing duties, `apiAddAdmin` and `apiAddGroupAdmin` grant admin rights on the contest itself.

## The Scoreboard

The live standings are served by `apiScoreboard`, with an incremental event feed from `apiScoreboardEvents` that the front end replays to animate rank changes. Two fields you set at creation govern visibility, and they compose: **`scoreboard`** (0–100) controls how much of the *running* contest the board is live for — your freeze — while **`show_scoreboard_after`** decides whether it's fully revealed once the contest ends. A common configuration is `scoreboard: 100, show_scoreboard_after: true` for a transparent practice, versus `scoreboard: 0, show_scoreboard_after: true` for a "results at the end only" selection. `default_show_all_contestants_in_scoreboard` controls whether admins and non-participants are listed alongside contestants by default.

Updates arrive in real time over the **Broadcaster** WebSocket at `wss://omegaup.com/events/` — a separate Go service in the [`omegaup/quark`](https://github.com/omegaup/quark) repo, not part of the PHP backend — so a solved problem climbs the board without anyone reloading. If your network is locked down, that WebSocket needs to be reachable (see the checklist below) or the board silently falls back to slower polling. When you run two sittings of the same event and want one combined ranking — a morning and an afternoon section, say — `apiScoreboardMerge` folds several contests into a single scoreboard.

## Contest Modes

Beyond the per-field knobs, three broad modes cover almost every real event:

**Standard (shared clock).** The default: one `start_time`, one `finish_time`, `window_length` left `null`. Everyone competes on the same wall clock. This is the ICPC/classroom shape.

**Virtual (USACO-style replay).** `Contest::apiCreateVirtual` (`Contest.php:2735`) clones a *finished* contest into a fresh one you can take like a mock exam — the original must already be over or it throws `originalContestHasNotEnded`. Combined with `window_length`, this is how a student "runs" last year's national olympiad at 7pm on a Tuesday and still gets the authentic time pressure: their personal timer starts when they open it. Remember that problems in a virtual contest are frozen — `forbiddenInVirtual` blocks editing.

**Lockdown.** An integrity mode you opt into purely by *which hostname* your contestants connect through — covered next, because at a school it's really a networking decision.

## Running a Contest at a School (network checklist)

If contestants sit in a **school lab** or on a locked-down network, allow outbound **HTTPS (port 443)** to omegaUp and the few services it leans on. Everything is HTTPS — a request to port 80 just gets a redirect to 443 — so port 443 is all you need to open.

**Required:**

- **`https://omegaup.com`** — standard contest mode.
- **`https://arena.omegaup.com`** — *only* if you intentionally use **lockdown mode** (below). If you do use lockdown, you must **block** `omegaup.com` for contestants, or they can simply switch to the normal host and walk around every restriction.
- **`https://ssl.google-analytics.com`** — used by the site.

**Optional (each degrades one convenience if blocked, nothing breaks):**

- **`https://secure.gravatar.com`** — the avatar in the top-right corner.
- **`https://accounts.google.com`** — "Sign in with Google."
- **`https://connect.facebook.net`** and **`https://s-static.*.facebook.com`** — "Sign in with Facebook."

There is one non-obvious firewall rule that will save your event: configure blocked hosts to **REJECT/DENY with an explicit response**, never **DROP**. On a DROP, the browser gets no answer and keeps waiting — it will hang for roughly **20–30 seconds** per blocked domain before giving up, and to a room full of students the whole page just looks frozen. An explicit reject fails fast and the UI stays responsive.

### Lockdown mode (`arena.omegaup.com`)

Point contestants at `https://arena.omegaup.com/` instead of the normal host and they enter **lockdown mode**, built for when you need stronger guarantees that students can't pass information to each other through the platform. Much of the site's functionality is deliberately switched off, and **no per-contest exceptions are possible** — the value of the lock is that it can't be selectively unlocked. The features most commonly missed under lockdown are:

- **Admin mode.**
- **Practice mode.**
- **Viewing the source of past submissions** — where the normal site shows your old code, lockdown shows an error message instead.

If your situation genuinely needs one of the things lockdown blocks, the answer is not to poke a hole in it — it's to not use lockdown, and connect through `https://omegaup.com` instead.

### Contestant environment (Windows lab vs. the judge)

Submissions are graded on **Linux**, so any reasonably recent Linux distribution on the lab machines matches the evaluation environment exactly. Windows is where the papercuts live: code that pulls in the Windows-only `conio.h` header won't compile on the judge, and older Windows toolchains print `long long` with `%I64d` instead of the portable `%lld`. Coach your contestants toward POSIX-friendly I/O — `%lld` (or C++ streams) and standard headers — so a program that ran on the lab PC doesn't die on submission.

### Large events (100+ participants)

If you're planning a big contest — **100 or more** concurrent contestants — email **hello@omegaup.com** well in advance so the team can confirm capacity for your date. It's a courtesy that prevents a bad surprise on the day.

## Related documentation

- **[API Reference](../../reference/api.md)** — the full endpoint reference behind everything here.
- **[Arena](../arena.md)** — the interface contestants actually see.
- **[Real-time Updates](../realtime.md)** — how the Broadcaster WebSocket drives the live scoreboard.
