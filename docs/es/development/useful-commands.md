---
title: Comandos de desarrollo útiles
description: Comandos y atajos comunes para el desarrollo de omegaUp
icon: bootstrap/terminal
---
# Comandos de desarrollo útiles

Este es el conjunto de comandos de trabajo que utilizará día a día: linting, los conjuntos de pruebas de PHP y Vue, la compilación de Webpack y los scripts de bases de datos que mantienen honestos su esquema local y sus datos iniciales. Cada comando a continuación se reproduce exactamente como debe escribirlo: las banderas soportan carga, así que no las parafrasee.

Lo más importante que debes hacer antes que nada es **dónde** ejecutas cada comando. El desarrollo de omegaUp ocurre a través de un límite: algunas herramientas se ejecutan en su máquina host (necesita su socket Docker, su instalación de Node o un navegador), y otras se ejecutan *dentro* del contenedor `frontend` (necesita el tiempo de ejecución PHP, la conexión MySQL en el puerto `13306` y el código montado en `/opt/omegaup`). Ejecutar un comando en el lado equivocado de ese límite es el primer tropiezo más común, por lo que cada sección indica su ubicación de ejecución y varios scripts se niegan activamente a ejecutarse en el lugar equivocado en lugar de fallar crípticamente.

Para entrar al contenedor en primer lugar:

```bash
docker exec -it omegaup-frontend-1 /bin/bash
```
Esto abre un shell bash dentro del contenedor frontend y lo lleva a `/opt/omegaup` (el repositorio, montado en enlace desde su host). El contenedor se llama `omegaup-frontend-1` en Docker Compose V2 (el esquema `<project>-<service>-<n>`, donde el nombre del proyecto por defecto es su directorio `omegaup`). En instalaciones anteriores de Compose V1, el mismo contenedor se llama `omegaup_frontend_1` con guiones bajos; si `docker exec` se queja de que el contenedor no existe, ejecute `docker compose ps` para ver el nombre exacto que produjo su configuración.

!!! consejo "Cómo saber de qué lado estás"
    Dentro del contenedor, su mensaje se encuentra en `/opt/omegaup`; en el host es donde clonó el repositorio (por ejemplo, `~/dev/omegaup`). Varios scripts detallan esto: `git rev-parse --show-toplevel` devolviendo `/opt/omegaup` es exactamente cómo `lint.sh` y `runtests.sh` detectan que están dentro del contenedor.

## Linting y validación

### Ejecute todos los linters omegaUp

```bash
./stuff/lint.sh
```
Ejecute esto desde la **raíz del proyecto en su host**, fuera del contenedor: activa su propia imagen de Docker (`omegaup/hook_tools:v1.0.9`) para ejecutar los linters en un entorno anclado y reproducible, por lo que necesita su socket Docker. Debido a eso, `lint.sh` se niega explícitamente a ejecutarse dentro del contenedor: si `git rev-parse --show-toplevel` regresa como `/opt/omegaup`, imprime *"Ejecutar ./stuff/lint.sh dentro de un contenedor no es compatible"* y sale, y si no puede encontrar un binario de `docker`, le indica que instale Docker o que se mueva fuera del contenedor. Ambos mensajes son el script que lo protege de una ejecución que silenciosamente haría algo incorrecto.

Sin argumentos, `lint.sh` no destruye todo el árbol: adivina el conjunto de archivos que realmente cambió al compararlos con la base de combinación de su rama y `upstream/main` (recurriendo a `origin/main` si no ha agregado el control remoto `upstream`), razón por la cual una primera ejecución después de la clonación sin un upstream puede comportarse de manera diferente a lo esperado. Sin embargo, rara vez es necesario invocarlo manualmente: está conectado al gancho git `pre-push`, por lo que se ejecuta automáticamente en cada `git push` y bloquea el envío si algo no está limpio.

### Validar estilo sin arreglar

