---
title: Agregar un tipo de notificación
description: Cómo conectar una notificación nueva de un extremo a otro, desde la tabla de Notificaciones hasta el menú desplegable de campana de Vue
icon: bootstrap/bell
---
# Agregar un nuevo tipo de notificación

La pequeña campana en la barra de navegación con la insignia de conteo roja se alimenta exactamente de una tabla y un componente de Vue. Una vez que comprenda cómo se hablan esos dos, agregar un nuevo tipo de notificación: "obtuvo una insignia", "se aceptó su registro en el concurso", "un administrador le dejó comentarios" es un pequeño cambio mecánico. Esta página recorre todo el camino en el orden en que realmente viajan los datos: algo sucede en el servidor, una fila llega a la tabla `Notifications`, `apiMyList` la pasa a la barra de navegación y `Notification.vue` decide cómo dibujarla.

La única idea a la que debemos aferrarnos antes que nada: una notificación es solo **un `user_id` más un blob de JSON**. Todo lo interesante vive en esa columna JSON `contents`, y todo el diseño es que el servidor decide *qué decir* mientras que el frontend decide *cómo decirlo* basándose en un único discriminador `type`. Obtenga la forma JSON correcta y la mayor parte del trabajo estará hecho.

## El modelo de datos: una fila, un blob JSON

Las notificaciones se encuentran en la tabla MySQL `Notifications`, expuesta a través del par DAO/VO habitual: [`frontend/server/src/DAO/Notifications.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Notifications.php) (el DAO público) y [`frontend/server/src/DAO/VO/Notifications.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/VO/Notifications.php) (el objeto de valor). Una fila tiene solo cinco columnas: `notification_id`, `user_id`, `timestamp`, `read` y `contents`. Cuatro de ellos son la contabilidad que la plataforma administra por usted: la clave principal, a qué campana pertenece, cuándo se activó y si el usuario la descartó. La columna `read` importa más de lo que parece: todo el "recuento de no leídos" y el flujo de marcar como leído cuelgan de ese único booleano, y solo aparece una notificación mientras se `read = 0`.

Todo lo que realmente diseñas va a **`contents`, que es una cadena JSON**. Como mínimo deberá llevar un `type`:

```json
{
  "type": "yourNotificationType",
  "any_field": "whatever payload this type needs"
}
```
El campo `type` es el discriminador que le dice a [`Notification.vue`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/components/notification/Notification.vue) qué diseño representar, con una imagen o sin ella, qué icono, si enlaza en algún lugar, qué texto mostrar. Las claves restantes son una **carga útil** de formato libre: asígneles el nombre que necesite el tipo, porque su única función es transportar los datos específicos que el diseño interpolará. El ejemplo mínimo clásico, sacado directamente del cron insignia, es un blob de dos campos donde `badge` es la carga útil:

```json
{
  "type": "badge",
  "badge": "500score"
}
```
Dice "esta es una notificación de insignia y la insignia en cuestión es `500score`", lo cual es suficiente para que la interfaz encuentre el arte de la insignia, cree la oración y enlace a la página de la insignia.

## El esquema `contents` es un tipo real generado

