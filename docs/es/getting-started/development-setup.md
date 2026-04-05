---
title: Configuración del entorno de desarrollo
description: Guía completa para configurar su entorno de desarrollo omegaUp local
icon: bootstrap/tools
---
# Configuración del entorno de desarrollo

Esta guía lo guiará en la configuración de un entorno de desarrollo local para omegaUp usando Docker.

!!! consejo "Videotutorial"
    Tenemos un [video tutorial](http://www.youtube.com/watch?v=H1PG4Dvje88) que demuestra visualmente el proceso de configuración.

## Requisitos previos

Antes de comenzar, asegúrese de tener instalado lo siguiente:

- **Docker Engine**: [Instalar Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
- **Docker Compose 2**: [Instalar Docker Compose](https://docs.docker.com/compose/install/linux/#install-the-plugin-manually)
- **Git**: Para clonar el repositorio

!!! nota "Usuarios de WSL"
    Si está utilizando WSL (Subsistema de Windows para Linux), siga la [guía oficial de integración de WSL de Docker Desktop] (https://docs.docker.com/desktop/features/wsl).

### Configuración específica de Linux

Si está ejecutando Linux, después de instalar Docker, agregue su usuario al grupo de Docker:

```bash
sudo usermod -a -G docker $USER
```
Cierra sesión y vuelve a iniciarla para que los cambios surtan efecto.

!!! advertencia "Git Knowledge"
    Si no está seguro de usar Git, le recomendamos leer [este tutorial de Git](https://github.com/shekhargulati/git-the-missing-tutorial) primero.

## Paso 1: bifurcar y clonar el repositorio

1. **Bifurcar el repositorio**: visita [github.com/omegaup/omegaup](https://github.com/omegaup/omegaup) y haz clic en el botón "Bifurcar"

2. **Clona tu tenedor**:
   ```bash
   git clone --recurse-submodules https://github.com/YOURUSERNAME/omegaup
   cd omegaup
   ```
3. **Inicializar submódulos** (si es necesario):
   ```bash
   git submodule update --init --recursive
   ```
## Paso 2: Iniciar contenedores Docker

### Configuración por primera vez

En su primera ejecución, extraiga las imágenes de Docker e inicie los contenedores:

```bash
docker-compose pull
docker-compose up --no-build
```
Esto tardará entre 2 y 10 minutos. Sabrá que está listo cuando vea un resultado similar a:

```
frontend_1     | Child frontend:
frontend_1     |        1550 modules
frontend_1     |     Child HtmlWebpackCompiler:
frontend_1     |            1 module
...
```
### Ejecuciones posteriores

Después de la primera ejecución, puedes iniciar contenedores más rápido con:

```bash
docker compose up --no-build
```
La bandera `--no-build` evita reconstruir todo, acelerando significativamente el inicio.

!!! nota "`docker compose` frente a `docker-compose`"
    Docker Compose V2 usa el comando `docker compose` (con espacio). Instalaciones antiguas pueden tener el binario `docker-compose`; ambos sirven si tu Docker lo soporta. Esta guía usa `docker compose`.

## Paso 3: acceda a su instancia local

Una vez que los contenedores se estén ejecutando, acceda a su instancia local de omegaUp en:

**http://localhost:8001**

## Paso 4: Acceder a la consola del contenedor

Para ejecutar comandos dentro del contenedor:

```bash
docker exec -it omegaup-frontend-1 /bin/bash
```
El código base se encuentra en `/opt/omegaup` dentro del contenedor.

## Cuentas de Desarrollo

Su instalación local incluye cuentas preconfiguradas:

### Cuenta de administrador
- **Nombre de usuario**: `omegaup`
- **Contraseña**: `omegaup`
- **Rol**: Administrador (privilegios de administrador de sistemas)

### Cuenta de usuario habitual
- **Nombre de usuario**: `user`
- **Contraseña**: `user`
- **Rol**: Usuario habitual

### Cuentas de prueba

Para fines de prueba, puede utilizar estas cuentas de prueba:

| Nombre de usuario | Contraseña |
|----------|----------|
| `test_user_0` | `test_user_0` |
| `test_user_1` | `test_user_1` |
| ... | ... |
| `course_test_user_0` | `course_test_user_0` |

!!! información "Verificación por correo electrónico"
    En el modo de desarrollo, la verificación de correo electrónico está deshabilitada. Puede utilizar direcciones de correo electrónico ficticias al crear cuentas nuevas.

## Ejecución de pruebas localmente

Si desea ejecutar pruebas de JavaScript/TypeScript fuera de Docker:

### Requisitos previos

1. **Node.js**: Versión 16 o superior
2. **Yarn**: Administrador de paquetes

### Pasos de configuración

1. **Inicializar submódulos de Git**:
   ```bash
   git submodule update --init --recursive
   ```
Esta descarga requiere dependencias:
   - `pagedown` - Editor de rebajas
   - `iso-3166-2.js` - Códigos de país/región
   - `csv.js` - Análisis CSV
   - `mathjax` - Representación matemática

2. **Instalar dependencias**:
   ```bash
   yarn install
   ```
3. **Ejecutar pruebas**:
   ```bash
   yarn test
   ```
### Inicio rápido (clon nuevo)

Para un clon nuevo, use este único comando:

```bash
git clone --recurse-submodules https://github.com/YOURUSERNAME/omegaup
cd omegaup
yarn install
yarn test
```
## Estructura de la base de código

El código base de omegaUp está organizado de la siguiente manera:

```
omegaup/
├── frontend/
│   ├── server/
│   │   └── src/
│   │       ├── Controllers/    # Business logic & API endpoints
│   │       ├── DAO/            # Data Access Objects
│   │       └── libs/           # Libraries & utilities
│   ├── www/                    # Frontend assets (TypeScript, Vue.js)
│   ├── templates/              # Smarty templates & i18n files
│   ├── database/               # Database migrations
│   └── tests/                  # Test files
```
Para más detalle, consulte la [Descripción general de la arquitectura](../architecture/index.md) y la [arquitectura de frontend](../architecture/frontend.md).

El flujo de contribución (ramas, PR, remotos) está en [Contribuyendo](contributing.md).

## Visual Studio Code con Docker

Puede editar desde el anfitrión con [Visual Studio Code](https://code.visualstudio.com/) mientras Docker ejecuta el stack.

### Extensiones recomendadas

- [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) o [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) para adjuntarse a un contenedor en ejecución
- Extensiones PHP, Vue y ESLint según los archivos que modifique

### Adjuntarse al contenedor frontend

1. Inicie el entorno: `docker compose up --no-build` (o `docker compose up` la primera vez).
2. En VS Code, use **Attach to Running Container** y elija el contenedor del frontend (a menudo `omegaup-frontend-1`; el nombre exacto aparece en `docker compose ps`).
3. En la ventana adjunta, abra la carpeta **`/opt/omegaup`** (el proyecto montado dentro del contenedor).

También puede editar el clon en el anfitrión: el mismo árbol se monta en `/opt/omegaup` y webpack dentro del contenedor recoge los cambios.

!!! consejo "Flujo heredado con Vagrant / SSH"
    Si usa una VM con [omegaup/deploy](https://github.com/omegaup/deploy), puede usar **Remote - SSH** con la salida de `vagrant ssh-config`, como en la [documentación de VS Code Remote SSH](https://code.visualstudio.com/docs/remote/ssh). Para nuevos colaboradores, prefiera Docker cuando sea posible.

## GitHub OAuth (inicio de sesión local con GitHub)

### 1. Crear la OAuth App en GitHub

1. Abra [Configuración para desarrolladores de GitHub](https://github.com/settings/developers).
2. **OAuth Apps → New OAuth App**.
3. Indique:
   - **Homepage URL**: `http://localhost:8001/`
   - **Authorization callback URL**: `http://localhost:8001/login?third_party_login=github`
4. Registre la aplicación y copie el **Client ID** y el **Client Secret**.

### 2. Configurar omegaUp

1. Cree o edite **`frontend/server/config.php`** (solo local; no suba secretos a git).
2. Añada:

```php
<?php
define('OMEGAUP_GITHUB_CLIENT_ID', 'your_real_client_id_here');
define('OMEGAUP_GITHUB_CLIENT_SECRET', 'your_real_client_secret_here');
```

3. Si el botón sigue desactivado, reinicie el contenedor frontend una vez.

!!! fracaso "Nunca suba secretos OAuth"
    No confíe `config.php` con credenciales. No edite `config.default.php` para secretos. Guarde ID y secreto fuera del repositorio.

Véase también [Seguridad → integración OAuth](../architecture/security.md#oauth-integration).

## Problemas comunes

### La aplicación web no muestra mis cambios

Asegúrese de que Docker se esté ejecutando:

```bash
docker compose up --no-build
```
Si el problema persiste pide ayuda en los canales de comunicación de omegaUp.

### El navegador redirige HTTP a HTTPS

Si su navegador sigue cambiando `http` a `https` para localhost, puede desactivar las políticas de seguridad para `localhost`. [Consulte esta guía](https://hmheng.medium.com/exclude-localhost-from-chrome-chromium-browsers-forced-https-redirection-642c8befa9b).

### Error de MySQL no encontrado

Si encuentra este error al ingresar a GitHub:

```
FileNotFoundError: [Errno 2] No such file or directory: '/usr/bin/mysql'
```
Instale el cliente MySQL fuera del contenedor:

```bash
sudo apt-get install mysql-client mysql-server
```
Luego configure la conexión MySQL:

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
### Error de conexión MySQL

Si MySQL está instalado pero aparece un error de socket local, los hooks que se ejecutan en `git push` esperan un cliente **TCP** hacia el puerto Docker **13306**. Use el bloque `~/.mysql.docker.cnf` y el enlace `.my.cnf` descritos en [Contribuyendo → Configuraciones adicionales](contributing.md).

### Submódulos Git / JS de terceros

Si faltan módulos bajo `frontend/www/third_party/js/`:

```bash
git submodule update --init --recursive
```

### Reconstruir la imagen frontend

Tras cambios grandes de dependencias:

```bash
docker compose build frontend
docker compose up
```

### Permisos: `phpminiadmin`, `venv` o reinicios en bucle

**Causa**: clon o `docker compose` como **root** o carpeta del proyecto propiedad de root.

**Solución**: como usuario normal, vuelva a clonar bajo su home, pertenezca al grupo `docker` y ejecute `docker compose` **sin** `sudo`. No use `sudo git clone`.

### Errores de `policy-tool` / `mysql` al hacer push

Instale el cliente MySQL en el **anfitrión** y configure TCP como arriba. Para el entorno de despliegue, abra un issue en [omegaup/deploy](https://github.com/omegaup/deploy/issues).

## Próximos pasos

- **[Aprenda cómo contribuir](contributing.md)** - Cree sucursales y envíe solicitudes de extracción
- **[Revisar las pautas de codificación](../development/coding-guidelines.md)** - Comprenda nuestros estándares de codificación
- **[Explora la arquitectura](../architecture/index.md)** - Entiende cómo funciona omegaUp

## Obtener ayuda

Si encuentra problemas que no se tratan aquí:

1. Consulte la [Guía para obtener ayuda](getting-help.md)
2. Busque [issues existentes en GitHub](https://github.com/omegaup/deploy/issues)
3. Pregunte en nuestro [servidor de Discord](https://discord.gg/gMEMX7Mrwe)

---

**¿Listo para comenzar a codificar?** Dirígete a la [Guía de contribución](contributing.md) para saber cómo enviar tu primera solicitud de extracción.
