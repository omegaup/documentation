---
title: Coding Guidelines
description: Coding standards and best practices for omegaUp development
icon: bootstrap/code
---

# Coding Guidelines

Most of the rules on this page are not enforced by a human reviewer scolding you in a pull request comment. They are checked automatically on GitHub by linters and integration tests, and wherever we can we push a rule down into that automation so it catches regressions on its own and frees the code review to focus on the interesting parts of your change. So think of this page less as a list of decrees and more as the reasoning behind what the machine is already going to tell you, written down so you understand *why* before the CI does it for you. The single meta-rule that everything else descends from: **prefer to explain _why_ things are done the way they are done** rather than restate _what_ the code obviously does.

You can check your code against nearly all of this locally, before you ever push, with:

```bash
./stuff/lint.sh validate
```

That script doesn't run the tools directly on your machine. It shells out to a pinned Docker image (currently `omegaup/hook_tools:v1.0.9`) so that every contributor gets byte-identical results from `yapf`, `prettier`, `phpcbf`, Psalm, and `mypy` regardless of what's installed on their laptop. Run it *outside* the container — if `OMEGAUP_ROOT` resolves to `/opt/omegaup`, the script refuses and tells you so, because that path only exists inside the dev container where Docker-in-Docker isn't available. Called with no arguments it guesses the set of files you changed (diffing against `upstream/main`, or `origin/main` if you haven't added the upstream remote) and runs in `fix` mode, editing them in place; pass `validate` when you only want it to report.

## General principles

