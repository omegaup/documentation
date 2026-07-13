---
title: Database Patterns
description: Understanding DAO/VO patterns in omegaUp
icon: bootstrap/table
---

# Database Patterns: DAO/VO

Every byte omegaUp reads from or writes to MySQL 8.0 goes through one narrow door: the **DAO/VO** layer under `frontend/server/src/DAO/`. Controllers never open a `mysqli` connection, never concatenate a `SELECT`, and never see a raw result row. They ask a Data Access Object for typed objects and hand typed objects back. The reason is not aesthetic — it is that omegaUp is a contest platform where a scoreboard query firing during a live event with thousands of concurrent submissions has to be predictable, reviewable, and injection-proof. Centralizing all SQL in one layer means every query is prepared (parameterized), every query is greppable, and the expensive ones are cacheable in exactly one place.

The layer has three tiers, and the split matters because two of them are machine-written and one is yours:

- **VO (Value Object)** — `frontend/server/src/DAO/VO/`. One dumb, typed data-holder class per table. Auto-generated. Do not edit.
- **Base DAO** — `frontend/server/src/DAO/Base/`. One `abstract` class per table holding the boilerplate CRUD SQL (create/read-by-primary-key/update/delete). Auto-generated. Do not edit.
- **Public DAO** — `frontend/server/src/DAO/`. One class per table that `extends` its Base and is where **you** add the hand-written queries the generator can't guess. This is the only tier you touch by hand.

Both generated tiers open with the same shouting header, and it is load-bearing:

```php
/** ************************************************************************ *
 *                    !ATENCION!                                             *
 *                                                                           *
 * Este codigo es generado automáticamente. Si lo modificas, tus cambios     *
 * serán reemplazados la proxima vez que se autogenere el código.            *
 * ************************************************************************* */
```

If you see that banner at the top of a file, anything you write in it will be silently reverted the next time someone runs the generator. That is why the public DAO tier exists as a *separate file* extending the base — so your custom methods live somewhere the generator will never overwrite.

## The VO: a typed row, and nothing more

A Value Object maps one-to-one to a table. Take [`frontend/server/src/DAO/VO/Runs.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/VO/Runs.php), the object for the `Runs` table (the judged result of a submission). It `extends \OmegaUp\DAO\VO\VO`, declares a `FIELD_NAMES` constant listing exactly the columns that exist, and exposes one public typed property per column with its schema default baked in:

```php
class Runs extends \OmegaUp\DAO\VO\VO {
    const FIELD_NAMES = [
        'run_id' => true,
        'submission_id' => true,
        'version' => true,
        'commit' => true,
        'status' => true,
        'verdict' => true,
        // ...
    ];

    /** @var string */
    public $status = 'new';   // a fresh Run starts life as 'new'

    /** @var float */
    public $score = 0.00;

    /** @var \OmegaUp\Timestamp */
    public $time;             // CURRENT_TIMESTAMP
}
```

The constructor takes an optional `?array $data` — the associative row you'd get straight out of `mysqli` — and does three jobs before it trusts a single value. First it rejects garbage: `array_diff_key($data, self::FIELD_NAMES)` catches any column that isn't in the table, and an unknown column throws `Unknown columns: ...` immediately, so a typo'd SELECT alias blows up at hydration instead of silently surfacing a `null` three layers up. Second it *coerces* every field to its declared type — `run_id` through `intval`, `score` through `floatval`, `commit` through `strval` — because a raw `mysqli` row hands you strings for everything and omegaUp runs under Psalm with strict types, so a stringy `"42"` where an `int` is expected is a static-analysis failure. Third, timestamps get special handling: `time` is round-tripped through `\OmegaUp\DAO\DAO::fromMySQLTimestamp()` into an `\OmegaUp\Timestamp` (omegaUp's internal POSIX-seconds wrapper), and if the row omits `time` entirely the VO defaults it to `new \OmegaUp\Timestamp(\OmegaUp\Time::get())` — "now" — rather than leaving it null.

The field-level PHPDoc is worth reading rather than skipping, because it carries semantics the column name hides. On `Runs`, `commit` is documented as *"El hash SHA1 del commit en la rama master del problema con el que se realizó el envío"* and `version` as *"El hash SHA1 del árbol de la rama private"* — i.e. these two look like generic strings but are git object hashes tying a judged run to the exact problem revision it ran against. Strip that comment and the next person treats them as opaque text and breaks rejudging.

The shared base [`\OmegaUp\DAO\VO\VO`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/VO/VO.php) gives every VO three ways out to the wire: `asArray()` (via `get_object_vars`) for JSON marshaling, `asFilteredArray($filters)` to emit only a whitelisted subset of fields (used constantly in API responses so a controller can return, say, a user's public columns without leaking the password hash), and `__toString()` which is just `json_encode` of `asArray()`. A VO is deliberately behavior-free: no queries, no validation beyond type coercion, no business rules. It is a suitcase for a row.

## The Base DAO: the CRUD you never write

The generated abstract base holds the four operations that are identical for every table, differing only in column list. Look at [`frontend/server/src/DAO/Base/Runs.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Base/Runs.php): it's an `abstract class Runs` whose every method is `final public static`, so the queries are called as `RunsDAO::getByPK(...)` and a subclass can't accidentally shadow them. Every method funnels through the singleton `\OmegaUp\MySQLConnection::getInstance()` and — this is the whole security argument — uses `?` placeholders with a separate `$params` array, never string interpolation:

