---
title: Adding a Notification Type
description: How to wire a brand-new notification end-to-end, from the Notifications table through the Vue bell dropdown
icon: bootstrap/bell
---

# Adding a New Notification Type

The little bell in the navbar with the red count badge on it is fed by exactly one table and one Vue component. Once you understand how those two talk to each other, adding a new kind of notification — "you earned a badge", "your contest registration was accepted", "an admin left you feedback" — is a small, mechanical change. This page walks the whole path in the order the data actually travels: something happens on the server, a row lands in the `Notifications` table, `apiMyList` hands it to the navbar, and `Notification.vue` decides how to draw it.

The one idea to hold onto before anything else: a notification is just **a `user_id` plus a blob of JSON**. Everything interesting lives in that JSON `contents` column, and the whole design is that the server decides *what to say* while the frontend decides *how to say it* based on a single `type` discriminator. Get the JSON shape right and most of the work is done.

## The data model: one row, one JSON blob

Notifications live in the `Notifications` MySQL table, exposed through the usual DAO/VO pair — [`frontend/server/src/DAO/Notifications.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Notifications.php) (the public DAO) and [`frontend/server/src/DAO/VO/Notifications.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/VO/Notifications.php) (the value object). A row has only five columns: `notification_id`, `user_id`, `timestamp`, `read`, and `contents`. Four of those are bookkeeping the platform manages for you — the primary key, whose bell it belongs to, when it fired, and whether the user has dismissed it. The `read` column matters more than it looks: the whole "unread count" and the mark-as-read flow hang off that single boolean, and a notification is only ever surfaced while `read = 0`.

Everything you actually design goes into **`contents`, which is a JSON string**. At minimum it must carry a `type`:

```json
{
  "type": "yourNotificationType",
  "any_field": "whatever payload this type needs"
}
```

The `type` field is the discriminator that tells [`Notification.vue`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/components/notification/Notification.vue) which layout to render — with an image or without, which icon, whether it links somewhere, what text to show. The remaining keys are a free-form **payload**: name them whatever the type needs, because their only job is to carry the specific data that layout will interpolate. The classic minimal example, straight out of the badge cron, is a two-field blob where `badge` is the payload:

```json
{
  "type": "badge",
  "badge": "500score"
}
```

That says "this is a badge notification, and the badge in question is `500score`" — which is enough for the frontend to find the badge art, build the sentence, and link to the badge page.

## The `contents` schema is a real, generated type

