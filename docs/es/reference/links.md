---
title: Enlaces útiles
description: Los repositorios que componen omegaUp, dónde empezar a contribuir y un puntero a la API
icon: bootstrap/link
---
# Enlaces útiles

omegaUp no es un programa único: son un puñado de servicios que se comunican entre sí a través de
HTTP, distribuido en varios repositorios. Si alguna vez has visto
[`omegaup/omegaup`](https://github.com/omegaup/omegaup) has visto la interfaz PHP y
la API, pero no el evaluador Go que realmente compila y ejecuta los envíos, ni el git
Servidor que almacena problemas como repositorios controlados por versión. Esta página es el mapa: cual repositorio
contiene qué, por dónde empezar si desea contribuir y dónde está la API siempre actualizada
vidas de referencia. Cuando un enlace apunta a un código, apunta al repositorio que *posee* ese código,
no el monorepo, por lo que aterrizas donde realmente se debe realizar el cambio.

## Los repositorios

Hay tres que importan para casi todo, además de algunos satélites. La razón por la que
existe división es que las piezas están escritas en diferentes idiomas y evolucionan
diferentes relojes: la interfaz es PHP + Vue y se envía en cada fusión a `main`, mientras que el
Grader es Go y se envía como un binario versionado al que la interfaz llama a través de la red. mantener
ese límite en mente: es por eso que "arreglar la cola" y "arreglar el formulario de envío" viven en
diferentes repositorios.

### omegaup/omegaup: la interfaz y la API

[`github.com/omegaup/omegaup`](https://github.com/omegaup/omegaup) es el grande y el
uno en el que pasarás la mayor parte de tu tiempo. Es el backend de PHP 8.1 (php-fpm detrás de nginx, el
código `\OmegaUp\...` con espacio de nombres en
[`frontend/server/src`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src)),
los componentes de archivo único de Vue 2.7 + TypeScript en
[`frontend/www/js/omegaup/components`](https://github.com/omegaup/omegaup/tree/main/frontend/www/js/omegaup/components),
y toda la API REST pública. Cada controlador vive en
[`frontend/server/src/Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers),
y cada método `apiXxx` en un controlador es exactamente un punto final, por lo que
[`Run.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Run.php)'s
`apiCreate` *es* `/api/run/create/`. Lo que este repositorio **no** contiene es el calificador, el
runner o sandbox: cuando es necesario juzgar un envío, la clase PHP
[`\OmegaUp\Grader`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Grader.php)
simplemente hace una llamada curl a `OMEGAUP_GRADER_URL` (predeterminado `https://localhost:21680`) y deja
el servicio Go hace el verdadero trabajo.

### omegaup/quark — calificador, corredor, locutor

[`github.com/omegaup/quark`](https://github.com/omegaup/quark) es el backend propiamente dicho, escrito
en Go, y su propio archivo README lo describe en tres partes:

- **calificador**: gestiona la cola de ejecución/envío. En particular, *no ejecuta nada por sí mismo*;
  simplemente mantiene la cola y las manos trabajan. Cuando PUBLICAS un envío, esto es lo que
  `\OmegaUp\Grader` está hablando.
- **corredor**: solicita al evaluador nuevos envíos, luego compila y ejecuta el código dentro del
  [omegajail sandbox](https://github.com/omegaup/omegajail) con cada entrada, compara el
  salida a la respuesta esperada (ejecutando un validador si el problema lo necesita) y asigna un
  puntuación por caso. Básicamente es una interfaz bonita y distribuida para el sandbox.
- **locutor**: envía notificaciones en vivo a todos los participantes de un concurso o curso: las carreras se obtienen
  calificados, cambios en los marcadores, nuevas aclaraciones, etc.

Si está buscando un error sobre *por qué un veredicto fue incorrecto* o *por qué la cola se detuvo*,
este es el repositorio, no el de PHP. La zona de pruebas en sí es un repositorio más caído:
[`omegaup/omegajail`](https://github.com/omegaup/omegajail): porque se aislan los que no son de confianza
El código concursante es un problema lo suficientemente difícil como para merecer su propio proyecto.

### omegaup/gitserver — problemas como repositorios de git

[`github.com/omegaup/gitserver`](https://github.com/omegaup/gitserver) es el servicio Go que
almacena cada problema como su propio repositorio git: declaraciones, casos de prueba, validadores, configuraciones,
todo versionado. Es por eso que editar un problema produce un historial de confirmaciones real que puedes revertir:
la "base de datos" para el *contenido* del problema es git, no MySQL. La interfaz habla con él cada vez que un
Se crea o edita el problema y el corredor lee los casos de prueba al calificarlo.

### Los satélites

Estos aparecen con menos frecuencia, pero vale la pena saber que existen:

| Repositorio | Para qué sirve |
|------------|---------------|
| [omegaup/libinteractive](https://github.com/omegaup/libinteractive) | Genera el texto estándar que permite que un problema sea *interactivo* (el código del concursante y un proceso de juez intercambian mensajes). Escrito en el artículo de la revista IOI de 2015 a continuación. |
| [omegaup/omegajail](https://github.com/omegaup/omegajail) | La caja de arena a la que se dirige el corredor. Aísla los envíos que no son de confianza en el nivel de llamada al sistema. |
| [omegaup/implementar](https://github.com/omegaup/deploy) | Scripts de implementación y configuración de producción. |
| [omegaup/kit de herramientas para solucionar problemas](https://github.com/omegaup/omegaup/wiki) | Herramientas para solucionar problemas de creación (consulte la wiki para conocer el punto de entrada actual). |

## Dónde empezar a contribuir

El flujo de trabajo se encuentra en el repositorio principal y la única fuente de verdad es
[`CONTRIBUTING.md`](https://github.com/omegaup/omegaup/blob/main/CONTRIBUTING.md) — léelo
antes de su primer RP, porque las reglas de asignación se aplican mediante la automatización, no por la buena voluntad.
Algunas cosas que vale la pena saber desde el principio para no sorprenderse:

- **Reclamar un problema con `/assign`.** Puedes mantener hasta **2 asignaciones activas** a la vez,
  y `/assign` solo funciona cuando alguien con asociación de repositorio abrió el problema
  `OWNER`, `MEMBER` o `COLLABORATOR`: ese filtro existe, por lo que el robot de asignación no entrega
  problemas que presentaron usuarios aleatorios. Si es la primera vez que contribuye, no puede autoasignarse
  hasta que tenga al menos un PR fusionado aquí; Hasta entonces, comente y un mantenedor ayudará.
- **Configure el entorno antes que nada.** El tutorial completo de Docker: brindando el
  contenedores, ejecutar las pruebas, sembrar usuarios de prueba y solucionar problemas para cuando
  el contenedor no arranca: vive en
  [`frontend/www/docs/Development-Environment-Setup-Process.md`](https://github.com/omegaup/omegaup/blob/main/frontend/www/docs/Development-Environment-Setup-Process.md),
  o en la guía [Configuración de desarrollo](../getting-started/development-setup.md) de este sitio.
- **Siga las pautas de codificación.** No son pedantería de estilo en sí misma; la meta-regla
  todo el código base que se ejecuta es *explica por qué, no qué*. Ver
  [Pautas de codificación](../development/coding-guidelines.md) aquí, o las canónicas
  [versión wiki](https://github.com/omegaup/omegaup/wiki/Coding-guidelines-(English-version)).

Para el día a día, estas son las páginas a las que los mantenedores realmente dirigen a los nuevos contribuyentes:

| Guía | Qué cubre |
|-------|----------------|
| [Contribuyendo](../getting-started/contributing.md) | El bucle fork → branch → PR y por qué nunca te comprometes con `main`. |
| [Obteniendo ayuda](../getting-started/getting-help.md) | Dónde preguntar cuando estás atascado (y la [wiki "Cómo obtener ayuda"](https://github.com/omegaup/omegaup/wiki/How-to-Get-Help)). |
| [Comandos útiles](../development/useful-commands.md) | Las invocaciones exactas de `docker-compose`, lint y prueba que ejecutará todos los días. |
| [Prueba](../development/testing.md) | PHPUnit, Jest y Cypress: cómo ejecutarlos y cómo escribir uno. |
| [Guía de migración](../development/migration-guide.md) | La migración en vivo de Vue 2.7 → Vue 3 (la antigua Smarty → Vue está terminada). |
| [Inicio de Wiki](https://github.com/omegaup/omegaup/wiki) | La wiki original de notas de trabajo, sigue siendo la fuente más profunda para casos extremos de configuración. |

Y las superficies de GitHub en las que vivirás:

| Recurso | Enlace |
|----------|------|
| Rastreador de problemas | [omegaup/omegaup/problemas](https://github.com/omegaup/omegaup/issues) |
| Buenos primeros números | [Etiqueta `Good first issue`](https://github.com/omegaup/omegaup/labels/Good%20first%20issue) |
| Abrir solicitudes de extracción | [omegaup/omegaup/tira](https://github.com/omegaup/omegaup/pulls) |
| Código de conducta | [`CODE_OF_CONDUCT.md`](https://github.com/omegaup/omegaup/blob/main/CODE_OF_CONDUCT.md) |
| Discord (canal principal) | [discord.gg/gMEMX7Mrwe](https://discord.gg/gMEMX7Mrwe) |

## Un puntero a la API

Todo lo que hace la interfaz web, lo hace llamando a la misma API REST pública a la que puedes llamar
usted mismo: cada actualización del marcador, cada envío, cada inicio de sesión es solo una solicitud HTTP para
`/api/...`. Las reglas son las mismas para todos ellos: HTTP simple GET o POST, JSON back, **HTTPS
solo** (una llamada HTTP simple obtiene una redirección `301`, no un éxito silencioso, porque el rastreo
el tráfico del concurso es un verdadero vector de trampa), cada URL bajo `https://omegaup.com/api/`, y
autenticación a través de un token que obtiene de `user/login` y lo envía de vuelta en una cookie llamada `ouat`.
Una consecuencia que vale la pena recordar: solo puedes tener **una sesión activa a la vez**, por lo que
Iniciar sesión mediante programación cancelará la sesión de su navegador y viceversa.

!!! consejo "Lea esto primero"

    Las reglas transversales completas: transporte, token de autenticación `ouat` y
    Sobre de respuesta `status`/`errorcode`/`errorname`/`error`: están escritos en el
    Página **[Referencia API](api.md)**, con un ejemplo trabajado de `curl`.

Lo único que deliberadamente **no** guardamos aquí es una lista mantenida manualmente de puntos finales,
porque se pudriría en el momento en que alguien editara un controlador. El autoritario y siempre actual
la superficie es *generada desde la fuente* por
[`frontend/server/cmd/APITool.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/cmd/APITool.php)
- la misma herramienta que emite el cliente frontend escrito
[`api.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/api.ts) y
[`api_types.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/api_types.ts).
Para ver exactamente qué acepta y devuelve una llamada, lea el método `apiXxx` en su controlador en
[`frontend/server/src/Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers)
en lugar de confiar en cualquier mesa.

## Sitios oficiales

| Recurso | URL | Qué es |
|----------|-----|------------|
| Plataforma | [omegaup.com](https://omegaup.com) | El juez en vivo y el sistema de concurso. |
| Organización | [omegaup.org](https://omegaup.org) | La organización sin fines de lucro, nuestra misión e impacto. |
| Blog | [blog.omegaup.com](https://blog.omegaup.com) | Anuncios, tutoriales, notas de la versión. |
| Estado | [estado.omegaup.com](https://status.omegaup.com) | Estado del sistema en vivo e historial de incidentes. |

## Antecedentes académicosDos artículos de la revista IOI son los antecedentes autorizados de por qué el sistema está construido de la forma en que
Vale la pena leerlo si desea conocer la intención del diseño detrás de la arquitectura, no solo la actual.
código:

- [omegaUp: Sistema de gestión de concursos basado en la nube](http://www.ioinformatics.org/oi/pdf/v8_2014_169_178.pdf) (IOI Journal, 2014): el artículo de arquitectura original.
- [libinteractive: una mejor manera de escribir tareas interactivas](https://ioinformatics.org/journal/v9_2015_3_14.pdf) (IOI Journal, 2015): el diseño detrás de [`omegaup/libinteractive`](https://github.com/omegaup/libinteractive).

El lugar más amplio es el [IOI Journal en ioinformatics.org](https://ioinformatics.org/), y
omegaUp surgió de la [Olimpiada Mexicana de Informática (OMI)](https://www.olimpiadadeinformatica.org.mx/).

## Ver también

- **[Referencia de API](api.md)**: las reglas transversales para llamar a cualquier punto final.
- **[Partes internas del sistema](../architecture/internals.md)**: cómo una llamada `run/create` realmente fluye desde `\OmegaUp\ApiCaller` a través de un controlador y sale a la niveladora Go.
- **[Grader Internals](../architecture/grader-internals.md)** y **[Runner Internals](../architecture/runner-internals.md)**: qué sucede dentro del quark una vez que la interfaz entrega un envío.

---

!!! consejo "¿Falta un enlace?"
    Si conoce un recurso que pertenece aquí, [abra un PR](https://github.com/omegaup/omegaup/pulls) con los documentos.
