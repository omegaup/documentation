---
title: Patrones de bases de datos
description: Comprender los patrones DAO/VO en omegaUp
icon: bootstrap/table
---
# Patrones de base de datos: DAO/VO

omegaUp utiliza el patrón **DAO/VO (Objeto de acceso a datos/Objeto de valor)** para todas las interacciones de la base de datos.

## Descripción general del patrón

### Objetos de valor (VO)
- Mapear directamente a las tablas de la base de datos.
- Una clase de VO por mesa.
- Generado automáticamente a partir del esquema.
- Ubicado en `frontend/server/src/DAO/VO/`

### Objetos de acceso a datos (DAO)
- Clases estáticas para operaciones de bases de datos.
- Una clase DAO por mesa
- Métodos: `search()`, `getByPK()`, `save()`, `delete()`
- Ubicado en `frontend/server/src/DAO/`

## Ejemplo de uso

### Buscando usuarios

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
### Creando un registro

```php
// Create new VO
$problem = new Problems();
$problem->setTitle('My Problem');
$problem->setAlias('my-problem');
$problem->setAuthorId($userId);

// Save using DAO
ProblemsDAO::save($problem);
```
### Obteniendo la clave principal

```php
// Get user by ID
$user = UsersDAO::getByPK($userId);
if ($user !== null) {
    echo $user->getUsername();
}
```
## Principios clave

### Sin SQL directo en los controladores
Los controladores nunca escriben SQL directamente. Usan DAO:

```php
// ✅ Good: Using DAO
$runs = RunsDAO::searchByUserId($userId);

// ❌ Bad: Direct SQL
$runs = $conn->query("SELECT * FROM Runs WHERE user_id = ...");
```
### Evite consultas O(n)
Cree consultas manuales para viajes sencillos de ida y vuelta:

```php
// ❌ Bad: Multiple queries
foreach ($users as $user) {
    $runs = RunsDAO::searchByUserId($user->userId);
}

// ✅ Good: Single query
$userIds = array_map(fn($u) => $u->userId, $users);
$runs = RunsDAO::searchByUserIds($userIds);
```
## Generación automática

Las clases VO y DAO se generan automáticamente a partir del esquema de la base de datos:

1. Modificar el esquema de la base de datos (agregar migración)
2. Ejecute `./stuff/update-dao.sh`
3. Se regeneran las clases VO y DAO.

## Notificaciones de usuario (tabla `Notifications`)

La interfaz carga las notificaciones pendientes desde la tabla **`Notifications`**. La columna **`contents`** es JSON que controla el render en [`Notification.vue`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/components/notification/Notification.vue).

Incluya al menos `type`; el resto es **payload** según el tipo. Tipos frecuentes: `badge` (campo `badge`), `demotion` (`status`, `message`), `general_notification` (`message`, `url` opcional). Para i18n puede usarse un objeto `body` con `localizationString`, `localizationParams`, `url`, `iconUrl`.

Ejemplo: `{ "type": "badge", "badge": "500score" }`. Código de referencia: [`stuff/cron/assign_badges.py`](https://github.com/omegaup/omegaup/blob/main/stuff/cron/assign_badges.py).

!!! consejo "Dudas"
    Pregunte en [Discord](https://discord.gg/gMEMX7Mrwe).

## Documentación relacionada

- **[Arquitectura de backend](../architecture/backend.md)** - Estructura de backend
- **[Esquema de base de datos](../architecture/database-schema.md)** - Descripción general del esquema
- **[Pautas de codificación](coding-guidelines.md)** - Pautas de PHP
