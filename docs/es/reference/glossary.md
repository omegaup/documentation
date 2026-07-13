---
title: Glosario
description: Terminología y definiciones utilizadas en omegaUp
icon: bootstrap/book
---
# Glosario

Este es el vocabulario que los mantenedores realmente usan en la revisión del código, en el rastreador de problemas y cuando algo falla a las 2 a.m. Deliberadamente no es un diccionario alfabético de palabras de moda de MVC: las entradas se agrupan según su ubicación en la vida de un envío, porque así es como se construye el sistema y cómo terminará depurándolo. Casi todos los términos enlazan con el símbolo, archivo o clave de configuración exacto que lo implementa, por lo que puede leer la verdad en lugar de confiar en esta página.

Dos cosas que vale la pena interiorizar antes de seguir leyendo. Primero, omegaUp son **dos repositorios que hablan a través de HTTP**, no uno: el monorepo de PHP ([`omegaup/omegaup`](https://github.com/omegaup/omegaup)) es la interfaz, la API y la aplicación web; la maquinaria de evaluación real (Grader, Runner, Broadcaster y Sandbox) se encuentra en el repositorio de Go [`omegaup/quark`](https://github.com/omegaup/quark), con problemas de almacenamiento en [`omegaup/gitserver`](https://github.com/omegaup/gitserver). Cuando esta página dice que el lado PHP "llama al Grader", significa literalmente un `curl` sobre `OMEGAUP_GRADER_URL`. En segundo lugar, gran parte de la antigua tradición wiki (HHVM, Smarty, un clasificador de 8 colas con nombres) está muerta; donde se ha movido la implementación de un término, la entrada lo dice.

---

## El canal de envío

Estos son los componentes por los que pasa una sola presentación, aproximadamente en el orden en que los toca. Si solo lees una sección, lee ésta: es el lomo del que cuelga todo lo demás.

### Arena

La Arena es la interfaz de usuario del concurso y la práctica: la pantalla de panel dividido donde un concursante lee un problema, escribe código en el editor integrado, lo envía y observa la actualización del marcador y las aclaraciones en vivo. **No** es un servicio separado (se presentó como uno para una hipotética "v2" hace años y nunca se dividió); hoy es Vue 2.7 simple ejecutándose en el navegador, con un punto de entrada de TypeScript por modo en `frontend/www/js/omegaup/arena/`: `contest_contestant.ts` para un concurso en vivo, `contest_practice.ts` para [modo de práctica](#practice-mode) y `contest_virtual.ts` para un [concurso virtual](#virtual-contest). Todo lo que hace es una llamada API ordinaria: envía código a `/api/run/create/`, sondea `/api/contest/scoreboard/` y abre un socket [Broadcaster](#broadcaster) para actualizaciones push, de modo que no tiene que sondear para cada veredicto. Consulte [Arena](../features/arena.md) para conocer el recorrido orientado al usuario y [Arquitectura de interfaz](../architecture/frontend.md) para conocer cómo están conectados los puntos de entrada de Vue.

### Ejecutar / Envío

Una **presentación** es lo que envía el concursante (código fuente + idioma + qué problema y, si corresponde, qué concurso); una **ejecución** es el artefacto calificado que regresa. En la base de datos, estas en realidad son dos tablas: `Submissions` contiene el código y los metadatos, `Runs` contiene el [veredicto](#verdict), la puntuación, el tiempo de ejecución y la memoria, porque un solo envío se puede calificar más de una vez (un [rejuicio](#rejudge) produce una nueva ejecución para el mismo envío). Todo es creado por `\OmegaUp\Controllers\Run::apiCreate` (`frontend/server/src/Controllers/Run.php`, alrededor de la línea 415), que es la función más instructiva del backend para leer: en una sola pasada valida que todos los campos obligatorios estén presentes, que el problema pertenece al concurso, que el [límite de tiempo](#time-limit) no haya expirado, que el usuario no esté excediendo la tasa de envío (`Run::$defaultSubmissionGap = 60` segundos entre envíos al mismo problema). por defecto), y que el concurso es público o el usuario fue invitado explícitamente. Solo después de todo eso se entrega al clasificador en la línea ~573 a través de `\OmegaUp\Grader::getInstance()->grade($run, trim($source))`. Cada ejecución se identifica mediante un `guid` opaco: esa es la identificación que ve en las URL y pasa a `/api/run/status/`.

Un campo con el que te tropezarás: `submit_delay` es *el número de minutos desde que se abrió el problema (o comenzó el concurso) hasta que se envió el envío*, y es exactamente en lo que se convierte el marcador [penalización](#penalty). Es `0` para [práctica](#practice-mode) y para envíos públicos de problemas fuera de cualquier concurso; `submission_deadline` también es `0` cuando no estás dentro de un concurso.

### Calificador

El evaluador es el cerebro de la mitad evaluadora: un servicio Go en [`omegaup/quark`](https://github.com/omegaup/quark) (`cmd/omegaup-grader/`) que posee la cola de carreras pendientes y se las entrega a los [corredores](#runner). El backend de PHP nunca toca la cola directamente: solo le habla HTTP a través de `\OmegaUp\Grader` (`frontend/server/src/Grader.php`), presiona `OMEGAUP_GRADER_URL` (`https://localhost:21680` predeterminado) en `/run/new/{run_id}/` para poner en cola una nueva ejecución, `/run/grade/` para forzar un [rejuicio](#rejudge), `/broadcast/` para desplegar un mensaje a través del [Transmisor](#broadcaster) y `/grader/status/` para leer el estado de la cola. Esa carga útil de estado (`run_queue_length`, `runner_queue_length`, `runners`, `broadcaster_sockets`, `embedded_runner`) es lo que `\OmegaUp\Controllers\Grader::apiStatus` muestra en el panel de administración.

Dos hechos de implementación que importan y contradicen la antigua wiki. Primero, el modelo de cola tiene **cuatro niveles de prioridad, no ocho colas con nombre**: `grader/queue.go` define `QueuePriorityHigh (0)`, `QueuePriorityNormal (1)`, `QueuePriorityLow (2)` y `QueuePriorityEphemeral (3)` con `QueueCount = 4`; un envío de concurso normal ingresa en `QueuePriorityNormal`, y el nivel efímero es especial porque deliberadamente *no* persiste los resultados en el sistema de archivos (respalda el campo de juego "ejecutar este fragmento"). En segundo lugar, el clasificador asume que los corredores pueden morir: el `InflightMonitor` en `grader/queue.go` arma un `connectTimeout` y un `readyTimeout` de **10 minutos cada uno**, y si un corredor toma una carrera y luego se queda en silencio después de esa fecha límite, se presume que está muerta y la carrera se vuelve a poner en cola, se reintenta hasta `Config.Grader.MaxGradeRetries` veces antes de ser abandonada. Consulte [Conceptos internos del clasificador](../architecture/grader-internals.md) para conocer la máquina de estado completa.

### Corredor

Un Runner es un trabajador de Go (también en `omegaup/quark`, `cmd/omegaup-runner/`) que realiza la compilación y ejecución real. **Extrae** el trabajo en lugar de ser forzado a hacerlo: sondea durante mucho tiempo el punto final `/run/request/` del Grader y, cuando se ejecuta, compila el código fuente y lo ejecuta en cada [caso de prueba](#test-case) dentro del [sandbox](#minijail--omegajail), transmitiendo los resultados. El mejor modelo mental, directamente de las notas de diseño originales, es que el Runner *sabe cómo compilar, ejecutar y alimentar entradas a un programa, y ​​comprobar si es correcto; es básicamente una bonita interfaz distribuida para el entorno de pruebas.* Muchos Runners se registran con un Grader y se les envía por turnos (hoy en día no hay afinidad, aunque existió en un momento y no sería difícil volver a agregarla). Si a un Runner se le entrega una ejecución pero no tiene el conjunto de entradas del problema almacenado en caché localmente, lo dice y el Grader vuelve a enviar la entrada `.zip`; si la compilación falla, elimina los archivos temporales y devuelve el stderr del compilador como [CE](#verdict). Consulte [Conceptos internos del corredor](../architecture/runner-internals.md).

### Minicárcel / omegacárcel

Esta es la zona de pruebas que hace que sea seguro ejecutar C++ de un extraño en su servidor. El linaje: **minijail** es el encarcelador de procesos de bajo nivel (el binario enviado en `Dockerfile.minijail` como `minijail-xenial-distrib`), y **omegajail** es el envoltorio de omegaUp que lo rodea; en Runner es `OmegajailSandbox` (`runner/sandbox.go`), que desembolsa hasta `bin/omegajail` bajo un `omegajailRoot` con banderas como `--root`. Aplica el [tiempo](#time-limit) y los [límites de memoria](#memory-limit), bloquea el acceso a la red y limita el sistema de archivos, por lo que un envío que intenta abrir un socket, fork-bomb o leer `/etc/passwd` simplemente no puede. Cuando un programa intenta una llamada al sistema prohibida, el sandbox lo cancela y la ejecución regresa [RFE](#verdict) (error de función restringida). Tenga en cuenta que se encuentra completamente en `omegaup/quark`, no en el repositorio de PHP: realizar un grep del monorepo para `minijail` devuelve cero resultados por diseño, porque la interfaz nunca lo invoca y solo ve el veredicto. Consulte [Zona de pruebas](../features/sandbox.md).

### Locutor

The Broadcaster es el servicio de distribución en tiempo real (Go, `omegaup/quark`, `broadcaster/`). Cuando sucede algo que un concursante debería ver: llega un [veredicto](#verdict), se responde una [aclaración](#clarification), el [marcador](#scoreboard) cambia, el lado PHP llama a `\OmegaUp\Broadcaster`, que realiza una PUBLICACIÓN en el `/broadcast/` del evaluador, y el emisor envía ese mensaje a cada cliente conectado relevante para que el [Arena](#arena) se actualiza sin sondeo. "Relevante" se decide mediante filtros en `broadcaster/filter.go`: un `UserFilter`, `ProblemFilter`, `ProblemsetFilter`, `ContestFilter` y un `AllEventsFilter` general, por lo que un mensaje para el concurso X solo llega a los sockets suscritos al concurso X. Habla dos transportes (`broadcaster/transport.go`): `WebSocketTransport` y un respaldo `SSETransport`. Consulte [Arquitectura de emisora](../architecture/broadcaster.md) y [Actualizaciones en tiempo real](../features/realtime.md).

### Servidor Git

Los problemas se almacenan como **repositorios git**, un repositorio por problema, y GitServer ([`omegaup/gitserver`](https://github.com/omegaup/gitserver), Go) es lo que los sirve y versiona. Cada edición de una declaración, caso de prueba o [validador](#validator) es una confirmación, por lo que un problema tiene un historial completo y un concurso se puede anclar a una versión de problema específica incluso después de que el autor siga editando (consulte [Versión de problemas](../features/problem-versioning.md)). El lado PHP lo alcanza en `OMEGAUP_GITSERVER_URL` (`http://localhost:33861` predeterminado, de `OMEGAUP_GITSERVER_PORT`) autenticado con `OMEGAUP_GITSERVER_SECRET_TOKEN`. Consulte [arquitectura de GitServer](../architecture/gitserver.md).

---

## Veredictos

### VeredictoEl resultado de una carrera en una palabra. La lista canónica y autorizada es `VerdictList` en `common/problemsettings.go` en `omegaup/quark`, y se almacena **ordenada de peor a mejor**; este orden soporta carga, porque cuando un envío se juzga caso por caso, el veredicto final es el veredicto del *peor* caso, por lo que "los peores tipos primero" es como lo elige el corredor:

`JE` → `CE` → `RFE` → `VE` → `MLE` → `RTE` → `TLE` → `OLE` → `WA` → `PA` → `AC` → `OK`

Cada uno:

- **`AC` (Aceptado)**: todos los casos son correctos dentro de los límites. El que tu quieras.
- **`PA` (Parcialmente aceptado)**: algunos casos/[grupos](#test-group) aprobaron, otros no, y el [modo de puntuación](#score-mode) otorga crédito parcial.
- **`WA` (Respuesta incorrecta)**: el resultado estaba bien formado pero era incorrecto en al menos un caso.
- **`OLE` (límite de salida excedido)**: el programa imprimió más del [límite de salida] permitido (#output-limit); Runner también genera esto si un programa en una configuración interactiva hace que su padre se desborde.
- **`TLE` (límite de tiempo excedido)**: se superó el [límite de tiempo] por caso (#time-limit).
- **`RTE` (Error de tiempo de ejecución)**: falla: error de segmento, excepción no detectada, salida distinta de cero, división por cero.
- **`MLE` (Límite de memoria excedido)**: superó el [límite de memoria](#memory-limit).
- **`VE` (Error del validador)**: el [validador] personalizado del problema (#validator) no pudo producir una puntuación utilizable (un error del autor del problema, no un error del concursante).
- **`RFE` (Error de función restringida)**: el [sandbox](#minijail--omegajail) eliminó el programa por intentar una llamada al sistema prohibida, p. intentando abrir un socket de red.
- **`CE` (Error de compilación)** — no se compiló; Se devuelve el stderr del compilador para que el concursante pueda ver por qué.
- **`JE` (Error de evaluación)** — Fallo propio de omegaUp: datos de prueba incorrectos, un validador roto o problemas de infraestructura. Si ve esto, consulte los registros del calificador, no culpe al concursante.
- **`OK`**: un marcador interno por caso de "este caso funcionó bien" utilizado dentro del Runner, no un veredicto final de cara al usuario.

El veredicto llega a `Runs.verdict` y lleva al [Locutor](#broadcaster) a la [Arena](#arena). Consulte [Veredictos](../features/verdicts.md) para ver ejemplos prácticos de cada uno.

---

## Concursos, cursos y su fontanería compartida

### Concurso

Una competencia cronometrada sobre un conjunto de [problemas](#problem), propiedad de `\OmegaUp\Controllers\Contest`. Un concurso tiene una política estricta de `start_time`/`finish_time`, un [marcador](#scoreboard), un [modo de puntuación](#score-mode) y una [penalización](#penalty), un `admission_mode` (público o solo por invitación) y un `window_length` opcional: el reloj por concursante para "obtienes N minutos desde cuando *tú* empiezas", que devuelve `null` cuando el concurso no se configuró de esa manera. Tenga en cuenta que un concurso no almacena sus problemas directamente; apunta a un [conjunto de problemas](#problemset).

### Curso

Un contenedor estructurado y orientado a la clase: una secuencia de tareas, cada una de las cuales es en sí misma un [conjunto de problemas](#problemset), además de estudiantes, fechas límite, seguimiento del progreso y asistentes docentes opcionales. Propiedad de `\OmegaUp\Controllers\Course`. La división mental es que un **concurso es un evento de una sola vez** y un **curso es una clase continua**, pero debido a que ambos agrupan los problemas en conjuntos de problemas, comparten casi toda la maquinaria de presentación de ejecución, marcador y aclaración que se encuentra debajo.

### Conjunto de problemas

La abstracción que permite que los concursos y las tareas del curso reutilicen el mismo código. Un **conjunto de problemas** es simplemente "un conjunto de problemas que las personas enfrentan", identificado por `problemset_id`; un concurso *tiene* un conjunto de problemas y cada tarea del curso *es* un conjunto de problemas (`\OmegaUp\Controllers\Problemset`). Esta es la razón por la que una [ejecución](#run--submission) lleva un `problemset_id` en lugar de un `contest_id`: a la ejecución no le importa si se envía a un concurso o a una tarea, solo qué conjunto de problemas la gobierna. Si alguna vez se siente confundido acerca de por qué la lógica del concurso y del curso se ven tan similares, esta es la respuesta: son el mismo conjunto de problemas de plomería con tapas diferentes.

### Aclaración

El canal de preguntas y respuestas del concurso. Un concursante hace una pregunta sobre un problema vía `\OmegaUp\Controllers\Clarification::apiCreate` (`frontend/server/src/Controllers/Clarification.php`); se almacena en la tabla `Clarifications` con un indicador `public`. Cuando un organizador responde, o lo marca como público, el controlador lo empuja a través del `\OmegaUp\Broadcaster` estático para que aparezca en vivo en la [Arena](#arena) de quienes preguntan (o en la de todos, si es pública) sin una actualización. La bandera `public` es el matiz importante: una aclaración privada va sólo a quien pregunta, una pública se transmite a todo el concurso para que todos vean la misma decisión.

### Marcador

La clasificación en vivo. Construido en `frontend/server/src/Scoreboard.php` y, esta es la parte que la gente olvida, está **muy almacenado en caché** en Redis bajo claves distintas para las dos audiencias: `CONTESTANT_SCOREBOARD_PREFIX` (lo que ven los jugadores, respetando [congelación](#scoreboard-freeze)) y `ADMIN_SCOREBOARD_PREFIX` (la verdad no congelada para los organizadores), cada uno con un `..._EVENTS_PREFIX` paralelo para la línea de tiempo animada. La clasificación se ordena por puntos totales y luego por [penalización] total (#penalty), y cómo se agrega la penalización entre los problemas depende de `penalty_calc_policy` (`sum` agrega la penalización de cada problema; `max` toma solo la mayor). Debido a que es costoso volver a calcular, Arena escucha los empujones de [Broadcaster](#broadcaster) en lugar de volver a buscarlos constantemente.

### Penalización

El tiempo de desempate en la puntuación al estilo ICPC: con puntos iguales, quien acumuló menos penalizaciones ocupará un lugar más alto. **Cuando** la penalización comienza a contar se establece mediante `penalty_type`, una enumeración con exactamente cuatro valores (`Contest.php`): `contest_start` (minutos contados desde el inicio del concurso), `problem_open` (desde que *ese concursante* abrió por primera vez *ese problema*), `runtime` (use el tiempo de ejecución real de la solución) y `none` (sin penalización alguna: carrera de puntuación pura). **Cómo** se agregan los problemas es el `penalty_calc_policy` separado (`sum` vs `max`) que se describe en [Marcador](#scoreboard). El valor bruto por envío es el `submit_delay` de la ejecución; Los envíos incorrectos antes de los aceptados añaden una penalización fija adicional (convencionalmente, 20 minutos cada uno en las reglas del ICPC).

### Modo de puntuación

Cómo los resultados por caso de un problema se resumen en un número, establecido por `score_mode` con tres valores (`Contest.php`): `all_or_nothing` (obtiene la máxima puntuación solo si cada caso es [AC](#verdict) - ICPC clásico), `partial` (suma los pesos de los casos/[grupos](#test-group) que aprobó - IOI clásico), y `max_per_group` (tomar el mejor resultado por grupo y sumarlos). Esto es lo que decide si una solución de medio derecho gana [PA](#verdict) y algunos puntos o solo [WA](#verdict) y cero.

### Congelación del marcador

El mecanismo de suspenso: cerca del final de un concurso, el [marcador] público (#scoreboard) deja de actualizarse para los concursantes mientras los organizadores siguen viendo las clasificaciones en vivo, implementado como la división entre los cachés `CONTESTANT_SCOREBOARD_PREFIX` y `ADMIN_SCOREBOARD_PREFIX`. Las presentaciones todavía se juzgan normalmente; solo se lleva a cabo la *vista* pública, por lo que la revelación final es dramática y nadie puede aplicar ingeniería inversa a su posición exacta para jugar los últimos minutos.

### Modo de práctica

Una vez finalizado un concurso (o sobre cualquier problema público), puedes seguir enviando mensajes para aprender sin nada en juego. En `Run::apiCreate`, esta es la rama `isPractice`: `submit_delay` se fuerza a `0` y no se acumula [penalización](#penalty), y el acceso está controlado por `Problems::getPracticeDeadline` en lugar del reloj del concurso; envíelo después de esa fecha límite y será rechazado. El punto de entrada de Arena es `contest_practice.ts`. El punto es permitir que la gente resuelva viejos problemas sin contaminar ninguna clasificación en vivo.

### Concurso virtual

Volver a ejecutar un concurso terminado contra su reloj *original* para que puedas experimentarlo como si estuvieras compitiendo: los mismos problemas, la misma duración, pero cambiado al ahora y puntuado en un marcador privado que no toca los resultados históricos reales. Punto de entrada `contest_virtual.ts`. Es la forma honesta de "tomar" un concurso pasado para practicar bajo presión en tiempo real.

### Bloqueo

Un **cambio global de solo lectura para todo el sitio**, no una función anti-trampas por concurso. Cuando `OMEGAUP_LOCKDOWN` está activado, `\OmegaUp\Controllers\Controller::ensureNotInLockdown()` lanza `ForbiddenAccessException('lockdown')` desde cada punto final mutante, por lo que el sitio sigue ofreciendo lecturas pero rechaza escrituras, utilizadas durante migraciones o incidentes. Tiene un compañero `OMEGAUP_LOCKDOWN_DOMAIN` (por defecto `localhost-lockdown`). No lo confunda con las características de seguridad de los exámenes del concurso; éste es el interruptor de apagado del operador para escrituras.

---

## Anatomía del problema

### Problema

La unidad atómica de contenido: una declaración, especificación de entrada/salida, restricciones, [casos de prueba](#test-case), límites y un [validador](#validator) opcional, almacenado como un repositorio de git en el [GitServer](#gitserver) y propiedad del lado PHP de `\OmegaUp\Controllers\Problem`. Todo lo demás (concursos, cursos, carreras) existe para que las personas se presenten ante los problemas.

### Caso de prueba

Un archivo de entrada emparejado con su salida esperada. Un envío es [AC](#verdict) solo si satisface todos los casos de prueba dentro de [límites](#time-limit); el [veredicto](#verdict) del peor de los casos se convierte en el veredicto de la ejecución.

### Grupo de pruebaUn conjunto de casos de prueba con nombre que puntúan juntos y se utiliza para la calificación de estilo de subtarea. La convención de nomenclatura es mecánica y vale la pena conocerla: el grupo de un caso es *todo lo anterior al primer `.` en su nombre* (por lo que `2.a`, `2.b`, `2.c` pertenecen todos al grupo `2`), y bajo `all_or_nothing`/`max_per_group` [puntuación](#score-mode) un grupo otorga sus puntos solo si Todo el grupo está satisfecho. Los pesos están normalizados para que sumen 1 o, de forma predeterminada, 1/(número de casos) cuando no se especifican.

### Validador

Para problemas con más de una respuesta correcta (cualquier orden, tolerancia de punto flotante, "imprimir cualquier ruta más corta"), una diferencia de texto sin formato no sirve, por lo que el autor envía un programa **validador** que lee la salida del concursante y decide la puntuación. La estrategia de comparación es el [tipo de validador](#validator-type). Si el validador falla, la ejecución es [VE](#verdict), no [WA](#verdict); esa distinción le indica de quién es el error.

### Tipo de validador

Cómo se verifica la salida. `token` / `token-caseless` compara token por token (opcionalmente ignorando mayúsculas y minúsculas), `token-numeric` compara números dentro de un épsilon (por lo que `1.0000001` coincide con `1.0`), `literal` exige una coincidencia exacta de bytes y `custom` entrega la decisión al programa [validador] del autor (#validator).

### Límite de tiempo / Límite de memoria / Límite de salida {#time-limit}

Los tres límites máximos de recursos que el [sandbox](#minijail--omegajail) aplica por caso. **Límite de tiempo** es el tiempo de pared/CPU (incumplirlo produce [TLE](#verdict)); **límite de memoria** es el límite de espacio de direcciones en KiB (incumplirlo produce [MLE](#verdict)); El **límite de salida** limita la cantidad de bytes que un programa puede imprimir (incumpliéndolo produce [OLE](#verdict)), que existe por lo que un `while(true) printf(...)` infinito no puede llenar un disco. Estas son configuraciones por problema; la aplicación real son las banderas omegajail en `runner/sandbox.go`, no PHP.

---

## Bloques de construcción de backend

### Controlador

Las clases PHP que implementan la API y contienen la lógica empresarial, en `frontend/server/src/Controllers/` bajo el espacio de nombres `\OmegaUp\Controllers`. Una convención que molesta a los recién llegados: los nombres de clases **eliminan el sufijo `Controller`**: el punto final de ejecución reside en la clase `Run` (`\OmegaUp\Controllers\Run` completamente calificado), no en `RunController`; así mismo `Contest`, `Problem`, `Clarification`, `Grader`. Los métodos API públicos tienen el prefijo `api…` (`apiCreate`, `apiStatus`).

### ApiCaller/punto de entrada

Cada solicitud de `/api/...` llega a `frontend/www/api/ApiEntryPoint.php`, que `require` llama a `frontend/server/bootstrap.php` y luego llama a `\OmegaUp\ApiCaller::httpEntryPoint()`. `ApiCaller` (`frontend/server/src/ApiCaller.php`) es el despachador: analiza la ruta, verifica el [token de autenticación](#authentication-token) e invoca el método `api…` del controlador correcto. Esa cadena (archivo de entrada → bootstrap → ApiCaller → `Controller::apiXxx`) es la puerta de entrada para todo el backend. Consulte [Arquitectura de backend](../architecture/backend.md).

### DAO (objeto de acceso a datos)

La capa de acceso a datos generada. Cada tabla obtiene una base abstracta generada automáticamente en `frontend/server/src/DAO/Base/` (por ejemplo, `Base/Runs.php`, que contiene el SQL sin formato `INSERT`/`UPDATE`) además de un contenedor público editable manualmente en `frontend/server/src/DAO/` donde se encuentran las consultas personalizadas. La división existe, por lo que la regeneración del texto estándar nunca obstaculiza sus consultas personalizadas. El acceso es vía `mysqli` contra MySQL 8.0 (`MySQLConnection.php`). Consulte [Patrones de base de datos](../development/database-patterns.md).

### VO (objeto de valor)

Los objetos de fila escritos por los que se mueven los DAO, en `frontend/server/src/DAO/VO/` (por ejemplo, `VO/Runs.php`). Un VO es un registro con propiedades escritas y un mapa `FIELD_NAMES`: usted recupera los VO de un DAO, los muta y se los devuelve al DAO para que persistan. Juntos **DAO + VO** son la forma en que el código base evita la escritura a mano de cadenas SQL en los controladores; la página [Patrón MVC](../architecture/mvc-pattern.md) tiene la imagen completa.

### Token de autenticación

La credencial que identifica a un usuario en llamadas API, contenida en la cookie `ouat` y validada por [`ApiCaller`](#apicaller--entrypoint). Debajo del capó, estos son tokens PASETO (`paragonie/paseto`), no las cadenas ad-hoc que describía la antigua wiki. Una llamada no autenticada a un punto final protegido devuelve un error de permiso, no una redirección, porque la API debe consumirse mediante programación.

### Rejuzgar

Volver a ejecutar un [envío](#run--submission) existente para producir un [ejecución](#run--submission) nuevo: después de corregir un [caso de prueba](#test-case) incorrecto, se corrige un [validador](#validator) o se modifican los límites. El lado PHP lo activa llamando al punto final `/run/grade/` del Grader; en la [cola](#grader) un nuevo juez ingresa con una prioridad más baja para no privar a las presentaciones del concurso en vivo.

---

## Documentación relacionada

- **[Grader internals](../architecture/grader-internals.md)**: la máquina de estado de cola, envío y reintento
- **[Runner internals](../architecture/runner-internals.md)**: compila/ejecuta la canalización y la llamada de sandbox
- **[Transmisor](../architecture/broadcaster.md)** y **[Actualizaciones en tiempo real](../features/realtime.md)**: cómo llegan las actualizaciones en vivo a la Arena
- **[GitServer](../architecture/gitserver.md)** — problemas como repositorios de git
- **[Arquitectura de backend](../architecture/backend.md)** y **[patrón MVC](../architecture/mvc-pattern.md)**: controladores, DAO/VO, el punto de entrada API
- **[Veredictos](../features/verdicts.md)** — cada veredicto con ejemplos
- **[Sandbox](../features/sandbox.md)** — aislamiento minijail/omegajail
- **[Idiomas](languages.md)**: compiladores admitidos y claves de idioma