```php
final public static function getByPK(int $run_id): ?\OmegaUp\DAO\VO\Runs {
    $sql = '
        SELECT `Runs`.`run_id`, `Runs`.`submission_id`, /* ...all columns... */
        FROM `Runs`
        WHERE (`run_id` = ?)
        LIMIT 1;';
    $params = [$run_id];
    $row = \OmegaUp\MySQLConnection::getInstance()->GetRow($sql, $params);
    if (empty($row)) {
        return null;
    }
    return new \OmegaUp\DAO\VO\Runs($row);
}
```

`getByPK` returns `?\OmegaUp\DAO\VO\Runs` — the `?` is not decoration, it's the contract: **a miss returns `null`, and the caller must handle it.** `create()` runs the `INSERT`, then writes the freshly minted auto-increment id back onto the VO (`$Runs->run_id = ...->Insert_ID()`) and returns the affected-row count, so after a create you can read the new primary key straight off the object you passed in. `update()` returns `Affected_Rows()`. `delete()` is the sharp one: if the `DELETE` touches zero rows it doesn't return quietly, it throws `\OmegaUp\Exceptions\NotFoundException('recordNotFound')`, on the logic that asking to delete a row that isn't there is a bug in the caller, not a no-op — and the docblock warns that a deleted object *cannot* be resurrected by re-inserting, because `create()` will mint a new primary key rather than reuse the old one.

Two generated helpers exist purely so tests and hot paths don't pay for hydration they won't use. `existsByPK($run_id)` runs `SELECT COUNT(*)` and returns a `bool` "**sin necesidad de cargar sus campos**" — cheaper than `getByPK` when you only need to know *whether* a row exists, because you skip building the VO. `countAll()` returns the total row count the same way, mostly for tests that assert on cardinality.

`getAll()` is the one Base method with a landmine, and the generator documents it inline: it reads the *entire* table into an array of VOs, "*consume una cantidad de memoria proporcional al número de registros regresados*". It defaults to 100 rows per page (`$filasPorPagina = 100`), ordered by the primary key `run_id` ascending, and it hardens the two parameters that would otherwise be injection vectors — the sort column is passed through `MySQLConnection::escape()` and the direction through `Validators::validateInEnum($tipoDeOrden, 'order_type', ['ASC', 'DESC'])` — because unlike a `?` value, a column name and sort direction can't be a bound parameter and have to be sanitized by hand. Use `getAll()` on `Countries` or `Languages`; never reach for it on `Runs` or `Submissions`, which have millions of rows.

## The base `DAO` utility class

Sitting under all of this is [`\OmegaUp\DAO\DAO`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/DAO.php), a `final` class of static helpers the generated code leans on. It owns transactions — `transBegin()`, `transEnd()`, and `transRollback()` wrap `MySQLConnection`'s `StartTrans()` / `CompleteTrans()` / `FailTrans()` — so when a controller needs several writes to succeed or fail together (create a problem, its ACL, and its problemset in one shot) it brackets them in `DAO::transBegin()` / `DAO::transEnd()`. It owns the timestamp bridge (`toMySQLTimestamp` / `fromMySQLTimestamp`) that translates between omegaUp's `\OmegaUp\Timestamp` and MySQL's `'Y-m-d H:i:s'` in UTC via `gmdate`. And it exposes `isDuplicateEntryException($e)`, which lets a caller catch a unique-key collision (a duplicate username, say) and turn it into a friendly validation error instead of a 500 — it inspects a `\OmegaUp\Exceptions\DatabaseOperationException` and asks `->isDuplicate()`.

