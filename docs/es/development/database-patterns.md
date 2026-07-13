---
title: Patrones de bases de datos
description: Comprender los patrones DAO/VO en omegaUp
icon: bootstrap/table
---
# Patrones de base de datos: DAO/VO

Cada byte que omegaUp lee o escribe en MySQL 8.0 pasa por una puerta estrecha: la capa **DAO/VO** bajo `frontend/server/src/DAO/`. Los controladores nunca abren una conexión `mysqli`, nunca concatenan un `SELECT` y nunca ven una fila de resultados sin procesar. Le piden a un objeto de acceso a datos los objetos mecanografiados y los objetos mecanografiados a mano. La razón no es estética: es que omegaUp es una plataforma de concursos en la que una consulta de marcador que se activa durante un evento en vivo con miles de envíos simultáneos debe ser predecible, revisable y a prueba de inyecciones. Centralizar todo SQL en una capa significa que cada consulta está preparada (parametrizada), cada consulta se puede recuperar y las costosas se pueden almacenar en caché exactamente en un lugar.

La capa tiene tres niveles y la división es importante porque dos de ellos están escritos por máquina y uno es suyo:

- **VO (Objeto de valor)** — `frontend/server/src/DAO/VO/`. Una clase de titular de datos tonta y escrita por tabla. Generado automáticamente. No editar.
- **Base DAO** — `frontend/server/src/DAO/Base/`. Una clase `abstract` por tabla que contiene el CRUD SQL estándar (crear/leer por clave primaria/actualizar/eliminar). Generado automáticamente. No editar.
- **DAO público** — `frontend/server/src/DAO/`. Una clase por tabla que `extends` es su base y es donde **usted** agrega las consultas escritas a mano que el generador no puede adivinar. Este es el único nivel que tocas con la mano.

Ambos niveles generados se abren con el mismo encabezado de grito, y soporta carga:

```php
/** ************************************************************************ *
 *                    !ATENCION!                                             *
 *                                                                           *
 * Este codigo es generado automáticamente. Si lo modificas, tus cambios     *
 * serán reemplazados la proxima vez que se autogenere el código.            *
 * ************************************************************************* */
```
Si ve ese banner en la parte superior de un archivo, todo lo que escriba en él se revertirá silenciosamente la próxima vez que alguien ejecute el generador. Es por eso que el nivel DAO público existe como un *archivo separado* que extiende la base, de modo que sus métodos personalizados vivan en algún lugar donde el generador nunca sobrescribirá.

## El VO: una fila escrita y nada más

