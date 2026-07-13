---
title: Contribuyendo a omegaUp
description: Aprenda cómo contribuir con código a omegaUp a través de solicitudes de extracción
icon: bootstrap/code-tags
---
# Contribuyendo a omegaUp

¡Gracias por su interés en contribuir con omegaUp! Esta página lo guía a través de todo el ciclo de una contribución: bifurcar y clonar, mantener su copia local honesta antes de tocar algo, bifurcar, abrir una buena solicitud de extracción y corregir una después de haber impulsado algo de lo que no está orgulloso. Aquí nada es exótico: es el flujo de trabajo cotidiano que el equipo de mantenimiento realmente utiliza, con el razonamiento adjunto para que puedas improvisar de forma segura cuando tu situación no coincida con el camino feliz.

Antes de escribir una línea de código, lo invitamos a leer las [Pautas de codificación](../development/coding-guidelines.md). Vale la pena internalizar pronto su estrella del norte: es preferible explicar *por qué* las cosas se hacen de la manera en que se hacen en lugar de *qué* hace el código. Seguirlos hace que su cambio sea mucho más fácil de leer y fusionar para un revisor, por lo que el esfuerzo se amortiza la misma semana.

## Por qué nunca te comprometes con `main`

Después de bifurcar omegaUp, la rama `main` en su bifurcación siempre debe permanecer como un espejo byte por byte de la rama `main` de `omegaup/omegaup`, que contiene los últimos cambios que el equipo de revisión ya aprobó. Ésa es la razón de la regla que verá repetida en todas partes: **nunca se comprometa directamente con `main`**. Una vez que sus confirmaciones aterrizan en `main` y el `main` ascendente continúa, es realmente doloroso arrastrar su `main` a un estado limpio: termina rebasando, reiniciando o forzando su camino para salir de un hoyo que cavó sin ningún motivo. En su lugar, cree una rama separada para cada cambio que desee enviar como una solicitud de extracción y deje que `main` no haga más que realizar un seguimiento en sentido ascendente.

## Requisitos previos

Antes de comenzar:

1. [Configure su entorno de desarrollo](development-setup.md)
2. Lea las [Pautas de codificación](../development/coding-guidelines.md)
3. Sepa [cómo obtener ayuda](getting-help.md) si se queda atascado

## Cada RP necesita un problema asignado

!!! importante "Requerido antes de abrir un PR"
    Cada solicitud de extracción **debe** estar vinculada a un problema de GitHub existente que le esté **asignado**. Esto no es burocracia en sí misma: es la forma en que el equipo evita que dos personas creen silenciosamente la misma solución, y esto se aplica mediante la automatización, por lo que un PR sin un problema asignado detrás no se puede fusionar sin importar cuán bueno sea el código.

### Cómo asignar un problema

