---
title: Guías de desarrollo
description: Guías para desarrolladores, estándares de codificación y mejores prácticas
icon: bootstrap/code-tags
---
# Quiero Desarrollarme en omegaUp

Gracias por su interés en contribuir con omegaUp. Esta página es la puerta de entrada al código base: le indica de qué está hecho realmente el sistema, en qué repositorio reside cada pieza, a qué parte del árbol probablemente pertenece su cambio y qué guía leer a continuación una vez que haya elegido un camino.

Si aún no está familiarizado con omegaUp como *usuario*, hágalo primero. Vaya a [omegaup.com](https://omegaup.com/), cree una cuenta y resuelva uno o dos problemas para sentir el ciclo de enviar y obtener un veredicto desde afuera antes de leer el código que lo ejecuta. Luego [omegaup.org](https://omegaup.org/) lo orientará sobre la organización y las áreas en las que trabajamos. Es mucho más fácil razonar sobre `apiCreate` una vez que haya visto su propio envío ponerse verde.

## El modelo mental de 30 segundos

omegaUp no es un programa, es una pequeña constelación de servicios, y lo más útil que hay que internalizar antes de clonar algo es **qué repositorio posee qué**, porque un cambio en cómo se calcula un veredicto y un cambio en cómo se muestra una página de concurso en bases de código completamente diferentes y en diferentes idiomas.

- **[omegaup/omegaup](https://github.com/omegaup/omegaup)** es el más grande, el PHP + Vue **frontend y API monorepo**. Aquí es donde seguramente querrás empezar. Representa cada página, expone toda la superficie `/api/`, posee el esquema MySQL y se comunica con todo lo demás en la red. Cuando la gente dice "el código base omegaUp" sin calificación, se refieren a este repositorio.
- **[omegaup/quark](https://github.com/omegaup/quark)** es el **backend de evaluación**, escrito en Go: el *calificador* (posee la cola de envío y calcula los veredictos), el *corredor* (compila y ejecuta el código de usuario), el *transmisor* (envía actualizaciones del marcador/veredicto en vivo a través de WebSockets) y *minijail* (la zona de pruebas que realmente limita un envío en ejecución). Nada de esto está en el repositorio de PHP. El lado PHP solo *llama* al calificador a través de HTTP.
- **[omegaup/gitserver](https://github.com/omegaup/gitserver)** es un servicio Go que almacena cada problema como su propio repositorio git, que es como funciona el control de versiones de problemas, de modo que un concurso se puede vincular a una revisión exacta de la declaración de un problema y los casos de prueba.

Una versión de una sola línea para tener en cuenta: ** PHP monorepo es una aplicación web bastante distribuida que delega el trabajo peligroso (ejecutar código que no es de confianza) al evaluador Go en quark y almacena los problemas como repositorios de git en gitserver. ** Todo lo que aparece a continuación es una consecuencia de esa división.

!!! nota "Una corrección con la que la antigua wiki te hará tropezar"
    La documentación anterior describe la interfaz que se ejecuta en HHVM y la renderización con plantillas de Smarty, y describe una migración de Smarty→Vue en progreso. Los tres están obsoletos. El backend es estándar **PHP 8.1** (php-fpm detrás de nginx), el shell del lado del servidor es **Twig 3** y la migración de Smarty→Vue está *realizada*: la aplicación actualmente tiene **257 componentes de un solo archivo Vue 2.7** y **414 archivos TypeScript** contra exactamente **una** plantilla de aplicación (un shell de diseño Twig). La única migración que aún está activa es Vue 2 → Vue 3. Si lee "HHVM" o "Smarty" en cualquier lugar, trate el reclamo circundante como sospechoso.

## Arquitectura de un vistazo

Estos son los componentes y cómo se conectan. Los nombres en clave internos temporales están escritos en *cursiva*.

| Componente | Qué es | Repositorio / idioma |
| --- | --- | --- |
| *Frontal* | Los controladores y toda la superficie del `/api/`: concursos, problemas, usuarios, rankings, el marcador. Representa el sitio y llama al *Backend* para compilar y ejecutar el código. | [omegaup/omegaup](https://github.com/omegaup/omegaup) — PHP 8.1 + MySQL 8.0 |
| *UX* | La interfaz de cada página: componentes de un solo archivo de Vue 2.7 en TypeScript, incluidos en Webpack 5 y montados en el shell Twig. | [omegaup/omegaup](https://github.com/omegaup/omegaup) — Vue 2.7 + TS 4.4 |
| *Calificador* | Es propietario de la cola de envío, envía carreras a *Runners*, recopila sus resultados y calcula el veredicto. | [omegaup/quark](https://github.com/omegaup/quark) — Ir |
| *Corredor* | Sabe cómo compilar, ejecutar y alimentar entradas a un envío y comprobar si son correctas. Esencialmente una interfaz bonita y distribuida para *Minijail*. | [omegaup/quark](https://github.com/omegaup/quark) — Ir |
| *Locutor* | Envía actualizaciones en vivo (nuevos veredictos, cambios en el marcador) a los navegadores conectados a través de WebSockets. | [omegaup/quark](https://github.com/omegaup/quark) — Ir |
| *Minicárcel* | La zona de pruebas que limita un envío en ejecución: una bifurcación de la zona de pruebas de Linux utilizada en Chrome OS, reforzada para juzgar C/C++/Python/Java/Karel y más que no son de confianza. | [omegaup/quark](https://github.com/omegaup/quark) — C |
| *Gitservidor* | Almacena cada problema como un repositorio de git para que los concursos puedan fijar una revisión exacta del problema. | [omegaup/gitserver](https://github.com/omegaup/gitserver) — Ir |

Si desea conocer los antecedentes autorizados y extensos, se publicaron dos artículos en la revista IOI y siguen siendo la mejor lectura profunda sobre *por qué* el sistema tiene esta forma: [omegaUp: Sistema de gestión de concursos y plataforma de capacitación basado en la nube en la Olimpiada Mexicana de Informática](http://ioinformatics.org/oi/pdf/v8_2014_169_178.pdf) (Chávez, González, Ponce, 2014) y [libinteractive: Una mejor manera de escribir interactivo Tareas](https://ioinformatics.org/journal/v9_2015_3_14.pdf) (Chávez, 2015). Para la versión en el repositorio, lea [Descripción general de la arquitectura](../architecture/index.md) y, cuando esté listo para seguir un envío de principio a fin, [Conceptos internos del sistema](../architecture/internals.md).

## Siga una solicitud real antes de tocar cualquier cosa

La forma más rápida de crear un mapa de este código base es rastrear un único envío, porque esa ruta toca casi todas las capas que editará. Cuando presionas "enviar" en la Arena, el código se PUBLICA en `/api/run/create/`, y aquí es donde va:

1. **`frontend/www/api/ApiEntryPoint.php`** es el punto de entrada literal. Hace `require_once('../../server/bootstrap.php')` y luego `echo \OmegaUp\ApiCaller::httpEntryPoint()`. Cada solicitud de API que realiza el navegador llega aquí primero.
2. **`frontend/server/bootstrap.php`** conecta el mundo (configuración, carga automática, base de datos, registro) y lo pasa a **`\OmegaUp\ApiCaller`** (`frontend/server/src/ApiCaller.php`), que analiza la URL, la resuelve en un controlador y la envía al método `apiXxx` correspondiente.
3. Para un envío, ese método es **`\OmegaUp\Controllers\Run::apiCreate`**, en [`frontend/server/src/Controllers/Run.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Run.php) (actualmente alrededor de la línea 415). Tenga en cuenta que la clase es **`Run`**, no `RunController`: los controladores omegaUp eliminan el sufijo `Controller` (`Contest`, `Problem`, `Grader`, `Submission`,…). En el interior, `apiCreate` ejecuta todas las comprobaciones en orden: que todos los campos requeridos estén presentes (problema, concurso, idioma, fuente), que el problema realmente pertenece al concurso, que el límite de tiempo del concurso no haya expirado, que el usuario no exceda el límite de tasa de envío y que el concurso sea público o que el usuario haya sido invitado explícitamente, *antes* de aceptar la ejecución. Este es el patrón que debe imitar en cualquier lugar donde agregue un punto final: valide primero, en un barrido legible.
4. Una vez aceptada la ejecución, `apiCreate` llama a **`\OmegaUp\Grader::getInstance()->grade($run, trim($source))`** (actualmente alrededor de la línea 573). Ese es el límite de este repositorio. **`\OmegaUp\Grader`** (`frontend/server/src/Grader.php`) es un cliente ligero HTTP/curl: *no* ejecuta ningún código por sí mismo. ENVÍA la ejecución a la niveladora Go en `OMEGAUP_GRADER_URL`, cuyo valor predeterminado es `https://localhost:21680` (configurado en `frontend/server/config.default.php`).
5. A partir de ahí, la cola, los corredores y la minijail viven en **quark**, en Go, y no están en este repositorio en absoluto. Cuando quiera comprender *esa* mitad (las disciplinas de la cola, cómo se envía un corredor, cómo la minicárcel finge la ausencia de una red), lea [Grader Internals](../architecture/grader-internals.md) y [Runner Internals](../architecture/runner-internals.md).

Comprender ese límite (PHP valida y pone en cola, Go califica y sandboxes) le indica inmediatamente a qué repositorio pertenece un error determinado.

## El código y las cuentas que obtienes

En el contenedor de desarrollo en ejecución, todo está en **`/opt/omegaup`**. La instalación incluye dos cuentas preconfiguradas para que no se quede atrapado en un muro de inicio de sesión en el primer inicio: **`omegaup` / `omegaup`** (administrador) y **`user` / `user`** (un usuario normal). Siéntase libre de crear tantos más como necesite para realizar pruebas.

Estos son los directorios en los que estamos trabajando activamente y *por qué* cada uno es importante:- **[`frontend/database`](https://github.com/omegaup/omegaup/tree/main/frontend/database)**: el SQL base que crea el esquema, más todas las migraciones agregadas desde entonces. Si su cambio afecta la forma de los datos, aterriza aquí como un nuevo archivo SQL, no como un archivo base editado a mano.
- **[`frontend/server/src`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src)**: todo PHP, con espacio de nombres en `\OmegaUp\` (PSR-4). Este es el servidor. En su interior:
    - **[`Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers)**: la lógica empresarial y la superficie `/api/`. Cada método `apiXxx` aquí es un punto final público. Si está agregando o cambiando el comportamiento al que un cliente puede llamar, está trabajando aquí.
    - **[`DAO/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/DAO)**: la capa de acceso a datos, dividida deliberadamente. **`DAO/Base/`** contiene las clases base generadas automáticamente con el SQL de creación/actualización/eliminación/obtención sin procesar para cada tabla, y **`DAO/VO/`** contiene los objetos de valor generados automáticamente (uno por forma de fila). *No editas manualmente ninguno de estos*: se generan. Cuando necesita consultas personalizadas, las agrega al contenedor DAO público en `DAO/`, para que el código generado pueda regenerarse sin obstaculizar su trabajo.
    - **[`Template/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Template)**: las extensiones personalizadas de Twig 3 (`EntrypointNode`, `JsIncludeNode`, `VersionHashNode` y `Loader`) que permiten que el shell Twig único inyecte puntos de entrada de Vue y hashes de versión de eliminación de caché.
- **[`frontend/www`](https://github.com/omegaup/omegaup/tree/main/frontend/www)** — la interfaz. Los archivos TypeScript llaman a los controladores y masajean las respuestas; los componentes de un solo archivo de Vue lo representan todo con HTML/CSS. Cada archivo `.vue` se encuentra en `frontend/www/js/omegaup/`, y la mayor parte de ellos (actualmente 248 de 257) en `frontend/www/js/omegaup/components/`. Dos archivos aquí son especiales y **no deben editarse a mano**: `frontend/www/js/omegaup/api.ts` y `api_types.ts`, ambos abiertos con `// generated by frontend/server/cmd/APITool.php. DO NOT EDIT.`. Son el puente escrito entre PHP y TypeScript: `APITool.php` lee los tipos de Psalm de los controladores y emite el TS coincidente, por lo que la interfaz llama a la API de una manera completamente verificada. Cambie la forma de un controlador, vuelva a ejecutar `APITool.php` y los tipos siguen.
- **[`frontend/tests`](https://github.com/omegaup/omegaup/tree/main/frontend/tests)** — las pruebas del controlador PHPUnit. También hay pruebas unitarias de Jest colocadas con componentes y especificaciones de extremo a extremo de Cypress en `cypress/e2e/`.
- **[`frontend/templates`](https://github.com/omegaup/omegaup/tree/main/frontend/templates)**: los archivos de internacionalización (inglés, español, portugués) y `template.tpl`, el único shell Twig que envuelve cada página.

## Elige un camino en

A dónde vayas desde aquí depende de lo que quieras cambiar.

- **Trabajo de interfaz de usuario/UI**: una página, un componente, un formulario. Estás viviendo en `frontend/www/js/omegaup/components/` escribiendo SFC de Vue 2.7 en TypeScript, diseñados con Bootstrap 4.6 + bootstrap-vue 2.21. Lea [Componentes](components.md) y, si desea crear un componente de forma aislada, configure Storybook (`yarn storybook`, en el puerto 6006). Una regla estricta desde el principio: **no utilices jQuery**: esta es una aplicación de Vue, hazlo a la manera de Vue.
- **Trabajo de backend/API**: un nuevo punto final, una verificación de permisos, una consulta. Estás en `frontend/server/src/Controllers/` y la capa DAO. Lea la [Arquitectura de backend](../architecture/backend.md), el [patrón MVC](../architecture/mvc-pattern.md) que seguimos y los [Patrones de base de datos](database-patterns.md) para utilizar la división DAO/VO correctamente en lugar de escribir SQL sin formato en un controlador.
- **El proceso de evaluación**: cómo se compila, se protege o se califica el código. Ese trabajo está en los repositorios de Go **quark** y **gitserver**, no aquí. Comience con [Grader Internals](../architecture/grader-internals.md), [Runner Internals](../architecture/runner-internals.md) y [Sandbox](../features/sandbox.md).
- **Veredictos, concursos, problemas como conceptos de dominio**: lea la sección [Características](../features/index.md) y la [Referencia de veredictos](../features/verdicts.md) para saber qué significan realmente `AC`, `TLE`, `MLE` y sus amigos antes de tocar el código que los emite.

## Antes de escribir una línea: configuración, pruebas y reglas

Tres cosas son innegociables y cada una tiene su propia guía:

1. **[Configura tu entorno](../getting-started/development-setup.md)**: desarrollamos en Docker. Windows y Ubuntu son los caminos más transitados; macOS funciona pero necesita configuración adicional. Su pago se monta en el contenedor en `/opt/omegaup`, MySQL 8.0 escucha en el puerto `13306` y el clasificador en `21680`.
2. **[Lea las pautas de codificación](coding-guidelines.md)**: se trata de criterios de ingeniería razonados, no de estilos arbitrarios. La metarregla de carga: los comentarios deben explicar *por qué*, no *qué*. Uno representativo para darle una idea: cada parámetro `undefined`/`null` duplica las combinaciones con las que se puede llamar a una función y eso crece exponencialmente, así que mantenga el recuento de parámetros anulables **por debajo de 10**. Delegamos la aplicación mecánica a herramientas (Psalm, PHP_CodeSniffer, Prettier, ESLint, yapf/flake8/mypy en el lado de Python); Ejecute `./stuff/lint.sh validate` antes de presionar y le dirá qué solucionar.
3. **[Escribir pruebas](testing.md)**: cada cambio de funcionalidad se envía con pruebas y deben estar 100 % verdes antes de confirmar. PHPUnit para controladores, Jest para componentes, Cypress para flujos de un extremo a otro. Ejecute la suite con `stuff/runtests.sh`.

Cuando el cambio esté listo, siga [Cómo realizar una solicitud de extracción](../getting-started/contributing.md). Una cosa que vale la pena interiorizar desde el principio, porque es el error que los nuevos contribuyentes cometen primero: después de bifurcar, mantenga su `main` sincronizado con el `main` de omegaUp y **nunca se comprometa directamente con él**: `main` refleja el upstream aprobado por revisión, por lo que si `git push upstream` alguna vez falla, significa que se comprometió con `main` por accidente. (La recuperación es `git push upstream -f`, pero la verdadera solución es realizar una bifurcación para cada cambio).

## Decisiones de diseño que vale la pena conocer

Unos pocos principios atraviesan todo el sistema, y conocer el razonamiento le impide "arreglar" algo que es deliberado:

- **Cifrar todo.** *Toda* la comunicación con omegaUp y entre sus subsistemas está cifrada, de cliente a servidor y de componente a componente. Este no es un dogma de seguridad abstracto: en un concurso de programación real, alguien se sentó y olió el tráfico, y entre eso y los ataques al estilo Firesheep, el listón para hacer esto es lo suficientemente bajo como para que no haya excusa para no hacerlo. Se habla con el calificador a través de HTTPS por el mismo motivo.
- **Minimizar contraseñas; identidad federada.** Nos apoyamos en OAuth2/OpenID (Facebook, GitHub) porque cada contraseña que *no* almacenas es una que no puedes filtrar, y un usuario debería poder vincular múltiples identidades: un estudiante que se registró como `user@email.com` debería poder demostrar que también es propietario de `a0001@school.mx` y fusionar las dos cuentas.
- **Mantener los componentes desacoplados.** Se espera que parte de la responsabilidad del *Frontend* migre hacia *Arena* con el tiempo, por lo que las piezas se mantienen lo más independientes posible en lugar de soldarlas estrechamente. Cuando tenga la tentación de cruzar el límite de un componente, recuerde que es posible que no se quede en un solo componente.

## Quizás también quieras

- [Cómo comenzar](../getting-started/index.md): la parte superior del embudo de contribuyentes.
- [Comandos útiles](useful-commands.md): los encantamientos diarios para el contenedor de desarrollo.
- [Guía de migración](migration-guide.md): el trabajo de actualización actual de Vue 2 → Vue 3.
- [Descripción general de la arquitectura](../architecture/index.md) y [Partes internas del sistema](../architecture/internals.md): la historia completa de principio a fin de un envío.
- [Referencia de API](../reference/api.md): la superficie del punto final y el sobre de solicitud/respuesta.