```bash
./stuff/lint.sh validate
```
El modo predeterminado *corrige* lo que puede (delega a `yapf`, `prettier`, `phpcbf` y amigos dentro de la imagen de herramientas de gancho); En cambio, `validate` solo verifica e informa, sin cambiar nada en el disco. Utilice esto en situaciones similares a CI o cuando quiera ver qué está mal antes de dejar que el autofixer reescriba sus archivos.

### Generar archivos de traducción `.lang`

```bash
./stuff/lint.sh --linters=i18n fix --all
```
Esto ejecuta solo el linter `i18n` y regenera los archivos `*.lang` en todas las configuraciones regionales a partir de los tres archivos fuente de verdad `es.lang`, `en.lang` y `pt.lang`. Ejecútelo cada vez que agregue o cambie una cadena orientada al usuario para que los archivos generados por idioma permanezcan sincronizados; de lo contrario, el linter i18n fallará. También se ejecuta fuera del contenedor, desde la raíz del proyecto.

## Pruebas

### Ejecute todas las pruebas y validaciones de PHP

```bash
./stuff/runtests.sh
```
Esta es la puerta de backend completa y está destinada a ejecutarse **dentro del contenedor**. Incluye cuatro comprobaciones distintas que, de otro modo, ejecutaría por separado: `stuff/db-migrate.py validate` (confirma que sus migraciones son consistentes), `stuff/policy-tool.py validate` y `stuff/mysql_types.sh`, que es la más pesada, ejecuta los controladores y las insignias PHPUnit suites *más* la verificación de tipo de retorno de MySQL que verifica que sus métodos DAO realmente coincidan con las formas que devuelven sus consultas, y finalmente Psalm con `--show-info=false`.

`runtests.sh` reconoce la ubicación: ejecútelo dentro del contenedor e invoca esas herramientas directamente; ejecútelo en el host y se insertará de forma transparente en el contenedor con `docker compose exec -T frontend` para cada paso. De cualquier manera, cuando finaliza la parte del contenedor, le recuerda que debe ejecutar las dos comprobaciones del lado del host que *no* puede hacer desde adentro (`./stuff/lint.sh` y las pruebas de Selenium/UI a través de `python3 -m pytest ./frontend/tests/ui/ -s`) porque necesitan Docker y un navegador respectivamente. No te saltes ese recordatorio; un `runtests.sh` verde por sí solo no es una construcción ecológica.

### Ejecute pruebas unitarias de PHP para un archivo específico

```bash
./stuff/run-php-tests.sh frontend/tests/controllers/$MY_FILE.php
```
Cuando estás iterando en un controlador, no quieres todo el conjunto. Este contenedor ejecuta PHPUnit solo contra el archivo que nombre (omita el nombre del archivo por completo para ejecutar todo bajo `frontend/tests/`). Conecta la configuración real de la suite por usted (`--bootstrap frontend/tests/bootstrap.php`, `--configuration frontend/tests/phpunit.xml` y la cobertura escrita en `coverage.xml`) y luego pasa cualquier argumento *extra* directamente a `phpunit`. Ese paso a través es la parte útil: para ejecutar un único método de prueba, puede agregar el propio filtro de PHPUnit, por ejemplo.

```bash
./stuff/run-php-tests.sh frontend/tests/controllers/UserRankTest.php --filter testUserRankingClassName
```
Ejecute esto dentro del contenedor, ya que PHPUnit necesita la conexión MySQL en vivo.

### Ejecute pruebas de Cypress de un extremo a otro (interactivo)

```bash
npx cypress open
```
Esto abre Cypress Test Runner, la GUI donde eliges una especificación, observas cómo maneja un Chrome real e inspeccionas las fallas paso a paso con instantáneas de viajes en el tiempo: la forma más rápida de depurar una prueba e2e inestable. Se ejecuta en el **host**, fuera del contenedor (necesita un navegador real y, en Linux, puede necesitar `libasound2` y otras dependencias de X instaladas antes de su lanzamiento). Las especificaciones en sí se encuentran en `cypress/e2e/*.cy.ts`; actualmente hay unas diez, que cubren cursos, grupos, el IDE, navegación, certificados, concursos y los flujos de creación/colección de problemas.