Primero, **busque o cree un problema**. Explore los [problemas existentes](https://github.com/omegaup/omegaup/issues) o, si está solucionando algo que nadie ha presentado todavía, [abra un nuevo problema](https://github.com/omegaup/omegaup/issues/new) que describa el error o la característica para que haya algo a lo que señalar su PR.

Entonces **reclamalo**. omegaUp ejecuta el bot [`takanome-dev/assign-issue-action`](https://github.com/takanome-dev/assign-issue-action) con precisión para que no tenga que esperar a que un mantenedor haga clic en "asignar" en cada ticket. Comenta sobre el problema con:

- `/assign`: asígnese el problema usted mismo.
- `/unassign`: elimínate del problema cuando no puedas continuar, para que otra persona pueda solucionarlo.

El bot también puede ofrecer asignar el problema cuando su comentario deje claro que desea trabajar en ello.

Finalmente, haga referencia al problema en su descripción de relaciones públicas con `Fixes #1234` o `Closes #1234` (usando su número de problema real). GitHub lee esa línea y cierra el problema automáticamente en el momento en que su PR se fusiona, por lo que el rastreador se mantiene honesto sin que nadie lo arregle a mano.

!!! fracaso "Un RP sin problema asignado no pasará sus comprobaciones"
    Si su PR no está vinculado a un problema que se le ha asignado, las comprobaciones automáticas fallan y el PR no se puede fusionar. Reclama el problema primero.

### Los límites de asignación y por qué existen

El bot impone algunos plazos para que los problemas reclamados pero abandonados no se pudran indefinidamente y bloqueen a otros contribuyentes:

- Puede tener como máximo **5** números asignados a usted a la vez en todo el repositorio. El límite evita que una sola persona acumule el trabajo atrasado.
- Después de que te asignen, debes **abrir una solicitud de extracción** (un PR **borrador** cuenta) dentro de **7 días**. La ventana es lo que convierte el "ya lo haré" en un progreso real o en un asunto liberado.
- Se publica un recordatorio aproximadamente a la mitad, aproximadamente **3,5 días**, por lo que una semana ocupada no le costará el problema por sorpresa.
- Si no existe ningún PR antes del día 7, se le **desasignará automáticamente** y se le **bloqueará para que no pueda volver a asignarse el mismo problema**; Si aún lo deseas después de eso, pregúntale a un mantenedor.

Hay una excepción deliberada: si **usted fue el autor del problema** y ya tiene al menos **10 RP fusionados** en este repositorio, puede autoasignar sus propios problemas **sin** que cuenten contra el límite de 5 asignaciones activas: se ha ganado la confianza y es su problema. La regla de los 7 días para un PR todavía se aplica incluso entonces, y los problemas escritos por *otras* personas aún cuentan para su límite de 5.

!!! consejo "No pierdas una tarea que pretendías conservar"
    Comente `/assign` y luego abra un PR **borrador** el mismo día; eso satisface la regla de los 7 días de inmediato y le otorga todo el tiempo que necesita para terminar. Si realmente necesita más tiempo, solicite a un encargado de mantenimiento que agregue la etiqueta **`📌 Pinned`**, que exime al problema del barrido de desasignación automática.

## Configura tu bifurcación y tus controles remotos (una vez)

Sólo haces esto una vez por clon. omegaUp usa los mismos dos nombres remotos que el flujo de trabajo de bifurcación estándar de GitHub, por lo que todos los tutoriales y herramientas de git que ya conoces siguen funcionando:

- **`origin`**: tu bifurcación, `https://github.com/YOURUSERNAME/omegaup.git`: desde donde **empujas** ramas y abres solicitudes de extracción.
- **`upstream`**: el repositorio canónico, `https://github.com/omegaup/omegaup.git`: desde donde **extraes** los cambios aprobados por el equipo de revisión.

!!! nota "Las páginas wiki más antiguas intercambiaron estos nombres"
    Algunas de las páginas wiki más antiguas de omegaUp usaban `origin` para el repositorio canónico y un segundo control remoto para la bifurcación, lo opuesto a la convención aquí. Este sitio sigue la convención estándar anterior (`origin` = tu bifurcación, `upstream` = canónico). Si está haciendo una referencia cruzada a una página antigua y un comando se lee al revés, ese es el motivo.

### 1. Bifurcar el repositorio

Visite [github.com/omegaup/omegaup](https://github.com/omegaup/omegaup) y haga clic en el botón **Fork** para crear su propia copia de `omegaup/omegaup`.

### 2. Clona tu tenedor

```bash
git clone https://github.com/YOURUSERNAME/omegaup.git
cd omegaup
```
### 3. Agregue `upstream` y verifique

Tu nuevo clon ya tiene `origin` apuntando a tu bifurcación. Agregue `upstream` para que pueda recuperar los cambios del repositorio canónico:

```bash
git remote add upstream https://github.com/omegaup/omegaup.git
git remote -v
```
Deberías ver exactamente esto: dos líneas para cada control remoto, `origin` en tu bifurcación y `upstream` en el repositorio canónico:

```
origin     https://github.com/YOURUSERNAME/omegaup.git (fetch)
origin     https://github.com/YOURUSERNAME/omegaup.git (push)
upstream   https://github.com/omegaup/omegaup.git (fetch)
upstream   https://github.com/omegaup/omegaup.git (push)
```
Si `origin` apunta a algún lugar incorrecto (más comúnmente porque clonaste la URL canónica en lugar de tu bifurcación), vuelve a señalarlo sin volver a clonar:

```bash
git remote set-url origin https://github.com/YOURUSERNAME/omegaup.git
```
## Mantenga su `main` actualizado antes de comenzar

Vale la pena repetirlo: no debes realizar cambios en `main`, porque es muy difícil devolverlo a un estado decente una vez que los cambios se han fusionado. Pero es una buena idea sincronizarlo de vez en cuando (siempre justo antes de realizar un nuevo cambio) para que su trabajo comience desde el mismo compromiso que está analizando el equipo de revisión:

```bash
git checkout main               # Switch back to main if you were on a feature branch
git fetch upstream              # Download the latest omegaup/main
git pull --rebase upstream main # Replay upstream's commits under yours, keeping main linear
git push origin main            # Update your fork's main to match
```
!!! Advertencia "Si se rechaza `git push origin main`"
    Un envío rechazado a `main` significa que rompió la regla y cometió algo directamente en `main`: su `main` y el `main` ascendente ahora han divergido. La solución limpia es mover esas confirmaciones a una rama de funciones y restablecer `main` a `upstream/main`; Pregúntele a un mantenedor si no está seguro de cómo hacerlo. Sólo si comprende exactamente lo que está descartando debe sobrescribir el `main` de su horquilla con `git push origin main --force-with-lease`. La verdadera lección es la que se encuentra en la parte superior de esta página: en primer lugar, no se comprometa con `main`; en su lugar, bifurque.

## Iniciar un nuevo cambio

### 1. Bifurcación del último `main` ascendente

Cree su rama directamente desde `upstream/main` para que comience desde el código aprobado por la revisión, luego envíela a su bifurcación de inmediato para que haya un hogar para ella en GitHub:

```bash
git fetch upstream
git checkout -b feature-name upstream/main   # New branch, synced with omegaUp's main
git push -u origin feature-name              # Publish it to your fork; -u sets up tracking
```
!!! consejo "Nombra la sucursal después del cambio"
    Los nombres descriptivos como `fix-login-bug` o `add-dark-mode-toggle` indican a los revisores para qué sirve la sucursal de un vistazo y mantienen su propia lista de sucursales navegable meses después.

### 2. Haz tus cambios

Escriba su código siguiendo las [pautas de codificación](../development/coding-guidelines.md), agregue pruebas para lo que cambió y asegúrese de que el conjunto existente aún pase. Un cambio con pruebas es un cambio en el que un revisor puede confiar.

### 3. Establece tu identidad de git (solo la primera vez)

Si nunca has configurado git en esta máquina, hazlo una vez para que tus confirmaciones se atribuyan correctamente:

```bash
git config --global user.email "your-email@domain.com"
git config --global user.name "your-username"
```
### 4. Comprometerse

```bash
git add .
git commit -m "Write a clear description of what changed and why"
```
Un mensaje de confirmación que explica *por qué* se realizó el cambio, no solo *qué* archivo se movió, es la misma cortesía que las pautas de codificación solicitan en los comentarios de su código, y es lo que un revisor lee primero.

### 5. Ejecute los validadores antes de presionar

Ejecute el linter desde **fuera** del contenedor, en la raíz del repositorio:

```bash
./stuff/lint.sh
```
Sin argumentos, `stuff/lint.sh` descubre qué archivos cambió (se diferencia de `upstream/main` o `origin/main` si no tiene un control remoto `upstream`) y ejecuta el paso `fix` solo sobre esos archivos, activando el contenedor `omegaup/hook_tools` fijado para realizar el formato real y las comprobaciones estáticas para cada idioma que usa omegaUp. Alinea el código, elimina las líneas muertas y valida. Si solo desea *verificar* sin reescribir archivos, pase `validate` explícitamente: `./stuff/lint.sh validate`.

!!! nota "Debe ejecutarse fuera del contenedor"
    `stuff/lint.sh` se niega a ejecutarse cuando su directorio de trabajo es `/opt/omegaup` (la ruta en la que se encuentra el código *dentro* del contenedor de desarrollo) e imprime `Running ./stuff/lint.sh inside a container is not supported.`. Necesita el Docker de su host para iniciar la imagen de las herramientas de enlace, así que ejecútelo desde el shell del host, no desde dentro de `docker exec`.

!!! nota "El gancho de preempuje ejecuta esto por usted"
    omegaUp instala un gancho git `pre-push` que ejecuta `stuff/lint.sh ... validate` automáticamente, por lo que un envío con errores de pelusa se detiene antes de que salga de su máquina. Ejecutar el linter usted mismo primero solo significa que encontrará y solucionará los problemas según su propio cronograma en lugar de que el push rebote.

## Abrir la solicitud de extracción

### 1. Empuja tu rama

```bash
git push -u origin feature-name
```
El indicador `-u` vincula su sucursal local con la sucursal en su bifurcación (`origin`), por lo que cada inserción posterior es simplemente `git push` sin argumentos: el seguimiento ya está configurado.

### 2. Abra el PR en GitHub

Vaya a su bifurcación en `https://github.com/YOURUSERNAME/omegaup`, use el selector de rama para cambiar a `feature-name` y haga clic en **Solicitud de extracción**. GitHub ofrecerá abrir el PR contra el `main` de `omegaup/omegaup`: ahí es exactamente donde lo desea.

### 3. Escribe la descripción

Una buena descripción es lo que hace que sus relaciones públicas se revisen rápidamente. Incluya lo que hace el cambio, el problema que cierra, qué cambió realmente y cómo sabe que funciona:

```markdown
## Description
Brief description of what this PR does.

## Related Issue
Fixes #1234  <!-- Replace with your real issue number -->

## Changes Made
- Change 1
- Change 2

## Testing
How you tested the change.

## Screenshots (if applicable)
Before/after images for any UI change.
```
!!! importante "Siempre haga referencia al problema"
    La línea `Fixes #1234` / `Closes #1234` no es una decoración opcional: es lo que vincula el PR con su problema asignado (satisfaciendo la verificación automatizada) y lo que cierra el problema automáticamente cuando el PR se fusiona.

## Actualizar un PR después de la revisión

Los revisores dejarán comentarios. Abordelos de la misma manera que realizó el cambio original: confirme en la misma rama y presione. Esta vez no hay `-u` porque la sucursal ya está rastreando `origin`:

```bash
git add .
git commit -m "Address review: <what you changed>"
git push
```
El PR abierto se actualiza automáticamente con las nuevas confirmaciones y el revisor las ve la próxima vez que mira.

## Arregle un PR que ya impulsó

A veces presionas y solo entonces notas que la rama contiene tres confirmaciones "wip", "oops" y "typo", o la confirmación superior tiene un mensaje que preferirías no inmortalizar. Debido a que esta es *tu* rama de funciones y no un historial compartido, eres libre de reescribirla y forzarla. La única regla estricta es la misma que en el resto de esta página: **solo reescribe el historial en tu propia rama de funciones; nunca fuerces el envío a `main` en el repositorio canónico.**

### Cambiar solo el mensaje del último compromiso

Si el mensaje en su confirmación más reciente es incorrecto, modifíquelo; esto abre su editor en el mensaje existente:

```bash
git commit --amend
```
Verás el mensaje actual seguido del texto de ayuda de git:

```
Old commit message

# Please enter the commit message for your changes. Lines starting
# with '#' will be ignored, and an empty message aborts the commit.
```
Edite la línea superior, guarde y cierre. Confirme que fue necesario con `git log`, que ahora debería mostrar su nuevo mensaje contra esa confirmación. Si ya habías enviado la confirmación, el control remoto aún tiene la versión anterior, así que actualízala:

```bash
git push --force-with-lease
```
`--force-with-lease` es la forma segura de `--force`: se niega a sobrescribir la rama remota si alguien más la presionó desde la última vez que la recuperó, por lo que una presión forzada nunca puede afectar silenciosamente el trabajo de un colaborador.

### Elimina los compromisos desechables

Para combinar una serie de confirmaciones desordenadas en una confirmación limpia, rebase interactivamente el último `n` de ellos:

```bash
git rebase -i HEAD~n
```
Reemplace `n` con la cantidad de confirmaciones que desea contraer. Git abre un editor que los enumera primero: los más antiguos:

```
pick commit-1
pick commit-2
pick commit-3
...
pick commit-n
```
Mantenga el de arriba como `pick`, que es el compromiso cuyo mensaje sobrevive, y cambie cada línea debajo de `pick` a `fixup` (o simplemente `f`), lo que incorpora los cambios de ese compromiso en el de arriba y descarta su mensaje:

```
pick  commit-1
f     commit-2
f     commit-3
...
f     commit-n
```
Guardar y cerrar. Luego publique la rama reescrita:

```bash
git push --force-with-lease
```
El PR ahora muestra una única confirmación ordenada en lugar del rastro de reparación y ninguno de los mensajes descartados aparece en el historial.

## Después de enviar

Una vez que el PR está abierto, se desarrolla una secuencia predecible. GitHub Actions ejecuta la batería completa de pruebas y validaciones; asegúrese de que todas sean verdes, ya que una marca roja es lo primero en lo que un revisor hará rebotar el PR. Luego, un miembro del equipo omegaUp revisa su código; aborde todo lo que generen enviando más compromisos a la misma rama. Una vez que se aprueba y se fusiona, hay una espera más: los RP fusionados pasan a producción en la **implementación del fin de semana**, por lo que su cambio se activa después del siguiente fin de semana en lugar de en el instante en que se fusiona.

## Limpiar después de una fusión

Una vez que su PR se fusiona, la sucursal habrá hecho su trabajo. Eliminarlo localmente:

```bash
git branch -D feature-name
```
Elimínelo también en GitHub, ya sea desde la página **Sucursales**, desde el PR fusionado (GitHub ofrece un botón de eliminación) o desde la línea de comando:

```bash
git push origin --delete feature-name
```
Incluso después de eliminar la rama remota, su repositorio local mantiene una referencia obsoleta de seguimiento remoto, que puede ver con `git branch -a`. Elimine esas referencias muertas para que `git branch -a` deje de enumerar ramas que ya no existen:

```bash
git remote prune origin --dry-run  # Preview what would be pruned
git remote prune origin            # Actually remove the stale references
```
## Problemas ambientales que puedes encontrar en el primer intento

Estos son los problemas de configuración con los que los contribuyentes primerizos suelen tropezar. Cada uno muestra el síntoma para que pueda comparar el suyo y luego la solución.

### La configuración regional de la VM no es `en_US.UTF-8`

La máquina virtual de desarrollo no viene con `en_US.UTF-8` como configuración regional predeterminada, algo de lo que se quejan algunas herramientas. Solucionarlo siguiendo [esta guía de Askubuntu](https://askubuntu.com/questions/881742/locale-cannot-set-lc-ctype-to-default-locale-no-such-file-or-directory-locale/893586#893586).

### Faltan dependencias de PHP

Una compra nueva no tiene directorio `vendor/`, por lo que faltan dependencias de PHP hasta que las instales:

```bash
composer install
```
### `FileNotFoundError: ... 'mysql'` al empujar

Si su envío aborta con algo como esto:

```
FileNotFoundError: [Errno 2] No such file or directory: 'mysql'
error: failed to push some refs to 'https://github.com/YOURUSERNAME/omegaup.git'
```
lo que le dice es que el enlace previo al envío intentó ejecutar el cliente `mysql` y no pudo encontrarlo: MySQL no está instalado en su host. El **servidor** MySQL se ejecuta dentro del contenedor de desarrollo, pero el cliente que invoca el enlace debe vivir en el host, **fuera** del contenedor. Instale ambos paquetes allí:

```bash
sudo apt install mysql-client mysql-server
```
Luego apunte al cliente al MySQL del contenedor, que está publicado en el puerto **13306** (no el 3306 predeterminado, por lo que no choca con ningún MySQL que ya esté ejecutando):

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
Con `.my.cnf` vinculado, el cliente lee esa configuración automáticamente y el enlace previo al envío puede llegar a la base de datos.

## Adónde ir a continuación

- **[Pautas de codificación](../development/coding-guidelines.md)**: los estándares que hacen que sus relaciones públicas sean fáciles de revisar.
- **[Comandos útiles](../development/useful-commands.md)**: la referencia de comandos de desarrollo diario.
- **[Guía de pruebas](../development/testing.md)**: cómo escribir y ejecutar las pruebas que su PR necesita.
- **[Cómo obtener ayuda](getting-help.md)**: dónde preguntar cuando estás atascado.
- **[Descripción general de la arquitectura](../architecture/index.md)**: cómo encajan las piezas que estás cambiando.
- Únase al [servidor de Discord](https://discord.gg/gMEMX7Mrwe) para hablar con la comunidad.

---

**¿Listo para hacer tu primera contribución?** Reclama un problema, ramifica `upstream/main` y abre tu PR.
