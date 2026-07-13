---
title: Badges
description: Achievement system implementation
icon: bootstrap/award
---

# Badges

Badges are the small achievements omegaUp awards to users — "solved 100 problems",
"coder of the month", "contest administrator". What makes them pleasant to work with is
that a badge is almost entirely **declarative**: you don't write code that decides who
earns it, you write a SQL query that *selects* who has earned it, drop it in a folder, and
omegaUp does the rest. Implementing one is a well-worn path.

## Adding a badge, step by step

1. **Pick an alias.** It must be unique and at most **32 characters**. Everything else is
   named after it.

2. **Create its folder.** Make a directory in
   [`frontend/badges/`](https://github.com/omegaup/omegaup/tree/main/frontend/badges) whose
   name is exactly the alias. From here on this is your `badgeFolder`.

3. **Add an icon (optional).** If the badge has a custom icon, put its SVG in `badgeFolder`
   as `icon.svg`.

4. **Write the awarding query.** Create `badgeFolder/query.sql` containing a single MySQL
   `SELECT` that returns the `user_id`s of every user who should receive the badge. This
   query *is* the badge's logic, so you need to know the shape of the data — keep the
   [database schema](https://github.com/omegaup/omegaup/blob/main/frontend/database/schema.sql)
   open while you write it, and aim for something simple and cacheable rather than clever.

5. **Add localizations.** Create
   [`badgeFolder/localizations.json`](https://github.com/omegaup/omegaup/blob/main/frontend/badges/legacyUser/localizations.json)
   with the badge's name and description translated into Spanish (`es`), English (`en`), and
   Portuguese (`pt`). The name may be at most **50 characters**.

6. **Load the localizations.** Run `./stuff/lint.sh` so the strings in `localizations.json`
   are propagated into the corresponding message files.

7. **Write the test.** Create `badgeFolder/test.json`. Its `testType` field chooses how the
   badge's unit test runs:

    - **`"testType": "apicall"`** — build the scenario by calling controller APIs to create
      the data the badge depends on (problems, users, contests, runs, …). You describe it
      with an `actions` array, whose entries can be:
        - `changeTime` — move the system clock, so you can test time-dependent badges.
        - `apicalls` — call a specific API, giving the calling user's username and password
          and the parameters. The APIs are all the public static `api…` methods on the
          controllers in
          [`frontend/server/src/Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers).
        - `scripts` — run one of omegaUp's cron scripts (`aggregateFeedback`, `assignBadges`,
          `updateUserRank`), which live in
          [`stuff/cron/`](https://github.com/omegaup/omegaup/tree/main/stuff/cron).

      End an `apicall` test with an `expectedResults` field listing the usernames that
      should receive the badge. See
      [`coderOfTheMonth/test.json`](https://github.com/omegaup/omegaup/blob/main/frontend/badges/coderOfTheMonth/test.json)
      for a worked example.

    - **`"testType": "phpunit"`** — write a classic PHPUnit test named `<alias>Test.php`,
      saved under
      [`frontend/tests/badges/`](https://github.com/omegaup/omegaup/tree/main/frontend/tests/badges),
      following the same structure as omegaUp's other unit tests (and free to use the
      [factories](https://github.com/omegaup/omegaup/tree/main/frontend/tests/factories)).

    Each has its trade-offs: prefer `phpunit` for a badge that would otherwise need many
    near-identical API calls; otherwise `apicalls` is the lighter option.

8. **Run the tests** to confirm your query and test actually award the badge to the right
   people:

    ```bash
    ./vendor/bin/phpunit --bootstrap frontend/tests/bootstrap.php \
      --configuration frontend/tests/phpunit.xml frontend/tests/badges/ --debug
    # or simply
    ./stuff/runtests.sh
    ```

9. **Open the pull request.** If nothing errored, your badge is ready — send it in.

For reference, two merged badge PRs make good templates to follow:
[Contest Administrator](https://github.com/omegaup/omegaup/pull/2602/files) and
[Virtual Contest Administrator](https://github.com/omegaup/omegaup/pull/2603/files).

If anything is unclear while you build one, don't hesitate to reach out — see
[Getting Help](../getting-started/getting-help.md).