## When to write a custom DAO method

The generated base covers exactly one access shape: single-table, single-row, keyed by primary key. The moment you need a `JOIN`, an aggregate, a filtered list, or a batched write, the generator has nothing for you and you write the method by hand in the public DAO. That's not a workaround — it's the designed seam. The public class `extends` the base, inherits all the free CRUD, and adds whatever the feature needs.

[`frontend/server/src/DAO/Runs.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Runs.php) is the vivid example: around forty hand-written methods layered on top of the seven inherited ones. Most are joins the base could never express, like `getBestProblemScore`, which walks from a `Submissions` row to its current `Runs` row to find a user's top score on a problem:

```php
final public static function getBestProblemScore(
    int $problemId,
    int $identityId
): ?float {
    $sql = '
        SELECT r.score * 100
        FROM Submissions s
        INNER JOIN Runs r ON s.current_run_id = r.run_id
        WHERE s.identity_id = ? AND s.problem_id = ? AND
              r.status = "ready" AND s.`type` = "normal"
        ORDER BY r.score DESC, r.penalty ASC
        LIMIT 1;';
    $val = [$identityId, $problemId];
    /** @var float|null */
    return \OmegaUp\MySQLConnection::getInstance()->GetOne($sql, $val);
}
```

Notice the `/** @var float|null */` annotation right before the return. `mysqli` hands back untyped scalars and `GetOne` / `GetAll` return `mixed`, so Psalm can't know the shape on its own; the `@var` (and, for multi-column rows, a full array-shape docblock like `@return list<array{alias: string, contest_score: float|null, guid: string, ...}>`) is how the custom DAO stays type-safe and, crucially, how the shape flows all the way out to TypeScript. Those return-shape annotations are read by `frontend/server/cmd/APITool.php`, the generator that produces `frontend/www/js/omegaup/api_types.ts` — so a sloppy docblock on a DAO method surfaces as a wrong type in the Vue frontend.

The other reason to hand-write a method is to **collapse round-trips**, and this is where the scaffold's "avoid O(n) queries" rule gets its teeth. The anti-pattern is calling a per-row DAO method inside a loop:

```php
// ❌ Bad: one query per user — O(n) round-trips to MySQL
foreach ($users as $user) {
    $notification = new \OmegaUp\DAO\VO\Notifications([/* ... */]);
    \OmegaUp\DAO\Notifications::create($notification);
}
```

Each iteration is a full network round-trip to MySQL; a hundred users is a hundred sequential trips, and under contest load that's how you melt the database. The fix is a single custom method that does the batch in one query. [`\OmegaUp\DAO\Notifications::createBulk`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Notifications.php) is the canonical write-side version, and its docblock states the win plainly — *"reducing database round-trips from O(N) to O(1)"* — by building one multi-row `INSERT` with a placeholder tuple per row:

```php
public static function createBulk(array $notifications): int {
    if (empty($notifications)) {
        return 0;
    }
    $rowPlaceholders = [];
    $params = [];
    foreach ($notifications as $notification) {
        $rowPlaceholders[] = '(?, ?, ?, ?)';
        $params[] = is_null($notification->user_id) ? null : intval($notification->user_id);
        $params[] = \OmegaUp\DAO\DAO::toMySQLTimestamp($notification->timestamp);
        $params[] = intval($notification->read);
        $params[] = $notification->contents;
    }
    $sql = 'INSERT INTO `Notifications` (`user_id`, `timestamp`, `read`, `contents`)
            VALUES ' . join(', ', $rowPlaceholders) . ';';
    \OmegaUp\MySQLConnection::getInstance()->Execute($sql, $params);
    return \OmegaUp\MySQLConnection::getInstance()->Affected_Rows();
}
```

Sending 500 badge notifications after a cron run is one `INSERT` instead of 500. Even here the `?` discipline holds — the placeholders are generated, the values stay bound. `Notifications` also shows the third job of the public DAO tier: it hoists the table's domain vocabulary into class constants (`Notifications::DEMOTION`, `Notifications::CERTIFICATE_AWARDED`, `Notifications::CONTEST_CLARIFICATION_REQUEST`, …) so the rest of the codebase refers to notification kinds by name, not by magic string.

## The query philosophy: *sencillito, carismático y cacheable*

The maintainers have a phrase for the queries that back the pages contestants hit hardest — a contest's public landing, a scoreboard, a problem list. The wiki describes the ideal contest-details query as *"un query sencillito, carismático y cacheable"*: little, charismatic, and cacheable. It's a joke, but it's also the actual design rule. "Little" means it touches few tables and returns the minimum the page needs — mini-ranking, time remaining, problem stubs — not the whole object graph. "Cacheable" means it's deterministic and read-mostly, so the result can be memoized and served without touching MySQL at all. When you're deciding whether to add a custom DAO method or fatten an existing one, this is the bar: if the query is on a hot read path, make it small enough that its result can live in Redis.

## Caching with Redis (and APCu)

The cache lives in [`frontend/server/src/Cache.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Cache.php). `\OmegaUp\CacheAdapter` is an abstraction over two backends selected by `OMEGAUP_CACHE_IMPLEMENTATION` in `config.default.php` — the default is `'apcu'` (per-process in-memory, fine for a single box), and production flips it to `'redis'`, which `pconnect`s to `REDIS_HOST` (`'redis'`) on `REDIS_PORT` (`6379`) and authenticates with `REDIS_PASS`. Everything above the adapter is backend-agnostic, so DAO and controller code never knows or cares which store is behind it.

