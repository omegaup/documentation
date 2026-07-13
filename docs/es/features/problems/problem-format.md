---
title: Formato del problema
description: Estructura de archivos ZIP para la creación manual de problemas
icon: bootstrap/file-document
---
# Problema de formato (ZIP manual) {#problem-format-manual-zip}

Esta página es para quienes tienen experiencia en resolver problemas y necesitan crear un problema a mano.
`.zip`, o editar un omegaUp ya implementado, porque necesitan algo que
Las herramientas de apuntar y hacer clic no exponen: problemas de **Karel**, tareas **interactivas**,
un **validador personalizado** o un control preciso sobre agrupaciones y pesos. si lo eres
recién está comenzando, o su problema es una simple tarea de "leer entrada, imprimir salida",
utilice el [Creador de problemas (CDP)](https://omegaup.com/problem/creator) en su lugar y
Ahórrese el embalaje: hay un [tutorial de CDP en YouTube](https://www.youtube.com/watch?v=cUUP9DqQ1Vg).

!!! consejo "Tutoriales en vídeo"
    Si sigue la ruta manual, será útil ver a alguien hacerlo primero:
    [parte 1](https://www.youtube.com/watch?v=LfyRSsgrvNc) y
    [parte 2](https://www.youtube.com/watch?v=i2aqXXOW5ic) del manual
    tutorial de creación de problemas.

Lo más importante que debes internalizar antes de construir cualquier cosa: el
`.zip` que subes **no** es lo que almacena omegaUp. Cuando subes, omegaUp's
gitserver (el servicio Go en [`omegaup/gitserver`](https://github.com/omegaup/gitserver)
que mantiene cada problema como su propio repositorio git) descomprime el archivo, lee
su `cases/`, su `testplan` opcional y cualquier `settings.json` que incluya,
y **lo compila todo en un `settings.json` canónico** que el
la clasificadora realmente consume. `testplan` y cualquier `settings.json` parcial que haya enviado
se eliminan después de plegarlos, precisamente porque ahora son redundantes
con el archivo generado (ver
[`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L463-L492)).
Así que piense en el `.zip` como *fuente* y en el `settings.json` como el *artefacto compilado*.
que es exactamente por qué los nombres de directorio y las extensiones de archivo a continuación deben ser
letra perfecta.

## Los ajustes configurables (modelo mental) {#the-configurable-settings-mental-model}

Ya sea que los configure a través de la interfaz de usuario web o los envíe en metadatos empaquetados, cada
El problema conlleva el mismo puñado de perillas. Comprender lo que cada uno *significa* -
y el veredicto que obtiene cuando se excede es lo que le permite empaquetar correctamente.

### Validador: cómo se juzga la producción del concursante {#validator-how-the-contestants-output-is-judged}

El validador decide si un resultado es correcto y otorga una puntuación por caso en
`[0.0, 1.0]`. omegaUp envía cinco, cuyos nombres canónicos viven en
[`ProblemParams.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/ProblemParams.php#L28-L40)
(lado PHP) y
[`common/problemsettings.go`](https://github.com/omegaup/quark/blob/main/common/problemsettings.go#L30-L48)
(lado de la niveladora):

- **`token`**: token por token. Lee cada token (una serie de hasta
  **4,194,304** caracteres imprimibles contiguos: 4 MiB, el `MaxTokenLength` en
  el [`tokenizer.go`](https://github.com/omegaup/quark/blob/main/runner/tokenizer.go#L13) del corredor —
  separados por espacios en blanco) tanto del `.out` esperado como del concursante
  salida y requiere que las dos secuencias de tokens sean **idénticas**. Este es el
  predeterminado y lo que deseas para casi todo.
- **`token-caseless`**: igual que `token`, pero primero pone en minúsculas cada token, por lo que
  `Yes` y `yes` coinciden. Busque esto cuando la capitalización no sea parte del
  respuesta.
- **`token-numeric`** — lee únicamente tokens numéricos, los interpreta como números,
  y los acepta cuando el valor del concursante esté dentro de un **absoluto *o*
  error relativo de 1e-9** del valor esperado (el `Tolerance` predeterminado, también
  `1e-9`, instalado en
  [Configuración predeterminada de `Problem.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L4560)).
  Las dos secuencias deben tener la misma longitud. Úselo para punto flotante
  respuestas donde los últimos dígitos pueden tambalearse.
- **`literal`** (se muestra en la interfaz de usuario como "interpretar la salida estándar como puntuación"): dice
  la salida estándar del concursante, la analiza como un solo flotante y **lo sujeta a
  `[0.0, 1.0]` para usar directamente como puntuación del caso**. Es casi exclusivamente para
  Problemas **interactivos**: el proceso interactuante, no el concursante, imprime el
  puntuación, lo que evita que el concursante simplemente imprima `1.0` para hacer trampa.
- **`custom`** (`validator.<lang>`): incluye un programa que lee el
  salida estándar del concursante (y, si así lo desea, la entrada y salida esperada del caso) y
  imprime la partitura misma. Los detalles completos y los ejemplos elaborados se encuentran en
  [Validador personalizado](#custom-validator-validatorlang) a continuación.

### Idiomas: lo que podrá presentar el concursante {#languages-what-the-contestant-may-submit}

- **C, C++, Java, Python, …** — el concursante envía la fuente en uno de omegaUp
  Idiomas admitidos.
- **Karel** — el concursante envía un programa de Karel. Ver el
  [Problemas de Karel](#karel-problems) para saber cómo crear los casos.
- **Solo resultados**: el concursante carga un `.zip` de respuestas para cada caso.
  en lugar de un programa. Si quieres *también* dejarles pegar un solo caso
  responda como texto plano en lugar de como zip, el problema debe tener exactamente **uno**
  caso denominado `Main.in`/`Main.out`.
- **No hay presentaciones**: el concursante no puede enviar nada. Esto existe puramente para
  mostrar contenido (una lectura, una lección) dentro de un curso.

### Límites de tiempo, memoria y salida {#time-memory-and-output-limits}

Cada uno de estos se asigna a un veredicto específico cuando el programa del concursante lo cruza,
y cada uno tiene un valor predeterminado real. El formulario de creación de problemas actualmente completa previamente estos
valores (ver
[`Problem.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L5952-L5961)),
y el propio `DefaultLimits` de la niveladora
([`common/problemsettings.go`](https://github.com/omegaup/quark/blob/main/common/problemsettings.go#L193))
Estoy de acuerdo con ellos, por lo que un paquete que omite límites aún se ejecuta de manera sensata:

- **Límite de tiempo: `TimeLimit` (ms), `1000` predeterminado**: el tiempo máximo de **CPU** que
  El sistema operativo permite que el proceso del concursante se ejecute *para cada caso* antes de que lo eliminen con
  **`TLE`**. Este es tiempo de CPU, no de reloj de pared, por lo que es tiempo inactivo o bloqueado
  no cuenta en su contra.
- **Límite de tiempo total (pared total): `OverallWallTimeLimit` (ms), predeterminado
  `60000`**: el tiempo máximo **real** que el calificador espera por el problema *completo*
  para finalizar antes de detenerlo con **`TLE`**. Cualquier caso que no llegó a ejecutarse
  antes de esta fecha límite simplemente **no se evalúa**. Para mantener los resultados al menos
  algo consistente cuando esto se activa, los casos se evalúan en **lexicográfico
  orden**, por lo que los casos que se omiten son deterministas y no aleatorios.
- **Límite de memoria: `MemoryLimit` (KiB), `32768` predeterminado** (es decir, 32 MiB): el
  RAM máxima (montón + pila) que el sistema operativo permite que el programa use antes de eliminarlo con
  **`MLE`**. Se expresa en
  [kibibytes](https://en.wikipedia.org/wiki/Kibibyte), por lo que `32768` KiB = 32 MiB.
- **Límite de salida — `OutputLimit` (bytes), `10240` predeterminado** — el máximo del programa
  puede escribir en stdout *o* stderr antes de que se elimine con **`OLE`**. Para ordinario
  problemas de token omegaUp normalmente **detecta automáticamente** esto desde sus archivos `.out` —
  toma el más grande y agrega 10 KiB de espacio libre, por lo que rara vez lo configuras por
  mano. **Pero si usas un validador personalizado debes configurarlo explícitamente**, porque
  No existe un `.out` sencillo con el que comparar.
- **Límite de entrada: `inputLimit` (bytes), `10240` predeterminado**: la longitud máxima de
  el **código fuente** del concursante. Baja esto cuando quieras detener a la gente.
  de pegar una tabla de respuestas precalculada en lugar de resolver realmente la
  problema.
- **Límite de tiempo del validador: `validatorTimeLimit` (ms), `1000` predeterminado**: cuánto tiempo
  el evaluador espera a que un *validador personalizado* emita un veredicto para cada caso antes
  rendirse con **`JE`**.
- **Tiempo de pared adicional para libinteractive — `ExtraWallTime` (ms), `0` predeterminado** — cómo
  cuánto tiempo espera el evaluador hasta que el programa *interactor* termine cada caso (más allá
  los límites normales) antes de detenerlo con **`TLE`**. Sólo relevante para
  problemas interactivos.

!!! nota "Los validadores personalizados obtienen sus propios límites más generosos"
    En el momento en que cambia el validador a `custom`, omegaUp genera un conjunto separado
    de límites para el proceso *validador*: actualmente **256 MiB** de memoria, **30 s**
    Límite de tiempo de CPU, **5 s** de tiempo total de pared y **10 KiB** de salida
    ([`Problem.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L4606-L4611)).
    La idea es que juzgar puede darse el lujo de ser más lento y más hambriento que el
    La solución del concursante.

### Todo lo demás {#everything-else}

- **Fuente**: atribución/origen de la declaración, mostrada a los concursantes.
- **Aparece en el listado público**: si el problema se puede mostrar públicamente y
  utilizado en concursos y cursos de *otras personas*.
- **Enviar aclaraciones por correo electrónico**: si omegaUp le envía un correo electrónico a usted (el autor) cuando
  El usuario pide una aclaración sobre este problema.
- **Etiquetas**: etiquetas de clasificación.

## El diseño ZIP {#the-zip-layout}

Guarde todo en un archivo **`.zip`**, no en `.rar`, `.tar.bz2`, `.7z` o
`.zx`. El nombre del zip en sí no importa. Un mínimo problema de idioma
se ve así:

```
problem.zip
├── cases/                 # Required: the .in/.out test data
│   ├── 1.in
│   ├── 1.out
│   └── …
├── statements/            # Required: at least one <locale>.markdown
│   └── es.markdown
├── solutions/             # Optional: editorial / official write-up
├── interactive/           # Optional: libinteractive bundle
├── validator.cpp          # Optional: custom validator (one of validator.<lang>)
├── settings.json          # Optional: pre-baked settings (usually generated for you)
└── testplan               # Optional: per-case weights
```
Un paquete de referencia real y funcional se encuentra en el repositorio de
[`frontend/tests/resources/testproblem.zip`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/resources/testproblem.zip),
y hay muchos más debajo
[`frontend/tests/resources`](https://github.com/omegaup/omegaup/tree/main/frontend/tests/resources).

!!! advertencia "`cases/` y `statements/` deben ubicarse en la raíz"
    Es *críticamente* importante que `cases/` y `statements/` estén directamente en
    la raíz del `.zip`, sin **ninguna** carpeta intermedia que los envuelva; esto
    ha picado a suficientes personas como para ganarse su propio virus,
    [omegaup#310](https://github.com/omegaup/omegaup/issues/310). En Linux/Mac el
    Una forma confiable de hacerlo bien es ingresar `cd` al directorio del problema y ejecutar
    `zip -r myproblem.zip *`, que comprime el *contenido* en lugar del contenedor
    carpeta. Y como omegaUp se ejecuta en **Linux, los nombres distinguen entre mayúsculas y minúsculas**:
    No se encontrará la carpeta llamada `Cases`, ni tampoco un archivo de entrada que termine
    en `.In` en lugar de `.in`.

### `cases/` {#cases}

Esta carpeta contiene todos los casos de prueba como archivos `.in`/`.out` emparejados. Los **nombres base
debe coincidir** — `1.in` con `1.out`, `hola.in` con `hola.out` — pero el nombre base
en sí mismo es arbitrario. Internamente, el implementador solo acepta archivos que coincidan con el
expresión regular `^cases/([^/]+)\.in$`
([`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L130)),
y si la carpeta falta o está vacía, la carga falla por completo con
`cases/ directory missing or empty`
([`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L1095)).
Cada `.in` que espera envíos debe tener un `.out` coincidente, o el despliegue
errores con `failed to find the output file for cases/<name>`.

**El `.` (punto) en un nombre de caso está reservado para agrupación.** No coloque un punto en un
nombre del caso a menos que quiera agrupar: el texto *antes del primer punto* se convierte en el
**nombre del grupo** (`strings.SplitN(caseName, ".", 2)[0]` en
[`common/problemsettings.go`](https://github.com/omegaup/quark/blob/main/common/problemsettings.go#L336-L342)).
Entonces `grupo1.caso1.in`, `grupo1.caso1.out`, `grupo1.caso2.in`, `grupo1.caso2.out`
forme **un grupo** (`grupo1`) con **dos casos**.

Los **casos agrupados** existen porque a veces el conjunto de respuestas plausibles es pequeño y
no desea que un concursante obtenga un crédito parcial por una suposición afortunada: ganar un
Los puntos del grupo debes resolver **cada caso en ese grupo**. No hay límite en
el número de grupos, y los grupos pueden tener diferente número de casos.

Tampoco hay un límite estricto en el número de casos, pero **mantenga el caso total
carga útil inferior a ~100 MB**. Más casos significa que cada envío tarda más en calificarse,
y en un concurso en vivo que se traduce directamente en tiempos de espera en las colas, especialmente
doloroso cuando una solución lenta, vinculada a `TLE`, está por delante de todos los demás en el
cola.

### `statements/` {#statements}

Esto contiene la declaración del problema en Markdown (el mismo estilo que usa Wikipedia), uno
archivo por configuración regional: `es.markdown`, `en.markdown`, `pt.markdown`. Al menos uno es
requerido. Puede obtener una vista previa exactamente de cómo se representarán Markdown y LaTeX en
[omegaup.com/redaccion.php](https://omegaup.com/redaccion.php) — por favor, hágalo
esto y confirme que las tablas de entrada/salida se ven bien, porque una declaración confusa
Es una experiencia miserable a mitad de la competencia.

LaTeX es totalmente compatible. Envuelva los nombres de las variables en `$…$`: escriba `$n$`, `$x$`,
`$x_i$` para un subíndice, para que se destaquen de la prosa y los concursantes puedan encontrar
ellos de un vistazo. Se lee mejor y evita ambigüedades.

### `solutions/` {#solutions}

Estructuralmente idéntico a `statements/`: el artículo oficial de la solución en
Markdown, nombrado según la configuración regional (`es.markdown` y traducciones `en.markdown`,
`pt.markdown`). El paquete en
[`testproblem.zip`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/resources/testproblem.zip)
Incluye un ejemplo de soluciones.

### `interactive/` (opcional) {#interactive-optional}

Problemas interactivos: donde el programa del concursante habla de un lado a otro con un
juzgar el proceso en lugar de leer una entrada fija, debe construirse con
[libinteractive](https://omegaup.com/libinteractive/); esa página documenta el
Formato de la interfaz `.idl` y cómo se generan las calzas. Para una completa y real
referencia de cómo se estructura el zip de un problema interactivo, utilice
[Cueva de IOI 2013](https://omegaup.com/resources/cave.zip) como plantilla.

Una comodidad que el implementador maneja por usted: casos de muestra de libinteractive en
`interactive/examples/` **no necesita un `.out`** — gitserver genera un vacío
uno automáticamente
([`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L495-L514)).

### Validador personalizado (`validator.<lang>`) {#custom-validator-validatorlang}

Cuando la comparación de tokens no es suficiente: múltiples respuestas correctas, juez especial
puntuación, crédito parcial: envíe exactamente **un** archivo llamado `validator.<lang>` a
la **raíz** del zip, donde `<lang>` es uno de `c`, `cpp`, `java`, `p` (Pascal),
o `py`. Solo necesitas un validador y es **independiente del concursante
idioma**.

Aquí está el contrato exacto y vale la pena hacerlo bien:

- Su validador lee el **resultado del concursante en su propia entrada estándar** — simple `scanf`
  / `cin` / `input()`. Mentalmente, el evaluador ejecuta el equivalente de
  `./contestant < data.in | ./validator <casename>`, donde `<casename>` es el
  Nombre `.in` del caso actual **sin la extensión**.
- Puede abrir un archivo llamado literalmente **`data.in`**: la misma entrada que se envió a
  el concursante y un archivo llamado **`data.out`**: el resultado esperado emparejado
  con ese `data.in`. Lea cualquiera de los dos, ambos o ninguno.
- **Debe imprimir un solo flotante en `[0.0, 1.0]` en la salida estándar**: la fracción del
  caso el concursante acertó. **No imprimir nada → `JE`.** Imprimir menos de 0 → el
  la puntuación se fija en 0; imprimir más de 1 → fijado a 1.
- El validador se ejecuta **dentro del mismo entorno limitado** que los programas de los concursantes. Si *el
  el propio validador* se porta mal (`WA`, `RFE`, `RTE`,…), se juzga el envío
  **`JE`**: por lo tanto, un validador con errores falla ruidosamente en lugar de obtener una puntuación errónea en silencio.
- **De todos modos debes enviar archivos `.out` aunque no se vayan a utilizar** para
  comparación. Los archivos vacíos están bien; simplemente tienen que existir para que el emparejamiento de casos
  tiene éxito.

Un validador para [sumas](https://omegaup.com/arena/problem/sumas) (leer dos
números enteros, imprima su suma) en C++ 17; observe cómo se leen los `a` y `b` originales
de `data.in`, la suma esperada de `data.out`, la respuesta del concursante de
stdin e imprime `1.0` o `0.0`:

```c++
#include <iostream>
#include <fstream>

int main() {
  // read "data.in" to get the original input.
  int64_t a, b;
  {
    std::ifstream original_input("data.in", std::ifstream::in);
    original_input >> a >> b;
  }
  // you can store anything that helps you evaluate in "data.out".
  int64_t sum;
  {
    std::ifstream original_output("data.out", std::ifstream::in);
    original_output >> sum;
  }

  // read standard input to get the contestant's output.
  int64_t contestant_sum;
  if (!(std::cin >> contestant_sum)) {
    // anything you print to cerr is ignored, but it's useful for debugging.
    std::cerr << "Error reading the contestant's output\n";
    std::cout << 0.0 << '\n';
    return 0;
  }

  // determine whether the answer is incorrect.
  if (sum != contestant_sum && sum != a + b) {
    std::cerr << "Incorrect output\n";
    std::cout << 0.0 << '\n';
    return 0;
  }

  // If execution reaches here, the contestant's output is correct.
  std::cout << 1.0 << '\n';
  return 0;
}
```
El mismo validador en Python 3:

```python
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import sys

def _main():
  # read "data.in" to get the original input.
  with open('data.in', 'r') as f:
    a, b = [int(x) for x in f.read().strip().split()]
  # you can store anything that helps you evaluate in "data.out".
  with open('data.out', 'r') as f:
    expected_sum = int(f.read().strip())

  score = 0
  try:
    # Read the contestant's output.
    contestant_sum = int(input().strip())

    # Determine whether the output is incorrect.
    if contestant_sum not in (expected_sum, a + b):
      # Anything printed to sys.stderr is ignored, but useful for debugging.
      print('Incorrect output', file=sys.stderr)
      return

    # If execution reaches here, the contestant's output is correct.
    score = 1
  except:
    logging.exception("Error reading the contestant's output")
  finally:
    print(score)

if __name__ == '__main__':
  _main()
```
### `testplan` (opcional) {#testplan-optional}

De forma predeterminada **cada caso vale `1/number-of-cases`**: el implementador asigna cada
caso un peso de `1/1` y el clasificador normaliza todos los pesos para que sumen 1
(`AddCaseName(caseName, big.NewRat(1, 1), false)` en
[`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L453-L461),
pesos divididos por el total en
[`common/literalinput.go`](https://github.com/omegaup/quark/blob/main/common/literalinput.go#L317-L333)).
Cuando desee que los casos se ponderen de manera desigual, suelte un archivo llamado **`testplan`** (no
extensión) en la raíz del zip, una línea por caso: el nombre del archivo del caso
**sin la extensión**, espacios en blanco, luego el número de puntos. por un problema
con estuches `cases/caso1.in`, `cases/grupo2.caso1.in`, `cases/grupo2.caso2.in`:

```
caso1 5
grupo2.caso1 10
grupo2.caso2 0
```
Algunas cosas del analizador
([`NewCaseWeightMappingFromTestplan`](https://github.com/omegaup/quark/blob/main/common/problemsettings.go#L305-L334))
realmente se aplica, haciendo coincidir cada línea con
`^\s*([^#[:space:]]+)\s+([0-9.]+)\s*$`:

- **Sin espacios en los nombres de los archivos de casos**: el token del nombre del caso no puede contener
  espacio en blanco.
- **`#` inicia un comentario**: una línea cuyo primer carácter que no sea un espacio es `#` (y cualquier
  línea que no coincide con el patrón) se omite, para que pueda anotar su
  plan de prueba.
- El `testplan` y el `.zip` deben **concordar en el conjunto de cajas**. gitserver se ejecuta
  una *diferencia simétrica* en ambos sentidos
  ([`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L463-L488)):
  un caso en el plan de prueba pero que falta en `cases/` falla con
  `testplan missing case "<name>"`, y un caso en `cases/` pero ausente en el
  El plan de prueba falla con `.zip missing case "<name>"`. No se puede especificar a medias.

**Para calificar a todo un grupo** sin dividir los puntos entre sus casos, el
La convención es poner la puntuación total del grupo en el **primer** caso y **0** en todos.
los demás, como lo hace `grupo2.caso1 10` / `grupo2.caso2 0` arriba.

Esto interactúa con la **política de puntuación** del grupo, uno de los dos valores en
[`ProblemParams.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/ProblemParams.php#L48-L49):
`sum-if-not-zero` (valor predeterminado: un grupo obtiene la **suma** de las puntuaciones de sus casos,
pero solo si son *todos* distintos de cero) o `min` (el grupo obtiene el **mínimo** de
las puntuaciones de sus casos multiplicadas por el peso del grupo). El valor predeterminado es por qué el
La convención de "puntos en el primer caso, cero en el resto" funciona: resuelve el todo
agrupa y recoges todo el peso; Se pierde cualquier caso y el grupo colapsa.
cero.

### `settings.json` (generalmente generado, ocasionalmente escrito a mano) {#settingsjson-usually-generated-occasionally-hand-written}

La mayoría de las veces *nunca* escribirás este archivo: es el artefacto compilado de gitserver.
produce desde su `cases/`, `testplan` y límites, ordenados en
[`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L580-L597).
Su forma es la estructura `ProblemSettings`.
([`common/problemsettings.go`](https://github.com/omegaup/quark/blob/main/common/problemsettings.go#L174-L182)):
un bloque `Limits`, un bloque `Validator` (`Name`, `Tolerance`, opcional
`GroupScorePolicy`, validador personalizado opcional `Limits`), una matriz de grupos `Cases`
cada uno con sus casos ponderados y, para problemas interactivos, un `Interactive`
bloque. Si *envías* tu propio `settings.json`, gitserver lo lee y aún así
permite que un `testplan` anule los pesos de la caja encima. De cualquier manera, sólo el
El `settings.json` generado sobrevive en el repositorio de problemas implementado.

## Imágenes {#images}

omegaUp tiene soporte de imágenes nativas :). Para incrustar una imagen en una declaración, agregue el
archivo de imagen a su zip **dentro de `statements/`** y haga referencia a él desde su
`es.markdown` con Markdown ordinario:

```markdown
![Alt text](image.jpg)
```
Los formatos admitidos son **jpg, gif, png**. Tenga en cuenta el tamaño: Markdown **no**
cambie su escala, así que mantenga las imágenes con **650 píxeles de ancho** o menos.

## Ejemplo de zips {#example-zips}

Los zips que omegaUp utiliza en sus propias pruebas son las mejores plantillas para copiar:
[`frontend/tests/resources`](https://github.com/omegaup/omegaup/tree/main/frontend/tests/resources).

## Problemas de Karel {#karel-problems}

Primero, prueba [karel.js](https://omegaup.com/karel.js/): convierte casos para
usted y es mucho menos problemático que lo que sigue.

Si ya tiene sus casos y prefiere no volver a hacerlos en karel.js, el
Los pasos siguientes son para **Windows** y suponemos que tienes **Python 2.7** instalado y encendido.
su `PATH` (la ruta de instalación predeterminada suele ser `C:\Python27`); verificar que puedes
ejecute `python` desde la consola de DOS antes de comenzar.

1. Tenga estos archivos a mano:
   [el kit de herramientas de Karel](https://docs.google.com/file/d/0B6Rb3__ksbxDRC1VSDV0amRYNmc/edit?usp=sharing) —
   `karel.exe` (ejecuta una solución contra un mundo), `kcl.exe` (la solución
   compilador), el script Python `karel_mdo_convert.py` y el contenedor
   `karel-to-omegaup.bat` que los une.
2. Coloque sus casos MDO y KEC en una carpeta. Para generarlos puedes utilizar el
   Karel, creador de casos, de [KarelOMI.zip](http://www.cimat.mx/~amor/Omi/Utilerias/KarelOMI.zip).
3. También necesitas tu **solución**. Si programa en Java, déle a la solución un
   Extensión `.JS` (por lo que `kcl.exe` la interpreta como karel-java); para Pascal, use
   `.PAS` (karel-pascal).
4. Coloque los archivos ejecutables, el script Python y el `.bat`, todos en la misma carpeta.
5. Ejecute `karel-to-omegaup.bat` sin argumentos y le solicitará el
   ruta de la solución y la ruta de los casos, o páselos en la línea de comando:
   cite rutas que contengan espacios:

   ```
   karel-to-omegaup.bat "karel vs chuzpa\solucion.js" "karel vs chuzpa\casos"
   ```
6. Con todo en su lugar, el script primero compila la solución con `kcl.exe`.
   (produciendo un `.KX`), luego construye los mundos `.IN` a partir de cada `.MDO` en los casos
   carpeta. Tenga en cuenta que el convertidor de Python necesita que exista el `.KEC` coincidente: para
   `caso1.MDO` también debes tener `caso1.KEC`. De aquellos extrae buscas,
   orientación y posición en cada `.IN`.
7. Luego ejecuta `karel.exe` con cada `.IN` generado y el `.KX` compilado.
   solución para producir el `.OUT` correspondiente, por lo que una solución *correcta* es esencial,
   ya que las salidas son tan correctas como son.
8. El `.bat` coloca una carpeta `cases` (con los pares `.IN`/`.OUT`) dentro de su
   directorio de casos.
9. Finalmente, agregue una carpeta `statements` con `es.markdown` y comprímala exactamente como
   Tendrías un problema de idioma.

## Cómo se junta todo {#how-it-all-comes-together}

Para cerrar el ciclo: cuando subes, gitserver
[`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go)
descomprime el archivo, valida que `cases/` existe y que cada caso enviado tiene
su `.out`, pliega `testplan`/`settings.json` en un `settings.json` canónico,
confirma todo como una nueva revisión del repositorio git del problema, y
elimina el ahora redundante `testplan`. En el momento de la calificación, la interfaz PHP
(`\OmegaUp\Controllers\Run::apiCreate` →
[`\OmegaUp\Grader::grade`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Grader.php))
entrega el envío al evaluador Go a través de HTTP, que dice que `settings.json`,
normaliza los pesos de los casos para que sumen 1, ejecuta cada caso bajo el sandbox contra
sus límites, aplica el validador y acumula las puntuaciones por caso a través del
política de puntuación del grupo. Cada ruta y extensión en este documento existe para hacer que
la canalización se resuelve correctamente, por lo que es importante lograr que sean exactamente correctas.

## Documentación relacionada {#related-documentation}

- **[Creando problemas](creating-problems.md)**: el flujo de trabajo de creación y las rutas de la interfaz de usuario
- **[Veredictos](../verdicts.md)**: qué significan `AC`, `TLE`, `MLE`, `OLE`, `JE` y el resto
