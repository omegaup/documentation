---
title: Migration Guide
description: The house style for building a page in Vue + TypeScript on top of the Twig shell, plus the current Vue 2 to Vue 3 upgrade.
icon: bootstrap/arrow-right
---

# Migration Guide: How We Build a Page

Once upon a time this page described a migration in flight: pull a Smarty `.tpl`
apart, hand the data to a Vue component, delete the template. That migration is
**done**. The frontend is now Vue single-file components end to end — as of this
writing 257 `.vue` files and 414 `.ts` files against a single application
template, `frontend/templates/template.tpl`, and that lone survivor is a Twig 3
shell, not Smarty. Smarty is gone; HHVM is gone; the backend is plain PHP 8.1
running under php-fpm behind nginx.

So read this page two ways. First, the step-by-step below is no longer a
one-time chore — it is **the house style** for wiring any new page into omegaUp,
because every page still travels the same road: a PHP controller assembles a
typed `payload`, the Twig shell serializes it into the HTML, a TypeScript
entrypoint parses it back, and a Vue component renders it. Learn this path once
and you can add a page without asking anyone how the plumbing works. Second, the
one migration that *is* still live is **Vue 2.7 → Vue 3**; the codemod and the
learning materials for that effort live in the repo already, and there's a
section at the bottom on where to point your attention for it.

## The Road a Page Travels

Before the checklist, hold the whole pipeline in your head, because every step
below is just one station on it. When a browser asks for, say, the sign-in page,
the controller method `\OmegaUp\Controllers\User::apiLoginDetailsForTypeScript`
(in `frontend/server/src/Controllers/User.php`) builds an array with two
important keys: an `entrypoint` naming which compiled TypeScript bundle should
run, and a `templateProperties` holding the `payload` (the data the page needs)
and a `title`. The Twig shell renders that payload verbatim into the page as
`<script type="text/json" id="payload">…</script>` — you can see the exact line
in `frontend/templates/template.tpl` — and then `{% entrypoint %}` drops in the
`<script>` tag for the compiled bundle, followed by an empty
`<div id="main-container"></div>` for Vue to mount into. On the client, the
entrypoint `.ts` file reads that JSON back through a generated parser, `new
Vue(...)`s a component into `#main-container`, and hands it the payload as props.

That is the road. Notice the field is `templateProperties`, **not**
`smartyProperties` — if you find the old name in a years-old branch, that's the
Smarty-era spelling and it no longer exists in the codebase. Notice too that the
controller never renders HTML; it returns data, and the shell + the entrypoint
do the rendering. Keeping that division is the whole point: PHP owns the data and
its types, Vue owns the pixels.

## Step 1 — Configure the PHP Payload

Start on the server, because the types you define here are the contract the whole
front end is generated from.

Find the controller method that serves your page. The convention is a method
suffixed `ForTypeScript` — for the sign-in view that's
`apiLoginDetailsForTypeScript` in `frontend/server/src/Controllers/User.php`. Its
job is to gather every piece of data the page needs and put it under
`templateProperties['payload']`. Anything the component will render must live
inside that `payload`; anything left outside it never reaches the browser.

Once the data is assembled, give the payload a **Psalm type**. This is not
optional bookkeeping — it is the single source of truth from which the TypeScript
types and the runtime parser are auto-generated. You declare the type as a
`@psalm-type` annotation and reference it in the method's `@return` docblock. In
`User.php` the sign-in method is annotated:

```php
/**
 * @return array{
 *   entrypoint: string,
 *   templateProperties: array{
 *     payload: LoginDetailsPayload,
 *     title: \OmegaUp\TranslationString
 *   }
 * }
 */
```

`LoginDetailsPayload` is a named Psalm type declared elsewhere in the file, and
that name is exactly what you'll parse against on the client — so choose it well.
Two more fields in that return shape earn their keep:

- **`title`** is a `\OmegaUp\TranslationString`, not a bare string. It must
  resolve to an `omegaupTitle…` key that exists in all three of `en.lang`,
  `es.lang`, and `pt.lang`, because omegaUp renders the page title in whatever
  language the account is configured for. Skip the `.lang` entry and the title
  renders as the raw key.
- **`entrypoint`** is the name of the compiled bundle that will render this
  payload — a plain string like `'login_signin'`. It does not have to exist yet;
  you'll create it in Step 2. It maps to an entry in the Webpack config (more on
  that in a moment).