**Declare types at every interface.** Every function must declare the types of its parameters and its return value — this is not optional and the static analyzers will fail the build without it. We use [TypeScript](https://www.typescriptlang.org/) (currently 4.4.4) in the frontend, [Psalm](https://psalm.dev/) (currently 4.29, configured in `psalm.xml`) for the PHP in `frontend/server/`, and [mypy](https://mypy-lang.org/) for the Python tooling under `stuff/`. Beyond the interface, it's also preferred to annotate the types of arrays and maps declared *inside* a function, because a bare `[]` or `array()` tells the next reader nothing about what it's meant to hold.

**Write everything in English** — code, identifiers, and comments alike. omegaUp is a project with contributors across many countries, and English is the one language everyone touching the code is assumed to read.

**New or changed behavior ships with tests.** Any change to functionality — a bug fix, a new feature, an altered edge case — must come with the new or modified tests that pin it down. This is a hard rule, not a nicety, and it is checked in CI.

**Avoid `null` and `undefined` wherever you can**, and especially in function parameters — this is where they do the most damage, and it deserves its own section below.

**Avoid functions (and Vue components) that fork their behavior on a flag.** A boolean parameter that makes a function do one substantially different thing when `true` and another when `false` is really two functions wearing a trench coat. Split them into two clearly-named functions and call the right one at the call site; in Vue, abstract the differing behavior into a [`slot`](https://vuejs.org/v2/guide/components-slots.html) so the caller supplies it. This keeps each unit doing one comprehensible thing.

**Use the [Guard Clause Pattern](https://refactoring.com/catalog/replaceNestedConditionalWithGuardClauses.html)** whenever possible — return early on the exceptional cases so the happy path isn't buried under nested `if`s.

**Delete dead code, never comment it out.** There must be no commented-out blocks lingering "just in case." If you need it back, it's in the git history — that is exactly what version control is for, and a commented block is just noise that rots and misleads.

**Minimize the distance between where a variable is declared and where it is first used.** The point is to shrink the amount of irrelevant code a reader has to hold in their head to know what a variable currently contains; declaring things at the top of a long function and using them fifty lines down forces everyone to keep re-scrolling.

**Comment the _why_, not the _what_.** A comment that says `// increment counter` above `counter++` is worse than no comment, because it's clutter that can silently go stale. Comments earn their place by explaining the non-obvious: the reasoning, the constraint, the historical gotcha that made the code look strange.

```php
// Bad — restates what the code plainly does:
// Increment counter
$counter++;

// Better — explains why this line exists at all:
// Count retries so we can back off once we exceed the rate-limit threshold.
$counter++;
```

### The `null`/`undefined` rule and why it exists

This deserves more than a bullet, because it's the rule people most often get wrong. `null` should only mean "the user didn't provide this," and `undefined` should only appear in the declaration of optional TypeScript parameters. Don't declare a type that can be *both* `null` and `undefined` at once — pick the one that carries meaning. 

Here is the reasoning that makes the rule non-negotiable rather than stylistic: **each parameter that can independently be `null` or `undefined` doubles the number of distinct input combinations the function must correctly handle, and that count grows exponentially.** Two nullable parameters is four combinations; four is sixteen; ten is over a thousand states you are implicitly claiming to have thought about and tested. **Keep the number of such combinations under 10.**

And when nullability *is* legitimate, the nullable fields must be able to be null *independently of one another*. If you find that a subset of parameters must always be passed together — all present or all absent — that's a signal they belong in their own type, not as loose optional arguments. For example, a custom validator needs both a language and a timeout, but only when custom validation is turned on at all:

```php
// Bad — validatorLanguage and validatorTimeout are secretly coupled to
// customValidator, but nothing in the signature says so, and they multiply
// the combination count:
function myFunc(
    \OmegaUp\DAO\VO\Problems $problem,
    bool $customValidator,
    ?string $validatorLanguage = null,
    ?int $validatorTimeout = null,
): void {
```

Group the coupled fields into an intermediate type, so "custom validation is on" and "here are its two required settings" become a single, indivisible piece of state:

```php
/**
 * @psalm-type ValidatorOptions=array{language: string, timeout: int}
 */
// ...
/**
 * @param null|ValidatorOptions $customValidatorOptions
 */
function myFunc(
    \OmegaUp\DAO\VO\Problems $problem,
    ?array $customValidatorOptions = null,
): void {
```

Now there is exactly one nullable parameter instead of three, `null` unambiguously means "no custom validation," and it's impossible to represent the nonsensical state of a language without a timeout.

### Naming

Use [camelCase](https://en.wikipedia.org/wiki/Camel_case) for function, variable, and class names. The exceptions where [snake_case](https://en.wikipedia.org/wiki/Snake_case) is correct are all places where the name is dictated by something outside our PHP/TypeScript world:

- MySQL column names
- Python variables and parameters (snake_case is the Python community norm, and `yapf`/`pylint` expect it)
- API parameters (they cross the wire and appear in `api_types.ts`, so their casing is a contract)

And **avoid abbreviations** in both identifiers and comments. `cnt`, `usr`, `tmp` save a few keystrokes for the author and cost every future reader a moment of "wait, what's that" — an abbreviation that's obvious to you is rarely obvious to everyone.

## Formatting

We deliberately do not argue about formatting; we delegate the entire question to automated tools so nobody spends a code review on brace placement. [`yapf`](https://github.com/google/yapf) formats Python, [`prettier`](https://prettier.io/) formats TypeScript and Vue, and [`phpcbf`](https://github.com/squizlabs/PHP_CodeSniffer) (the auto-fixing half of PHP_CodeSniffer) formats PHP. Running `./stuff/lint.sh` with no arguments applies all three to your changed files in place.

The rules those tools enforce, for reference:

- 2 or 4 spaces of indentation depending on the file type — never tabs.
- Unix line endings (`\n`), not Windows (`\r\n`).
- Opening brace on the same line as the statement that introduces it.
- A space between a keyword and its parenthesis for `if`, `else`, `while`, `switch`, `catch`, and `function` — but *no* space before the parenthesis of a function *call*.
- No spaces just inside parentheses.
- A space after every comma, none before.
- A space on both sides of every binary operator.
- At most one blank line in a row.
- No empty comments.
- Only `//` line comments; never `/* ... */` block comments.

```php
if (condition) {
    stuff;
}
```

## PHP

**Tests pass 100% before you commit — no exceptions.** Run them locally; a red suite is never "probably fine."

**Avoid O(n) database round trips.** A loop that calls a DAO method once per element — including anything that touches the auto-generated DAOs under `frontend/server/src/DAO/` — turns one logical operation into *n* network round trips to MySQL, and that's the classic way an endpoint that's snappy with test data falls over in production. Write a single manual query that does the whole job in one trip instead.

```php
// Bad — one query per user, N round trips to MySQL:
foreach ($users as $user) {
    $runs = \OmegaUp\DAO\Runs::getByUserId($user->user_id);
}

// Better — one query for all of them:
$runs = \OmegaUp\DAO\Runs::getByUserIds(
    array_map(fn ($u) => $u->user_id, $users)
);
```

**Only API functions may receive `\OmegaUp\Request`.** The `apiXxx` methods on the controllers under `frontend/server/src/Controllers/` (in the `\OmegaUp\Controllers` namespace) are the boundary where an untyped, user-supplied request enters the system — for instance `\OmegaUp\Controllers\Run::apiCreate(\OmegaUp\Request $r)`, which validates the request and then, once everything checks out, hands the work off with `\OmegaUp\Grader::getInstance()->grade(...)`. Every function *behind* that boundary must take typed parameters instead. So each `apiXxx` method's job is to validate the request, extract each field into a correctly-typed local variable, and then call the internal functions with those variables — never to pass `$r` deeper into the code. This keeps the typed core of the system genuinely typed and confines all the "did the user actually send this field" uncertainty to one thin layer.

**Document every function** in the block-comment style Psalm and the reviewers expect — a one-line summary, a short explanation of *why* it exists when that isn't obvious, and `@param`/`@return` annotations:

```php
/**
 * set
 *
 * If cache is on, save the value under key with the given timeout.
 *
 * @param string $value
 * @param int $timeout
 * @return boolean
 */
public function set($value, $timeout) { ... }
```

**Report errors with exceptions**, not sentinel return values. A function that returns `true`/`false` is fine when the boolean is a genuinely expected answer ("does this user exist?"), but "something went wrong" is what exceptions are for.

**All APIs return associative arrays.** This is what `\OmegaUp\ApiCaller` serializes back to the client and what `frontend/server/cmd/APITool.php` reads to generate the typed frontend client, so the shape is a contract, not a convenience.

**Use [RAII](https://en.wikipedia.org/wiki/Resource_Acquisition_Is_Initialization)** when it fits, mainly for resource management (files, locks, and the like) — tie a resource's lifetime to an object's so cleanup can't be forgotten on an early return or an exception.

## Vue

omegaUp's UI is Vue 2.7.16 single-file components (currently mid-migration to Vue 3, tracked in the root `vue-upgrade-tool/` and `vue-js-tutorial/` directories) under `frontend/www/js/omegaup/components/`. A few rules keep those components maintainable and translatable.

**Prefer `slot`s over behavior flags**, for the same reason as functions: a component that radically changes what it renders based on a boolean prop is two components fused together. Expose the varying part as a [`slot`](https://vuejs.org/v2/guide/components-slots.html) and let the caller fill it in. If several call sites want the same variant, wrap it in *another* component that provides that slot.

**Never hardcode user-facing text.** The whole interface has to render in multiple languages, so every string the user sees comes from a translation key (`T.someKey`), not a literal. And **don't concatenate translation strings** — word order differs between languages, so gluing fragments together produces garbage in some of them. Use `ui.formatString` with named parameters so the translation itself controls the ordering:

```html
<!-- Bad — the fixed word order can't survive translation:
     contestRanking = "Contest ranking: "
-->
<div>{{ T.contestRanking }} {{ user.rank }} {{ user.username }}</div>

<!-- Better — the whole sentence, with slots, lives in the translation string:
     contestRanking = "Contest ranking: %(rank) %(username)"
-->
<div>{{ ui.formatString(T.contestRanking, { rank: user.rank, username: user.username }) }}</div>
```

**Don't hardcode colors** as hex or `rgb(...)`. Declare them as CSS variables and reference those, because dark mode works by swapping the variable values — a literal `#ffffff` is a white square that dark mode can't reach.

**Avoid lifecycle hooks unless the component genuinely touches the DOM** — and try to avoid touching the DOM in the first place. In a reactive framework, reaching for `mounted()` to poke at an element is usually a sign that some state should have been reactive instead. Which is the other half of this: **prefer [computed properties and watchers](https://vuejs.org/v2/guide/computed.html)** over manually recomputing and reassigning variables. Let Vue's reactivity track the dependencies for you rather than doing it by hand and getting it subtly wrong.

**Add a Storybook story for every new component**, and update the story when you change a component's props or states. Storybook (currently 7.6) lets you develop and eyeball a component in isolation, decoupled from the rest of the app — good for reuse and for reviewers who want to see every state without clicking through the live site. You don't even need Docker up to run it:

```bash
yarn storybook
```

That launches the dashboard at [localhost:6006](http://localhost:6006). To add a story, drop a `Component.stories.ts` file next to the component (e.g. `Badge.stories.ts` beside `Badge.vue`), import the component, and export a `meta` plus one `StoryObj` per state you want to showcase:

```ts
import { StoryObj, Meta } from '@storybook/vue';
import Badge from './Badge.vue';

const meta: Meta<typeof Badge> = {
  component: Badge,
  // argTypes turns props into interactive controls in the dashboard.
  argTypes: {},
};
export default meta;

type Story = StoryObj<typeof meta>;

export const Unlocked: Story = {
  // args are the props passed to the component for this story.
  args: {
    badge_alias: '100solvedProblems',
    unlocked: true,
  },
};
```

Coverage here is still thin — currently around 10 story files against 257 components — so a new story is nearly always a net addition, not a duplicate.

## TypeScript

**When a function grows past 2–3 parameters** — and *especially* if several share the same type, and *definitely* if several are optional — switch to a single object parameter. Positional arguments of the same type are a bug waiting to happen (`updateProblem(problem, currentVersion, previousVersion)` silently swaps two strings and typechecks fine); named object fields make the call self-documenting and order-independent:

```ts
// Bad — four positional params, two of them interchangeable strings:
function updateProblem(
  problem: Problem,
  previousVersion: string,
  currentVersion: string,
  points?: number,
): void { ... }

// Better — one object, every argument named at the call site:
function updateProblem({
  problem,
  previousVersion,
  currentVersion,
  points,
}: {
  problem: Problem;
  previousVersion: string;
  currentVersion: string;
  points?: number;
}): void { ... }
```

**Avoid [type assertions](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-assertions).** An `as` cast is you overriding the compiler, so it's only allowed where the compiler genuinely can't know the type:

- interacting with the DOM (`document.querySelector` and friends);
- annotating an empty literal, e.g. `null as null | string` or `[] as Foo[]`;
- in tests, to declare `params` in the Vue constructor.

**Don't touch the generated API client by hand.** `frontend/www/js/omegaup/api.ts` and `frontend/www/js/omegaup/api_types.ts` both begin with `// generated by frontend/server/cmd/APITool.php. DO NOT EDIT.` — they are regenerated from the PHP controllers' `@omegaup-request-param` annotations and DAO types, so an edit you make there is one `APITool.php` run away from being silently overwritten. Change the PHP, then regenerate.

**Don't use jQuery!** It has been deprecated and can no longer be used anywhere in the codebase. Reach for the framework (Vue reactivity, refs) or plain DOM APIs instead.

## Python

The Python here is the ~24 tooling scripts under `stuff/`, checked by `mypy`, `flake8`, and `pylint` and formatted by `yapf`.

**Past 2–3 parameters, make them keyword-only** — the same reasoning as the TypeScript object rule, expressed the Pythonic way with a bare `*` in the signature so callers *must* name each argument:

```python
# Bad — positional, and previous/current are easy to swap:
def update_problem(problem: Problem, previous_version: str,
                   current_version: str, points: Optional[int] = None) -> None: ...

# Better — the leading * forces every caller to name its arguments:
def update_problem(
    *,
    problem: Problem,
    previous_version: str,
    current_version: str,
    points: Optional[int] = None,
) -> None: ...
```

**Use snake_case for functions and variables, CamelCase for classes** — standard Python style, which `pylint` enforces.

**Import modules, not names.** Avoid `from module import function`; import the module and use dotted access, so at every call site it's obvious where `function` came from and there's no ambiguity about which `function` you meant:

```python
# Bad — where did function come from three screens later?
from module import function
function()

# Better — the origin travels with every call:
import module
module.function()
```

The one exception is the `typing` module, where `from typing import Optional, List` is idiomatic and universally understood.

## Related documentation

- **[Testing Guide](testing.md)** — how to write the tests that every functional change requires
- **[Useful Commands](useful-commands.md)** — the day-to-day development commands
- **[Components Guide](components.md)** — building Vue components in depth

---

**Remember:** almost everything above is enforced by automation, so run `./stuff/lint.sh validate` before you commit and let the tools catch it first.
