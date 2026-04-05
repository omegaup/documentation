---
title: Contribuyendo a omegaUp
description: Aprenda cómo contribuir con código a omegaUp a través de solicitudes de extracción
icon: bootstrap/code-tags
---
# Contribuyendo a omegaUp

¡Gracias por su interés en contribuir con omegaUp! Esta guía lo guiará a través del proceso de envío de su primera contribución.

## Descripción general del proceso de desarrollo

La rama `main` en tu bifurcación siempre debe mantenerse actualizada con la rama `main` del repositorio omegaUp. **Nunca te comprometas directamente con `main`**. En su lugar, cree una rama separada para cada cambio que planee enviar mediante una solicitud de extracción.

## Requisitos previos

Antes de comenzar:

1. ✅ [Configura tu entorno de desarrollo](development-setup.md)
2. ✅ Lea las [Pautas de codificación](../development/coding-guidelines.md)
3. ✅ Comprenda [cómo obtener ayuda](getting-help.md) si se queda atascado

## Requisito de asignación de problemas

!!! importante "Requerido antes de abrir PR"
    Cada solicitud de extracción **debe** estar vinculada a un problema de GitHub existente que le esté **asignado**.

### Pasos para asignar el problema

1. **Buscar o crear un problema**:
   - Examinar [problemas existentes](https://github.com/omegaup/omegaup/issues)
   - O [crear una nueva edición](https://github.com/omegaup/omegaup/issues/new) describiendo la corrección de errores o la característica

2. **Expresar interés**:
   - Comentar el tema expresando su interés en trabajar en él.
   - Espere a que un mantenedor se lo asigne.

3. **Empiece a trabajar**:
   - Una vez asignado, puedes crear tu sucursal y comenzar a codificar.
   - Haga referencia al problema en su descripción de PR usando: `Fixes #1234` o `Closes #1234`

!!! fracaso "Las relaciones públicas fracasarán sin la asignación de problemas"
    Si su PR no está vinculado a un problema asignado, las comprobaciones automáticas fallarán y su PR no se podrá fusionar.

### Asignación automática (bot)

Este repositorio usa [`takanome-dev/assign-issue-action`](https://github.com/takanome-dev/assign-issue-action) para que puedas reclamar trabajo sin depender siempre de una asignación manual.

**Comandos** (comenta en el issue de GitHub):

- `/assign` — te asigna el issue.
- `/unassign` — te desasigna del issue.

El bot también puede sugerir la asignación si tu comentario muestra interés en trabajar en el issue.

**Límites y plazos**

- Como máximo **5** issues asignados a la vez (en todo el repositorio).
- Tras la asignación debes **abrir un pull request** (vale un PR en **borrador**) en un plazo de **7 días**.
- A mitad de ese plazo (~3.5 días) se publica un recordatorio.
- Si no hay PR al día 7, se te **desasigna automáticamente** y **no podrás volver a autoasignarte** en ese issue; pide ayuda a un mantenedor si aún lo necesitas.

**Autores de issues con experiencia**

- Si **tú creaste el issue** y tienes al menos **10 PR fusionados** en este repositorio, puedes autoasignarte **sin** que cuente el límite de 5 para issues **que tú abriste**.
- La regla de los **7 días** (abrir PR tras la asignación) sigue igual.
- En issues **creados por otras personas**, el límite habitual de **5** asignaciones activas aplica.

**Consejos**

- Escribe `/assign` y abre pronto un borrador de PR para no perder la asignación.
- Usa `/unassign` si no puedes continuar.
- Si necesitas más tiempo, pide a un mantenedor la etiqueta **`📌 Pinned`** en el issue.

## Configuración de su horquilla y controles remotos

Solo necesitas hacer esto una vez. Los nombres siguen el **flujo habitual de forks en GitHub**:

- **`origin`** — tu fork (`https://github.com/YOURUSERNAME/omegaup.git`): donde **empujas** ramas y desde donde abres pull requests.
- **`upstream`** — el repositorio canónico (`https://github.com/omegaup/omegaup.git`): de donde **traes** los cambios oficiales.

Algunas páginas antiguas de la wiki de omegaUp usaban los nombres al revés; en este sitio de documentación usamos la convención anterior.

### 1. Bifurcar el repositorio

Visite [github.com/omegaup/omegaup](https://github.com/omegaup/omegaup) y haga clic en el botón "Bifurcar".

### 2. Clona tu bifurcación

```bash
git clone https://github.com/YOURUSERNAME/omegaup.git
cd omegaup
```

### 3. Añade `upstream` y comprueba los remotos

El clon ya tiene **`origin`** apuntando a tu fork. Añade **`upstream`** una vez:

```bash
git remote add upstream https://github.com/omegaup/omegaup.git
git remote -v
```

Deberías ver:

```
origin     https://github.com/YOURUSERNAME/omegaup.git (fetch)
origin     https://github.com/YOURUSERNAME/omegaup.git (push)
upstream   https://github.com/omegaup/omegaup.git (fetch)
upstream   https://github.com/omegaup/omegaup.git (push)
```

Si `origin` es incorrecto, corrígelo con:

```bash
git remote set-url origin https://github.com/YOURUSERNAME/omegaup.git
```

## Actualizando tu sucursal principal

Mantén tu `main` local y el `main` de **tu fork** alineados con el `main` de **omegaUp**:

```bash
git checkout main
git fetch upstream
git pull --rebase upstream main
git push origin main
```

!!! Advertencia "Si el push a main falla"
    Si `git push origin main` falla porque hiciste commits directamente en `main`, pide ayuda para dejar la rama limpia o usa `git push origin main --force-with-lease` solo si entiendes el riesgo. En general, **no hagas commits en `main`**; usa una rama de trabajo.

## Comenzando un nuevo cambio

### 1. Crear una rama de funciones

Crea una rama desde el último `main` oficial:

```bash
git fetch upstream
git checkout -b feature-name upstream/main
git push -u origin feature-name
```
!!! consejo "Nombrar sucursales"
    Utilice nombres de rama descriptivos como `fix-login-bug` o `add-dark-mode-toggle`.

### 2. Haga sus cambios

- Escribe tu código siguiendo las [pautas de codificación](../development/coding-guidelines.md)
- Escribe pruebas para tus cambios.
- Asegurarse de que todas las pruebas pasen

### 3. Confirme sus cambios

```bash
git add .
git commit -m "Write a clear description of your changes"
```
!!! consejo "Confirmar mensajes"
    Escriba mensajes de confirmación claros y descriptivos. Consulte [Confirmaciones convencionales](https://www.conventionalcommits.org/) para conocer las mejores prácticas.

### 4. Ejecutar validadores

Antes de presionar, ejecute el script linting:

```bash
./stuff/lint.sh
```
Este comando:
- Alinea elementos de código
- Elimina líneas innecesarias
- Realiza validaciones para todos los idiomas utilizados en omegaUp.

!!! nota "Ganchos de preempuje"
    Este script también se ejecuta automáticamente a través de enlaces previos al envío, pero ejecutarlo manualmente garantiza que los cambios cumplan con los estándares.

### 5. Configurar el usuario de Git (solo la primera vez)

Si no ha configurado la información de usuario de Git:

```bash
git config --global user.email "your-email@domain.com"
git config --global user.name "Your Name"
```
## Creando una solicitud de extracción

### 1. Impulsa tus cambios

```bash
git push -u origin feature-name
```
El indicador `-u` configura el seguimiento entre su rama local y **`origin`** (su fork). Si ya empujó la rama al crearla, basta con `git push`.

### 2. Abrir solicitud de extracción en GitHub

1. Vaya a [github.com/YOURUSERNAME/omegaup](https://github.com/YOURUSERNAME/omegaup)
2. Haga clic en "Sucursal" y seleccione su sucursal.
3. Haga clic en "Solicitud de extracción"
4. Complete la descripción del PR

### 3. Plantilla de descripción de relaciones públicas

La descripción de su PR debe incluir:

```markdown
## Description
Brief description of what this PR does.

## Related Issue
Fixes #1234  <!-- Replace with your issue number -->

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
Describe how you tested your changes.

## Screenshots (if applicable)
Add screenshots if your changes affect the UI.
```
!!! importante "Se requiere referencia del problema"
    Incluya siempre `Fixes #1234` o `Closes #1234` en su descripción de PR. Esto cierra automáticamente el problema cuando se fusiona el PR.

## Actualizando su solicitud de extracción

Si necesita realizar cambios después de crear el PR:

```bash
git add .
git commit -m "Description of additional changes"
git push  # No -u flag needed after first push
```
El PR se actualizará automáticamente con sus nuevas confirmaciones.

## ¿Qué sucede después del envío?

1. **Verificaciones automatizadas**: GitHub Actions ejecutará pruebas y validaciones.
2. **Revisión de código**: un mantenedor revisará su código
3. **Comentarios de direcciones**: realice los cambios solicitados y envíe actualizaciones
4. **Fusionar**: una vez aprobado, su PR se fusionará
5. **Implementación**: los cambios se implementan los fines de semana.

!!! info "Implementaciones de fin de semana"
    Los RP fusionados se implementan en producción durante las implementaciones de fin de semana. Verá sus cambios en vivo después de la próxima implementación.

## Eliminando ramas

Después de fusionar su PR:

### Eliminar sucursal local

```bash
git branch -D feature-name
```
### Eliminar rama remota

1. Vaya a GitHub y haga clic en "Sucursales".
2. Encuentra tu sucursal y haz clic en el ícono de eliminar.

O usa Git:

```bash
git push origin --delete feature-name
```
### Limpiar referencias remotas

Elimina referencias de seguimiento obsoletas (por ejemplo, tras borrar una rama en GitHub):

```bash
git remote prune origin --dry-run  # Vista previa
git remote prune origin             # Aplicar
```

## Corregir un pull request (commits o historial)

Si ya empujaste commits y necesitas **aplanar**, **eliminar** o **editar** commits recientes, usa rebase interactivo y luego empuja con precaución:

### Squash o fixup de los últimos `n` commits

```bash
git rebase -i HEAD~n
```

Sustituye `n` por cuántos commits quieres tocar. En el editor, deja el primero como `pick` y cambia el resto a `fixup` (o `f`). Guarda y cierra.

Prefiere **`--force-with-lease`** para no sobrescribir trabajo ajeno por error:

```bash
git push --force-with-lease
```

### Cambiar solo el mensaje del último commit

Si el commit malo es el **último** y aún **no** lo has empujado:

```bash
git commit --amend
```

Si ya lo empujaste:

```bash
git commit --amend
git push --force-with-lease
```

!!! Advertencia "Reescribir historial público"
    Reescribe historial solo en **tu** rama de trabajo. Nunca hagas force-push a `main` del repositorio canónico.
## Configuraciones adicionales

### Configuración regional

Es posible que la máquina virtual no tenga `en_US.UTF-8` como configuración regional predeterminada. Para solucionar este problema, siga [esta guía](https://askubuntu.com/questions/881742/locale-cannot-set-lc-ctype-to-default-locale-no-such-file-or-directory-locale/893586#893586).

### Dependencias del compositor

En la primera configuración, instale las dependencias de PHP:

```bash
composer install
```
### Configuración de MySQL

Si encuentra errores de MySQL al enviar, instalar y configurar MySQL:

```bash
sudo apt install mysql-client mysql-server

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
## Recursos

- **[Pautas de codificación](../development/coding-guidelines.md)** - Nuestros estándares de codificación
- **[Comandos útiles](../development/useful-commands.md)** - Referencia de comandos de desarrollo
- **[Guía de pruebas](../development/testing.md)** - Cómo escribir y ejecutar pruebas
- **[Cómo obtener ayuda](getting-help.md)** - Dónde hacer preguntas

## Próximos pasos

- Revise la [Descripción general de la arquitectura](../architecture/index.md) para comprender el código base.
- Consulte las [Guías de desarrollo](../development/index.md) para obtener guías detalladas.
- Únase a nuestro [servidor de Discord](https://discord.gg/gMEMX7Mrwe) para conectarse con la comunidad

---

**¿Listo para hacer tu primera contribución?** ¡Elige un problema, crea una rama y envía tu PR!
