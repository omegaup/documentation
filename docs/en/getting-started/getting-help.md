---
title: Getting Help
description: Learn how to effectively ask questions and get help from the omegaUp community
icon: bootstrap/help-circle
---

# Getting Help

You are going to have questions — about how the development environment refuses to come up, about a stack trace deep inside `frontend/server/src/Controllers/`, about how the GSoC application process actually works at omegaUp. That is expected, and asking is encouraged. But *how* you ask decides how good an answer you get and how fast it arrives, so this page is less a list of chat links and more a guide to getting your question answered well. The whole philosophy behind it is one line: the more context you put in up front, the less back-and-forth everyone spends, and the more likely a busy volunteer stops to help you at all.

## Search before you ask

Nearly every question a newcomer hits has been hit before, often several times, often the same week during GSoC season. So the first move is never "post the question" — it is a two-minute search, because the answer is very likely already written down somewhere and you will get it instantly instead of waiting hours for a human to wake up in another timezone.

Three places are worth searching, in roughly this order of usefulness:

- **This documentation site.** Use the search box at the top. If your problem is environment setup, the [Development Setup](development-setup.md) page walks the whole `docker compose` flow; if it is about opening a pull request, [Contributing to omegaUp](contributing.md) covers the git workflow; if it is "how does *this* subsystem work", the [Architecture](../architecture/index.md) section traces the real code paths end to end. If your question is API-shaped, the generated [API reference](../reference/api.md) lists every endpoint.
- **Discord message history.** Our community lives in the [omegaUp Discord server](https://discord.com/invite/K3JFd9d3wk), and the working channel for contributors is **#dev_training**. Discord's search bar is genuinely powerful — search a keyword from your error (`port already allocated`, `wait-for-it`, the name of a failing service) and you will very often land on a thread where someone asked exactly this, this year or a past year, with the fix already posted underneath. This is why we insist everyone posts publicly (more on that below): the searchable archive only exists because past questions were asked where everyone could see them.
- **Google.** If your question is about Git, Docker, PHP 8.1, TypeScript, or anything that is not specific to omegaUp, Google will almost always beat waiting for a maintainer. Reserve the human channels for the omegaUp-specific parts nobody else on the internet knows.

If you are applying through Google Summer of Code, read the GSoC ideas-and-FAQ page for that year (linked from the [Community/GSoC](../community/gsoc/index.md) section) *before* asking about the process. It answers most application-process questions directly, and the FAQ specifically covers the recurring ones about timelines, proposals, and how candidates are evaluated.

!!! tip "Search widens, not narrows"
    If your first keyword returns nothing, try a *different* phrasing rather than a more specific one — copy the distinctive line out of the error message, drop the parts that are unique to your machine (paths, container IDs), and search the middle. The signal is usually one or two words, like `port is already allocated`, not the whole traceback.

## Where to ask: #dev_training, publicly

When search comes up empty, post your question in the **#dev_training** channel of the [Discord server](https://discord.com/invite/K3JFd9d3wk). omegaUp coordinates on Discord rather than a traditional mailing list, so #dev_training *is* the mailing list — treat it as the public record it will become.

Two rules here, and both exist for the same reason — a public question helps far more people than a private one:

- **Post in the channel, never in a direct message.** A DM to a maintainer reaches exactly one person, who may be asleep, busy, or simply not the one who knows the answer. The same question in #dev_training reaches everyone, so the fastest available person answers, *and* the answer becomes searchable for the next person who hits your exact wall. If you found nothing in search, you are almost certainly not the last person who will need this.
- **Don't tag specific people.** We deliberately run an inclusive, anyone-can-jump-in culture, and @-ing one maintainer signals "this is between you and me" and quietly discourages everyone else from replying. Ask the room, not a person.

!!! important "GitHub is for confirmed bugs and design discussion, not for setup help"
    Discord is where you get *unstuck*. GitHub is where things get *tracked*. Once you have confirmed a reproducible bug in the code (not a problem with your own machine), open an issue at [omegaup/omegaup/issues](https://github.com/omegaup/omegaup/issues) with the reproduction steps. For feature ideas and longer-form design conversations, use [GitHub Discussions](https://github.com/omegaup/omegaup/discussions). Do not open a GitHub issue because `docker compose up` failed on your laptop — that is a #dev_training question until you have proven the bug lives in the repo and not in your environment.

## How to ask so you actually get answered

A good question front-loads everything a helper needs to diagnose you without a single follow-up. Vague questions get vague answers or silence; specific questions get specific fixes, because you have done the helper's first three questions for them. Include, up front:

- **What you were trying to do** and the exact command you ran.
- **What you expected** to happen versus **what actually** happened.
- **The full error message or log**, copy-pasted as text (not a screenshot of your terminal — nobody can search or copy from a screenshot).
- **What you have already tried**, so nobody wastes a reply suggesting the thing you did an hour ago.
- **Relevant environment details** when they could matter: your OS and version, Docker version, and — for omegaUp specifically — whether the containers finished booting (the dev stack can take **2–10 minutes** to come fully up the first time, and a lot of "it's broken" turns out to be "it wasn't ready yet").

### A question that gets answered

```markdown
Setting up the dev environment on Ubuntu 22.04. `docker compose up` fails.

Expected: all containers start and I can open the frontend on localhost:8001.
Actual: the frontend container never binds; I get a port-conflict error.

Error:
ERROR: for frontend  Cannot start service frontend: driver failed programming
external connectivity on endpoint omegaup-frontend-1:
Bind for 0.0.0.0:8001 failed: port is already allocated

What I've tried:
- `lsof -i :8001` showed a leftover process; I killed it and re-ran — same error.
- Waited ~10 min in case it was still booting.
- Searched Discord for "port already allocated", found one thread but it was
  about port 13306 (MySQL), not 8001.
```

That question names the port omegaUp actually publishes for the frontend (**8001**), shows the verbatim Docker error, proves the asker already ruled out the boot-time delay and a stale process, and even cites the near-miss thread they found — so whoever picks it up can go straight to the real cause instead of re-asking the obvious. A helper who knows the stack will immediately recognize the ports in play (frontend on **8001**, MySQL on **13306**, the Go grader on **21680**) and can zero in fast.

### A question that gets ignored

```markdown
docker not working help pls
```

!!! failure "Why this one dies unanswered"
    There is nothing to act on: no command, no error text, no OS, no sign of what "not working" means or what was already tried. Answering it requires four rounds of "what OS?", "what command?", "paste the error", "what have you tried?" — and most people will simply scroll past rather than start that interrogation. The fix is not more politeness; it is more information.

For a deeper treatment of this same idea, we recommend Mike Ash's short essay [*Getting Answers*](https://www.mikeash.com/getting_answers.html) — it is the canonical write-up of how to ask a technical question that people want to answer.

## Reply to the existing thread, don't start a new one

If your search turned up a thread that is *close* but the answer there did not resolve your case, reply in that thread rather than opening a fresh one. Two reasons, both about the next person: it keeps everything about one problem in one place, and it means whoever fixes it fixes it *for the record*, so the reader who hits this in six months finds the whole story — original symptom, failed attempts, working fix — in a single scroll instead of scattered across three half-answered threads. Reposting the same question in a new thread splits the knowledge and makes it likelier nobody ever writes down the real answer.

## Close the loop when it's solved

This is the step everyone forgets and it matters more than it looks. When your problem is resolved — whether someone helped you or you cracked it yourself — **go back to the thread and say how you solved it.**

The reason is concrete and slightly selfish on the community's behalf: if you leave the thread open, people who did not see your last message will keep reading it, keep thinking, and keep spending their time trying to help someone who is already unstuck. An unclosed thread quietly wastes the exact volunteer effort you were grateful for. And when the next person hits your identical error, your posted fix is the thread the search bar hands them. Say what worked, thank whoever helped, and if the fix differed from what was suggested, spell out the difference — that delta is often the most useful sentence in the whole thread.

## Help the next person

Getting help and giving help are the same loop viewed from two sides, so once you have your footing, read the questions other contributors post in #dev_training and answer the ones you can. This is not just good citizenship — **we take it into account when selecting GSoC candidates.** A contributor who reliably helps peers demonstrates exactly the collaboration the project runs on, and it shows up in how we evaluate applications. Practically, you rarely need to be an expert: pointing someone at the right doc page, recognizing an error you personally fought last week, or just confirming "yes, that 2–10 minute boot is normal, wait it out" is often the entire answer. Explaining a thing you just learned is also the fastest way to be sure you actually understand it.

## The short version

If you remember nothing else: **search first** (docs, Discord history, Google), **ask in #dev_training publicly** with your command, your verbatim error, and what you already tried, **reply to existing threads** instead of starting new ones, **post your fix** when it is solved so nobody keeps chasing a closed problem, and **help your peers** because the searchable archive that just saved you was built by people doing exactly that.

---

**Still stuck?** Jump into the [omegaUp Discord](https://discord.com/invite/K3JFd9d3wk) and ask in **#dev_training** — with your error pasted in and your OS named, you will usually have an answer before you finish your coffee.
