---
title: Gestión de concursos
description: Guía para crear y gestionar concursos de programación
icon: bootstrap/cog
---
# Gestión de concursos {#managing-contests}

Esta página recorre todo lo que usted hace como persona que *dirige* un concurso: el maestro que organiza una práctica semanal para una clase, el organizador del club que organiza una selección regional, el entrenador que reproduce el IOI del año pasado como una sesión de entrenamiento. Seguimos el flujo real: crear el concurso, colgarle los problemas, decidir quién participa, ajustar el marcador y elegir el modo que se adapta a tu sala. Cada perilla aquí se asigna a un campo en `\OmegaUp\DAO\VO\Contests` y a un punto final en `\OmegaUp\Controllers\Contest` (`frontend/server/src/Controllers/Contest.php`), por lo que cuando la interfaz de usuario oculta algo, sabrá exactamente qué parámetro alcanzar.

## Creando un concurso {#creating-a-contest}

El formulario del concurso que completa en el sitio es el componente Vue `frontend/www/js/omegaup/components/contest/Form.vue`; cuando lo envía, se PUBLICA en `Contest::apiCreate` (`Contest.php:2941`). Dos puertas se activan antes de que se escriba algo: `Controller::ensureNotInLockdown()` (no se pueden crear concursos desde el host de bloqueo `arena.omegaup.com`; más sobre esto a continuación) y `ensureMainUserIdentityIsOver13()`, porque la creación de concursos está vinculada a una cuenta completa y omegaUp no permite que las identidades menores de 13 años posean una.

Lo más sorprendente de `apiCreate` es que **todos los concursos nacen privados**, sin importar lo que pidas. El controlador codifica `'admission_mode' => 'private'`, y si pasa cualquier `admission_mode` que no sea `'private'`, arroja `contestMustBeCreatedInPrivateMode` en lugar de respetarlo silenciosamente. Esto es deliberado: construyes el concurso en una sala silenciosa (agregas problemas, verificas el reloj, invitas a un coadministrador) y solo *entonces* lo haces público a través de `apiUpdate`. Nadie se topa con un concurso a medio terminar.

### Los campos básicos {#the-basic-fields}

Estos cuatro son la identidad del concurso y se requieren:

- **`title`** — el nombre humano que se muestra en los listados (por ejemplo, "Selectivo Regional 2026").
- **`alias`**: el slug corto que se encuentra en la URL. Se puede acceder al concurso en `/arena/<alias>`, así que manténgalo en minúsculas y con URL segura; `Validators::alias` hace cumplir eso.
- **`description`**: texto libre que se muestra en la página de introducción del concurso antes de que ingrese el concursante.
- **`start_time` / `finish_time`**: ambas son marcas de tiempo. `finish_time` debe ser *estrictamente* mayor que `start_time` o `validateCommonCreateOrUpdate` arroja `contestNewInvalidStartTime`. Los dos juntos definen la duración del concurso, y esa duración tiene un límite: `MAX_CONTEST_LENGTH_SECONDS` es `60 * 60 * 24 * 31`, es decir, **31 días** para un organizador normal; los administradores del sistema obtienen `MAX_CONTEST_LENGTH_SYSADMIN_SECONDS` = **60 días**. Solicita un concurso de 40 días como profesor y recuperarás el `contestLengthTooLong` con el `max_days` que tienes permitido.

### Las perillas de afinación (y lo que realmente hacen) {#the-tuning-knobs-and-what-they-actually-do}

Todo lo que va más allá de lo básico tiene un valor predeterminado sensato, por lo que puedes dejarlos en paz para un primer concurso y volver una vez que sepas lo que quieres. Los valores predeterminados a continuación son los escritos en `VO/Contests`:

