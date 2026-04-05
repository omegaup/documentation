---
title: Managing Contests
description: Guide to creating and managing programming contests
icon: bootstrap/cog
---

# Managing Contests

Complete guide to creating and managing programming contests in omegaUp.

## Creating a Contest

### Basic Information

- **Title**: Contest name
- **Alias**: Short identifier (used in URLs)
- **Description**: Contest description
- **Start Time**: When the contest begins
- **End Time**: When the contest ends
- **Public/Private**: Visibility setting

### Advanced Settings

- **Window Length**: USACO-style individual timers
- **Scoreboard Visibility**: Percentage of time scoreboard is visible
- **Points Decay**: Time-based score decay factor
- **Penalty Policy**: How penalties are calculated
- **Submission Gap**: Seconds between submissions

## Contest Types

### Standard Contest
- Fixed start and end time
- Shared timer for all participants
- Traditional contest format

### Virtual Contest (USACO-style)
- Individual timer per participant
- Starts when participant enters
- Window-based duration

## Managing Problems

Add problems to your contest:

1. Create or select problems
2. Set point values
3. Order problems
4. Configure problem-specific settings

## Managing Participants

### Public Contests
- Open to all users
- No invitation needed

### Private Contests
- Invite specific users
- Manage participant list
- Control access

## Scoreboard Configuration

- **Visibility**: Control when scoreboard is visible
- **Freeze**: Freeze scoreboard before contest ends
- **Refresh**: Real-time updates via WebSocket

## Running a contest at a school (network checklist)

If contestants use a **school lab** or locked-down network, allow outbound **HTTPS (port 443)** to omegaUp and related services.

**Required / usual**

- **`https://omegaup.com`** — standard contest mode
- **`https://arena.omegaup.com`** — only if you intentionally use **lockdown mode** (see below). If you use lockdown, **block** normal `omegaup.com` for contestants so they cannot bypass restrictions.
- **`https://ssl.google-analytics.com`** — used by the site

**Optional**

- **`https://secure.gravatar.com`** — avatars
- **`https://accounts.google.com`** — “Sign in with Google”

Only **HTTPS** is supported; HTTP redirects to HTTPS. Prefer firewall **REJECT/DENY with an explicit response** over **DROP** for blocked hosts, or browsers may wait tens of seconds per blocked domain and the UI will feel frozen.

### Lockdown mode (`arena.omegaup.com`)

Lockdown mode trades flexibility for integrity: many features are restricted (for example admin views, **practice mode**, and viewing **past submission source**). **No exceptions** are made per contest—if you need those features, use **`https://omegaup.com`** instead of the arena hostname.

### Contestant environment (Windows vs judge)

Submissions are graded on **Linux**. Code that relies on Windows-only headers (for example `conio.h`) or non-portable `printf` formats may fail even if it runs on lab PCs. Prefer POSIX-friendly I/O and `long long` with `%lld` (or C++ streams).

### Large events (100+ participants)

Email **hello@omegaup.com** well in advance so capacity can be confirmed for your date.

## Related documentation

- **[Contests API](../../api/contests.md)** — API endpoints
- **[Arena](../arena.md)** — contest interface