The shape of `contents` is not folklore; it is a Psalm type that gets compiled into TypeScript, so the frontend and backend agree on it at build time. The canonical definition is the `@psalm-type NotificationContents` annotation at the top of [`frontend/server/src/Controllers/Notification.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Notification.php#L8):

```php
@psalm-type NotificationContents=array{
    type: string,
    badge?: string,
    message?: string,
    status?: string,
    url?: string,
    body?: array{
        localizationString: string,
        localizationParams: list<string, string>,
        url: string,
        iconUrl: string
    }
}
```

[`APITool.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/cmd/APITool.php) reads that annotation and regenerates the mirror interface in [`frontend/www/js/omegaup/api_types.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/api_types.ts) (search for `interface NotificationContents` — it carries the DO-NOT-EDIT banner because it is generated). So if your new notification needs a brand-new top-level field in `contents` — something that isn't already `badge`, `message`, `status`, `url`, or the `body` object — you edit the `@psalm-type` in `Notification.php`, then regenerate `api_types.ts` so the Vue side can read your field without TypeScript complaining. If you can express your data inside the existing `body` payload (see below), you can skip this step entirely, which is one more reason to prefer it.

## Two rendering styles: the per-type switch vs. the localized `body`

Here is the single most important decision, and the reason to read `Notification.vue` before you write any server code. There are **two ways** a notification gets drawn, and they live side by side in the same component:

1. **The legacy per-`type` switch.** For a handful of hardcoded types (`badge`, `demotion`, `general_notification`), `Notification.vue` has explicit `switch (this.notification.contents.type)` arms that pick an icon, build the text, and compute the link from the payload fields directly. Every one of those getters ends in a `default:` arm, so an unrecognized type still renders — it just gets the generic `/media/info.png` icon and no text.

2. **The localized `body` path.** If `contents.body` is present, it wins over the switch for icon, text, and URL alike — every getter checks `if (this.notification.contents.body)` first and returns from the `body` before it ever reaches the `switch`. The `body` carries a `localizationString` (a translation key), `localizationParams` (values to interpolate), a `url`, and an `iconUrl`. This is the modern, i18n-friendly path, and it is why newer notification types don't need a single new line of Vue: they hand the component a translation key and it renders generically.

The practical upshot: **for a new type, use the `body` path unless you genuinely need custom markup.** It means you add a translation string and call one PHP helper, and you never touch `Notification.vue`. The per-type switch is only worth it when the layout itself is special (badges, for instance, build an `<img>` path from the payload and need bespoke styling).

### What the switch actually does

To see why the `body` path is easier, look at what you'd otherwise have to add. `Notification.vue` computes four things off `contents`, and each is a getter with the same shape — check `body` first, then switch on `type`:

- **`iconUrl`** — `body.iconUrl` if a body exists; otherwise `badge` → `/media/dist/badges/${badge}.svg`, `demotion` → `/media/banned.svg` when `status == 'banned'` else `/media/warning.svg`, `general_notification` → `/media/email.svg`, and everything else → `/media/info.png`.
- **`text`** — `body`-based notifications render Markdown instead (see next), so `text` only serves the plain arms: `demotion` and `general_notification` both return `contents.message` (or `''` if it's absent), and every other type returns `''`.
- **`notificationMarkdown`** — if a `body` exists, it's `ui.formatString(T[body.localizationString], body.localizationParams)`; otherwise the only non-empty arm is `badge`, which builds `ui.formatString(T.notificationNewBadge, { badgeName: T['badge_' + badge + '_name'] })`. That resolves against the translation string `notificationNewBadge = "You have received a new badge: **%(badgeName)**."` in [`frontend/templates/en.lang`](https://github.com/omegaup/omegaup/blob/main/frontend/templates/en.lang), which is why badge notifications come out as bold Markdown.
- **`url`** — `body.url` if a body exists; otherwise `general_notification` → `contents.url`, `badge` → `/badge/${badge}/`, and `demotion` → `''` (there's a standing `// TODO: Add link to problem page.` right there in the source, a good example of the kind of half-finished edge you'll find and shouldn't be surprised by).

Notice that adding a type to the switch means touching **four getters** and getting the icon, text, markdown, and link all consistent — versus the `body` path, where you supply those four things as data in one JSON object.

## Naming the type: add a constant, don't sprinkle string literals

The type string is shared between the server that writes it and the Vue that reads it, so it wants a single source of truth. The DAO already collects them as class constants at the top of [`frontend/server/src/DAO/Notifications.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Notifications.php) — currently around twenty of them, including `CERTIFICATE_AWARDED = 'certificate-awarded'`, `CONTEST_REGISTRATION_ACCEPTED = 'contest-registration-accepted'`, `CONTEST_REGISTRATION_REJECTED = 'contest-registration-rejected'`, `COURSE_SUBMISSION_FEEDBACK = 'course-submission-feedback'`, `DEMOTION = 'demotion'`, and a dozen more course/contest registration and clarification variants. Add your new type there as a constant so the whole PHP side refers to `\OmegaUp\DAO\Notifications::YOUR_TYPE` rather than a bare string that can drift out of sync with a typo.

One wrinkle worth knowing so it doesn't trip you up: the older switch types in `Notification.vue` (`badge`, `general_notification`) are *not* in that constant list — they predate it and are written as raw literals in places like the badge cron. The constants are all kebab-case (`certificate-awarded`); the legacy switch types are snake/lower (`general_notification`). That's not a rule you need to obey, just a seam between the old and new styles you'll notice. New types should follow the constant convention.

## Creating the notification from the server

There are two realistic places a notification is born: inside a PHP request, or from a Python cron.

### From PHP: use the Notification controller helpers

`\OmegaUp\Controllers\Notification` (in [`Notification.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Notification.php)) exists precisely so you don't hand-roll the DAO insert. For a localized `body`-style notification aimed at a list of users, the one-liner is `setCommonNotification`, which takes the user IDs, a `\OmegaUp\TranslationString`, the type, a URL, and the localization params, and assembles the whole `body` blob for you (it even fills in `iconUrl` as `/media/info.png` by default):

```php
\OmegaUp\Controllers\Notification::setCommonNotification(
    userIds: $userIds,
    localizationString: new \OmegaUp\TranslationString('notificationYourNewString'),
    notificationType: \OmegaUp\DAO\Notifications::YOUR_TYPE,
    url: "/somewhere/{$alias}/",
    localizationParams: ['contestTitle' => $contest->title],
);
```

Under the hood that calls `setNotification(userIds, contents)`, which loops the user IDs into `\OmegaUp\DAO\VO\Notifications` value objects and persists them with `\OmegaUp\DAO\Notifications::createBulk(...)`. The `createBulk` name is deliberate: it does a single bulk `INSERT` instead of one query per user, turning what would be O(N) round-trips into O(1) — which matters when you're notifying every participant of a contest at once. If you need something the helper doesn't model, the fuller example is `createForCourseAccessRequest`, which json-encodes a complete `body` (with its own `localizationString`, `localizationParams`, `url`, and `iconUrl`) by hand and calls `\OmegaUp\DAO\Notifications::create(...)` for a single user.

### From Python cron: insert the row directly

Crons don't go through the PHP controller — they write the `Notifications` row themselves. The badge assigner, [`stuff/cron/assign_badges.py`](https://github.com/omegaup/omegaup/blob/main/stuff/cron/assign_badges.py), is the reference: in `save_new_owners` it builds a tuple per new badge owner and executes a plain `INSERT INTO Notifications (user_id, contents) VALUES (%s, %s)`, where `contents` is `json.dumps({'type': 'badge', 'badge': badge})`. That's the whole trick — the cron only has to produce the same JSON shape the frontend expects; the `notification_id`, `timestamp`, and `read` columns take their defaults. If you're adding a cron-driven notification, mirror this: build your `contents` dict with a `type` and payload, `json.dumps` it, and insert.