- **`window_length`** (`int` minutos, predeterminado `null`): este es el cronómetro personal estilo USACO. `null` significa "puede enviar durante todo el período entre `start_time` y `finish_time`": un reloj compartido para todos. Configúrelo, digamos, `180`, y cada concursante tendrá su propia ventana de 180 minutos que comienza a correr en el momento en que *ellos* abren el concurso. Eso es lo que permite que una clase de 30 personas se siente en horarios escalonados y aun así cada uno tenga las mismas tres horas. Nota `apiCreate` almacena `$r['window_length'] ?: null`, por lo que un `0` vuelve a colapsar y queda "sin ventana".
- **`submissions_gap`** (`int` segundos, `60` predeterminado): la espera mínima que debe cumplir un concursante entre dos presentaciones sobre cualquier problema. El valor predeterminado 60 existe para mitigar el comportamiento de "enviar y ver" de fuerza bruta y evitar que una persona inunde la cola de jueces; déjelo para una práctica relajada, levántelo para una selección de alto riesgo.
- **`scoreboard`** (`int` 0–100, predeterminado `1`): lea esto como *el porcentaje del tiempo transcurrido del concurso durante el cual el marcador en vivo es visible para los concursantes*. `100` significa que la placa está activa en todo momento; `0` significa que estará oscuro durante todo el concurso. Este es tu marcador **congelado**: configúralo en `80` y las clasificaciones dejarán de actualizarse silenciosamente durante el último 20% del concurso, por lo que el drama de la última hora permanecerá en secreto. (Consulte la sección [Marcador](#the-scoreboard) para saber cómo se compone con `show_scoreboard_after`.)
- **`points_decay_factor`** (`float`, predeterminado `0.00`): cuánto se desvanece el valor de un problema a medida que corre el tiempo, lo que recompensa las soluciones tempranas. `0` significa que no hay deterioro: un problema vale lo mismo en el minuto 1 que en el minuto 179. Para la calibración, **TopCoder usa `0.7`**. La mayoría de los concursos escolares dejan esto en 0.
- **`penalty`** (minutos `int`, `1` predeterminado) y **`penalty_type`** (enumeración `'contest_start' | 'problem_open' | 'runtime' | 'none'`): la maquinaria de desempate. `penalty` es el número de minutos que cada envío *rechazado* añade a tu tiempo; `penalty_type` decide lo que mide el reloj: minutos desde que comenzó el concurso (`contest_start`, la convención ICPC), minutos desde que *usted abrió personalmente* ese problema (`problem_open`, que se combina naturalmente con `window_length`), el tiempo de ejecución real del programa en milisegundos (`runtime`), o nada en absoluto (`none`). **`penalty_calc_policy`** (enum `'sum' | 'max'`) luego dice si la penalización de un concursante es la suma de los problemas o simplemente el peor.
- **`score_mode`** (enumeración `'partial' | 'all_or_nothing' | 'max_per_group'`, validada por `ensureOptionalEnum`): cómo puntúa una solución parcialmente correcta. `partial` otorga crédito proporcional a los casos de prueba aprobados; `all_or_nothing` otorga a un problema la máxima puntuación sólo cuando *cada* caso es AC y cero en caso contrario (estilo olímpico clásico); `max_per_group` obtiene la mejor puntuación obtenida en cada grupo de prueba. Hay un `partial_score` booleano más antiguo (`true` predeterminado) que es anterior a esta enumeración y expresa la misma intención de parcial versus todo o nada.
- **`feedback`** (enumeración `'none' | 'summary' | 'detailed'`, predeterminado `'none'`): cuánto aprende el concursante de una presentación. `none` oculta el veredicto por completo (se someten al estilo oscuro final de IOI); `summary` muestra el porcentaje de casos aprobados más el veredicto del peor de los casos; `detailed` revela el veredicto caso por caso. Las sesiones de práctica quieren `detailed`; una selección real normalmente quiere `none` o `summary`.
- **`show_scoreboard_after`** (`bool`, predeterminado `true`): si el marcador completo se revela a todos una vez que finaliza el concurso, independientemente de lo que hizo `scoreboard` durante la carrera.
- **`languages`** (filtro opcional): restringe los lenguajes de programación permitidos. Déjelo `null` para permitir todos los idiomas admitidos por omegaUp; configúrelo para bloquear un concurso para principiantes, por ejemplo, solo en Python.
- **`contest_for_teams`** (`bool`, predeterminado `false`) más **`teams_group_alias`**: convierte el concurso en un evento de equipo cuyos participantes provienen de un grupo de equipos en lugar de invitaciones individuales. Esta bandera cambia la forma en que agrega participantes (ver más abajo), así que decídalo desde el principio.
- **`check_plagiarism`** (`bool`, predeterminado `false`): ejecuta el detector de plagio de omegaUp en todas las presentaciones después del concurso.

## Gestión de problemas {#managing-problems}

Un concurso comienza vacío; le cuelga problemas con `Contest::apiAddProblem` (`Contest.php:3461`), que controla el componente `contest/AddProblem.vue`. Solo un administrador del concurso puede hacer esto (el `validateContestAdmin` se ejecuta primero) y está **prohibido en un concurso virtual** (`forbiddenInVirtual`), ya que un concurso virtual es una repetición congelada de un conjunto de problemas existente, no uno nuevo que usted edite.

Dos parámetros dan forma a cada suma. **`points`** es `ensureFloat('points', 0, INF)`: cualquier peso no negativo, por lo que puede hacer que el problema difícil valga 300 y el calentamiento valga 50. **`order_in_contest`** (`1` predeterminado) corrige dónde aparece el problema en la lista. Hay un techo rígido: `MAX_PROBLEMS_IN_CONTEST` es **30** (definido en `frontend/server/config.default.php:176`), y el `apiAddProblem` número 31 arroja `contestAddproblemTooManyProblems`.

Una sutileza que vale la pena internalizar: agregar un problema lo fija a un **commit git específico** de ese problema (a través de `Problem::resolveCommit`, que resuelve el parámetro opcional `commit` o el compromiso maestro del problema). Esto congela los datos exactos de la prueba y la declaración que verán sus concursantes, de modo que un autor que edite la versión en vivo del problema a mitad del concurso no pueda cambiar el terreno bajo un evento en ejecución. Después de la escritura, `apiAddProblem` invalida dos cachés (`Cache::CONTEST_INFO` para el alias y el caché del marcador a través de `Scoreboard::invalidateScoreboardCache`), por lo que el cambio aparece inmediatamente en lugar de mostrar una página de concurso obsoleta. Para solucionar un problema, `apiRemoveProblem` es la imagen reflejada.

## Gestión de participantes {#managing-participants}

Debido a que cada concurso es privado hasta que usted indique lo contrario, la lista de participantes *es* la lista de control de acceso. La forma de completarlo depende de `admission_mode`, que configuró a través de `apiUpdate` (la enumeración es `'private' | 'public' | 'registration'`):

- **`private`**: solo pueden participar las identidades que usted invite explícitamente. Esta es la opción predeterminada y correcta para un salón de clases.
- **`public`**: cualquier usuario de omegaUp puede unirse sin invitación. `is_invited` es lo que distingue a alguien que agregaste deliberadamente de alguien que simplemente entró en un concurso público, lo cual es importante cuando luego lees la lista de participantes.
- **`registration`** — los concursantes *solicitan* acceso y tú los apruebas. Sus solicitudes aparecen a través de `apiRequests`, y usted acepta o rechaza cada una con `apiArbitrateRequest`. Este es el término medio para un evento abierto pero examinado.Para un concurso privado invitas a las personas una a la vez con `Contest::apiAddUser` (`Contest.php:3859`), pasando un `usernameOrEmail`. Escribe una fila `ProblemsetIdentities` con `is_invited => true` (y `score`/`time` puesto a cero, `end_time` nulo, por lo que su ventana personal no se ha iniciado). Un problema está aquí: si el concurso se creó con `contest_for_teams`, `apiAddUser` se niega con `usersCanNotBeAddedInContestForTeams`: un concurso en equipo extrae su lista de un grupo, por lo que usa `apiAddGroup` (o `apiReplaceTeamsGroup`) en lugar de agregar individuos. Y una comodidad: si el concurso es en modo `registration`, invitar a alguien a través de `apiAddUser` también **acepta previamente** su solicitud de acceso a través de `preAcceptAccessRequest`, por lo que se salta la cola de solicitudes por completo.

Invitar a toda una clase, con un nombre de usuario a la vez, se vuelve obsoleto rápidamente, por eso existe `apiAddGroup`: cree un grupo una vez (su lista de "Periodo 3 CS") y agregue todo el grupo a cualquier concurso en una sola llamada. Para traspasar las tareas de coorganización, `apiAddAdmin` y `apiAddGroupAdmin` otorgan derechos de administrador sobre el concurso en sí.

## El marcador {#the-scoreboard}

Las clasificaciones en vivo son proporcionadas por `apiScoreboard`, con una transmisión de eventos incremental de `apiScoreboardEvents` que la interfaz reproduce para animar los cambios de clasificación. Dos campos que usted establece en la creación gobiernan la visibilidad y se componen: **`scoreboard`** (0–100) controla la cantidad de competencia *en ejecución* que el tablero está activo (su congelación), mientras que **`show_scoreboard_after`** decide si se revelará por completo una vez que finalice la competencia. Una configuración común es `scoreboard: 100, show_scoreboard_after: true` para una práctica transparente, versus `scoreboard: 0, show_scoreboard_after: true` para una selección de "resultados solo al final". `default_show_all_contestants_in_scoreboard` controla si los administradores y los no participantes aparecen junto a los concursantes de forma predeterminada.

Las actualizaciones llegan en tiempo real a través del WebSocket **Broadcaster** en `wss://omegaup.com/events/`, un servicio Go separado en el repositorio [`omegaup/quark`](https://github.com/omegaup/quark), que no forma parte del backend de PHP, por lo que un problema resuelto sube al tablero sin que nadie tenga que recargar. Si su red está bloqueada, es necesario que se pueda acceder a ese WebSocket (consulte la lista de verificación a continuación) o la placa volverá silenciosamente a un sondeo más lento. Cuando organizas dos sesiones del mismo evento y quieres una clasificación combinada (por ejemplo, una sección de la mañana y otra de la tarde), `apiScoreboardMerge` reúne varias competencias en un solo marcador.

## Modos de concurso {#contest-modes}

Más allá de los controles por campo, tres modos amplios cubren casi todos los eventos reales:

**Estándar (reloj compartido).** El valor predeterminado: un `start_time`, un `finish_time`, un `window_length` y un `null`. Todos compiten en el mismo reloj de pared. Ésta es la forma del CIPC/aula.

**Virtual (repetición estilo USACO).** `Contest::apiCreateVirtual` (`Contest.php:2735`) clona un concurso *terminado* en uno nuevo que puedes realizar como un examen simulado: el original ya debe haber terminado o arrojará el `originalContestHasNotEnded`. En combinación con `window_length`, así es como un estudiante "dirige" la Olimpiada nacional del año pasado un martes a las 19:00 horas y aún así recibe la auténtica presión del tiempo: su cronómetro personal comienza cuando lo abre. Recuerde que los problemas en un concurso virtual están congelados: el `forbiddenInVirtual` bloquea la edición.

**Bloqueo.** Un modo de integridad al que puedes optar únicamente por *el nombre de host* a través del cual se conectan tus concursantes. Se trata a continuación, porque en una escuela es realmente una decisión de networking.

## Realizar un concurso en una escuela (lista de verificación de la red) {#running-a-contest-at-a-school-network-checklist}

Si los concursantes se sientan en un **laboratorio escolar** o en una red bloqueada, permita la salida **HTTPS (puerto 443)** a omegaUp y a los pocos servicios en los que se apoya. Todo es HTTPS: una solicitud al puerto 80 simplemente recibe una redirección al 443, por lo que el puerto 443 es todo lo que necesita para abrir.

**Requerido:**

- **`https://omegaup.com`** — modo de concurso estándar.
- **`https://arena.omegaup.com`** — *solo* si usas intencionalmente el **modo de bloqueo** (a continuación). Si usas el bloqueo, debes **bloquear** `omegaup.com` para los concursantes, o simplemente pueden cambiar al anfitrión normal y sortear todas las restricciones.
- **`https://ssl.google-analytics.com`** — utilizado por el sitio.

**Opcional (cada uno degrada una comodidad si se bloquea, nada se rompe):**

- **`https://secure.gravatar.com`**: el avatar en la esquina superior derecha.
- **`https://accounts.google.com`** — "Iniciar sesión con Google".
- **`https://connect.facebook.net`** y **`https://s-static.*.facebook.com`** — "Iniciar sesión con Facebook".

Hay una regla de firewall no obvia que guardará su evento: configure los hosts bloqueados para **RECHAZAR/DENEGAR con una respuesta explícita**, nunca **DROP**. En un DROP, el navegador no obtiene respuesta y sigue esperando; se bloqueará durante aproximadamente **20 a 30 segundos** por dominio bloqueado antes de darse por vencido, y para una sala llena de estudiantes, toda la página parece congelada. Un rechazo explícito falla rápidamente y la interfaz de usuario sigue respondiendo.

### Modo de bloqueo (`arena.omegaup.com`) {#lockdown-mode-arenaomegaupcom}

Dirija a los concursantes a `https://arena.omegaup.com/` en lugar del anfitrión normal y entrarán en **modo de bloqueo**, creado para cuando necesita garantías más sólidas de que los estudiantes no puedan pasarse información entre sí a través de la plataforma. Gran parte de la funcionalidad del sitio está desactivada deliberadamente y **no son posibles excepciones por concurso**; el valor del bloqueo es que no se puede desbloquear de forma selectiva. Las funciones que más comúnmente se pasan por alto durante el bloqueo son:

- **Modo administrador.**
- **Modo práctica.**
- **Ver la fuente de envíos anteriores**: donde el sitio normal muestra su código anterior, el bloqueo muestra un mensaje de error.

Si su situación realmente necesita una de las cosas que el bloqueo bloquea, la respuesta no es hacerle un agujero: es no usar el bloqueo y, en su lugar, conectarse a través de `https://omegaup.com`.

### Entorno del concursante (laboratorio de Windows frente al juez) {#contestant-environment-windows-lab-vs-the-judge}

Los envíos se califican en **Linux**, por lo que cualquier distribución de Linux razonablemente reciente en las máquinas del laboratorio coincide exactamente con el entorno de evaluación. Windows es donde viven los cortes de papel: el código que incluye el encabezado `conio.h` exclusivo de Windows no se compilará en el juez, y las cadenas de herramientas más antiguas de Windows imprimen `long long` con `%I64d` en lugar del `%lld` portátil. Entrene a sus concursantes sobre E/S compatibles con POSIX (`%lld` (o transmisiones C++) y encabezados estándar) para que un programa que se ejecutó en la PC del laboratorio no muera al enviarse.

### Eventos grandes (más de 100 participantes) {#large-events-100-participants}

Si está planeando un concurso grande (**100 o más** concursantes simultáneos), envíe un correo electrónico a **hello@omegaup.com** con suficiente antelación para que el equipo pueda confirmar la capacidad para su fecha. Es una cortesía que evita una mala sorpresa ese día.

## Documentación relacionada {#related-documentation}

- **[Referencia de API](../../reference/api.md)**: la referencia completa del punto final detrás de todo lo que se encuentra aquí.
- **[Arena](../arena.md)**: la interfaz que realmente ven los concursantes.
- **[Actualizaciones en tiempo real](../realtime.md)**: cómo Broadcaster WebSocket controla el marcador en vivo.