Un objeto de valor se asigna uno a uno a una tabla. Tome [`frontend/server/src/DAO/VO/Runs.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/VO/Runs.php), el objeto de la tabla `Runs` (el resultado juzgado de un envío). `extends \OmegaUp\DAO\VO\VO` declara una constante `FIELD_NAMES` que enumera exactamente las columnas que existen y expone una propiedad pública escrita por columna con su esquema predeterminado integrado:

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
El constructor toma un `?array $data` opcional (la fila asociativa que obtendrías directamente de `mysqli`) y realiza tres trabajos antes de confiar en un único valor. Primero, rechaza la basura: `array_diff_key($data, self::FIELD_NAMES)` captura cualquier columna que no esté en la tabla, y una columna desconocida arroja `Unknown columns: ...` inmediatamente, por lo que un alias SELECT con error tipográfico explota durante la hidratación en lugar de hacer emerger silenciosamente un `null` tres capas arriba. En segundo lugar, *obliga* cada campo a su tipo declarado (de `run_id` a `intval`, de `score` a `floatval`, de `commit` a `strval`) porque una fila `mysqli` sin procesar le proporciona cadenas para todo y omegaUp se ejecuta bajo Psalm con tipos estrictos, por lo que un `"42"` fibroso donde se espera un `int` es un error de análisis estático. En tercer lugar, las marcas de tiempo reciben un manejo especial: `time` pasa de ida y vuelta a través de `\OmegaUp\DAO\DAO::fromMySQLTimestamp()` a un `\OmegaUp\Timestamp` (el contenedor interno de segundos POSIX de omegaUp), y si la fila omite `time` por completo, el VO lo establece de forma predeterminada en `new \OmegaUp\Timestamp(\OmegaUp\Time::get())` - "ahora" - en lugar de dejarlo nulo.

Vale la pena leer el PHPDoc a nivel de campo en lugar de omitirlo, porque contiene semántica que oculta el nombre de la columna. En `Runs`, `commit` está documentado como *"El hash SHA1 del commit en la rama master del problema con el que se realizó el envío"* y `version` como *"El hash SHA1 del árbol de la rama private"*; es decir, estos dos parecen cadenas genéricas pero son hashes de objetos git que vinculan una ejecución juzgada con la revisión exacta del problema con la que se ejecutó. Elimina ese comentario y la siguiente persona lo tratará como texto opaco y dejará de juzgar.

La base compartida [`\OmegaUp\DAO\VO\VO`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/VO/VO.php) le da a cada VO tres salidas al cable: `asArray()` (a través de `get_object_vars`) para la clasificación JSON, `asFilteredArray($filters)` para emitir solo un subconjunto de campos incluidos en la lista blanca (usado constantemente en respuestas API para que un controlador pueda devolver, por ejemplo, las columnas públicas de un usuario sin filtrar el hash de la contraseña) y `__toString()`, que es solo `json_encode` de `asArray()`. Un VO está deliberadamente libre de comportamiento: sin consultas, sin validación más allá de la coerción de tipo, sin reglas comerciales. Es una maleta para una fila.

## El DAO Base: el CRUD que nunca escribes

La base abstracta generada contiene las cuatro operaciones que son idénticas para cada tabla, diferenciándose solo en la lista de columnas. Mire [`frontend/server/src/DAO/Base/Runs.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Base/Runs.php): es un `abstract class Runs` cuyo método es `final public static`, por lo que las consultas se llaman como `RunsDAO::getByPK(...)` y una subclase no puede seguirlas accidentalmente. Cada método canaliza a través del singleton `\OmegaUp\MySQLConnection::getInstance()` y (este es todo el argumento de seguridad) utiliza marcadores de posición `?` con una matriz `$params` separada, nunca interpolación de cadenas:

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
`getByPK` devuelve `?\OmegaUp\DAO\VO\Runs`: el `?` no es una decoración, es el contrato: **una señorita devuelve `null`, y la persona que llama debe manejarlo.** `create()` ejecuta el `INSERT`, luego escribe la identificación de incremento automático recién creada nuevamente en el VO (`$Runs->run_id = ...->Insert_ID()`) y devuelve el recuento de filas afectadas, por lo que después de una creación puede leer la nueva clave principal directamente del objeto. usted pasó. `update()` devuelve `Affected_Rows()`. `delete()` es el más claro: si el `DELETE` toca cero filas, no regresa silenciosamente, arroja `\OmegaUp\Exceptions\NotFoundException('recordNotFound')`, con la lógica de que pedir eliminar una fila que no existe es un error en la persona que llama, no una no operación, y el docblock advierte que un objeto eliminado *no* puede resucitar reinsertándolo, porque `create()` creará una nueva clave primaria en lugar de reutilizar el viejo.

Dos ayudantes generados existen únicamente para que las pruebas y los caminos calientes no paguen por la hidratación que no usarán. `existsByPK($run_id)` ejecuta `SELECT COUNT(*)` y devuelve un `bool` "**sin necesidad de cargar sus campos**" — más barato que `getByPK` cuando solo necesitas saber *si* existe una fila, porque te saltas la creación del VO. `countAll()` devuelve el recuento total de filas de la misma manera, principalmente para pruebas que afirman la cardinalidad.

