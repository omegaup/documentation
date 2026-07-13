---
title: Solución de problemas
description: Problemas comunes y soluciones
icon: bootstrap/tools
---
# Solución de problemas

Esta página recopila las fallas operativas que las personas realmente sufrieron al ejecutar omegaUp: la pila no arranca, la API no puede acceder a MySQL, las ediciones del frontend no aparecen o el evaluador es inaccesible y los envíos se bloquean. Para cada uno, presentamos el **error sin formato que verá**, luego explicamos **lo que realmente significa** y luego damos la **solución**, porque un síntoma que no puede interpretar es un síntoma que no puede resolver, y el texto del error es lo que nos permite relacionar su problema con una causa conocida.

Muchos de los tropiezos del *tiempo de desarrollo* (pago de propiedad raíz, rastreos de MySQL `git push`, redirecciones HTTPS forzadas, submódulos faltantes) ya tienen reseñas detalladas en [Configuración del entorno de desarrollo](../getting-started/development-setup.md#troubleshooting). Esta página es la compañera del lado de operaciones: asume que la pila estuvo parada en algún momento y ahora se está comportando mal, y enlaza con la página de configuración siempre que la causa raíz sea realmente un error de configuración.

Antes de profundizar, un modelo mental que ahorra mucho tiempo: **la pila local no es un proceso, es un gráfico de contenedores con un orden de arranque estricto.** En `docker-compose.yml`, el contenedor `frontend` `depends_on` `mysql`, `gitserver`, `grader` y `redis`; el `grader` espera a `mysql:13306` (`wait-for-it mysql:13306`) antes de comenzar; el `runner` espera a `grader:11302`; y `gitserver` también espera a `mysql:13306`. Entonces, cuando algo "no aparece", la primera pregunta siempre es *qué contenedor*, y la segunda es *qué estaba esperando*. `docker compose ps` responde a la primera; `docker compose logs <service>` responde al segundo.

---

## La pila no arranca

**Síntoma**: `docker compose up --no-build` nunca llega al estado listo o aparece un contenedor como `Restarting` / `Exited` en `docker compose ps` en lugar de `Up`.

Comience preguntando a Compose qué cree que se está ejecutando y luego lea el registro de cualquier servicio que no esté en buen estado:

```bash
docker compose ps               # which container is Restarting / Exited?
docker compose logs frontend    # then read that specific service's log
docker compose logs grader
```
La señal normal y saludable para un primer arranque **no es instantánea**: un arranque en frío tarda **entre 2 y 10 minutos** porque el contenedor `frontend` compila toda la aplicación Vue 2.7 + TypeScript con Webpack, MySQL inicializa su directorio de datos y el clasificador bloquea la base de datos. Lo que le indica que está realmente listo es un volcado del módulo Webpack que termina con algo como `Child grader: 1131 modules` (los recuentos exactos varían a medida que crece el código base). Si nunca ha visto un inicio exitoso en esta máquina, no considere una espera larga como un bloqueo: consulte el [resultado completo del estado listo en la guía de configuración](../getting-started/development-setup.md#step-2-bring-up-the-containers) y espere primero los diez minutos completos.

Una vez que haya aislado el contenedor defectuoso, los culpables habituales, en orden aproximado de frecuencia con que los vemos:

**El contenedor `frontend` se reinicia en un bucle con `Permission denied`.** Si los registros muestran `Permission denied` mientras se crea `phpminiadmin` o se escribe en `stuff/venv/`, el árbol del proyecto se clonó como **root** o `docker compose` se ejecutó con `sudo`, por lo que el montaje de enlace en `/opt/omegaup` es propiedad de root y el usuario no root del contenedor no puede escribir en él. Esto es lo suficientemente común como para que tenga su propia sección, [Mi entorno de desarrollo no aparece] (../getting-started/development-setup.md#my-dev-environment-wont-come-up), y la solución es volver a clonar como un usuario normal en su directorio de inicio, agregarse al grupo `docker` (`sudo usermod -a -G docker $USER`, luego cerrar sesión y volver a iniciarla), y nunca a `sudo git clone`. Intentar `chown` devolver el árbol de propiedad raíz a su lugar no vale la pena.

**Un contenedor dependiente comienza antes de lo que necesita.** Debido a que `grader` y `gitserver` se abren en `wait-for-it mysql:13306`, un MySQL que nunca sea accesible los dejará *atrapados* esperando, lo que a su vez deja a `frontend` esperando en `grader`. Si `docker compose ps` muestra `grader` o `gitserver` en estado de espera, no los depure; primero depure MySQL (siguiente sección). El orden importa: arreglar la hoja rara vez arregla la raíz.

**El puerto ya está en uso.** Si un contenedor muere inmediatamente con un error de vinculación como `Error starting userland proxy: listen tcp4 0.0.0.0:8001: bind: address already in use`, algo más en su host ya posee ese puerto. La pila publica un conjunto específico y memorable: **`8001`** (frontend HTTP), **`13306`** (MySQL), **`21680`** (grader HTTP API), **`33861`** (gitserver) y **`5672`/`15672`** (RabbitMQ). Encuentra y libera al delincuente:

```bash
lsof -i :8001        # or :13306, :21680, :33861
kill -9 <PID>        # or stop whatever service owns it
```
**No tienes disco o las imágenes están obsoletas.** Una compilación bloqueada o un OOM durante el inicio a menudo se remonta a una raíz de datos completa de Docker. Verificar y reclamar:

```bash
docker system df           # how much is images / containers / volumes eating?
docker system prune        # remove stopped containers, dangling images, unused networks
```
Si, en cambio, el error es "imagen no encontrada" o una falta de coincidencia después de una gran extracción, las imágenes fijadas (actualmente `omegaup/dev-php:20231008`, `omegaup/backend:v1.9.35`, `omegaup/runner:v1.9.35`, `omegaup/gitserver:v1.9.13`, `mysql:8.0.34`) deben actualizarse: `docker compose pull` toma el conjunto actual y solo lo necesita en la primera configuración o cuando `up` se queja de que falta una imagen o está obsoleta.

Como último recurso, y sólo cuando esté dispuesto a perder el estado local, puede borrar y reconstruir desde cero. Tenga en cuenta que `-v` descarta sus **volúmenes** (incluidos los datos de MySQL y los problemas de almacenamiento de git), por lo que volverá a ejecutar el arranque del entorno después:

```bash
docker compose down -v      # careful: this deletes the MySQL and omegaupdata volumes
docker compose up --no-build
```
---

## MySQL no es accesible

**Síntoma**: la API devuelve 500 y el registro de PHP o el navegador muestra un error de conexión como `SQLSTATE[HY000] [2002]` o `Can't connect to MySQL server`. Nada de lo que toca la base de datos funciona, que es básicamente todo.

El hecho que soporta la carga aquí es **dónde vive realmente MySQL y cómo PHP le habla.** La base de datos se ejecuta en el contenedor `mysql` (`mysql:8.0.34`), y la interfaz se conecta a través de TCP: `OMEGAUP_DB_HOST` tiene por defecto **`mysql:13306`** (ver `frontend/server/config.default.php`), y `\OmegaUp\MySQLConnection` usa el controlador **mysqli** (`mysqli_init()` / `real_connect()`), no PDO. Entonces, "no se puede conectar" casi siempre significa una de tres cosas: el contenedor no está activo, está activo pero aún se inicializa, o algo está apuntando al cliente al lugar equivocado.

Primero, confirme que el contenedor realmente se esté ejecutando y que haya terminado de inicializarse. MySQL 8.0 hace un trabajo real en el primer arranque, y la API rechazará la conexión hasta que imprima su línea lista:

```bash
docker compose ps mysql
docker compose logs mysql | tail -50
docker compose logs mysql | grep "ready for connections"
```
Si aún no ve `ready for connections`, esa es la respuesta completa: **espérelo**, no lo reinicie, porque un reinicio simplemente vuelve a ejecutar el mismo inicio lento. Esta es también la razón por la que `grader` y `gitserver` se abren en `wait-for-it mysql:13306`: todo lo posterior está escrito para asumir que MySQL aparece primero.

Si MySQL *está* listo pero la API aún no puede alcanzarlo, pruebe la conexión desde el interior del contenedor frontend, que es el entorno en el que PHP realmente se ejecuta:

```bash
docker compose exec frontend /bin/bash
mysql --host=mysql --port=13306 --user=omegaup --password=omegaup omegaup -e "SELECT 1"
```
Las credenciales locales predeterminadas son `omegaup` / `omegaup` en la base de datos `omegaup`, que coinciden con `MYSQL_USER` / `MYSQL_PASSWORD` / `MYSQL_DATABASE` en el servicio `mysql`. Si ese `SELECT 1` tiene éxito desde el interior del contenedor pero su herramienta falla desde el **host**, se ha topado con la confusión más común: **el host no tiene ruta a MySQL excepto TCP en `13306`.** Un cliente `mysql` del lado del host que utiliza de forma predeterminada un socket Unix fallará con `Can't connect to local MySQL server through socket '/var/run/mysqld/mysqld.sock'`, porque no hay un servidor local, está en Docker. Ese caso exacto (muerde el gancho de política `git push`, que se ejecuta en el host) tiene una corrección de configuración TCP que se puede copiar y pegar en [git push falla con "No se puede conectar al servidor MySQL local"](../getting-started/development-setup.md#git-push-fails-with-cant-connect-to-local-mysql-server).

Dos firmas de error de MySQL más que vale la pena interpretar, porque parecen conectividad pero no lo son:

- **`ERROR 3024 ... Query execution was interrupted, maximum statement execution time exceeded`.** El contenedor `mysql` se inicia con `--max_execution_time=30000` (30 segundos), por lo que una consulta realmente lenta se elimina en lugar de colgarse para siempre. Lea esto como "su consulta es demasiado lenta", no como "MySQL no funciona": `EXPLAIN` y busque un índice faltante.
- **`Lock wait timeout exceeded`.** El contenedor también configura `--lock_wait_timeout=10` y `--wait_timeout=20`, por lo que una transacción bloqueada en un bloqueo de fila durante más de ~10 segundos se cancela deliberadamente, para evitar que un escritor atascado atrape a todos. Encuentra el titular con `SHOW PROCESSLIST` y deja que termine o elimínalo, en lugar de aumentar el tiempo de espera.

Si los datos en sí están corruptos después de una falla grave (no solo inalcanzables), la opción nuclear es eliminar el volumen MySQL y reiniciar. Pierde todos los datos locales, así que solo haga esto en un cuadro de desarrollo:

```bash
docker compose down -v
docker compose up -d
```
---

## La aplicación web no muestra mis cambios

**Síntoma**: editó un archivo `.vue` o `.ts`, guardó, recargó el navegador y todavía muestra la interfaz de usuario anterior.

Esto confunde a la gente porque *parece* un error de almacenamiento en caché, pero normalmente no lo es. **El navegador recibe una compilación de Webpack, no sus archivos fuente**, por lo que una edición que no haya reconstruido es invisible sin importar cuántas veces actualice. La interfaz de usuario de cada página es un componente de archivo único de Vue 2.7 bajo `frontend/www/js/omegaup/components/`, compilado por Webpack 5 en el paquete que el shell Twig (`frontend/templates/template.tpl`) carga a través de sus etiquetas `{% entrypoint %}` / `{% jsInclude %}`. Nada de lo que escribe llega al navegador hasta que Webpack se vuelve a compilar.

Entonces, la solución es reconstruir, desde el interior del contenedor donde reside la cadena de herramientas:

```bash
docker compose exec frontend /bin/bash
cd /opt/omegaup && yarn run dev
```
`yarn run dev` ejecuta Webpack **una vez** en la interfaz. Si está iterando y no desea volver a ejecutarlo después de cada guardado, use `yarn dev:watch` en su lugar, que observa el árbol y lo reconstruye cuando cambia. Esta es la misma guía que la guía de configuración [¡La aplicación web no muestra mis cambios!](../getting-started/development-setup.md#the-web-app-is-not-showing-my-changes): vale la pena leerla allí para conocer el giro específico de Windows.

Hablando de eso: **en Windows, el observador pierde silenciosamente los eventos de cambio de archivos si su pago se encuentra bajo `/mnt/c/...`.** Los montajes de enlace de Docker a través del límite de Windows↔Linux no entregan eventos de inotify de manera confiable, por lo que `yarn dev:watch` no ve nada, nunca reconstruye y usted mira la salida obsoleta sin ningún error que lo explique. La solución no es un indicador de Webpack, sino mantener el repositorio dentro del sistema de archivos WSL2 de Linux (por ejemplo, `~/omegaup`), como se describe en la guía de configuración.

Si ha reconstruido exitosamente y *todavía* está obsoleto, analice esta breve lista antes de culpar a las herramientas: confirme que los contenedores realmente estén activos (`docker compose up --no-build`); realice una actualización completa real (`Ctrl+Shift+R` o `Cmd+Shift+R` en macOS) o abra DevTools → Red → **Desactivar caché** para que el navegador deje de ofrecer su propio paquete almacenado en caché; y si tocó la firma de un controlador PHP, recuerde que el cliente API escrito (`api.ts` / `api_types.ts`) se **genera**; no reflejará los cambios del controlador hasta que `frontend/server/cmd/APITool.php` lo regenere, no Webpack. No edites manualmente esos dos archivos; regenerarlos.

---

## El clasificador es inalcanzable

**Síntoma**: los envíos permanecen para siempre sin veredicto, o una acción de administrador que toca la calificación devuelve un 500. En el registro de PHP verá un error de canal `Grader`: `curl failed` con una URL en `https://localhost:21680`, o el mensaje de terminal `Maximum retry attempts exceeded`.

Aquí está la arquitectura que debe mantener para depurar esto, porque es en lo que se equivocó la antigua wiki: **el evaluador no es parte del código base de PHP.** El evaluador, el corredor, la emisora y el entorno limitado de minijail son servicios **Go** separados de [github.com/omegaup/quark](https://github.com/omegaup/quark) (el almacenamiento del problema es [github.com/omegaup/gitserver](https://github.com/omegaup/gitserver)), enviado como imágenes de Docker prediseñadas. El lado PHP es solo un cliente HTTP ligero: `\OmegaUp\Grader` (en [`frontend/server/src/Grader.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Grader.php)) envía solicitudes curl a **`OMEGAUP_GRADER_URL`**, que por defecto es **`https://localhost:21680`** (`frontend/server/config.default.php`). Cuando envía, `\OmegaUp\Controllers\Run::apiCreate` finalmente llama a `\OmegaUp\Grader::getInstance()->grade($run, $source)`, que envía un PUBLICACIÓN al `/run/new/{run_id}/` del clasificador. Si esa llamada HTTP no se puede completar, el envío nunca se califica, por lo que "calificador inalcanzable" es en realidad "el PHP no puede completar una solicitud HTTP a `21680`".

Esa conexión se **autentica mutuamente a través de TLS**, y aquí es donde las configuraciones locales se interrumpen con mayor frecuencia. La llamada curl en `\OmegaUp\Grader::curlRequestSingle` presenta un certificado de cliente (`CURLOPT_SSLCERT => /etc/omegaup/frontend/certificate.pem`, `CURLOPT_SSLKEY => /etc/omegaup/frontend/key.pem`), fija la CA a ese mismo certificado (`CURLOPT_CAINFO`) y, lo que es más importante, verifica estrictamente al par (`CURLOPT_SSL_VERIFYPEER => true`, `CURLOPT_SSL_VERIFYHOST => 2`, TLS 1.2). Por lo tanto, un certificado autofirmado o que no coincide no se aprueba silenciosamente; falla el apretón de manos. Si el error del clasificador `curl failed` menciona un problema de certificado/SSL en lugar de una conexión rechazada, sospeche que los certificados en `/etc/omegaup/frontend/`, no que el clasificador esté inactivo.

Diagnosticarlo en el orden en que realmente viaja la solicitud. En primer lugar, ¿el contenedor clasificador está nivelado y superó su propia espera de dependencia?

```bash
docker compose ps grader
docker compose logs grader | tail -50
```
Recuerde la puerta del clasificador `wait-for-it mysql:13306`: un clasificador atascado en espera es en realidad un problema de MySQL, así que verifique eso primero si el registro muestra que nunca se inició. El corredor es un contenedor separado que se registra con el clasificador en el puerto **interno** `11302` (`wait-for-it grader:11302`), que es distinto de la API HTTP `21680` con la que habla PHP; un calificador que está arriba pero que **no tiene corredores** aceptará envíos y nunca los terminará, así que verifique `docker compose logs runner` para ver el registro y los errores también.

A continuación, pregúntele directamente al evaluador cómo cree que se ve su cola. Hay un punto final de primera clase para esto: **`GET /api/grader/status/`**, servido por `\OmegaUp\Controllers\Grader::apiStatus`, que requiere una sesión de **administrador del sistema** (`\OmegaUp\Authorization::isSystemAdmin`, si no, `ForbiddenAccessException`) y devuelve `\OmegaUp\Grader::getInstance()->status()`, un proxy para el propio `/grader/status/` del calificador. La carga útil (`GraderStatus`) le indica exactamente dónde se encuentra un trabajo pendiente:

```json
{
  "grader": {
    "status": "ok",
    "broadcaster_sockets": 0,       // live WebSocket clients on the broadcaster
    "embedded_runner": false,       // is a runner running in-process?
    "queue": {
      "running": [],                // runs currently being judged: [{name, id}]
      "run_queue_length": 0,        // runs waiting to be dispatched
      "runner_queue_length": 0,     // runners idle and waiting for work
      "runners": []                 // names of registered runners
    }
  }
}
```
Léalo así: un `run_queue_length` en crecimiento con una lista `runners` vacía significa **no hay ningún corredor registrado**: el clasificador tiene trabajo pero nadie para hacerlo, así que mire el contenedor del corredor. Un sistema sano pero lento muestra ejecuciones moviéndose a través de `running`. Un `runners` vacío *y* cero todo normalmente significa que estás hablando con un evaluador que acaba de aparecer (o uno falso, ver más abajo).

Cuando PHP realmente no puede alcanzar `21680`, el cliente no se da por vencido ante el primer fallo. `\OmegaUp\Grader::curlRequest` **reintenta hasta 3 veces** con retroceso exponencial (`sleep(2^(n-1))`, limitado a 5 segundos), pero *solo* para errores que clasifica como transitorios: la lista actual en `isRetryableError` es `SSL connection timeout`, `HTTP/2 stream`, `SSL routines::unexpected eof`, `INTERNAL_ERROR`, `Connection timed out` y `Operation timed out`. Un `Connection refused` plano (el evaluador no escucha) **no** se puede volver a intentar y falla inmediatamente, mientras que un apretón de manos TLS inestable recibe tres disparos antes de que finalmente vea `Maximum retry attempts exceeded`. El presupuesto por intento también está limitado: `CURLOPT_CONNECTTIMEOUT => 5` y `CURLOPT_TIMEOUT => 30`, por lo que una sola llamada colgada no puede bloquear una página durante más de ~30 segundos. Si ve `Maximum retry attempts exceeded` en los registros, se trata de tres intentos transitorios fallidos (un clasificador intermitentemente en mal estado), no un error tipográfico de configuración, que fallaría en el primer intento.

Una vía de escape que vale la pena conocer para el trabajo de front-end: en realidad no se necesita un evaluador en vivo para desarrollar la mayor parte del sitio. La configuración de **`OMEGAUP_GRADER_FAKE`** (`false` predeterminado) hace que `\OmegaUp\Grader` cortocircuite cada llamada: `grade()` simplemente escribe la fuente en `/tmp/{guid}` y regresa, y `status()` devuelve un `GraderStatus` vacío pero bien formado. Si los envíos "tienen éxito" pero nunca producen un veredicto real y la cola siempre se lee vacía, verifique si está ejecutando el modo de calificación falsa antes de buscar un error de red que no existe.

---

## Referencia rápida de errores

Estas son las firmas que realmente verá, asignadas a la sección anterior que las explica. Cuando presente un problema, pegue el texto exacto: la cadena de error es lo que nos permite relacionar su síntoma con una causa conocida.

| Error que ves | Lo que realmente significa | Dónde buscar |
|---|---|---|
| `bind: address already in use` (`:8001`, `:13306`, `:21680`) | Otro proceso ya posee un puerto publicado | [La pila no arranca](#the-stack-wont-boot) |
| `Permission denied` creando `phpminiadmin` / bajo `stuff/venv/`, bucle de reinicio del contenedor | Repositorio clonado como raíz o `sudo docker compose`: el montaje de enlace es propiedad de la raíz | [No aparece (configuración)](../getting-started/development-setup.md#my-dev-environment-wont-come-up) |
| `SQLSTATE[HY000] [2002]` / `Can't connect to MySQL server` | Contenedor MySQL inactivo, aún inicializándose o host incorrecto | [No se puede acceder a MySQL](#mysql-is-not-reachable) |
| `Can't connect ... through socket '/var/run/mysqld/mysqld.sock'` | Cliente host que utiliza un socket Unix; MySQL es solo TCP en `13306` | [git push MySQL socket fix (configuración)](../getting-started/development-setup.md#git-push-fails-with-cant-connect-to-local-mysql-server) |
| `maximum statement execution time exceeded` | Consulta superó el contenedor `--max_execution_time=30000` (30s) | [No se puede acceder a MySQL](#mysql-is-not-reachable) |
| `Lock wait timeout exceeded` | Bloqueo de fila retenido más allá de `--lock_wait_timeout=10` (10 s), cancelado a propósito | [No se puede acceder a MySQL](#mysql-is-not-reachable) |
| Ediciones invisibles después de recargar | El navegador sirve para la compilación del paquete web, no para el código fuente; necesita una reconstrucción | [Los cambios no se muestran](#the-web-app-is-not-showing-my-changes) |
| Canal `Grader` `curl failed` @ `https://localhost:21680` | PHP no puede completar la llamada HTTPS al evaluador Go | [El clasificador es inalcanzable](#the-grader-is-unreachable) |
| `Maximum retry attempts exceeded` | 3 reintentos transitorios del evaluador, todos fallidos: clasificador intermitentemente en mal estado | [El clasificador es inalcanzable](#the-grader-is-unreachable) |

---

## Obtener más ayuda

Si nada de esto lo resuelve:

1. **Buscar problemas existentes** en [GitHub](https://github.com/omegaup/omegaup/issues): es posible que alguien ya haya encontrado la firma exacta.
2. **Pregunte en [Discord](https://discord.gg/gMEMX7Mrwe)** e incluya siempre el resultado del registro relevante; Es difícil ubicar un síntoma sin su texto de error.
3. **Presente un error** con los pasos de reproducción y el error textual; consulte [Obtener ayuda](../getting-started/getting-help.md) para saber qué constituye un buen informe.

## Documentación relacionada

- **[Configuración del entorno de desarrollo](../getting-started/development-setup.md)**: poner en marcha la pila y la solución de problemas en el momento de la configuración a los que remite esta página.
- **[Obtener ayuda](../getting-started/getting-help.md)**: dónde preguntar cuando estás atascado.
- **[Monitoreo](monitoring.md)** — observando la pila en producción.
- **[Configuración de Docker](docker-setup.md)**: cómo se conectan los contenedores.