When the payload and its type are in place, run `stuff/lint.sh`. Do this before
you touch any TypeScript, **because** the linter is what regenerates the client's
type definitions and the runtime parser from your Psalm type — the
`.ts` files you're about to write depend on that generated output existing. The
generated files are `frontend/www/js/omegaup/api_types.ts` (the type shapes and
the `payloadParsers`) and `frontend/www/js/omegaup/api.ts` (the typed
`apiCall<>` wrappers); both are produced by `frontend/server/cmd/APITool.php` and
both open with a `// generated by … DO NOT EDIT.` banner, so never hand-edit
them — fix the Psalm type and re-run the linter instead. You can also run
`stuff/runtests.sh` to confirm your controller change didn't break anything on
the PHP side.

## Step 2 — Wire Up the TypeScript Entrypoint

Thanks to the unified Twig shell, you don't touch `template.tpl` at all — the
shell already knows how to serialize your payload and inject the entrypoint
script. If the PHP side is correct, all your client work happens in the
entrypoint `.ts` file.

!!! note "Coming from a `.js` file?"
    If you're actually converting an old `.js` file to `.ts`, follow these same
    steps — but take advantage of the fact that most of the logic already exists.
    Don't rewrite it from scratch; get the existing behavior compiling under
    TypeScript first, then improve it.

First, make sure the `entrypoint` name you chose in Step 1 is registered in the
Webpack config and points at a real file. The frontend entries live in
`webpack.config-frontend.js` at the repo root; the sign-in entry is a single
line there:

```js
login_signin: './frontend/www/js/omegaup/login/signin.ts',
```

If that file doesn't exist yet, create it. The shape is boilerplate you can copy
from any neighboring entrypoint — `schools/schoolofthemonth.ts` is a clean,
minimal example. Every entrypoint imports the same core helpers (`OmegaUp` for
the ready hook, `types` for the parsers, `api` for typed API calls, `ui`, the
translation function `T` from `../lang`, `Vue`, and the component it mounts),
waits for the page to be ready, parses the payload, and mounts a Vue instance
into `#main-container`:

```ts
import { OmegaUp } from '../omegaup';
import { types } from '../api_types';
import Vue from 'vue';
import schoolOfTheMonth_List from '../components/schoolofthemonth/List.vue';

OmegaUp.on('ready', () => {
  const payload = types.payloadParsers.SchoolOfTheMonthPayload();
  new Vue({
    el: '#main-container',
    components: { 'school-of-the-month-list': schoolOfTheMonth_List },
    // …pass payload fields down as props here…
  });
});
```

The load-bearing line is `types.payloadParsers.SchoolOfTheMonthPayload()`. That
parser reads the `<script id="payload">` JSON the Twig shell wrote and returns it
**typed** as the exact shape you defined in PHP. The parser name is your Psalm
type name — `LoginDetailsPayload` in PHP becomes
`types.payloadParsers.LoginDetailsPayload()` in the entrypoint. If the parser you
want doesn't exist, it's almost always because the Psalm type is wrong or you
haven't re-run `stuff/lint.sh` since adding it — go back to Step 1, fix the type,
regenerate. Don't reach for `JSON.parse` or hand-roll the shape; the whole point
of the generated parser is that PHP and TypeScript can never disagree about what
the payload contains.

Two habits keep entrypoints clean. Do your **API calls here in the `.ts` file**,
not inside the component — the entrypoint fetches, the component displays.
`common/navbar.ts` is the canonical example of an entrypoint that calls an API
and feeds the result to its component. And import only what you use; the linter
will flag the rest.

## Step 3 — Build the Vue Component (Bootstrap 4)

The component receives, as props, the data your entrypoint parsed — and those
props carry the exact generated types from Step 1. Import them from
`api_types.ts` and type your `@Prop`s against them so a payload-shape change in
PHP surfaces as a compile error in the component, not a runtime surprise in
production:

```vue
<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator';
import { types } from '../../api_types';

@Component
export default class SchoolOfTheMonthList extends Vue {
  @Prop({ required: true })
  schools!: types.SchoolOfTheMonthPayload['schools'];
}
</script>
```

A few rules here are non-negotiable, and each has a reason:

- **Bootstrap 4, not 3, and not 5.** omegaUp is on `bootstrap ^4.6.0` with
  `bootstrap-vue ^2.21.2`, and the shell loads Bootstrap 4 CSS. Every class you
  use must be a BS4 class. If you're touching a `.vue` file that predates the
  migration and still carries BS3 markup, migrate it to BS4 in the same change —
  **if you don't, it won't work**, because the unified shell only ships the BS4
  stylesheet and BS3 class names will silently render unstyled.