### Ejecute Cypress sin cabeza

```bash
yarn test:e2e
```
Las mismas especificaciones sin la GUI: esto se expande a `cypress run --browser chrome`, ejecutando todas las especificaciones sin cabeza e imprimiendo los resultados en la terminal. Esto es lo que utiliza CI y lo que desea para un pase rápido de "¿Rompí algún flujo e2e?", ya que no espera a que haga clic en nada.

### Ejecute pruebas unitarias de Vue en modo de vigilancia

```bash
yarn run test:watch
```
Esto ejecuta las pruebas unitarias de Jest (Jest 26 a través de `ts-jest`) para la interfaz Vue/TypeScript en modo de vigilancia; bajo el capó, está `cross-env TZ=UTC jest --watchAll --notify` con alcance para archivos que coinciden con `frontend/www/js/.*test\.ts$`. El modo de vigilancia mantiene Jest residente y vuelve a ejecutar las pruebas afectadas cada vez que guarda un componente o su prueba, de modo que obtiene una señal roja/verde continua mientras trabaja en lugar de volver a activarla manualmente. El pin `TZ=UTC` es importante: fuerza una zona horaria determinista para que las pruebas sensibles a la fecha no pasen en su máquina y fallen en CI. Para una ejecución única, utilice `yarn test`; para cobertura utilice `yarn test:coverage`.

### Ejecute un archivo de prueba de unidad Vue específico

```bash
./node_modules/.bin/jest frontend/www/js/omegaup/components/$MY_FILE.test.ts
```
Cuando el modo de vigilancia se vuelve a ejecutar demasiado, invoque Jest directamente contra un único archivo de prueba. Todos los componentes de un solo archivo de Vue se encuentran bajo `frontend/www/js/omegaup/components/`, por lo que sus vecinos `.test.ts` también lo hacen. Este se ejecuta felizmente dentro o fuera del contenedor: es Node puro sin dependencia de MySQL.

## Construyendo la interfaz

El sitio es un shell Twig 3 que envuelve componentes de un solo archivo Vue 2.7 + TypeScript, incluidos en Webpack 5. Durante el desarrollo, casi siempre querrás que un observador reconstruya los paquetes a medida que los editas, en lugar de reconstruirlos manualmente.

```bash
yarn dev:watch
```
Este es el bucle cotidiano: ejecuta Webpack contra la configuración `frontend` en modo de desarrollo con `--watch`, por lo que cada guardado vuelve a agrupar solo los puntos de entrada del frontend. Los scripts relacionados cambian el alcance por la velocidad: `yarn dev` es la misma compilación una vez sin mirar; `yarn dev-all` / `yarn dev-all:watch` construye *todas* las configuraciones del paquete web (la interfaz, más el estilo y los paquetes secundarios) cuando un cambio afecta más que el código de la aplicación.

Para un paquete que se puede enviar, `yarn build` ejecuta Webpack en `--mode=production` (minimizado, sin mapas fuente), mientras que `yarn build-development` produce una compilación de desarrollo no minificada. Y para explorar componentes de forma aislada:

```bash
yarn storybook
```
Esto inicia Storybook (7.6) en el puerto `6006` a través de `storybook dev -p 6006`, lo que le brinda una zona de pruebas para renderizar y examinar componentes individuales de Vue sin iniciar toda la aplicación. Actualmente, la cobertura de historias es escasa (aproximadamente diez archivos `.stories` contra más de 250 componentes), por lo que no todos los componentes tienen una entrada todavía.

!!! nota "La aplicación web no muestra mis cambios"
    Si edita un archivo `.vue` o `.ts` y la página parece sin cambios, la causa habitual es que no se está ejecutando ningún observador para reconstruir el paquete. Asegúrese de que `yarn dev:watch` (o `yarn dev-all:watch`) se esté ejecutando y luego vuelva a cargar la página en **http://localhost:8001**. Los cambios de PHP, por el contrario, se recogen directamente desde el montaje del enlace sin necesidad de reconstrucción.

## Base de datos

### Restablecer la base de datos a su estado inicial

