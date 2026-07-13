---
title: Vue Components
description: Vue.js component development and Storybook integration
icon: bootstrap/view-grid
---

# Vue Components

Almost all of omegaUp's UI is Vue. The old Smarty-to-Vue migration is done: the app currently ships **257 single-file `.vue` components** against a single server-side template (`frontend/templates/template.tpl`, a Twig 3 shell that just wraps a Vue entrypoint and injects its JSON payload). So when you build a page today, you are almost always building — or wiring together — Vue components, not writing server-rendered HTML.

We are on **Vue 2.7.16 + TypeScript 4.4.4**, using the Options API through `vue-property-decorator` (class-style components with `@Component` / `@Prop`). There is a separate, slow-moving migration to Vue 3 living in the root-level `vue-upgrade-tool/` and `vue-js-tutorial/` directories, but everything you write today targets Vue 2.7, so don't reach for `<script setup>` or the Composition API.

## Where components live

Every `.vue` file lives under `frontend/www/js/omegaup/`, and **248 of the 257** sit specifically in `frontend/www/js/omegaup/components/`. There is no `frontend/www/js/components/` — if you go looking there you'll find nothing.

Inside `components/` the tree is grouped by the part of the product a component belongs to, not by type. A handful of truly generic building blocks sit at the top level (`Markdown.vue`, `CountryFlag.vue`, `ToggleSwitch.vue`, `RadioSwitch.vue`, `Autocomplete.vue`, `DatePicker.vue`), and everything feature-specific lives in a named subdirectory: `arena/`, `badge/`, `contest/`, `course/`, `group/`, `problem/`, `user/`, `homepage/`, `notification/`, `submissions/`, `common/`, and about a dozen more. Put a new component next to its siblings — a new badge widget belongs in `components/badge/`, not at the root — so the person after you can find it by feature.

### A basic component

```vue
<template>
  <div class="my-component">
    <h1>{% raw %}{{ title }}{% endraw %}</h1>
    <button @click="handleClick">{% raw %}{{ T.commonSave }}{% endraw %}</button>
  </div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator';
import T from '../../lang';

@Component
export default class MyComponent extends Vue {
  @Prop({ required: true })
  title!: string;

  T = T; // expose the translation table to the template

  handleClick(): void {
    this.$emit('clicked');
  }
}
</script>
```

Two rules that will bite you if you ignore them, both because they show up in code review every single time:

**Never hardcode user-facing text.** All strings come from the `T` translation table (`frontend/www/js/omegaup/lang`), so the same component renders in Spanish, English, and Portuguese without a rewrite. `<div>Hello</div>` fails review; `{% raw %}{{ T.helloWorld }}{% endraw %}` passes. And when a string has a runtime value in it, don't concatenate — `{% raw %}{{ T.greeting }} {{ userName }}{% endraw %}` breaks in languages where the word order differs — use `ui.formatString(T.greeting, { name: userName })` so the placeholder lands wherever the translator put it.

**Prefer slots over behavior flags.** A component that flips large chunks of its own markup based on a `mode` or `variant` prop turns into a tangle nobody wants to touch. Expose named `<slot>`s and let the caller supply the differing parts, so one component keeps one job:

```vue
<template>
  <div>
    <slot name="header"></slot>
    <slot name="content"></slot>
  </div>
</template>
```

Same spirit for styling: reach for the CSS variables (`var(--color-primary)`) instead of a literal `#ff0000`, so a component picks up theme changes for free rather than pinning a hex value that someone has to hunt down later.

## Storybook

Storybook is where you develop and eyeball a component **in isolation**, without booting the whole app. It gives you an interactive workshop: render a component on its own, flip its props from a sidebar, and see every state and variation side by side. That decoupling is the point — you can build and review a `Badge` or a `ContestCard` without a running backend, a logged-in user, or the right database rows, and reviewers can pull up exactly the states you built.

We're on **Storybook 7.6** (`storybook@^7.6.21`), driving Vue through `@storybook/vue` `7.4.6` on the `@storybook/vue-webpack5` builder — the same Webpack 5 toolchain the real app builds with, so a component that renders in Storybook renders the same way in production.