`getAll()` es el único método Base con una mina terrestre, y el generador lo documenta en línea: lee la tabla *completa* en una matriz de VO, "*consume una cantidad de memoria proporcional al número de registros regresados*". El valor predeterminado es 100 filas por página (`$filasPorPagina = 100`), ordenadas por la clave principal `run_id` en forma ascendente, y refuerza los dos parámetros que de otro modo serían vectores de inyección (la columna de clasificación se pasa a través de `MySQLConnection::escape()` y la dirección a través de `Validators::validateInEnum($tipoDeOrden, 'order_type', ['ASC', 'DESC'])`) porque, a diferencia de un valor de `?`, el nombre de una columna y la dirección de clasificación no pueden ser un parámetro vinculado y deben desinfectarse a mano. Utilice `getAll()` en `Countries` o `Languages`; nunca lo alcance en `Runs` o `Submissions`, que tienen millones de filas.

## La clase de utilidad básica `DAO`

Debajo de todo esto se encuentra [`\OmegaUp\DAO\DAO`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/DAO.php), una clase `final` de ayudantes estáticos en los que se apoya el código generado. Posee transacciones: `transBegin()`, `transEnd()` y `transRollback()` envuelven `StartTrans()` / `CompleteTrans()` / `FailTrans()` de `MySQLConnection`, por lo que cuando un controlador necesita varias escrituras para tener éxito o fallar juntas (crear un problema, su ACL y su conjunto de problemas de una sola vez), las coloca entre corchetes en `DAO::transBegin()` / `DAO::transEnd()`. Posee el puente de marca de tiempo (`toMySQLTimestamp` / `fromMySQLTimestamp`) que traduce entre `\OmegaUp\Timestamp` de omegaUp y `'Y-m-d H:i:s'` de MySQL en UTC a través de `gmdate`. Y expone `isDuplicateEntryException($e)`, que permite a una persona que llama detectar una colisión de clave única (un nombre de usuario duplicado, por ejemplo) y convertirlo en un error de validación amigable en lugar de un 500: inspecciona un `\OmegaUp\Exceptions\DatabaseOperationException` y pregunta `->isDuplicate()`.

## Cuándo escribir un método DAO personalizado

La base generada cubre exactamente una forma de acceso: tabla única, fila única, codificada por clave primaria. En el momento en que necesitas un `JOIN`, un agregado, una lista filtrada o una escritura por lotes, el generador no tiene nada para ti y escribes el método a mano en el DAO público. Esa no es una solución alternativa, es la costura diseñada. La clase pública `extends` la base, hereda todo el CRUD gratuito y agrega lo que la característica necesite.