```bash
./stuff/bootstrap-environment.py --purge
```
Ejecute esto dentro del contenedor cuando sus datos locales hayan quedado inutilizables o cuando simplemente desee hacer borrón y cuenta nueva para realizar pruebas. El indicador `--purge` elimina y vuelve a crear la base de datos desde cero; Luego, el script reproduce una serie de solicitudes de API reales para completarlo, presentando concursos, cursos, problemas y los usuarios de prueba que necesita para las pruebas manuales. La definición de lo que se crea se encuentra en `stuff/bootstrap.json`, por lo que si desea aparatos adicionales, ese es el archivo para editar. Siéntase libre de ejecutarlo tantas veces como necesite: un arranque nuevo es la forma más rápida de salir del problema "mi base de datos local no funciona".

### Aplicar migraciones de bases de datos localmente

```bash
./stuff/db-migrate.py migrate --databases=omegaup,omegaup-test
```
Después de agregar un nuevo archivo de migración `.sql`, se aplican los cambios de esquema pendientes a sus bases de datos locales. Nombrar **ambos** `omegaup` y `omegaup-test` es deliberado e importante: la segunda es la base de datos con la que se ejecuta la suite PHPUnit, por lo que si migra solo `omegaup` su aplicación funcionará pero `runtests.sh` fallará con un esquema de prueba obsoleto (y su propio paso `db-migrate.py validate` señalará la falta de coincidencia). Ejecútelo dentro del contenedor.

### Regenera `schema.sql` y los DAO de tu migración

```bash
./stuff/update-dao.sh
```
Las migraciones describen *cambios*; `schema.sql` y las clases DAO/VO generadas describen la forma *actual* de la base de datos y no se actualizan por sí mismas. Este script copia `frontend/database/schema.sql` en `frontend/database/dao_schema.sql` para activar la regeneración, luego ejecuta `stuff/update-dao.py` para reescribir las clases base DAO generadas automáticamente y los objetos de valor para que coincidan con sus nuevas columnas. Ejecútelo dentro del contenedor después de agregar una migración y observe el problema del orden: se regenera según el esquema confirmado, por lo que hace su trabajo una vez que el archivo de migración está en su lugar.

## Validación de tipo PHP

### Ejecute Psalm en la fuente PHP

```bash
find frontend/ \
    -name *.php \
    -and -not -wholename 'frontend/server/libs/third_party/*' \
    -and -not -wholename 'frontend/tests/badges/*' \
    -and -not -wholename 'frontend/tests/controllers/*' \
    -and -not -wholename 'frontend/tests/runfiles/*' \
    -and -not -wholename 'frontend/www/preguntas/*' \
  | xargs ./vendor/bin/psalm \
    --long-progress \
    --show-info=false
```
Esto ejecuta Psalm (el verificador de tipo estático configurado por `psalm.xml`) sobre el PHP propio, usando `find` para entregarle cada archivo `.php` *excepto* las rutas excluidas (bibliotecas de terceros bajo `frontend/server/libs/third_party/`, varios directorios de accesorios de prueba y el árbol `frontend/www/preguntas/` heredado) porque no son nuestros para verificar el tipo o ahogarían la ejecución en ruido. `--long-progress` le ofrece una barra de progreso en vivo para lo que es un pase lento de todo el árbol, y `--show-info=false` suprime los avisos informativos para que solo aparezcan errores tipográficos genuinos. Ejecútelo dentro del contenedor. Si solo desea verificar lo mismo, se ejecuta la puerta CI, `runtests.sh` ya invoca a `./vendor/bin/psalm --show-info=false` por usted.

## acoplador

### Iniciar el entorno de desarrollo

