---
title: Guía de prueba
description: Guía de pruebas completa para omegaUp
icon: bootstrap/flask
---
# Guía de prueba

omegaUp se prueba en tres capas, y cada una vive en un lugar diferente durante un
razón. Los controladores PHP y la API están cubiertos por pruebas de **PHPUnit 9** que se ejecutan
_dentro_ del contenedor Docker `frontend` (necesitan un MySQL 8.0 real, un verdadero
gitserver y toda la cadena de carga automática `\OmegaUp\`). Los componentes de Vue 2.7 y
el TypeScript bajo `frontend/www/js` está cubierto por las pruebas unitarias **Jest 26**,
que también se ejecuta dentro del contenedor pero solo necesita jsdom. y el completo
Viajes de usuario con clics: registrarse, iniciar sesión, crear un concurso, enviar una carrera.
están cubiertos por pruebas de extremo a extremo de **Cypress 15.7** que se ejecutan _en su host_,
conduciendo un Chrome real contra el contenedor sobre `http://127.0.0.1:8001`.

La regla que obligamos a todos a cumplir: las pruebas deben estar en verde antes de abrir un sorteo
solicitud, y cualquier comportamiento nuevo viene con una prueba que lo ejercita. CI se ejecutará
las tres suites nuevamente en su PR, por lo que una suite que solo pasa en su máquina
no esta pasando.

| Capa | Marco | Donde vive | Por donde corre |
|-------|-----------|----------------|---------------|
| Controladores PHP + API | PHPUnidad 9 | `frontend/tests/controllers/`, `frontend/tests/badges/` | Dentro del contenedor `frontend` |
| Unidades TypeScript/Vue | Broma 26 (jsdom) | `frontend/www/js/**/*.test.ts` | Dentro del contenedor `frontend` |
| Viajes de punta a punta | Ciprés 15.7 | `cypress/e2e/*.cy.ts` | En tu host, contra `127.0.0.1:8001` |

## Pruebas unitarias de PHP (PHPUnit)

### El único comando: `./stuff/runtests.sh`

El script que realmente ejecutamos antes de enviar es
[`stuff/runtests.sh`](https://github.com/omegaup/omegaup/blob/main/stuff/runtests.sh),
y es deliberadamente más que "solo PHPUnit". Primero decide si es
dentro de Docker verificando si la raíz del repositorio es `/opt/omegaup` (ahí es donde
el contenedor monta la fuente); Si es así, se ejecuta directamente; de lo contrario, se descascara.
en el contenedor con `docker compose exec -T frontend`. A partir de ahí, en
orden:

1. Valida las migraciones de esquemas con `stuff/db-migrate.py validate` y el
   políticas de autorización con `stuff/policy-tool.py validate`, porque una prueba
   ejecutar contra un esquema o política obsoleta no le dice nada útil.
2. Ejecuta [`stuff/mysql_types.sh`](https://github.com/omegaup/omegaup/blob/main/stuff/mysql_types.sh),
   cuál es la parte interesante (ver más abajo).
3. Ejecuta Psalm en todo el árbol con `vendor/bin/psalm --show-info=false`
   (Suprimimos el ruido a nivel de información para que solo los errores de tipo real fallen en la ejecución).
4. Verifica que los hashes de acción de GitHub fijados sean consistentes mediante
   `hack/gha-reversemap.sh verify-mapusage`, pero sólo si `yq` y `jq` están
   instalado; de lo contrario, imprime un aviso de omisión en lugar de fallar.

Cuando lo ejecuta dentro del contenedor, termina recordándole que ejecute
`./stuff/lint.sh` y las pruebas de UI de Python (`python3 -m pytest ./frontend/tests/ui/ -s`)
_fuera_ del contenedor, porque necesitan herramientas que el contenedor no lleva.

### Por qué existe `mysql_types.sh` (la parte inteligente)

`mysql_types.sh` no sólo ejecuta la suite PHPUnit, sino que también la ejecuta con MySQL
**registro de consultas generales** activado (`SET GLOBAL general_log = 'ON'` escribiendo en un
`TABLE`), captura todas las consultas que las pruebas realmente emitieron y luego las envía a
`stuff/process_mysql_return_types.py`. El punto es verificar que el
Las anotaciones de `@psalm-type` que escribimos a mano en la capa DAO coinciden con lo que MySQL
_realmente_ devuelve para esas columnas. Si agrega una consulta cuyo resultado tiene forma
no coincide con su tipo de Salmo declarado, este es el paso que lo atrapa - largo
antes de que se convierta en una sorpresa en tiempo de ejecución en un controlador. tambien corre
`process_mysql_explain_logs.py` para comprobar la integridad de los planes de consulta. Entonces "el tipo
comprobar" la mención de los documentos anteriores no es una suposición estática; está fundamentado en el
consultas que sus pruebas realmente se ejecutaron.

### Ejecutando la suite (o una prueba)

Debajo del capó, [`stuff/run-php-tests.sh`](https://github.com/omegaup/omegaup/blob/main/stuff/run-php-tests.sh)
es lo que realmente invoca PHPUnit. Sin argumentos ejecuta todo bajo
`frontend/tests/`; con argumentos los pasa directamente a `phpunit`,
para que obtengas el filtrado de PHPUnit de forma gratuita. Para iterar en una prueba de controlador único:

```bash
# From inside the container (or via docker compose exec -T frontend ...)
./stuff/run-php-tests.sh frontend/tests/controllers/UserRankTest.php \
    --filter testUserRankingClassName
```
Siempre conecta las mismas tres cosas: `--bootstrap frontend/tests/bootstrap.php`,
`--configuration frontend/tests/phpunit.xml` y
`--coverage-clover coverage.xml` (ese archivo Clover es lo que Codecov lee más tarde).

Las propias suites están declaradas en
[`frontend/tests/phpunit.xml`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/phpunit.xml):
un conjunto de **Controladores** sobre `frontend/tests/controllers/` (actualmente ~129 pruebas
archivos (esta es la mayor parte de la cobertura) y un conjunto de **Badges** sobre
`frontend/tests/badges/`. La cobertura se mide sobre `../server/` pero deliberadamente
excluye el código generado (`server/libs/dao/base/`), la configuración, el `cmd/`
scripts y las fuentes del complemento Psalm, porque medir archivos generados automáticamente
sólo diluiría el número.

!!! nota "Las pruebas necesitan un gitserver y el oyente lo proporciona"
    `phpunit.xml` registra `\OmegaUp\Test\GitServerTestSuiteListener`
    ([`GitServerTestSuiteListener.php`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/GitServerTestSuiteListener.php)).
    Las pruebas de creación y envío de problemas necesitan un backend git real para el problema
    almacenamiento, por lo que el oyente prepara uno para la ejecución de prueba. Por eso tu
    No se pueden ejecutar estas pruebas de manera significativa fuera del contenedor: las partes móviles
    que tocan (MySQL 8.0, gitserver) son servicios de contenedor, no simulacros.

Ayudantes en los que se apoyará al escribir nuevas pruebas se encuentran junto a las suites:
`frontend/tests/Utils.php`, el directorio `frontend/tests/Factories/` para
usuarios/concursos/problemas de construcción, y `ControllerTestCase.php` /
`BadgesTestCase.php` como clases base. También hay un `ApiCallerMock.php` para
impulsando la capa API sin pasar por HTTP.

## Pruebas unitarias de TypeScript / Vue (Jest)

La suite Jest cubre los ~180 archivos `*.test.ts` en `frontend/www/js`,
desde la lógica pura (`omegaup.test.ts`, `markdown.test.ts`, `csv.test.ts`)
a componentes de archivo único de Vue montados con `@vue/test-utils`. Los scripts npm en
[`package.json`](https://github.com/omegaup/omegaup/blob/main/package.json) todos
forzar `TZ=UTC` a través de `cross-env`, porque de lo contrario las afirmaciones de formato de fecha
pasar una máquina en una zona horaria y fallar en CI: fijar UTC mantiene a todos
resultados idénticos:

```bash
yarn test            # cross-env TZ=UTC jest 'frontend/www/js/.*test\.ts$'
yarn test:watch      # same, but --watchAll --notify — reruns on save
yarn test:coverage   # same, with --coverage=true
```
Para ejecutar un solo archivo mientras itera, omita el contenedor y presione el binario
directamente:

```bash
./node_modules/.bin/jest frontend/www/js/omegaup/components/RadioSwitch.test.ts
```
Las pruebas de componentes se leen así: monte el SFC con accesorios, luego haga valer
texto renderizado o eventos emitidos. Tenga en cuenta la convención de importación de traducciones.
(`T`) en lugar de codificar cadenas de UI, por lo que una prueba sobrevive a un cambio de copia:

```typescript
import { shallowMount } from '@vue/test-utils';
import T from '../lang';
import omegaup_RadioSwitch from './RadioSwitch.vue';

describe('RadioSwitch.vue', () => {
  it('Should render a simple radio switch with default descriptions', () => {
    const wrapper = shallowMount(omegaup_RadioSwitch, {
      propsData: { selectedValue: true },
    });
    expect(wrapper.text()).toContain(T.wordsYes);
    expect(wrapper.text()).toContain(T.wordsNo);
  });
});
```
Prefiera `shallowMount` sobre `mount` a menos que necesite específicamente componentes secundarios
renderizar: bloquea a los niños, lo que mantiene la prueba rápida y detiene una
error de un niño no relacionado al fallar la prueba. La configuración de broma
([`jest.config.js`](https://github.com/omegaup/omegaup/blob/main/jest.config.js))
hace las tuberías con las que de otro modo tropezarías: `testEnvironment: 'jsdom'`, un
`testURL` de `http://localhost:8001/` entonces código que dice `window.location`
se comporta, `vue-jest` para archivos `.vue` y entradas `moduleNameMapper` que se burlan
elimine las dependencias pesadas o exclusivas del navegador: `monaco-editor`, importaciones CSS/LESS,
y `sugar` se resuelven en códigos auxiliares en
`frontend/www/js/omegaup/__mocks__/` y `@/` se asignan a `frontend/www/`. Compartido
La configuración se ejecuta desde `frontend/www/js/omegaup/test.setup.ts` a través de
`setupFilesAfterEnv`.

## Pruebas de extremo a extremo de Cypress

Las 10 especificaciones siguientes
[`cypress/e2e/`](https://github.com/omegaup/omegaup/tree/main/cypress/e2e) —
`basic_commands`, `certificate`, `contest`, `course`, `course_2Part`, `group`,
`ide`, `navigation`, `problem_collection` y `problem_creator`, todos nombrados
`*.cy.ts`: controle un navegador real a través de todo el producto. A diferencia de PHPUnit y
Broma, **Cypress se ejecuta en su host, no dentro del contenedor Docker.** El
El contenedor sirve la aplicación en `http://127.0.0.1:8001` y Cypress.
(`baseUrl` en [`cypress.config.ts`](https://github.com/omegaup/omegaup/blob/main/cypress.config.ts))
apunta Chrome a esa dirección. Entonces necesitas Node, tus dependencias de Yarn
instalado y, en Linux, varias bibliotecas del sistema que Electron/Chrome
enlaces de corredor en contra.

### Instalar Cypress

Después de un `yarn install`, si falta el binario del navegador, verá
algo como:

```text
No version of Cypress is installed in: ~/.cache/Cypress/15.7.0/Cypress

Please reinstall Cypress by running: cypress install
```
Eso no es un problema de dependencia: el paquete npm está ahí, pero el contenido real
El binario Cypress que se encuentra bajo `~/.cache/Cypress/<version>/` no se descargó.
Arreglarlo con:

```bash
./node_modules/.bin/cypress install
```
La versión fijada es `cypress` en `package.json` (actualmente **15.7.0**); el
La ruta en cualquier mensaje de error le indica qué versión del binario Cypress está buscando.
for, que es la forma más rápida de detectar una discrepancia entre la versión y el caché después de una actualización.

### Bibliotecas del sistema Linux

Cypress falla rápidamente (antes de ejecutar una sola prueba) si es una biblioteca compartida.
necesita y el error nombra exactamente `.so`. Dos aparecen constantemente.
Si ves:

```text
~/.cache/Cypress/15.7.0/Cypress/Cypress: error while loading shared libraries:
libnss3.so: cannot open shared object file: No such file or directory
```
esa es la biblioteca criptográfica NSS. Y:

```text
error while loading shared libraries: libasound.so.2: cannot open shared object
file: No such file or directory
```
es ALSA (audio). Instale todo el conjunto de documentos Cypress como
[dependencias requeridas](https://on.cypress.io/required-dependencies):

```bash
sudo apt update
sudo apt install -y libgtk-3-0 libgbm-dev libnss3 libatk1.0-0 \
    libatk-bridge2.0-0 libgdk-pixbuf2.0-0 libxss-dev libasound2
```
En **Ubuntu 24.04+**, se cambió el nombre de ALSA para la transición time_t de 64 bits, por lo que
No se encontrará `libasound2`; en su lugar, instale `libasound2t64`. si una biblioteca
el error persiste después de la instalación, ejecute `sudo apt update` y vuelva a intentarlo; un rancio
El índice del paquete es el culpable habitual.

### Ejecutando las pruebas

La GUI es una forma agradable de desarrollar una especificación: muestra cada comando a medida que se ejecuta.
se ejecuta y le permite desplazarse sobre cualquier paso para ver una instantánea DOM de la página en ese punto exacto
momento, además de una herramienta de selección que escribe el `cy.get(...)` para cualquier elemento
haces clic:

```bash
npx cypress open
# or
./node_modules/.bin/cypress open
```
Sin cabeza es lo que hace CI y a lo que se asigna `yarn test:e2e`:

```bash
yarn test:e2e        # cypress run --browser chrome
```
Fijamos `--browser chrome` a propósito en lugar de dejar que tenga el valor predeterminado
Electron incluido, por lo que las ejecuciones locales coinciden con CI. Una ejecución graba un vídeo en
`cypress/videos/` y, en caso de error, una captura de pantalla en `cypress/screenshots/`, por lo que
Puedes ver lo que vio la prueba incluso en caso de falla sin cabeza.

Vale la pena conocer un par de configuraciones en `cypress.config.ts` porque
cambiar el comportamiento de las pruebas: `chromeWebSecurity: false` (por lo que cosas de origen cruzado como
Los iframes de OAuth no se bloquean en el desarrollo local), `experimentalStudio: true`
(habilita Studio, a continuación) y `experimentalMemoryManagement: true` con
`numTestsKeptInMemory: 0`: mantenemos cero pruebas anteriores en la memoria porque estas
los viajes son largos y, de lo contrario, Chrome se hincharía y colapsaría a mitad de camino.

### Comandos personalizados

La característica más útil de Cypress aquí son los **comandos personalizados**: un comando reutilizable
Función Cypress para que no reescribas el inicio de sesión (o la creación de un concurso o un problema)
creación) en cada especificación. Están declarados en
[`cypress/support/commands.ts`](https://github.com/omegaup/omegaup/blob/main/cypress/support/commands.ts).
`login` registra a un usuario publicando directamente en la API en lugar de impulsar el
forma, que es más rápida y menos escamosa:

```typescript
Cypress.Commands.add('login', ({ username, password }: LoginOptions) => {
  cy.request({
    method: 'POST',
    url: '/api/user/login/',
    form: true,
    body: { usernameOrEmail: username, password },
  }).then((response) => {
    expect(response.status).to.equal(200);
    cy.reload();
  });
});
```
Hay un hermano `loginAdmin` que codifica la cuenta de administrador inicializada.
(`omegaup` / `omegaup`), más `register`, `logout`, `logoutUsingApi`,
`createProblem`, `createCourse`, `createRun`, `createContest`,
`addProblemsToContest`, `createGroup` y más: la configuración completa del concurso/curso
vocabulario, por lo que una especificación se lee como una historia en lugar de un muro de clics.

Como estamos en TypeScript, agregar un comando son dos pasos y omitir el
El segundo es el error clásico: **declarar su tipo**, o TypeScript no lo sabrá.
`cy.myCommand()` existe. La interfaz `Chainable` vive en
[`cypress/support/cypress.d.ts`](https://github.com/omegaup/omegaup/blob/main/cypress/support/cypress.d.ts),
y los tipos de opciones (`LoginOptions`, `CourseOptions`, `ProblemOptions`,…) en
`cypress/support/types.d.ts`:

```typescript
declare global {
  namespace Cypress {
    interface Chainable {
      login(loginOptions: LoginOptions): void;
      loginAdmin(): void;
      register(loginOptions: LoginOptions): void;
      createProblem(problemOptions: ProblemOptions): void;
      // ...add your new command's signature here
    }
  }
}
```
### Eventos: no permita que una excepción de terceros interrumpa la ejecución

A veces es necesario que una prueba continúe incluso cuando se activa una excepción no detectada.
del código que no controlas. El caso concreto que obligó a esto: al correr
Cypress, la API de inicio de sesión de Google se negó a reconocer `127.0.0.1` (la IP de Docker)
como host permitido y lanzó `idpiframe_initialization_failed`, que por defecto
aborta toda la prueba. La solución es un controlador global `uncaught:exception` en
[`cypress/support/e2e.ts`](https://github.com/omegaup/omegaup/blob/main/cypress/support/e2e.ts)
que devuelve `false` exactamente para esos errores conocidos e inofensivos, por lo que la prueba
continúa:

```typescript
import './commands';

Cypress.on('uncaught:exception', (err, runnable) => {
  if (
    (err as any).message?.includes('idpiframe_initialization_failed') ||
    (err as any).error?.includes('idpiframe_initialization_failed') ||
    (err as any).message?.includes(
      'ResizeObserver loop completed with undelivered notifications',
    )
  ) {
    // Google API sign-in error, and a benign ResizeObserver warning
    return false;
  }
});
```
Tenga en cuenta que también se traga el bucle `ResizeObserver completado con datos no entregados.
Advertencia de notificaciones: un ruido benigno del navegador que, de lo contrario, alteraría su
pruebas. Coloque los controladores que solo desee para una especificación dentro de ese archivo de especificaciones en lugar de
aquí; `e2e.ts` es global y se aplica a todas las pruebas.

### Cypress Studio y los complementos

Debido a que `experimentalStudio` está activado, al abrir una especificación en la GUI aparece un botón
para **registrar** sus interacciones directamente en la especificación como comandos: haga clic en
a través del flujo y Studio escribe las llamadas `cy.*` por usted, ya sea extendiendo un
Prueba existente o andamiaje por uno nuevo. Una buena propiedad: Studio no
_no_ registrar el tiempo entre acciones, para que no tengas que apresurarte; tomar tanto tiempo
como quieras entre clics.

Dos complementos están conectados e importados en la parte superior de `commands.ts`:
**cypress-wait-until** (`cy.waitUntil(...)`, para sondear hasta que se cumpla una condición
- usado p.e. en `logout` para esperar a que se establezca la URL) y
**cypress-file-upload** (para `.attachFile(...)` en los flujos de carga de problemas).
El gancho `setupNodeEvents` en cargas `cypress.config.ts`
`cypress/plugins/index.js`, que registra una tarea `log` para que una prueba pueda imprimirse
el terminal que ejecuta Cypress.

### Cuando pasa localmente pero falla en CI

CI ejecuta las especificaciones fragmentadas en una matriz (consulte el trabajo `cypress` en
[`.github/workflows/ci.yml`](https://github.com/omegaup/omegaup/blob/main/.github/workflows/ci.yml)),
cada fragmento ejecuta `./node_modules/.bin/cypress run --browser chrome --spec '<specs>'`.
Cuando una prueba aparece en verde en su máquina pero en rojo en el PR, no adivine: observe lo que sucede.
el navegador CI vio. Abra la pestaña **Verificaciones** del PR, seleccione el **ciprés** fallido
trabajo y descargue los artefactos de la ejecución:

- `cypress-videos-shard-<shard>-<run_attempt>`: el vídeo de la ejecución real.
- `cypress-screenshots-shard-<shard>-<run_attempt>` — capturas de pantalla en este momento
  de fracaso.
- `frontend-test-logs-<run_attempt>`: registros del lado del contenedor, cuando el error es
  Realmente es el backend el que se comporta mal en lugar de la prueba.

El sufijo `<run_attempt>` es el número de intento de la ejecución del flujo de trabajo (visible
en la URL de ejecución, p.e. `/attempts/3`), por lo que si volvió a ejecutar un trabajo incorrecto, asegúrese de
Coge los artefactos del intento que realmente falló.

## Pruebas de interfaz de usuario de Python

Hay una suite de interfaz de usuario de estilo Selenium más pequeña en `frontend/tests/ui/` ejecutada con
`python3 -m pytest ./frontend/tests/ui/ -s`. Como le recuerda `runtests.sh`,
se ejecuta **fuera** del contenedor, por lo que no forma parte del contenedor
Flujo de PHPUnit.

## Cobertura de prueba

Llevamos la cobertura a **Codecov**. La cobertura de PHP proviene del informe Clover
(`coverage.xml`) que emite `run-php-tests.sh` y cobertura de TypeScript desde
`yarn test:coverage`. Los recorridos de Cypress **no** están conectados a la cobertura todavía;
demostrar que los viajes funcionan de principio a fin, pero no cuentan para la cobertura
número, así que no confíe en una prueba e2e para "cubrir" una unidad de lógica que un Jest o
La prueba PHPUnit debe poseer.

## Algunos hábitos que vale la pena mantener

Mantenga las pruebas unitarias realmente rápidas y genuinamente aisladas: cada prueba PHPUnit se construye
sus propios accesorios a través de los ayudantes `Factories/` y cada prueba de Jest monta su
propio componente, por lo que las pruebas nunca dependen del estado sobrante de cada uno o de
orden de ejecución. Busque la capa que coincida con lo que está probando: puro
Las funciones y los componentes individuales pertenecen a Jest, controlador/permiso/API.
El comportamiento pertenece a PHPUnit contra un MySQL real, y solo el completo
El recorrido del usuario entre páginas obtiene una especificación Cypress (son los más lentos y los más
más escamosos, así que gástelos deliberadamente). Y cuando tocas comportamiento, escribe o
actualice la prueba en el mismo cambio: un PR que cambia lo que hace el código pero
no es lo que afirman las pruebas el que los revisores enviarán.

## Documentación relacionada

- **[Pautas de codificación](coding-guidelines.md)**: los estándares que imponen los linters y el Salmo
- **[Comandos útiles](useful-commands.md)** — la hoja de trucos de comandos del día a día
- **[Configuración de desarrollo](../getting-started/development-setup.md)**: instale Node, Yarn y Docker antes de ejecutar cualquiera de estas funciones.