[`frontend/server/src/DAO/Runs.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Runs.php) es el ejemplo vívido: alrededor de cuarenta métodos escritos a mano superpuestos a los siete heredados. La mayoría son uniones que la base nunca podría expresar, como `getBestProblemScore`, que va desde una fila `Submissions` hasta su fila `Runs` actual para encontrar la puntuación más alta de un usuario en un problema:

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
Observe la anotación `/** @var float|null */` justo antes de la devolución. `mysqli` devuelve escalares sin tipo y `GetOne` / `GetAll` devuelve `mixed`, por lo que Psalm no puede conocer la forma por sí solo; el `@var` (y, para filas de varias columnas, un bloque de documentos con forma de matriz completa como `@return list<array{alias: string, contest_score: float|null, guid: string, ...}>`) es la forma en que el DAO personalizado mantiene la seguridad de tipos y, lo que es más importante, la forma en que la forma fluye hasta TypeScript. Esas anotaciones de forma de retorno son leídas por `frontend/server/cmd/APITool.php`, el generador que produce `frontend/www/js/omegaup/api_types.ts`, por lo que un bloque de documentos descuidado en un método DAO aparece como un tipo incorrecto en la interfaz de Vue.

La otra razón para escribir un método a mano es **contraer los viajes de ida y vuelta**, y aquí es donde la regla de "evitar consultas O(n)" del andamio cobra fuerza. El antipatrón llama a un método DAO por fila dentro de un bucle:

```php
// ❌ Bad: one query per user — O(n) round-trips to MySQL
foreach ($users as $user) {
    $notification = new \OmegaUp\DAO\VO\Notifications([/* ... */]);
    \OmegaUp\DAO\Notifications::create($notification);
}
```
Cada iteración es un viaje de ida y vuelta de la red completa a MySQL; cien usuarios son cien viajes secuenciales, y bajo carga de concurso así es como se funde la base de datos. La solución es un único método personalizado que realiza el lote en una sola consulta. [`\OmegaUp\DAO\Notifications::createBulk`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Notifications.php) es la versión canónica del lado de escritura, y su bloque de documentos indica claramente la victoria - *"reducción de los viajes de ida y vuelta de la base de datos de O(N) a O(1)"* - al construir un `INSERT` de varias filas con una tupla de marcador de posición por fila:

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
Enviar 500 notificaciones de insignia después de una ejecución cron es un `INSERT` en lugar de 500. Incluso aquí se mantiene la disciplina `?`: los marcadores de posición se generan, los valores permanecen limitados. `Notifications` también muestra el tercer trabajo del nivel DAO público: eleva el vocabulario de dominio de la tabla en constantes de clase (`Notifications::DEMOTION`, `Notifications::CERTIFICATE_AWARDED`, `Notifications::CONTEST_CLARIFICATION_REQUEST`,…) para que el resto del código base se refiera a los tipos de notificación por nombre, no por cadena mágica.

## La filosofía de consulta: *sencillito, carismático y cacheable*

Los mantenedores tienen una frase para las consultas que respaldan las páginas más afectadas por los concursantes: el inicio público de un concurso, un marcador, una lista de problemas. La wiki describe la consulta ideal de detalles del concurso como *"un query sencillito, carismático y cacheable"*: pequeña, carismática y cacheable. Es una broma, pero también es la regla de diseño real. "Pequeño" significa que toca algunas tablas y devuelve el mínimo que la página necesita (miniclasificación, tiempo restante, resúmenes de problemas), no el gráfico de objetos completo. "Cacheable" significa que es determinista y de lectura mayoritaria, por lo que el resultado se puede memorizar y servir sin tocar MySQL en absoluto. Cuando estás decidiendo si agregar un método DAO personalizado o ampliar uno existente, esta es la barra: si la consulta está en una ruta de lectura activa, hazla lo suficientemente pequeña como para que su resultado pueda vivir en Redis.

## Almacenamiento en caché con Redis (y APCu)

El caché se encuentra en [`frontend/server/src/Cache.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Cache.php). `\OmegaUp\CacheAdapter` es una abstracción de dos backends seleccionados por `OMEGAUP_CACHE_IMPLEMENTATION` en `config.default.php`; el valor predeterminado es `'apcu'` (por proceso en memoria, bien para una sola caja), y la producción lo convierte en `'redis'`, que es `pconnect` a `REDIS_HOST` (`'redis'`) en `REDIS_PORT` (`6379`) y se autentica con `REDIS_PASS`. Todo lo que está encima del adaptador es independiente del backend, por lo que DAO y el código del controlador nunca saben ni les importa qué tienda está detrás de él.

Las entradas de caché tienen un espacio de nombres mediante una **constante de prefijo**, y leer la lista de ellas en `Cache.php` es la forma más rápida de saber qué considera omegaUp que vale la pena almacenar en caché: `Cache::PROBLEM_STATEMENT` (`'statement-'`), `Cache::USER_PROFILE` (`'profile-'`), `Cache::CONTESTANT_SCOREBOARD_PREFIX` (`'scoreboard-'`), `Cache::CONTEST_INFO` (`'contest-info-'`), `Cache::PROBLEMS_LIST` (`'problems-list-'`), `Cache::RUN_COUNTS` (`'run-counts-'`) y un par de docenas más. Una clave completa es `prefix + id`, p. la caché de perfil para el usuario `omegaup` es `profile-omegaup`.