## Adding the translation string

If you took the `body` path (and you should), the `localizationString` you passed has to actually exist, or `ui.formatString(T[...], ...)` on the frontend resolves to `undefined`. Add your key to [`frontend/templates/en.lang`](https://github.com/omegaup/omegaup/blob/main/frontend/templates/en.lang) — and to `es.lang` and `pt.lang` alongside it — using the same `%(paramName)` interpolation the params object provides. The badge string is the pattern to copy: `notificationNewBadge = "You have received a new badge: **%(badgeName)**."`, where `%(badgeName)` lines up with the `badgeName` key handed to `formatString`. The value renders as Markdown, so `**bold**` and links work.

## Teaching Notification.vue to render it (only if you skipped `body`)

If your notification uses `body`, stop — you're done with the frontend, because the generic `body` arm in each getter already renders it. Only if you need a bespoke layout do you edit [`Notification.vue`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/components/notification/Notification.vue): add a `case 'yourType':` arm to the `iconUrl`, `text`/`notificationMarkdown`, and `url` getters so the icon, wording, and link are all covered, and add whatever scoped SCSS the layout needs at the bottom of the file. Keep them consistent — a type that returns a URL from `url` but nothing from the text getters will render as an empty clickable row, which is confusing. This is the path the wiki warns about: "this format will only work if the appropriate styles are created or adjusted in the Vue component."

## The read path: how the row gets back to the bell

It's worth seeing the return trip once, because it explains why `read` and `user_id` matter and where to look when a notification "doesn't show up."

When the navbar loads, [`frontend/www/js/omegaup/common/navbar.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/common/navbar.ts) calls the API `Notification.myList`, which hits `apiMyList` in the controller. That endpoint runs `ensureIdentity()` (you must be logged in), fetches rows via `\OmegaUp\DAO\Notifications::getUnreadNotifications($r->user)` — a query that selects `notification_id`, `contents`, and `timestamp` `WHERE user_id = ? AND read = 0 ORDER BY timestamp ASC` — `json_decode`s each `contents` string into the `NotificationContents` array, and `array_reverse`s the list so the newest sit on top. So: if your inserted row has `read` already truthy, or the wrong `user_id`, it silently never appears. That's the first thing to check when a notification goes missing.

The decoded list flows into `List.vue` (the dropdown), which shows the FontAwesome bell, a red count badge equal to `notifications.length`, and one `Notification.vue` per entry keyed by `notification_id`. Clicking a single notification, or "mark all as read", emits a `read`/`read-notifications` event back up to `navbar.ts`, which calls `Notification.readNotifications({ notifications: [...ids] })` and then re-fetches `myList` to refresh the badge. On the server, `apiReadNotifications` calls `ensureMainUserIdentity()`, then for each id loads the row and **checks that `notification->user_id === r->user->user_id`, throwing `ForbiddenAccessException` otherwise** (so you can't mark someone else's notifications read by guessing IDs), throws `NotFoundException` for an unknown id, and finally sets `read = true` and updates. If a notification carried a `url`, clicking it both marks it read and navigates there — which is why the `url` getter and `handleClick` in `Notification.vue` emit the `remove` event with the URL attached.

## The checklist, end to end

Pulling it together, adding a new notification type is, in order:

1. **Add a `type` constant** to `\OmegaUp\DAO\Notifications` so both sides share one spelling.
2. **Decide the payload shape.** Prefer the `body` path (`localizationString` + `localizationParams` + `url` + `iconUrl`) so the frontend renders it generically. Only invent new top-level `contents` fields if `body` can't express it — and if you do, update the `@psalm-type NotificationContents` in `Notification.php` and regenerate `api_types.ts` with `APITool.php`.
3. **Add the translation string** to `en.lang`/`es.lang`/`pt.lang` with matching `%(param)` placeholders.
4. **Emit the notification** — from PHP via `\OmegaUp\Controllers\Notification::setCommonNotification(...)` (or `createBulk` for many users), or from a cron with a direct `INSERT INTO Notifications (user_id, contents)` whose `contents` is `json.dumps({...})`.
5. **Only if you skipped `body`:** add the matching `case` arms to `Notification.vue`'s `iconUrl` / text / `url` getters plus any scoped styles.
6. **Verify** by logging in as the target user and watching the bell — remembering that the row must have `read = 0` and the correct `user_id` to ever surface.

!!! tip "When in doubt, ask"
    If you're unsure which `type` and payload shape fit your case, the maintainers would rather you ask than guess — raise it in the `#depto_tecnico` channel on Slack (or the developer channels on the omegaUp [Discord](https://discord.gg/gMEMX7Mrwe)). :)

## Related documentation

- **[Database Patterns](database-patterns.md)** — the DAO/VO layer the `Notifications` table rides on, including the `contents` JSON shape.
- **[Vue Components](components.md)** — component conventions, i18n with `ui.formatString`, and Storybook.
- **[Coding Guidelines](coding-guidelines.md)** — the PHP and TypeScript rules these changes must pass.