- **Avoid `id` attributes** inside components. The same component can be mounted
  more than once on a page, and duplicate `id`s are invalid HTML that breaks
  `document.getElementById` and accessibility tooling. Reach for a class or a
  `data-` attribute instead. If you genuinely must set an `id` (some third-party
  widget demands one), there is an escape hatch — an existing component flag that
  suppresses the linter's reserved-attribute check — but treat needing it as a
  smell.

The rest of the house rules for component code are short enough to state
outright, and they exist across every SFC in the tree:

- **Don't use jQuery.** We're a reactive component framework now; reaching into
  the DOM by hand fights the framework and desynchronizes Vue's virtual DOM from
  what's on screen.
- **Prefer the guard-clause pattern** — return early on the exceptional cases so
  the happy path reads top-to-bottom without deep nesting.
- **HTML element and attribute names in kebab-case; method names in camelCase.**
  Consistency here is what lets you grep the codebase and actually find things.
- **Use ES6 template-literal interpolation** rather than string concatenation —
  it's shorter and there's less to get wrong.
- **`let` and `const`, never `var`.** Block scope removes an entire category of
  hoisting bugs.
- **Strip debug logging before you commit.** `console.log` left in a component
  ships to every user's console.

## Step 4 — Test the Component in Jest

A new or modified component wants a test, and Codecov will point at the exact
lines your change left uncovered. Component tests use `@vue/test-utils`'
`shallowMount`, which renders the component one level deep (child components
become stubs) so you're testing this component in isolation rather than its whole
subtree. The pattern, taken from
`frontend/www/js/omegaup/components/arena/Arena.test.ts`, is to mount with
`propsData`, then assert on rendered text:

```ts
import { shallowMount } from '@vue/test-utils';
import arena_Arena from './Arena.vue';

describe('Arena.vue', () => {
  it('Should handle details for a contest', () => {
    const wrapper = shallowMount(arena_Arena, {
      propsData: { title: 'Hello omegaUp', activeTab: 'problems' },
    });
    expect(wrapper.find('.clock').text()).toBe('∞');
    expect(wrapper.find('div[data-arena-wrapper]>div>h2>span').text()).toBe(
      'Hello omegaUp',
    );
  });
});
```

Note the assertions target `.clock` and a `[data-arena-wrapper]` selector — not
an `id` — which is exactly why Step 3 tells you to avoid `id`s: class and
`data-` selectors are what your tests hang onto. Copy a neighboring test as a
starting point; the shape barely varies between components.

## The Live Migration: Vue 2 → Vue 3

Everything above describes building on the current stack — **Vue 2.7.16** with
TypeScript 4.4.4, the Options API via `vue-property-decorator`, Vuex 3, Webpack
5. That is what runs in production today. The one migration still in motion is
lifting the whole front end from Vue 2.7 to Vue 3, and the tooling for it already
sits at the repo root:

- **`vue-upgrade-tool/`** is a vendored codemod (built on `vue-metamorph`) that
  mechanically transforms Vue 2 code to Vue 3 — JS/TS files, SFCs, and unit
  tests alike. Heed its own warning: **the results are not guaranteed perfect,
  and you must manually verify every change it makes.** It also doesn't format
  its output nicely, so run Prettier/ESLint over anything it touches to bring the
  code back in line with our conventions.
- **`vue-js-tutorial/`** holds the learning material for getting comfortable with
  the Vue 3 idioms before you start converting real components.

Because 2.7 is the final Vue 2 release, much of your existing 2.7 code — the
`<script lang="ts">` SFCs, the typed props, the `payloadParsers` handshake — is
already close to Vue 3 shape, which is exactly why the pipeline in Steps 1–4
stays valid through the upgrade. The controller/payload/entrypoint/component road
doesn't change; what changes underneath is the component runtime. When you
convert a component, run the codemod, verify it by hand, re-run its Jest test,
and reformat before committing.

## Related Documentation

- [Coding Guidelines](coding-guidelines.md) — the full set of Vue and TypeScript
  standards these steps draw on.
- [Components Guide](components.md) — deeper conventions for component structure.
- [Frontend Architecture](../architecture/frontend.md) — how the Twig shell, the
  entrypoints, and the components fit together at large.