El único método que utilizará es `getFromCacheOrSet`: almacenamiento en caché de lectura en una sola llamada:

```php
$accessibleAclIds = \OmegaUp\Cache::getFromCacheOrSet(
    \OmegaUp\Cache::PROBLEM_IDENTITY_TYPE,   // prefix
    $cacheKeyId,                             // id
    fn () => /* the sencillito query goes here */,  // computed only on a miss
    $timeout                                 // TTL in seconds
);
```
En caso de acierto, devuelve el valor almacenado en caché y el cierre nunca se ejecuta; en caso de error, ejecuta el cierre, almacena el resultado bajo la clave con el TTL dado y lo devuelve. Debajo del capó, `set`/`get`/`delete`, cada cortocircuito cuando el caché está deshabilitado (`isEnabled()` falso): `get` devuelve `null`, `set` y `delete` devuelven `false`, por lo que una caja sin backend de caché se degrada para acceder a MySQL cada vez en lugar de fallar, y cada acierto/error/almacenamiento se registra a través de Monolog debajo del canal. nombre `cache` para cuando necesite ver por qué algo se sirve o no desde la memoria caché.

Los TTL son por dominio y se ajustan a la velocidad con la que los datos subyacentes se vuelven obsoletos, todo en `config.default.php` en segundos. El `APC_USER_CACHE_TIMEOUT` predeterminado global es `7 * 24 * 3600` (siete días) para datos que esencialmente nunca cambian. Pero la información de un concurso en vivo se almacena en caché durante solo segundos de `10` (`APC_USER_CACHE_CONTEST_INFO_TIMEOUT`), una declaración de problema para `60`, una lista de problemas para `60 * 30` (treinta minutos) y sesiones para `8 * 3600` para que coincidan con la vida útil del token de autenticación. `APC_USER_CACHE_PROBLEM_STATS_TIMEOUT` es `0`, que significa "caché sin caducidad, hasta que se invalide explícitamente". Estos números son el ajuste actual y deben revisarse: elija un TTL preguntando qué tan incorrecta puede estar la página y por cuánto tiempo.

### Invalidación: TTL, eliminación selectiva o aumento de versión