### Running it

There's a dedicated script, and — unlike most of omegaUp — **you do not need Docker up** to use it:

```bash
yarn storybook
```

That runs `storybook dev -p 6006` (see the `storybook` entry in `package.json`), which compiles the story collection and serves a dashboard at [http://localhost:6006](http://localhost:6006). Leave it running; it hot-reloads as you edit a component or its story.

### How it's wired

The configuration is two files under `.storybook/`:

- **`.storybook/main.ts`** points Storybook at the stories with the glob `../frontend/www/js/omegaup/**/*.stories.@(js|jsx|ts|tsx)` — anywhere under `frontend/www/js/omegaup/`, so it also catches non-`components/` stories like the ones under `graderv2/`. It registers three addons (`addon-links`, `addon-essentials`, `addon-interactions`), sets `staticDirs: ['../frontend/www']` so relative asset paths resolve exactly as they do in the app, aliases `@` to `frontend/www/`, and teaches the shared Webpack config how to load `.vue`, `.scss`, `.css`, and image files. `docs.autodocs` is set to `'tag'`, so a story only gets an auto-generated docs page if you opt in by tagging it.
- **`.storybook/preview.ts`** loads the global CSS every component assumes is present: `third_party/bootstrap-4.5.0/css/bootstrap.min.css` (we are on **Bootstrap 4**, with `bootstrap-vue`, not Bootstrap 5) plus FontAwesome 5.15.4 injected into the iframe `<head>`. It also declares the `controls` matchers that make Storybook auto-pick the right widget — any arg ending in `color`/`background` gets a color picker, anything ending in `Date` gets a date picker — and an `actions` regex (`^on[A-Z].*`) that logs matching handlers in the Actions panel.

Without `preview.ts` loading Bootstrap and FontAwesome, your component would render unstyled and iconless in Storybook even though it looks fine in the app — that mismatch is exactly what this file exists to prevent.

### The coverage reality

Be honest with yourself about the state of this: there are **currently only 10 `.stories` files for 257 components**. Storybook is not a place where every component already lives; it's a place we're gradually moving them into. If you're touching a component and it has no story, adding one is a genuinely welcome, low-risk contribution.

### Writing a story

The convention is one story file per component, named after it and sitting **right next to the `.vue` file**: for `Badge.vue` you create `Badge.stories.ts` in the same folder. (This is why the glob is a `**` recursive match rather than a single stories directory — stories live wherever their components live.)

We write **Component Story Format 3 (CSF3)**: a default-exported `meta` object describing the component, then one named export per state you want to show, each a `StoryObj`. Here is the real `ToggleSwitch.stories.ts`, which is a good minimal template to copy:

```ts
import { StoryObj, Meta } from '@storybook/vue';
import ToggleSwitch, { ToggleSwitchSize } from './ToggleSwitch.vue';

const meta: Meta<typeof ToggleSwitch> = {
  component: ToggleSwitch,
  title: 'Components/ToggleSwitch',
  argTypes: {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore FIXME: vue-property-decorator is deprecated, so we can't get prop types from the component
    textDescription: {
      control: 'text',
    },
    checkedValue: {
      control: 'boolean',
    },
    size: {
      control: 'select',
      options: ToggleSwitchSize,
    },
  },
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    textDescription: 'Text for the check',
    checkedValue: false,
    size: ToggleSwitchSize.Large,
  },
  render: (args, { argTypes }) => ({
    components: { ToggleSwitch },
    props: Object.keys(argTypes),
    template:
      '<toggle-switch :text-description="$props.textDescription" :checked-value="$props.checkedValue" :size="$props.size" />',
  }),
};

Default.storyName = 'ToggleSwitch';
```

Reading that top to bottom:

- **`title`** (`'Components/ToggleSwitch'`) is the path in the Storybook sidebar — the slash makes a folder. Follow the existing grouping: top-level and generic components go under `Components/...`, arena widgets under `Arena/...` (see `ContestCardv2.stories.ts` titled `'Arena/ContestCard'`), and so on.
- **`argTypes`** declares each prop and, crucially, *which control renders it* in the dashboard: `control: 'text'` gives a text box, `'boolean'` a toggle, `'select'` with `options` a dropdown. This is what turns a static render into a knob-driven playground where a reviewer can exercise every state by hand.
- **That `@ts-ignore FIXME`** is not boilerplate you can delete — it's load-bearing. Because we author components with the deprecated `vue-property-decorator`, Storybook 7's typing can't infer prop types straight off the component class, so we suppress the resulting error on `argTypes`. Copy the comment as-is; it documents *why* the ignore is there for the next person.
- **`args`** are the concrete default values fed into those controls when the story first renders.
- **`render`** builds the actual Vue instance. The `props: Object.keys(argTypes)` line forwards every declared arg into the wrapper component so the controls are wired to real props, and the `template` string mounts the component with those props bound. You only need `render` when the default mounting isn't enough — for a simple component you can often omit it and let Storybook mount the component directly.
- **`storyName`** overrides the label shown for that individual story (otherwise it's derived from the export name, e.g. `Default`).

Some components take a whole object rather than flat props, and the render function is where you assemble it. `Badge.stories.ts` collects its args and passes them in as a single bound object — `template: '<badge :badge="$props" />'` — with `badge_alias` exposed as a `select` control over the full list of real badge aliases (`'100solvedProblems'`, `'coderOfTheMonth'`, `'problemSetter'`, …) so you can flip through every badge visually.

### Showing multiple states

The real value shows up when a component has meaningfully different states — build a named export for each. `ContestCardv2.stories.ts` is the model: it defines one reusable `Template`, then exports `Default`, `Recommended`, `Current`, `Future`, and `Past`, each spreading the base args and overriding just the fields that differ (a recommended flag, start/finish times an hour ago versus a day out) so all five contest states line up side by side in the sidebar:

```ts
export const Future = Template.bind({});
Future.args = {
  contest: {
    ...Default.args.contest,
    title: 'Future Contest',
    start_time: new Date(Date.now() + 86400000), // 1 day from now
    finish_time: new Date(Date.now() + 172800000), // 2 days from now
    active: false,
  } as types.ContestListItem,
};
```

Note the `as types.ContestListItem` cast: the mock data is typed against the **generated** API types in `frontend/www/js/omegaup/api_types.ts` (produced by `frontend/server/cmd/APITool.php`, marked `DO NOT EDIT`), so your fixtures stay honest with the shape the backend actually sends. If a field is missing or the wrong type, TypeScript tells you in the story before it ever reaches a page.

`ContestCardv2.stories.ts` is also written in the older CSF2 style (`Template.bind({})` with `Story` from `@storybook/vue`) rather than CSF3 — both work and both are in the tree — but prefer the CSF3 `StoryObj` form shown above for anything new; it's what Storybook 7 is built around and where the ecosystem is heading.

## Component testing

Alongside stories, components carry Jest unit tests named `Component.test.ts` in the same folder (you'll see `Countdown.test.ts`, `Markdown.test.ts`, `ToggleSwitch.test.ts`, and friends sitting right next to their `.vue` files). Use `@vue/test-utils` to mount and assert:

```ts
import { mount } from '@vue/test-utils';
import MyComponent from './MyComponent.vue';

describe('MyComponent', () => {
  it('renders title', () => {
    const wrapper = mount(MyComponent, {
      propsData: { title: 'Test' },
    });
    expect(wrapper.text()).toContain('Test');
  });
});
```

Think of the two as complementary: the story is the visual, human-in-the-loop check of how a component *looks* across its states; the test is the automated guarantee of how it *behaves*. A well-covered component has both.

## Related Documentation

- **[Coding Guidelines](coding-guidelines.md)** — the full Vue/TypeScript rules (jQuery is banned, `T` for all strings, `ui.formatString` for interpolation)
- **[Testing Guide](testing.md)** — Jest, Cypress, and how to run the suites
- **[Frontend Architecture](../architecture/frontend.md)** — how the Twig shell, Webpack entrypoints, and Vue components fit together
