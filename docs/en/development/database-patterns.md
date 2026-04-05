---
title: Database Patterns
description: Understanding DAO/VO patterns in omegaUp
icon: bootstrap/table
---

# Database Patterns: DAO/VO

omegaUp uses the **DAO/VO (Data Access Object / Value Object)** pattern for all database interactions.

## Pattern Overview

### Value Objects (VO)
- Map directly to database tables
- One VO class per table
- Auto-generated from schema
- Located in `frontend/server/src/DAO/VO/`

### Data Access Objects (DAO)
- Static classes for database operations
- One DAO class per table
- Methods: `search()`, `getByPK()`, `save()`, `delete()`
- Located in `frontend/server/src/DAO/`

## Example Usage

### Searching Users

```php
// Create a VO with search criteria
$user = new Users();
$user->setEmail('user@example.com');

// Search using DAO
$results = UsersDAO::search($user);

// Process results
if (count($results) > 0) {
    $foundUser = $results[0];
    echo "User ID: " . $foundUser->getUserId();
    echo "Username: " . $foundUser->getUsername();
}
```

### Creating a Record

```php
// Create new VO
$problem = new Problems();
$problem->setTitle('My Problem');
$problem->setAlias('my-problem');
$problem->setAuthorId($userId);

// Save using DAO
ProblemsDAO::save($problem);
```

### Getting by Primary Key

```php
// Get user by ID
$user = UsersDAO::getByPK($userId);
if ($user !== null) {
    echo $user->getUsername();
}
```

## Key Principles

### No Direct SQL in Controllers
Controllers never write SQL directly. They use DAOs:

```php
// ✅ Good: Using DAO
$runs = RunsDAO::searchByUserId($userId);

// ❌ Bad: Direct SQL
$runs = $conn->query("SELECT * FROM Runs WHERE user_id = ...");
```

### Avoid O(n) Queries
Create manual queries for single round trips:

```php
// ❌ Bad: Multiple queries
foreach ($users as $user) {
    $runs = RunsDAO::searchByUserId($user->userId);
}

// ✅ Good: Single query
$userIds = array_map(fn($u) => $u->userId, $users);
$runs = RunsDAO::searchByUserIds($userIds);
```

## Auto-Generation

VO and DAO classes are auto-generated from the database schema:

1. Modify database schema (add migration)
2. Run `./stuff/update-dao.sh`
3. VO and DAO classes are regenerated

## User notifications (`Notifications` table)

The web UI loads pending rows for a user from the **`Notifications`** table. Each row’s **`contents`** column is JSON that drives rendering in [`Notification.vue`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/components/notification/Notification.vue).

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

### Localized “system” style (`body`)

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

tells the UI to render a badge-style notification; the extra fields are interpreted in `Notification.vue`. For a concrete server-side example, see [`stuff/cron/assign_badges.py`](https://github.com/omegaup/omegaup/blob/main/stuff/cron/assign_badges.py) in the main repository.

!!! tip "Questions"
    Ask in the omegaUp [Discord](https://discord.gg/gMEMX7Mrwe) developer channels if you are unsure which `type` and payload to use.

## Related Documentation

- **[Backend Architecture](../architecture/backend.md)** - Backend structure
- **[Database Schema](../architecture/database-schema.md)** - Schema overview
- **[Coding Guidelines](coding-guidelines.md)** - PHP guidelines