Cache entries are namespaced by a **prefix constant**, and reading the list of them in `Cache.php` is the fastest way to learn what omegaUp considers worth caching: `Cache::PROBLEM_STATEMENT` (`'statement-'`), `Cache::USER_PROFILE` (`'profile-'`), `Cache::CONTESTANT_SCOREBOARD_PREFIX` (`'scoreboard-'`), `Cache::CONTEST_INFO` (`'contest-info-'`), `Cache::PROBLEMS_LIST` (`'problems-list-'`), `Cache::RUN_COUNTS` (`'run-counts-'`), and a couple dozen more. A full key is `prefix + id` — e.g. the profile cache for user `omegaup` is `profile-omegaup`.

The one method you'll reach for is `getFromCacheOrSet` — read-through caching in a single call:

```php
$accessibleAclIds = \OmegaUp\Cache::getFromCacheOrSet(
    \OmegaUp\Cache::PROBLEM_IDENTITY_TYPE,   // prefix
    $cacheKeyId,                             // id
    fn () => /* the sencillito query goes here */,  // computed only on a miss
    $timeout                                 // TTL in seconds
);
```

On a hit it returns the cached value and the closure never runs; on a miss it runs the closure, stores the result under the key with the given TTL, and returns it. Under the hood `set`/`get`/`delete` each short-circuit when the cache is disabled (`isEnabled()` false) — `get` returns `null`, `set` and `delete` return `false` — so a box with no cache backend degrades to hitting MySQL every time rather than crashing, and every hit/miss/store is logged through Monolog under the channel name `cache` for when you need to see why something is or isn't being served from cache.

TTLs are per-domain and tuned to how fast the underlying data goes stale, all in `config.default.php` as seconds. The global default `APC_USER_CACHE_TIMEOUT` is `7 * 24 * 3600` — seven days — for data that essentially never changes. But a live contest's info is cached for only `10` seconds (`APC_USER_CACHE_CONTEST_INFO_TIMEOUT`), a problem statement for `60`, a problem list for `60 * 30` (thirty minutes), and sessions for `8 * 3600` to match the auth-token lifetime. `APC_USER_CACHE_PROBLEM_STATS_TIMEOUT` is `0`, meaning "cache with no expiry, until explicitly invalidated." These numbers are the current tuning and are meant to be revisited — pick a TTL by asking how wrong the page is allowed to be and for how long.

### Invalidation: TTL, targeted delete, or version bump