```bash
docker compose up --no-build
```
Así es como se reúne toda la pila: el contenedor `frontend` (php-fpm detrás de nginx, sirviendo en **http://localhost:8001**), MySQL 8.0 en el puerto `13306`, Redis y los servicios Go prediseñados (`gitserver`, `grader`, `broadcaster` y `runner`) extraídos de las imágenes de `omegaup/*`. `--no-build` omite la reconstrucción de las imágenes y simplemente ejecuta lo que ya tiene, que es lo que desea en un día normal; suéltelo (`docker compose up`) en una primera ejecución o después de cambios de imagen para que Compose construya/extraiga primero. El backend PHP frontal se comunica con Go `grader` a través de HTTP en `OMEGAUP_GRADER_URL` (`https://localhost:21680` predeterminado), mientras que las manos del clasificador trabajan con los corredores internamente en el puerto `11302`; esos servicios se encuentran en los repositorios `omegaup/quark` y `omegaup/gitserver` separados, no en este.

!!! nota "`docker compose` frente a `docker-compose`"
    Docker Compose V2 es el complemento de `docker compose` (con un espacio); Las configuraciones más antiguas tienen el binario `docker-compose` independiente. Cualquiera de los dos funciona siempre que su instalación proporcione uno de ellos; Los ejemplos aquí utilizan el formulario V2.

### Reiniciar el servicio Docker

```bash
systemctl restart docker.service
```
Ejecute esto en su **host** (Linux) cuando Docker se encuentre en mal estado, específicamente, si `docker exec` comienza a fallar con:

```bash
OCI runtime exec failed: exec failed: unable to start container process: open /dev/pts/0: operation not permitted: unknown
```
Ese error no es un problema con omegaUp; es el tiempo de ejecución del demonio Docker el que ha perdido la capacidad de asignar un pseudoterminal para su `exec`. Al reiniciar el demonio `docker.service` se borra, después de lo cual `docker exec -it omegaup-frontend-1 /bin/bash` vuelve a funcionar. (En macOS o Windows, el equivalente es reiniciar Docker Desktop).

## Referencia rápida

Cada comando, con el lado del límite del contenedor al que pertenece:

| Tarea | Comando | Dónde correr |
|------|---------|--------------|
| Ejecute todos los linters (autofix) | `./stuff/lint.sh` | Anfitrión, raíz del proyecto |
| Comprobar estilo sin arreglar | `./stuff/lint.sh validate` | Anfitrión, raíz del proyecto |
| Regenerar archivos `.lang` | `./stuff/lint.sh --linters=i18n fix --all` | Anfitrión, raíz del proyecto |
| Prueba PHP completa + puerta de validación | `./stuff/runtests.sh` | Contenedor interior |
| Un archivo de prueba PHP | `./stuff/run-php-tests.sh frontend/tests/controllers/$MY_FILE.php` | Contenedor interior |
| GUI de ciprés | `npx cypress open` | Anfitrión |
| Ciprés sin cabeza | `yarn test:e2e` | Anfitrión |
| Pruebas unitarias de Vue (ver) | `yarn run test:watch` | Cualquiera de los lados |
| Un archivo de prueba de Vue | `./node_modules/.bin/jest frontend/www/js/omegaup/components/$MY_FILE.test.ts` | Cualquiera de los lados |
| Vigilante de construcción de frontend | `yarn dev:watch` | Anfitrión |
| Paquete de producción | `yarn build` | Anfitrión |
| Zona de pruebas de componentes | `yarn storybook` (puerto 6006) | Anfitrión |
| Restablecer y inicializar la base de datos | `./stuff/bootstrap-environment.py --purge` | Contenedor interior |
| Aplicar migraciones | `./stuff/db-migrate.py migrate --databases=omegaup,omegaup-test` | Contenedor interior |
| Regenerar esquema + DAO | `./stuff/update-dao.sh` | Contenedor interior |
| Abrir un shell de contenedor | `docker exec -it omegaup-frontend-1 /bin/bash` | Anfitrión |
| Iniciar la pila | `docker compose up --no-build` | Anfitrión |

## Documentación relacionada

- **[Guía de pruebas](testing.md)**: la imagen completa en PHPUnit, Jest y Cypress
- **[Pautas de codificación](coding-guidelines.md)**: los estándares que aplican los linters
- **[Configuración de desarrollo](../getting-started/development-setup.md)**: hacer que el entorno se ejecute en primer lugar
