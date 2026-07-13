---
title: Configuración del entorno de desarrollo
description: Guía completa para configurar su entorno de desarrollo omegaUp local
icon: bootstrap/tools
---
# Configuración del entorno de desarrollo {#development-environment-setup}

Esta página lo guiará para configurar un omegaUp local completo (frontend, PHP API, MySQL y Go Grader/runner/gitserver) en su propia máquina con Docker. Toda la pila reside en un puñado de contenedores descritos por `docker-compose.yml`, por lo que no instala PHP 8.1, MySQL 8.0, Redis o RabbitMQ a mano; extraes imágenes prediseñadas y las abres. Ahora preferimos Docker para todos: la antigua máquina virtual Vagrant/VirtualBox suministrada desde [omegaup/deploy](https://github.com/omegaup/deploy) está obsoleta y ya no es la ruta admitida, por lo que si encuentra una página wiki que le indique que debe ir a `vagrant up`, omítala.

!!! consejo "Videotutorial"
    Si prefiere mirar que leer, tenemos un [videotutorial](http://www.youtube.com/watch?v=H1PG4Dvje88) que explica la misma configuración de principio a fin.

## Requisitos previos {#prerequisites}

Antes que nada, instale las dos piezas de herramientas Docker y Git:

- **Docker Engine** — [instalarlo](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository). Esto es lo que realmente hace funcionar los contenedores.
- **Docker Compose v2** — [instalar el complemento](https://docs.docker.com/compose/install/linux/#install-the-plugin-manually). Redactar es lo que dice `docker-compose.yml` y reúne toda la pila. Si todavía estás en Compose v1, puedes [migrar a v2](https://docs.docker.com/compose/install/linux/#install-using-the-repository); Tanto la ortografía `docker compose` (espacio) como `docker-compose` (guión) funcionan y esta guía las usa indistintamente.
- **Git**: para clonar el repositorio y porque todo el flujo de trabajo de contribución se basa en él.

!!! advertencia "¿Nuevo en Git?"
    Si aún no está seguro de Git, lea [este tutorial de Git](https://github.com/shekhargulati/git-the-missing-tutorial) antes de comenzar. Todo lo que ocurre después del clon (ramificaciones, solicitudes de extracción, mantener sincronizado a `main`) supone que puedes moverte en Git cómodamente.

### Linux: añádete al grupo `docker` {#linux-add-yourself-to-the-docker-group}

En Linux, ejecute esto una vez para poder invocar `docker` sin `sudo`:

```bash
sudo usermod -a -G docker $USER
```
Luego **cierre sesión y vuelva a iniciarla** para que la nueva membresía del grupo entre en vigencia. Esto importa más de lo que parece: si lo omite y comienza a buscar `sudo docker compose up`, el árbol del proyecto montado en enlace termina siendo propiedad de `root`, y el usuario no root del contenedor ya no puede escribir en él, lo que aparece más adelante como un desconcertante bucle de reinicio (consulte [Mi entorno de desarrollo no aparece](#my-dev-environment-wont-come-up)). Hágalo de la manera correcta una vez y evitará toda la clase de problema.

!!! nota "Windows: desarrollar dentro de WSL2"
    En Windows, ejecute todo a través de [WSL2](https://docs.docker.com/desktop/features/wsl) con la integración WSL de Docker Desktop habilitada y, esta es la parte que soporta la carga, **clone el repositorio en el sistema de archivos de Linux** (en algún lugar debajo de su inicio WSL, por ejemplo, `~/omegaup`), *no* bajo `/mnt/c/...`. Los montajes de enlace de Docker que cruzan el límite de Windows↔Linux son lentos y, lo que es peor, el `webpack --watch` dentro del contenedor pierde silenciosamente eventos de cambio de archivos en `/mnt/c`, por lo que sus ediciones nunca desencadenan una reconstrucción y usted se queda mirando la salida obsoleta. Mantener el pago en el lado de Linux es el reemplazo moderno del antiguo baile de sincronización de archivos WinSCP/Xming de la era Vagrant.

## Paso 1: Bifurcar y clonar {#step-1-fork-and-clone}

Primero bifurca [omegaup/omegaup](https://github.com/omegaup/omegaup) en GitHub (empujas a tu bifurcación, no al repositorio principal) y luego clonas tu bifurcación en un directorio vacío. La bandera `--recurse-submodules` es importante: varias dependencias de interfaz de terceros (`pagedown` para el editor Markdown, `iso-3166-2.js` para códigos de país, `mathjax` para renderizado matemático y más) viven en submódulos de Git, y la compilación se interrumpe sin ellos.

```bash
git clone --recurse-submodules https://github.com/YOURUSERNAME/omegaup
cd omegaup
```
Si clonó sin `--recurse-submodules`, o un submódulo parece vacío, insértelo explícitamente desde la raíz del repositorio:

```bash
git submodule update --init --recursive
```
## Paso 2: Abrir los contenedores {#step-2-bring-up-the-containers}

Desde la raíz del repositorio (`omegaup/`), extraiga las imágenes e inicie la pila:

```bash
docker-compose pull       # only needed the first time, or when the next command complains
docker-compose up --no-build
```
El `pull` toma las imágenes prediseñadas que Compose necesita: la interfaz PHP/nginx, MySQL 8.0, Redis, RabbitMQ y los servicios Go separados (`omegaup/backend`, `omegaup/runner`, `omegaup/gitserver`) que proporcionan el clasificador, el corredor y el almacenamiento de problemas. Sólo necesita volver a tirar cuando configura por primera vez o cuando `docker-compose up` se queja de que falta una imagen o está obsoleta. El indicador `--no-build` le indica a Compose que ejecute esas imágenes prediseñadas tal como están en lugar de reconstruirlas desde cero, que es lo que mantiene el inicio en minutos en lugar de una pausa para tomar café muy larga.

**El primer arranque tarda entre 2 y 10 minutos.** Después de esa espera, el contenedor de la interfaz ejecuta Webpack para compilar toda la interfaz de Vue 2.7 + TypeScript, MySQL se está inicializando y el calificador está esperando en la base de datos (`wait-for-it mysql:13306`). Lo que indica que realmente está listo es un volcado del módulo Webpack similar a este:

```
frontend_1     | Child frontend:
frontend_1     |        1550 modules
frontend_1     |     Child HtmlWebpackCompiler:
frontend_1     |            1 module
frontend_1     | Child style:
frontend_1     |        1 module
frontend_1     |     Child extract-text-webpack-plugin node_modules/extract-text-webpack-plugin/dist node_modules/css-loader/dist/cjs.js!node_modules/sass-loader/dist/cjs.js!frontend/www/sass/main.scss:
frontend_1     |            2 modules
frontend_1     | Child grader:
frontend_1     |        1131 modules
frontend_1     |     Child vs/editor/editor:
frontend_1     |            36 modules
frontend_1     |     Child vs/language/typescript/tsWorker:
frontend_1     |            41 modules
```
Una vez que vea eso, la interfaz habrá terminado su construcción y el sitio estará activo. Los recuentos exactos del módulo varían a medida que crece la interfaz; trátelos como una señal de "hemos terminado de compilar", no como una suma de verificación.

En ejecuciones posteriores, puede omitir el `pull` y simplemente iniciar la pila:

```bash
docker compose up --no-build
```
## Paso 3: Abra su instancia local {#step-3-open-your-local-instance}

Con los contenedores en funcionamiento, tu omegaUp local está en:

**[http://localhost:8001](http://localhost:8001)**

Ese es el puerto `8001`, publicado desde el contenedor frontend en `docker-compose.yml`. Tenga en cuenta que es `http` simple; consulte [la solución de redireccionamiento HTTPS del navegador](#my-browser-keeps-forcing-https) si su navegador insiste en reescribirlo.

## Paso 4: Obtenga un caparazón dentro del contenedor {#step-4-get-a-shell-inside-the-container}

Casi todos los comandos de desarrollo (ejecutar pruebas, invocar scripts `stuff/`, hurgar en la base de datos) se ejecutan *dentro* del contenedor frontend, porque ahí es donde realmente residen PHP 8.1, Node, Yarn y las herramientas. Abra un shell con cualquiera de estos (son equivalentes):

```bash
docker compose exec frontend /bin/bash
# or, by container name:
docker exec -it omegaup-frontend-1 /bin/bash
```
El nombre exacto del contenedor depende de su versión de Compose: la versión 2 lo nombra `omegaup-frontend-1` (guiones), el `docker-compose` anterior usaba `omegaup_frontend_1` (guiones bajos). Si no está seguro de cuál tiene, `docker compose ps` enumera los nombres reales. Dentro del contenedor, el código base está montado en **`/opt/omegaup`**: los mismos archivos que editas en tu host, por lo que un guardado en tu máquina es visible instantáneamente en el contenedor.

## Cuentas de Desarrollo {#development-accounts}

Su nueva instalación viene con dos cuentas ya configuradas, por lo que puede iniciar sesión inmediatamente sin registrar nada:

- **`omegaup`** / contraseña **`omegaup`**: un usuario con privilegios de administrador de sistemas. Úselo cuando necesite tocar la interfaz de usuario solo para administradores.
- **`user`** / contraseña **`user`**: un usuario normal y corriente, para probar la experiencia de usuario normal.

Además de eso, el conjunto de pruebas genera una lista estable de cuentas en las que puede iniciar sesión. La contraseña es siempre idéntica al nombre de usuario, lo que los hace fáciles de recordar:

| Nombre de usuario | Contraseña |
| -- | -- |
| `test_user_0` | `test_user_0` |
| `test_user_1` | `test_user_1` |
| `test_user_2` | `test_user_2` |
| `test_user_3` | `test_user_3` |
| `test_user_4` | `test_user_4` |
| `test_user_5` | `test_user_5` |
| `test_user_6` | `test_user_6` |
| `test_user_7` | `test_user_7` |
| `test_user_8` | `test_user_8` |
| `test_user_9` | `test_user_9` |
| `course_test_user_0` | `course_test_user_0` |
| `course_test_user_1` | `course_test_user_1` |
| `course_test_user_2` | `course_test_user_2` |

**Siéntete libre de crear tantos usuarios como necesites** para probar tus cambios. En el modo de desarrollo, la verificación de correo electrónico está desactivada, por lo que cualquier dirección ficticia funciona; nunca tendrás que revisar una bandeja de entrada para activar una cuenta.

## Estructura de la base de código {#codebase-structure}

El código omegaUp vive en `/opt/omegaup` dentro del contenedor (y en su clon en el host; es el mismo árbol montado en enlace). Estos son los directorios en los que trabajamos activamente en el día a día:

- **[`frontend/server/src/Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers)**: los controladores, con espacio de nombres `\OmegaUp\Controllers`, que contienen la lógica empresarial y exponen la API del servidor. Cada método estático `apiXxx` es un punto final API; por ejemplo, `\OmegaUp\Controllers\Run::apiCreate` (en [`Run.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Run.php)) es lo que maneja un envío. Tenga en cuenta que la clase es `Run`, no `RunController`; los controladores omegaUp eliminan el sufijo `Controller`.
- **[`frontend/server/src/DAO/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/DAO)**: la capa de acceso a datos. Está dividido a propósito: las clases base abstractas generadas automáticamente en `DAO/Base/` llevan el SQL sin formato, los objetos de valor simples en `DAO/VO/` reflejan las filas de la base de datos y los contenedores escritos a mano directamente en `DAO/` agregan las consultas que los controladores realmente llaman. Editas los contenedores y los VO, no las bases generadas.
- **[`frontend/server/src/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src)**: el resto de las bibliotecas y utilidades del servidor, incluido `ApiCaller.php` (el despachador de solicitudes) y `Grader.php` (el cliente HTTP ligero que se comunica con el evaluador Go).
- **[`frontend/templates/`](https://github.com/omegaup/omegaup/tree/main/frontend/templates)**: el shell HTML renderizado por el servidor más los archivos de internacionalización para inglés, español y portugués. Aquí hay una única plantilla, `template.tpl`, y a pesar de la extensión `.tpl` es **Twig 3**, no Smarty; Smarty ya no está. Sus etiquetas personalizadas (`{% entrypoint %}`, `{% jsInclude %}`) se implementan mediante nuestras propias extensiones Twig en `frontend/server/src/Template/`, y todo lo que hacen es iniciar una aplicación Vue y entregarle una carga útil JSON.
- **[`frontend/www/`](https://github.com/omegaup/omegaup/tree/main/frontend/www)**: toda la aplicación orientada al navegador. La interfaz de usuario de cada página es un componente de archivo único de Vue 2.7; los componentes se encuentran bajo `frontend/www/js/omegaup/components/`, y el cliente API escrito (`api.ts`, `api_types.ts`) se genera a partir de los controladores PHP mediante `frontend/server/cmd/APITool.php`; no edite manualmente esos dos, regénelos.

Una cosa que hace tropezar a la gente: el **nivelador, corredor, emisora ​​y minijail sandbox no están en este repositorio**. Son servicios Go separados en [github.com/omegaup/quark](https://github.com/omegaup/quark) (y el almacenamiento de problemas se encuentra en [github.com/omegaup/gitserver](https://github.com/omegaup/gitserver)). Docker los ejecuta como archivos binarios prediseñados, y el backend de PHP solo *habla* con el evaluador a través de HTTP a través de `\OmegaUp\Grader`, en `OMEGAUP_GRADER_URL` (`https://localhost:21680` predeterminado). Si está buscando un error de calificación, ese es el repositorio al que debe indicarle su editor, no este.

Para obtener un recorrido más profundo, consulte la [Descripción general de la arquitectura](../architecture/index.md) y la [Arquitectura frontend](../architecture/frontend.md). El flujo de trabajo de solicitud de rama y extracción se encuentra en [Contribuir](contributing.md).

## Edición con Visual Studio Code {#editing-with-visual-studio-code}

Puede editar en su host con [Visual Studio Code](https://code.visualstudio.com/) mientras la pila sigue ejecutándose en Docker. Debido a que su clon está montado en `/opt/omegaup`, guardar en el host es guardar en el contenedor: la recarga en caliente y el paquete web dentro del contenedor lo recogen sin ningún paso de copia, que es exactamente la fricción que existía para solucionar la antigua configuración Vagrant-plus-WinSCP y ya no es necesaria.

Dos formas de trabajar, dependiendo de cuánto desee que las herramientas propias de VS Code (PHP IntelliSense, el terminal integrado, extensiones) se ejecuten en el sistema de archivos del contenedor:

1. **Edite en el host, ejecútelo en Docker.** Simplemente abra su clon como una carpeta y edítelo normalmente. Camino más sencillo; tus partidas guardadas fluyen hacia el contenedor a través del soporte de enlace.
2. **Adjunte VS Code al contenedor en ejecución.** Instale la extensión [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) (o la extensión [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)). Con la pila arriba (`docker compose up --no-build`), abra la paleta de comandos y seleccione **Adjuntar al contenedor en ejecución**, elija el contenedor de interfaz (llamado `omegaup-frontend-1`; confirme con `docker compose ps`), luego **Archivo → Abrir carpeta** en **`/opt/omegaup`**. Ahora la terminal y los servidores de idiomas de VS Code se ejecutan *dentro* del contenedor, con el mismo PHP 8.1 y Nodo que usa la aplicación.

Agregue las extensiones PHP, Vue y ESLint según lo requieran los archivos que toque.

## GitHub OAuth (local "Iniciar sesión con GitHub") {#github-oauth-local-sign-in-with-github}

Para que el botón **Iniciar sesión con GitHub** funcione en **`http://localhost:8001/`**, registre una aplicación OAuth con GitHub y entregue sus credenciales a su configuración local.

### 1. Cree la aplicación OAuth en GitHub {#1-create-the-oauth-app-on-github}

Abra [Configuración de desarrollador de GitHub](https://github.com/settings/developers), vaya a **Aplicaciones OAuth → Nueva aplicación OAuth** y configure:

- **Nombre de la aplicación**: cualquier cosa, p.e. `omegaUp local`
- **URL de la página de inicio**: `http://localhost:8001/`
- **URL de devolución de llamada de autorización**: `http://localhost:8001/login?third_party_login=github`

Regístrelo, copie el **ID de cliente**, luego genere y copie el **Secreto de cliente**: GitHub solo muestra el secreto una vez, así que consígalo ahora.

### 2. Configurar omegaUp localmente {#2-configure-omegaup-locally}

Coloque las credenciales en **`frontend/server/config.php`**, el archivo de anulaciones locales (créelo si no existe). Este archivo es solo para *su* máquina: nunca lo confirme y nunca coloque secretos en el `config.default.php` controlado por versión.

```php
<?php
define('OMEGAUP_GITHUB_CLIENT_ID', 'your_real_client_id_here');
define('OMEGAUP_GITHUB_CLIENT_SECRET', 'your_real_client_secret_here');
```
Por lo general, no es necesario reiniciar Compose por completo para que un nuevo PHP `define` surta efecto, pero si el botón permanece atenuado, reinicie el contenedor de interfaz una vez.

!!! error "Nunca confirmes secretos de OAuth"
    Revierta o excluya `config.php` antes de enviarlo, y mantenga su ID de cliente/secreto en un administrador de contraseñas; si el contenedor se vuelve a crear y lleva `config.php` consigo, los querrá tener a mano. Si el botón de inicio de sesión permanece inactivo, la ID del cliente falta o es incorrecta en `config.php`; Si cambia de host o puerto, actualice la URL de devolución de llamada en la aplicación GitHub OAuth para que coincida, o la redirección fallará.

Consulte [Seguridad → OAuth](../architecture/security.md#oauth2-and-third-party-login) para saber cómo encaja el inicio de sesión de terceros en la plataforma.

## Solución de problemas {#troubleshooting}

Estos son los problemas que la gente realmente enfrenta, aproximadamente en el orden en que los enfrentan: primero el error sin procesar, luego lo que significa y luego la solución.

### ¡La aplicación web no muestra mis cambios! {#the-web-app-is-not-showing-my-changes}

Editó un archivo `.vue` o `.ts`, lo guardó, lo volvió a cargar y el navegador muestra el archivo anterior. La interfaz se sirve desde una *compilación* de paquete web, por lo que una edición no creada es invisible sin importar cuántas veces se actualice. Reconstrúyalo desde el interior del contenedor:

```bash
docker compose exec frontend /bin/bash
cd /opt/omegaup && yarn run dev
```
`yarn run dev` ejecuta Webpack una vez en el frontend; Si está iterando y no desea volver a ejecutarlo manualmente después de cada guardado, use `yarn dev:watch` en su lugar, que observa el árbol y lo reconstruye cuando cambia. (En Windows, esta es exactamente la razón por la que su pago debe residir en el sistema de archivos WSL2 de Linux y no en `/mnt/c`; el observador omite eventos de cambio a través de ese límite). Si aún no se actualiza después de una compilación exitosa, asegúrese de que los contenedores realmente se estén ejecutando (`docker compose up --no-build`) y, en su defecto, pregunte en nuestros [canales de comunicación](getting-help.md).

### Mi entorno de desarrollo no aparece :( {#my-dev-environment-wont-come-up}

**Síntomas**: los registros muestran `Permission denied` mientras se crea `phpminiadmin` o se escribe en `stuff/venv/`, el contenedor `developer-environment` sale y se reinicia en un bucle, y el sitio nunca funciona en `http://localhost:8001`.

**Causa**: el repositorio se clonó como **raíz**, o `docker compose` se ejecutó con `sudo`, por lo que el directorio del proyecto es propiedad de `root`. El montaje de enlace asigna su directorio de host a `/opt/omegaup`, y un árbol de propiedad raíz impide que el usuario no raíz del contenedor escriba en él, por lo que falla, muere y Compose lo reinicia para siempre.

**Solución**: no intentes "reparar" el árbol de propiedad raíz en su lugar; no vale la pena luchar. Como usuario normal, clone nuevamente en su directorio de inicio, asegúrese de haberse agregado al grupo `docker` (`sudo usermod -a -G docker $USER`, luego cierre sesión y vuelva a iniciarla) y ejecute **`docker compose` sin `sudo`**. Nunca `sudo git clone`.

### Mi navegador sigue forzando HTTPS {#my-browser-keeps-forcing-https}

Si su navegador reescribe `http://localhost:8001` a `https://` y luego no puede conectarse, ese es el comportamiento HSTS/HTTPS forzado del navegador, no omegaUp: la instancia local solo habla HTTP simple. Deshabilite la política HTTPS forzada para `localhost` siguiendo [esta guía](https://hmheng.medium.com/exclude-localhost-from-chrome-chromium-browsers-forced-https-redirection-642c8befa9b).

---

### `git push` falla con un rastreo de MySQL {#git-push-fails-with-a-mysql-traceback}

Cuando presiona, los enlaces de políticas de omegaUp ejecutan `stuff/policy-tool.py`, que necesita consultar la base de datos. En muchas máquinas, el primer impulso explota con un largo rastreo de Python que termina en:

```
Traceback (most recent call last):
  File "/home/ubuntu/dev/omegaup/stuff/policy-tool.py", line 124, in <module>
    main()
  ...
  File "/home/ubuntu/dev/omegaup/stuff/database_utils.py", line 75, in mysql
    return subprocess.check_output(args, universal_newlines=True)
  ...
FileNotFoundError: [Errno 2] No such file or directory: '/usr/bin/mysql'
error: failed to push some refs to 'https://github.com/user/omegaup'
```
Ese `FileNotFoundError: ... '/usr/bin/mysql'` significa que no hay ningún binario de cliente `mysql` en la máquina que ejecuta el enlace. El problema: `git push` se ejecuta en su **host**, fuera del contenedor, por lo que aunque MySQL 8.0 se ejecuta felizmente *en* Docker, el host no tiene un cliente con quien hablar. Instale el cliente **fuera del contenedor**:

```bash
sudo apt-get install mysql-client
```
### `git push` falla con "No se puede conectar al servidor MySQL local" {#git-push-fails-with-cant-connect-to-local-mysql-server}

A veces, el cliente se instala pero la inserción aún falla, esta vez con un error de socket antes del mismo rastreo:

```
mysql: [Warning] Using a password on the command line interface can be insecure.
ERROR 2002 (HY000): Can't connect to local MySQL server through socket '/var/run/mysqld/mysqld.sock' (2)
Traceback (most recent call last):
  File "/home/ubuntu/dev/omegaup/stuff/policy-tool.py", line 124, in <module>
    main()
  ...
subprocess.CalledProcessError: Command '['/usr/bin/mysql', '--user=root', '--password=omegaup', 'omegaup', '-NBe', 'SELECT COUNT(*) FROM `PrivacyStatements` WHERE ...']' returned non-zero exit status 1.
error: failed to push some refs to 'https://github.com/user/omegaup'
```
`Can't connect ... through socket '/var/run/mysqld/mysqld.sock'` es el regalo: el cliente está predeterminado en un **socket Unix local**, pero su MySQL no es local: está en un contenedor, al que solo se puede acceder a través de **TCP en el puerto 13306** (publicado desde el contenedor en `docker-compose.yml`). La solución es entregarle al cliente host una configuración TCP que apunte a ese puerto, luego vincularlo simbólicamente como el `.my.cnf` predeterminado, el gancho dice:

```bash
cat > ~/.mysql.docker.cnf <<EOF
[client]
port=13306
host=127.0.0.1
protocol=tcp
user=root
password=omegaup
EOF
ln -sf ~/.mysql.docker.cnf .my.cnf
```
Después de esto, la herramienta de políticas se conecta a través de TCP al MySQL Dockerizado y se realiza el envío. Este es el mismo patrón de configuración TCP documentado en la [Guía de contribución](contributing.md).

---

### Un script `stuff/` produce errores {#a-stuff-script-errors-out}

Si ejecuta uno de los scripts `stuff/` directamente en su host y obtiene el mismo rastreo de `/usr/bin/mysql` que se muestra arriba, la causa habitual es que **lo ejecutó fuera del contenedor**. La mayoría de esos scripts asumen el acceso a las herramientas y a la base de datos que solo existen dentro del contenedor frontend. Abra un shell en el contenedor (`docker compose exec frontend /bin/bash`) y ejecútelo allí. (Los enlaces `git push` anteriores son la excepción deliberada: estos *se* ejecutan en el host, por lo que necesitan el cliente MySQL del lado del host y la configuración TCP).

### Faltan módulos de terceros {#missing-third-party-modules}

Si la compilación o las pruebas fallan debido a que faltan módulos en `frontend/www/third_party/js/`, sus submódulos no están desprotegidos. Tirarlos hacia adentro:

```bash
git submodule update --init --recursive
```
### Errores de nodo/hilo después de realizar grandes cambios {#node-yarn-errors-after-pulling-big-changes}

Si Node o Yarn comienzan a arrojar errores justo después de generar un gran aumento de dependencia, la imagen de interfaz prediseñada puede no estar sincronizada con el nuevo `package.json`. Reconstrúyelo:

```bash
docker compose build frontend
docker compose up
```
---

Si encuentra algo que no se cubre aquí, presente un problema en [omegaup/deploy/issues](https://github.com/omegaup/deploy/issues) con sus pasos de reproducción y el mensaje de error exacto; el texto de error es lo que nos permite relacionar su síntoma con uno conocido.

## Próximos pasos {#next-steps}

- **[Más información sobre cómo contribuir](contributing.md)**: sucursales, controles remotos y envío de una solicitud de extracción.
- **[Revise las pautas de codificación](../development/coding-guidelines.md)**: las convenciones que respetamos el código.
- **[Explora la arquitectura](../architecture/index.md)**: cómo encajan las piezas que acabas de iniciar.

## Obteniendo ayuda {#getting-help}

Si estás atrapado en algo que esta página no cubre:

1. Consulte la [Guía para obtener ayuda](getting-help.md).
2. Busque los [problemas de GitHub] existentes (https://github.com/omegaup/deploy/issues).
3. Pregunta en nuestro [servidor de Discord](https://discord.gg/gMEMX7Mrwe).

---

**¿Listo para comenzar a codificar?** Dirígete a la [Guía de contribución](contributing.md) para enviar tu primera solicitud de extracción.