Because most writes go through DAOs but the cache is keyed by domain concepts, **invalidation lives in the controllers next to the write, not inside the DAO.** When a controller mutates something that a cache entry depends on, it deletes that entry by exact key. The profile-verification path in [`Controllers/User.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/User.php) does exactly this right after flipping a user's verified flag:

```php
// Expire profile cache
\OmegaUp\Cache::deleteFromCache(
    \OmegaUp\Cache::USER_PROFILE,
    strval($identity->username)
);
```

The rule of thumb: if a write makes a cached value wrong *right now* and a stale read would confuse a user (a just-verified account still showing as unverified), delete the specific key so the next read recomputes it; if a little staleness is harmless, let the TTL expire it on its own.

For the case where you'd otherwise have to delete hundreds of keys sharing a prefix — every scoreboard for a contest, say — there's `invalidateAllKeys($prefix)`, and its implementation is the clever bit. It does **not** scan and delete matching keys. Instead it keeps a version integer per prefix (`v{prefix}`) that's woven into every real key, and invalidation just increments it (`inc("v{prefix}")`). Old keys still physically sit in Redis but are now unreachable because every new read and write uses the bumped version, so they're never fetched or updated again and simply age out. One `INCR` invalidates an entire namespace in O(1) instead of an O(n) sweep — the same *sencillito* instinct applied to cache management itself.

## Regenerating the DAO and VO layer

You never hand-write a Base DAO or a VO. You change the schema and let the generator rewrite them. The source of truth is `frontend/database/schema.sql`; after you edit it (typically alongside a migration authored with `stuff/db-migrate.py`), run:

```sh
./stuff/update-dao.sh
```

That script copies `schema.sql` to `frontend/database/dao_schema.sql` to trigger regeneration, then runs `stuff/update-dao.py`, which rewrites everything under `frontend/server/src/DAO/Base/` and `frontend/server/src/DAO/VO/` from the templates in `stuff/dao_templates/` (with `stuff/dao_utils.py` and a `stuff/dao_linter.py` keeping the output consistent). Your hand-written methods in the public `frontend/server/src/DAO/` classes are untouched, because they live in different files — which is the entire reason for the base-vs-public split. If you find yourself wanting to edit a file that carries the `!ATENCION!` banner, stop: you either want a custom method in the public DAO, or you want a schema change and a regeneration.

## User notifications (`Notifications` table)

The web UI loads pending rows for a user from the **`Notifications`** table via [`\OmegaUp\DAO\Notifications::getUnreadNotifications`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Notifications.php) — itself a hand-written DAO method that selects `read = 0` rows ordered oldest-first. Each row's **`contents`** column is JSON that drives rendering in [`Notification.vue`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/components/notification/Notification.vue).

### JSON shape

At minimum, include a `type` string so the component picks the correct layout. Other keys are a **payload** specific to that type.

```json
{
  "type": "notificationType",
  "any_field": "value"
}
```

### Supported `type` values (high level)

| `type` | Purpose | Typical payload |
|--------|---------|-----------------|
| `badge` | Badge earned | `badge` — badge identifier (e.g. score milestone name) |
| `demotion` | Account/status change | `status`, `message` |
| `general_notification` | Free-form text | `message`, optional `url` |

### Localized "system" style (`body`)

For translations via the i18n system, you can use:

```json
{
  "type": "notification-type",
  "body": {
    "localizationString": "translationKey",
    "localizationParams": {
      "param1": "value1"
    },
    "url": "/path/to/resource",
    "iconUrl": "/media/icon.png"
  }
}
```

### Example (badge)

Inserting a row whose `contents` resembles:

```json
{
  "type": "badge",
  "badge": "500score"
}
```

tells the UI to render a badge-style notification; the extra fields are interpreted in `Notification.vue`. For a concrete server-side example, see [`stuff/cron/assign_badges.py`](https://github.com/omegaup/omegaup/blob/main/stuff/cron/assign_badges.py) — a cron that assigns badges and is exactly the kind of job that fans out many notifications, so it inserts them through `Notifications::createBulk` rather than one row at a time.

!!! tip "Questions"
    Ask in the omegaUp [Discord](https://discord.gg/gMEMX7Mrwe) developer channels if you are unsure which `type` and payload to use.

## Related Documentation

- **[Backend Architecture](../architecture/backend.md)** - Backend structure
- **[Database Schema](../architecture/database-schema.md)** - Schema overview
- **[Coding Guidelines](coding-guidelines.md)** - PHP guidelines