La forma de `contents` no es folklore; es un tipo de Salmo que se compila en TypeScript, por lo que el frontend y el backend lo acuerdan en el momento de la compilación. La definición canónica es la anotación `@psalm-type NotificationContents` en la parte superior de [`frontend/server/src/Controllers/Notification.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Notification.php#L8):

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
[`APITool.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/cmd/APITool.php) lee esa anotación y regenera la interfaz reflejada en [`frontend/www/js/omegaup/api_types.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/api_types.ts) (busque `interface NotificationContents`; lleva el banner NO EDITAR porque se genera). Entonces, si su nueva notificación necesita un nuevo campo de nivel superior en `contents` (algo que aún no es `badge`, `message`, `status`, `url` o el objeto `body`), edite el `@psalm-type` en `Notification.php`, luego regenere `api_types.ts` para que el lado de Vue pueda leer su campo sin quejarse de TypeScript. Si puede expresar sus datos dentro de la carga útil `body` existente (ver más abajo), puede omitir este paso por completo, lo cual es una razón más para preferirlo.

## Dos estilos de renderizado: el cambio por tipo versus el `body` localizado

Aquí está la decisión más importante y la razón para leer `Notification.vue` antes de escribir cualquier código de servidor. Hay **dos formas** de generar una notificación y conviven una al lado de la otra en el mismo componente:

1. **El conmutador heredado per-`type`.** Para un puñado de tipos codificados (`badge`, `demotion`, `general_notification`), `Notification.vue` tiene brazos `switch (this.notification.contents.type)` explícitos que seleccionan un icono, crean el texto y calculan el enlace directamente desde los campos de carga útil. Cada uno de esos captadores termina en un brazo `default:`, por lo que aún se representa un tipo no reconocido: solo obtiene el ícono genérico `/media/info.png` y ningún texto.

2. **La ruta `body` localizada.** Si `contents.body` está presente, supera el interruptor de ícono, texto y URL por igual: cada captador verifica primero `if (this.notification.contents.body)` y regresa desde `body` antes de llegar a `switch`. El `body` lleva un `localizationString` (una clave de traducción), un `localizationParams` (valores para interpolar), un `url` y un `iconUrl`. Esta es la ruta moderna y compatible con i18n, y es por eso que los tipos de notificación más nuevos no necesitan una sola línea nueva de Vue: le entregan al componente una clave de traducción y se representa genéricamente.

El resultado práctico: **para un nuevo tipo, use la ruta `body` a menos que realmente necesite un marcado personalizado.** Significa que agrega una cadena de traducción y llama a un asistente PHP, y nunca toca `Notification.vue`. El cambio por tipo solo vale la pena cuando el diseño en sí es especial (las insignias, por ejemplo, crean una ruta `<img>` a partir de la carga útil y necesitan un estilo personalizado).

### Qué hace realmente el interruptor

Para ver por qué la ruta `body` es más fácil, observe lo que de otro modo tendría que agregar. `Notification.vue` calcula cuatro cosas a partir de `contents`, y cada una es un captador con la misma forma; verifique primero `body`, luego active `type`:

- **`iconUrl`** — `body.iconUrl` si existe un cuerpo; de lo contrario `badge` → `/media/dist/badges/${badge}.svg`, `demotion` → `/media/banned.svg` cuando `status == 'banned'` sino `/media/warning.svg`, `general_notification` → `/media/email.svg`, y todo lo demás → `/media/info.png`.
- **`text`**: las notificaciones basadas en `body` generan Markdown (ver a continuación), por lo que `text` solo sirve los brazos simples: `demotion` y `general_notification` devuelven `contents.message` (o `''` si está ausente), y todos los demás tipos devuelven `''`.
- **`notificationMarkdown`** — si existe un `body`, es `ui.formatString(T[body.localizationString], body.localizationParams)`; de lo contrario, el único brazo que no está vacío es el `badge`, que construye el `ui.formatString(T.notificationNewBadge, { badgeName: T['badge_' + badge + '_name'] })`. Esto se resuelve con la cadena de traducción `notificationNewBadge = "You have received a new badge: **%(badgeName)**."` en [`frontend/templates/en.lang`](https://github.com/omegaup/omegaup/blob/main/frontend/templates/en.lang), razón por la cual las notificaciones de insignia aparecen como Markdown en negrita.
- **`url`** — `body.url` si existe un cuerpo; de lo contrario, `general_notification` → `contents.url`, `badge` → `/badge/${badge}/` y `demotion` → `''` (hay un `// TODO: Add link to problem page.` allí mismo en la fuente, un buen ejemplo del tipo de borde a medio terminar que encontrará y que no debería sorprenderle).

Tenga en cuenta que agregar un tipo al interruptor significa tocar **cuatro captadores** y hacer que el ícono, el texto, la reducción y el enlace sean consistentes, en comparación con la ruta `body`, donde proporciona esas cuatro cosas como datos en un objeto JSON.

## Nombrar el tipo: agregar una constante, no agregar cadenas literales

El tipo de cadena se comparte entre el servidor que la escribe y el Vue que la lee, por lo que quiere una única fuente de verdad. El DAO ya los recopila como constantes de clase en la parte superior de [`frontend/server/src/DAO/Notifications.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Notifications.php); actualmente hay alrededor de veinte de ellos, incluidos `CERTIFICATE_AWARDED = 'certificate-awarded'`, `CONTEST_REGISTRATION_ACCEPTED = 'contest-registration-accepted'`, `CONTEST_REGISTRATION_REJECTED = 'contest-registration-rejected'`, `COURSE_SUBMISSION_FEEDBACK = 'course-submission-feedback'`, `DEMOTION = 'demotion'` y una docena más de variantes de registro y aclaración de cursos/concursos. Agregue su nuevo tipo allí como una constante para que todo el lado PHP se refiera a `\OmegaUp\DAO\Notifications::YOUR_TYPE` en lugar de una cadena simple que puede desincronizarse con un error tipográfico.

Un detalle que vale la pena conocer para que no te haga tropezar: los tipos de conmutadores más antiguos en `Notification.vue` (`badge`, `general_notification`) *no* están en esa lista constante: son anteriores a ella y están escritos como literales sin formato en lugares como el cron de insignia. Las constantes son todas kebab-case (`certificate-awarded`); los tipos de interruptores heredados son serpiente/inferior (`general_notification`). Esa no es una regla que debas obedecer, solo notarás una unión entre los estilos antiguo y nuevo. Los nuevos tipos deben seguir la convención constante.

## Creando la notificación desde el servidor

Hay dos lugares realistas donde nace una notificación: dentro de una solicitud PHP o desde un cron de Python.

### Desde PHP: use los ayudantes del controlador de notificaciones

`\OmegaUp\Controllers\Notification` (en [`Notification.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Notification.php)) existe precisamente para que no tenga que enrollar manualmente el inserto DAO. Para una notificación localizada de estilo `body` dirigida a una lista de usuarios, el resumen es `setCommonNotification`, que toma los ID de usuario, un `\OmegaUp\TranslationString`, el tipo, una URL y los parámetros de localización, y ensambla todo el blob `body` para usted (incluso completa `iconUrl` como `/media/info.png` de forma predeterminada):