Debido a que la mayoría de las escrituras pasan por DAO, pero el caché está codificado por conceptos de dominio, **la invalidación reside en los controladores al lado de la escritura, no dentro del DAO.** Cuando un controlador muta algo de lo que depende una entrada de caché, elimina esa entrada por clave exacta. La ruta de verificación de perfil en [`Controllers/User.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/User.php) hace exactamente esto justo después de activar la bandera de verificación de un usuario:

```php
// Expire profile cache
\OmegaUp\Cache::deleteFromCache(
    \OmegaUp\Cache::USER_PROFILE,
    strval($identity->username)
);
```
La regla general: si una escritura hace que un valor almacenado en caché sea incorrecto *en este momento* y una lectura obsoleta confundiría a un usuario (una cuenta recién verificada todavía se muestra como no verificada), elimine la clave específica para que la siguiente lectura la vuelva a calcular; Si un poco de estancamiento es inofensivo, deje que el TTL lo expire por sí solo.

Para el caso en el que de otro modo tendrías que eliminar cientos de claves que comparten un prefijo (por ejemplo, cada marcador de un concurso), existe `invalidateAllKeys($prefix)`, y su implementación es la parte inteligente. **No** escanea ni elimina las claves coincidentes. En su lugar, mantiene una versión entera por prefijo (`v{prefix}`) que está entretejida en cada clave real, y la invalidación simplemente la incrementa (`inc("v{prefix}")`). Las claves antiguas todavía se encuentran físicamente en Redis, pero ahora son inalcanzables porque cada nueva lectura y escritura utiliza la versión modificada, por lo que nunca se recuperan ni se actualizan nuevamente y simplemente caducan. Un `INCR` invalida un espacio de nombres completo en O(1) en lugar de un barrido O(n): el mismo instinto *sencillito* aplicado a la administración de caché en sí.

## Regenerando la capa DAO y VO

Nunca escribes a mano un DAO Base o un VO. Cambias el esquema y dejas que el generador los reescriba. La fuente de la verdad es `frontend/database/schema.sql`; después de editarlo (normalmente junto con una migración creada con `stuff/db-migrate.py`), ejecute:

```sh
./stuff/update-dao.sh
```
Ese script copia `schema.sql` a `frontend/database/dao_schema.sql` para activar la regeneración, luego ejecuta `stuff/update-dao.py`, que reescribe todo en `frontend/server/src/DAO/Base/` y `frontend/server/src/DAO/VO/` desde las plantillas en `stuff/dao_templates/` (con `stuff/dao_utils.py` y `stuff/dao_linter.py` mantienen la salida consistente). Sus métodos escritos a mano en las clases públicas de `frontend/server/src/DAO/` no se modifican, porque viven en archivos diferentes, que es la razón principal de la división base-pública. Si desea editar un archivo que lleva el banner `!ATENCION!`, deténgase: o desea un método personalizado en el DAO público o desea un cambio de esquema y una regeneración.

## Notificaciones de usuario (tabla `Notifications`)

La interfaz de usuario web carga filas pendientes para un usuario de la tabla **`Notifications`** a través de [`\OmegaUp\DAO\Notifications::getUnreadNotifications`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Notifications.php), que en sí es un método DAO escrito a mano que selecciona las filas `read = 0` ordenadas por las más antiguas. La columna **`contents`** de cada fila es JSON que impulsa la representación en [`Notification.vue`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/components/notification/Notification.vue).

### Forma JSON

Como mínimo, incluya una cadena `type` para que el componente elija el diseño correcto. Otras claves son una **carga útil** específica de ese tipo.

```json
{
  "type": "notificationType",
  "any_field": "value"
}
```
### Valores `type` admitidos (nivel alto)

| `type` | Propósito | Carga útil típica |
|--------|---------|-----------------|
| `badge` | Insignia obtenida | `badge`: identificador de insignia (por ejemplo, nombre del hito de puntuación) |
| `demotion` | Cambio de cuenta/estado | `status`, `message` |
| `general_notification` | Texto en formato libre | `message`, opcional `url` |

### Estilo de "sistema" localizado (`body`)

Para traducciones a través del sistema i18n, puede utilizar:

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
### Ejemplo (insignia)

Insertando una fila cuyo `contents` se parezca a:

```json
{
  "type": "badge",
  "badge": "500score"
}
```
le dice a la interfaz de usuario que muestre una notificación de estilo insignia; los campos adicionales se interpretan en `Notification.vue`. Para ver un ejemplo concreto del lado del servidor, consulte [`stuff/cron/assign_badges.py`](https://github.com/omegaup/omegaup/blob/main/stuff/cron/assign_badges.py): un cron que asigna insignias y es exactamente el tipo de trabajo que distribuye muchas notificaciones, por lo que las inserta a través de `Notifications::createBulk` en lugar de una fila a la vez.

!!! consejo "Preguntas"
    Pregunte en los canales de desarrolladores de omegaUp [Discord](https://discord.gg/gMEMX7Mrwe) si no está seguro de qué `type` y carga útil utilizar.

## Documentación relacionada

- **[Arquitectura de backend](../architecture/backend.md)** - Estructura de backend
- **[Esquema de base de datos](../architecture/database-schema.md)** - Descripción general del esquema
- **[Pautas de codificación](coding-guidelines.md)** - Pautas de PHP
