---
title: Bienvenido
description: Documentación completa para la plataforma de programación educativa omegaUp
icon: bootstrap/home
---
![Logotipo de omegaUp](assets/images/omegaup.png){ width="300" style="max-width: 100%; height: auto; object-fit: contain;" }

# Bienvenido a la documentación de omegaUp

omegaUp es una plataforma educativa gratuita y de código abierto creada en torno a un juez automático en línea: usted escribe una solución, la envía y en cuestión de segundos recibe un veredicto (`AC`, `WA`, `TLE` y el resto) porque un evaluador de espacio aislado realmente ha compilado y ejecutado su código en cada caso de prueba. Decenas de miles de estudiantes y profesores en toda América Latina lo utilizan todos los días para practicar, enseñar y competir, desde el entrenamiento para las olimpíadas nacionales hasta los niños que dan sus primeros pasos en **Karel**, el lenguaje de robot en una red que omegaUp admite específicamente para que un niño de diez años pueda aprender a programar antes de saber qué es un bucle `for` (junto con los lenguajes que esperarías: C, C++, Java, Python, C#, Go, Haskell, Lua, Pascal y Ruby).

Estos documentos son para las personas que **construyen y ejecutan** esa plataforma: el colaborador que configura su entorno por primera vez, el desarrollador que rastrea cómo fluye realmente un envío a través del código y el operador que mantiene vivo el sitio en producción. Si solo desea *usar* omegaup.com para resolver problemas o realizar un concurso para su escuela, estará más feliz en el sitio mismo y en el [blog](https://blog.omegaup.com/), donde las funciones más nuevas se anuncian primero. Todo lo que aparece a continuación supone que deseas mirar debajo del capó.

!!! resumen "El modelo mental de un párrafo"

    omegaUp **no** es un programa único. Este repositorio, [`omegaup/omegaup`](https://github.com/omegaup/omegaup), es la **frontend de PHP 8.1 y monorepo API** (php-fpm detrás de nginx). Sirve un shell HTML delgado Twig 3 que inicia una aplicación de una sola página Vue 2.7 + TypeScript y expone cada característica como un punto final REST en `/api/`. **No** compila ni ejecuta su código. Cuando lo envía, el backend de PHP entrega la ejecución a través de HTTP a un **servicio Go Grader** completamente independiente (el proyecto [`omegaup/quark`](https://github.com/omegaup/quark): evaluador, corredor, emisora ​​y entorno de pruebas minijail), y los datos del problema residen en repositorios git administrados por un tercer servicio, [`omegaup/gitserver`](https://github.com/omegaup/gitserver). Saber en cuál de estos tres repositorios vive una cosa le ahorra horas; la mayor parte de esta documentación está organizada en torno a esa división.

## Inicio rápido

¿Nuevo en omegaUp? Comience aquí:

<div class="grid cards" markdown>

- :material-rocket-launch:{ .lg .middle } __[Comenzando](getting-started/index.md)__

    ---

    Cree un omegaUp local completo con `docker-compose`, cree sus usuarios de prueba y realice su primera solicitud de extracción. El entorno está en contenedores precisamente para que no tenga que instalar manualmente PHP, MySQL, Redis y Go Grader usted mismo: el primer `docker-compose up` puede tardar unos minutos mientras se extraen las imágenes y se inicia la base de datos.

    [:octicons-arrow-right-24: Comenzar](getting-started/index.md)

- :material-code-tags:{ .lg .middle } __[Arquitectura](architecture/index.md)__

    ---

    Siga un envío real de principio a fin: desde `OmegaUp.submit` en el navegador, pasando por `ApiEntryPoint.php` → `bootstrap.php` → `\OmegaUp\ApiCaller`, hasta `\OmegaUp\Controllers\Run::apiCreate` y a través de HTTP hasta el evaluador Go. Este es el mapa de cómo encajan los tres servicios.

    [:octicons-arrow-right-24: Más información](architecture/index.md)

- :material-api:{ .lg .middle } __[Referencia API](reference/api.md)__

    ---

    Cada página que representa la interfaz es solo una llamada autenticada a `/api/...`, por lo que la API puede hacer cualquier cosa que la interfaz de usuario pueda hacer. Conozca las reglas transversales (autenticación PASETO `auth_token`, transporte JSON y el sobre de respuesta `status`/`error`/`errorcode`) y luego siga la lista de puntos finales siempre actualizada y generada por el origen.

    [API de exploración :octicons-arrow-right-24:](reference/api.md)

- :material-tools:{ .lg .middle } __[Guías de desarrollo](development/index.md)__

    ---

    Las reglas internas que mantienen coherentes 257 componentes de Vue y una gran base de código PHP: pautas de codificación (sí, "¡No uses jQuery!"), cómo ejecutar Psalm, PHPUnit, Jest y Cypress localmente, y cómo los clientes `api.ts` / `api_types.ts` generados mantienen los tipos de frontend y backend al mismo tiempo.

    [Guías de lectura :octicons-arrow-right-24:](development/index.md)

</div>

## ¿Qué es omegaUp?

omegaUp existe para hacer que la práctica de programación deliberada sea gratuita y automática. Todo en la plataforma se basa en el juez en línea: la maquinaria que decide, objetivamente y en segundos, si una solución es correcta y lo suficientemente rápida:

- **Resolución de problemas**: una gran biblioteca de problemas de programación, cada uno con casos de prueba ocultos, un `time_limit` (comúnmente `1000` ms) y un `memory_limit` (comúnmente `32768` KiB), calificados automáticamente para que nadie tenga que revisar manualmente los envíos.
- **Concursos**: organiza un concurso de programación cronometrado para tu escuela, universidad o club, con un marcador en vivo. Todo el tráfico del concurso está cifrado por una razón concreta: en un concurso de programación anterior, alguien husmeó la red para hacer trampa, por lo que *cada* comunicación con omegaUp se realiza a través de TLS.
- **Cursos**: rutas de aprendizaje estructuradas que agrupan problemas en tareas, para que un profesor pueda desarrollar un semestre de práctica calificada.
- **Entrenamiento**: practica problemas organizados por tema y dificultad para que cualquiera pueda subir de nivel por su cuenta.

## Secciones de documentación

### :material-school:{ .lg } [Introducción](getting-started/index.md)
Todo lo que necesita para pasar de un clon nuevo a un sitio local en ejecución y una solicitud de extracción fusionada: la configuración de `docker-compose`, cuentas de prueba inicializadas (el administrador `omegaup`/`omegaup` y un `user`/`user` normal, además de los accesorios `test_user_0..9`), el flujo de trabajo de bifurcación y PR, y dónde obtener ayuda cuando el contenedor no arranca.

### :material-sitemap:{ .lg } [Arquitectura](architecture/index.md)
Una inmersión profunda en cómo los tres servicios (el frontend/API de PHP, el evaluador Go (quark) y el servidor git) realmente mueven una solicitud a través de código real: la capa de controlador bajo `frontend/server/src/Controllers/`, la capa de acceso a datos DAO/VO generada automáticamente sobre MySQL 8.0 y la transferencia HTTP al clasificador en `OMEGAUP_GRADER_URL` (`https://localhost:21680` predeterminado).

### :material-api:{ .lg } [Referencia API](reference/api.md)
Las reglas de transporte, autenticación y sobre de respuesta que se aplican a cada punto final, además de la referencia del punto final generada en el origen. Debido a que `frontend/server/cmd/APITool.php` genera la lista a partir de los controladores PHP, no puede perder la sincronización con lo que el servidor realmente acepta.

### :material-code-braces:{ .lg } [Desarrollo](development/index.md)
Estándares de codificación, la cadena de herramientas de análisis estático y linting (Psalm para PHP, `prettier`/ESLint para TypeScript), pruebas en PHPUnit, Jest 26 y Cypress 15.7, bases de datos y patrones de migración, y cómo crear componentes de un solo archivo de Vue sin luchar contra las convenciones existentes.

### :material-feature-search:{ .lg } [Características](features/index.md)
Funciones internas de función por función: cómo [Arena](features/arena.md) ofrece concursos, cómo [evaluador y corredor](features/sandbox.md) compila y ejecuta una presentación dentro de la minijail, qué significa cada [veredicto](features/verdicts.md), cómo [versión de problemas](features/problem-versioning.md) usa git y cómo [insignias](features/badges.md) y [Actualizaciones en tiempo real](features/realtime.md) funcionan.

### :material-server:{ .lg } [Operaciones](operations/index.md)
Ejecución de omegaUp en producción: configuración de nginx y php-fpm, la infraestructura Redis y RabbitMQ 3 de la que depende la aplicación, observabilidad a través de Prometheus y Monolog, y guías de solución de problemas para cuando algo se rompe.

### :material-account-group:{ .lg } [Comunidad](community/index.md)
Cómo convertirse en colaborador habitual, incluida la participación de larga data de omegaUp en [Google Summer of Code](community/gsoc/index.md).

## Hechos clave

!!! consejo "Educativo por diseño"
    omegaUp está diseñado para aulas y competiciones, no solo para la práctica en solitario: existen cursos, tareas y marcadores de concursos para que un profesor pueda ejecutar un programa completo en ellos. Por eso es compatible con Karel: la plataforma se encuentra con los estudiantes donde estén, incluidos los que aún no han escrito código real.

!!! éxito "Código abierto, tres repositorios"
    Se aceptan contribuciones de los tres: la interfaz/API de PHP en [`omegaup/omegaup`](https://github.com/omegaup/omegaup), la pila de calificación Go en [`omegaup/quark`](https://github.com/omegaup/quark) y el almacenamiento de problemas en [`omegaup/gitserver`](https://github.com/omegaup/gitserver). Verifique en qué repositorio reside un subsistema antes de buscar su código: el calificador y el sandbox **no** están en el monorepo de PHP.

!!! info "Calificación multilingüe"
    Los envíos se pueden escribir en C, C++, Java, Python, C#, Go, Haskell, Lua, Pascal, Ruby y Karel. El evaluador compila cada uno en un entorno aislado y lo ejecuta en cada caso de prueba, luego lo califica.

!!! advertencia "Todo está cifrado"
    Toda la comunicación con omegaUp y sus subsistemas se realiza a través de TLS. Esto no es un teatro de seguridad: cifrar todo minimiza la posibilidad de hacer trampa en concursos (el tráfico *ha* sido olfateado en una competencia real), y con herramientas como Firesheep, hacerlo bien es barato y no negociable.

## Involúcrate

- **Código de contribución**: comience con la [Guía de contribución](getting-started/contributing.md); el equipo de mantenimiento revisa cada RP según las [Pautas de codificación](development/index.md).
- **Informar problemas**: abra uno en [github.com/omegaup/omegaup/issues](https://github.com/omegaup/omegaup/issues).
- **Google Summer of Code**: omegaUp asesora a los estudiantes cada año; consulte el [programa GSoC](community/gsoc/index.md).

## Recursos- **Sitio web**: [omegaup.com](https://omegaup.com)
- **Blog**: [blog.omegaup.com](https://blog.omegaup.com)
- **Organización**: [omegaup.org](https://omegaup.org)
- **GitHub**: [github.com/omegaup/omegaup](https://github.com/omegaup/omegaup)

---

**¿Listo para comenzar?** Dirígete a [Cómo comenzar](getting-started/index.md) para abrir un omegaUp local con `docker-compose` y realizar tu primer cambio.