```php
\OmegaUp\Controllers\Notification::setCommonNotification(
    userIds: $userIds,
    localizationString: new \OmegaUp\TranslationString('notificationYourNewString'),
    notificationType: \OmegaUp\DAO\Notifications::YOUR_TYPE,
    url: "/somewhere/{$alias}/",
    localizationParams: ['contestTitle' => $contest->title],
);
```
Debajo del capó, llama a `setNotification(userIds, contents)`, que coloca los ID de usuario en objetos de valor `\OmegaUp\DAO\VO\Notifications` y los conserva con `\OmegaUp\DAO\Notifications::createBulk(...)`. El nombre `createBulk` es deliberado: realiza un único `INSERT` masivo en lugar de una consulta por usuario, convirtiendo lo que serían O(N) viajes de ida y vuelta en O(1), lo cual es importante cuando se notifica a todos los participantes de un concurso a la vez. Si necesita algo que el asistente no modela, el ejemplo más completo es `createForCourseAccessRequest`, que codifica en json un `body` completo (con sus propios `localizationString`, `localizationParams`, `url` y `iconUrl`) a mano y llama a `\OmegaUp\DAO\Notifications::create(...)` para un solo usuario.

### Desde cron de Python: inserte la fila directamente

Los crons no pasan por el controlador PHP: ellos mismos escriben la fila `Notifications`. El asignador de insignias, [`stuff/cron/assign_badges.py`](https://github.com/omegaup/omegaup/blob/main/stuff/cron/assign_badges.py), es la referencia: en `save_new_owners` crea una tupla por cada nuevo propietario de insignia y ejecuta un `INSERT INTO Notifications (user_id, contents) VALUES (%s, %s)` simple, donde `contents` es `json.dumps({'type': 'badge', 'badge': badge})`. Ese es el truco: el cron sólo tiene que producir la misma forma JSON que espera la interfaz; las columnas `notification_id`, `timestamp` y `read` toman sus valores predeterminados. Si está agregando una notificación controlada por cron, refleje esto: cree su dictado `contents` con un `type` y una carga útil, `json.dumps` e insértelo.

## Agregar la cadena de traducción

Si tomó la ruta `body` (y debería hacerlo), el `localizationString` que pasó realmente debe existir, o `ui.formatString(T[...], ...)` en la interfaz se resuelve en `undefined`. Agregue su clave a [`frontend/templates/en.lang`](https://github.com/omegaup/omegaup/blob/main/frontend/templates/en.lang), y a `es.lang` y `pt.lang` junto a ella, usando la misma interpolación `%(paramName)` que proporciona el objeto params. La cadena de la insignia es el patrón a copiar: `notificationNewBadge = "You have received a new badge: **%(badgeName)**."`, donde `%(badgeName)` se alinea con la clave `badgeName` entregada a `formatString`. El valor se representa como Markdown, por lo que `**bold**` y los enlaces funcionan.

## Enseñar Notification.vue a renderizarlo (solo si omitiste `body`)

Si su notificación usa `body`, deténgase: ya terminó con la interfaz, porque el brazo genérico `body` en cada captador ya lo representa. Solo si necesita un diseño personalizado, edite [`Notification.vue`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/components/notification/Notification.vue): agregue un brazo `case 'yourType':` a los getters `iconUrl`, `text`/`notificationMarkdown` y `url` para que el ícono, el texto y el enlace estén todos cubiertos, y agregue cualquier SCSS con alcance que el diseño necesite en la parte inferior del archivo. Manténgalos consistentes: un tipo que devuelve una URL de `url` pero nada de los captadores de texto se mostrará como una fila vacía en la que se puede hacer clic, lo cual es confuso. Esta es la ruta sobre la que advierte la wiki: "este formato sólo funcionará si se crean o ajustan los estilos apropiados en el componente Vue".

## La ruta de lectura: cómo la fila vuelve a la campana

Vale la pena ver el viaje de regreso una vez, porque explica por qué son importantes `read` y `user_id` y dónde buscar cuando una notificación "no aparece".

Cuando se carga la barra de navegación, [`frontend/www/js/omegaup/common/navbar.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/common/navbar.ts) llama a la API `Notification.myList`, que accede a `apiMyList` en el controlador. Ese punto final ejecuta `ensureIdentity()` (debe haber iniciado sesión), recupera filas a través de `\OmegaUp\DAO\Notifications::getUnreadNotifications($r->user)`, una consulta que selecciona `notification_id`, `contents` y `timestamp` `WHERE user_id = ? AND read = 0 ORDER BY timestamp ASC`, `json_decode` coloca cada cadena `contents` en la matriz `NotificationContents` y `array_reverse` la lista para que la más nueva se ubique en la parte superior. Entonces: si su fila insertada ya tiene el `read` verdadero, o el `user_id` incorrecto, nunca aparece silenciosamente. Eso es lo primero que hay que comprobar cuando se pierde una notificación.

La lista decodificada fluye hacia `List.vue` (el menú desplegable), que muestra la campana FontAwesome, una insignia de recuento rojo igual a `notifications.length` y un `Notification.vue` por entrada codificada por `notification_id`. Al hacer clic en una sola notificación, o "marcar todo como leído", se emite un evento `read`/`read-notifications` de respaldo a `navbar.ts`, que llama a `Notification.readNotifications({ notifications: [...ids] })` y luego vuelve a buscar `myList` para actualizar la insignia. En el servidor, `apiReadNotifications` llama a `ensureMainUserIdentity()`, luego, para cada identificación, carga la fila y **comprueba que `notification->user_id === r->user->user_id`, arrojando `ForbiddenAccessException` en caso contrario** (para que no pueda marcar las notificaciones de otra persona como leídas adivinando ID), arroja `NotFoundException` para una identificación desconocida y, finalmente, configura `read = true` y las actualizaciones. Si una notificación llevaba un `url`, al hacer clic en ella se marca como leída y se navega allí, razón por la cual el captador `url` y `handleClick` en `Notification.vue` emiten el evento `remove` con la URL adjunta.

## La lista de verificación, de principio a fin

En conjunto, agregar un nuevo tipo de notificación es, en orden:

1. **Agregue una constante `type`** a `\OmegaUp\DAO\Notifications` para que ambos lados compartan la misma ortografía.
2. **Decida la forma de la carga útil.** Prefiera la ruta `body` (`localizationString` + `localizationParams` + `url` + `iconUrl`) para que la interfaz la represente genéricamente. Solo invente nuevos campos `contents` de nivel superior si `body` no puede expresarlos y, si lo hace, actualice `@psalm-type NotificationContents` en `Notification.php` y regenere `api_types.ts` con `APITool.php`.
3. **Agregue la cadena de traducción** a `en.lang`/`es.lang`/`pt.lang` con marcadores de posición `%(param)` coincidentes.
4. **Emitir la notificación** — desde PHP vía `\OmegaUp\Controllers\Notification::setCommonNotification(...)` (o `createBulk` para muchos usuarios), o desde un cron con un `INSERT INTO Notifications (user_id, contents)` directo cuyo `contents` es `json.dumps({...})`.
5. **Solo si omitió `body`:** agregue los brazos `case` correspondientes a los captadores `iconUrl` / texto / `url` de `Notification.vue` más cualquier estilo con alcance.
6. **Verifique** iniciando sesión como usuario objetivo y mirando la campana, recordando que la fila debe tener `read = 0` y el `user_id` correcto para que aparezca.

!!! consejo "Ante la duda, pregunta"
    Si no está seguro de qué `type` y forma de carga útil se ajustan a su caso, los mantenedores preferirán que pregunte antes que adivinar: créelo en el canal `#depto_tecnico` en Slack (o en los canales de desarrollador en omegaUp [Discord](https://discord.gg/gMEMX7Mrwe)). :)

## Documentación relacionada

- **[Patrones de base de datos](database-patterns.md)**: la capa DAO/VO sobre la que se basa la tabla `Notifications`, incluida la forma JSON `contents`.
- **[Componentes de Vue](components.md)**: convenciones de componentes, i18n con `ui.formatString` y Storybook.
- **[Pautas de codificación](coding-guidelines.md)**: las reglas de PHP y TypeScript que deben cumplir estos cambios.
