---
title: Supported Languages
description: Programming languages supported by omegaUp
icon: bootstrap/code-tags
---

# Supported Languages

omegaUp accepts submissions in a fixed set of languages — the `language` column on a run is
an enum, so a submission is always one of the identifiers below and nothing else. The list
below is that enum, exactly as the database defines it. When you submit through the
[API](api.md), you pass one of these short identifiers (e.g. `cpp17-gcc`), not a
human-readable name.

Two conventions apply across every compiled language, and they trip people up if they don't
know them:

- **Your entry point must be called `Main`.** There is no per-problem build configuration;
  the runner compiles by convention. The main source file (and, for languages that need it,
  the main class) must be named `Main` — `Main.java` with `public class Main`, a `Main`
  executable for C/C++, and so on. See [Runner Internals](../architecture/runner-internals.md)
  for how compilation actually happens inside the sandbox.
- **Where a language offers both GCC and Clang**, the identifier names the toolchain
  explicitly (`-gcc` vs `-clang`), because the two occasionally disagree on borderline
  standard-conformance and a problem-setter may have tested against one of them.

## The languages

### C and C++

The workhorses of competitive programming, and the reason the C++ list is so long — each
standard revision is a separate identifier so an older problem keeps compiling the way it
always did:

| Identifier | Language |
| ---------- | -------- |
| `c` | C (legacy GCC) |
| `c11-gcc`, `c11-clang` | C11 |
| `cpp` | C++ (legacy GCC) |
| `cpp11`, `cpp11-gcc`, `cpp11-clang` | C++11 |
| `cpp17-gcc`, `cpp17-clang` | C++17 |
| `cpp20-gcc`, `cpp20-clang` | C++20 |

For new C++ submissions you almost always want `cpp17-gcc` or `cpp20-gcc`.

### Other general-purpose languages

| Identifier | Language |
| ---------- | -------- |
| `java` | Java |
| `kt` | Kotlin |
| `py3` | Python 3 |
| `py2` | Python 2 |
| `py` | Python (legacy alias) |
| `cs` | C# |
| `rb` | Ruby |
| `pl` | Perl |
| `pas` | Pascal |
| `hs` | Haskell |
| `lua` | Lua |
| `go` | Go |
| `rs` | Rust |
| `js` | JavaScript |

### The special ones

Three identifiers are not general-purpose languages, and knowing what they are explains a
lot about who omegaUp is built for:

- **`kp` and `kj` — Karel.** omegaUp grew out of the Mexican Olympiad in Informatics, whose
  entry-level track uses **Karel the Robot**, a teaching language where you program a robot
  on a grid. `kp` is Karel with Pascal-flavoured syntax and `kj` is Karel with Java-flavoured
  syntax — the same language, two surface grammars, so a beginner can use whichever their
  class taught. Karel problems are a first-class citizen, not a novelty.
- **`cat` — output-only.** For problems where you don't submit a program at all, you submit
  the *answer*. The `cat` "language" means the runner simply treats your submission as the
  output to be validated against the expected output. It is how output-only and
  data-file problems work.

!!! note "The set changes over time"
    New standards and toolchains are added as they mature (the C++ list is the clearest
    record of that). Treat the table above as current; the authoritative source is the
    `language` enum in [`frontend/database/schema.sql`](https://github.com/omegaup/omegaup/blob/main/frontend/database/schema.sql)
    and the compiler versions configured in the runner ([omegaup/quark](https://github.com/omegaup/quark)).
