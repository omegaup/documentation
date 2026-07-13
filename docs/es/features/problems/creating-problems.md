---
title: Creando problemas
description: Guía paso a paso para crear problemas de programación.
icon: bootstrap/plus-circle
---
# Creando problemas

Gracias por querer agregar contenido a omegaUp. Un problema son cuatro cosas unidas: una **declaración** que lee el concursante, un conjunto de **casos** (pares `.in`/`.out`) que definen lo que significa "correcto", un conjunto de **límites** que deciden cuándo se elimina un envío y un **validador** que decide cuán estrictamente se compara la salida. Esta página recorre los cuatro y explica *por qué* existe cada perilla, para que puedas elegir valores razonables en lugar de copiar los valores predeterminados a ciegas.

Hay dos formas de crear un problema y debes buscarlas en este orden:

- **The Problem Creator (CDP)** en [omegaup.com/problem/creator](https://omegaup.com/problem/creator) es un editor visual que cubre el caso común de forma intuitiva. Tiene algunas limitaciones, en particular, **no** soporta los problemas de Karel, por lo que si no puede expresar lo que necesita, vaya a la opción manual a continuación. Hay un [video tutorial](https://www.youtube.com/watch?v=cUUP9DqQ1Vg) si prefieres verlo primero.
- **La construcción manual del `.zip`** le brinda control total y es la opción correcta para Karel, tareas interactivas o validadores personalizados. El diseño del archivo sin formato se encuentra en [Formato del problema (ZIP manual)](problem-format.md); Esta página explica las *decisiones de contenido* que se incluyen en ese archivo. Vídeo en modo manual: [parte 1](https://www.youtube.com/watch?v=LfyRSsgrvNc), [parte 2](https://www.youtube.com/watch?v=i2aqXXOW5ic).

De cualquier manera, cuando presiona **Crear**, la solicitud llega a `\OmegaUp\Controllers\Problem::apiCreate` ([`frontend/server/src/Controllers/Problem.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L460)), que valida sus metadatos, crea un objeto `ProblemSettings` y entrega todo el paquete a `\OmegaUp\ProblemDeployer`. El implementador no almacena sus archivos en MySQL; los envía como un **repositorio git** en el servicio separado [omegaup-gitserver](https://github.com/omegaup/gitserver) ([`ProblemDeployer.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/ProblemDeployer.php#L91)), razón por la cual cada edición que realiza se convierte en una nueva revisión que puede publicar o revertir.

## La declaración

La declaración es Markdown y se encuentra en `statements/` en el archivo, un archivo por idioma: `es.markdown`, `en.markdown`, `pt.markdown`; esos tres (`en`, `es`, `pt`) son los únicos locales que omegaUp reconoce (`\OmegaUp\Controllers\Problem::VALID_LANGUAGES`). El español es el idioma predeterminado históricamente, por lo que la mayoría de los problemas heredados incluyen `es.markdown` y nada más.

Algunas cosas que hacen que las declaraciones se lean bien y el razonamiento detrás de cada una:

- **Envuelva cada variable en delimitadores matemáticos**: escriba `$n$`, `$x$`, `$x_i$` (los subíndices usan `_`) en lugar de un `n` simple. Esto no es decoración: durante un concurso en vivo una variable diferenciada de la prosa es mucho más fácil de detectar e imposible de confundir con una palabra en inglés, lo que reduce las aclaraciones.
- **LaTeX es totalmente compatible**, por lo que las fórmulas, sumatorias y matrices se procesan correctamente. Obtenga una vista previa de LaTeX *y* de la tabla de entrada/salida de muestra antes de publicar en [omegaup.com/redaccion.php](https://omegaup.com/redaccion.php): lo que ve allí es lo que ve el concursante.
- **Las imágenes van dentro de `statements/`** junto a Markdown, y usted hace referencia a ellas con la sintaxis de imagen simple de Markdown, `![alt text](imagen.jpg)`. Los formatos admitidos son **jpg, gif y png**. No hay cambio de escala en Markdown, por lo tanto, ajuste el tamaño de la imagen antes de agregarla; manténgala por debajo de **650 píxeles de ancho** o desbordará la columna de declaración.

Si tiene un artículo o editorial oficial, colóquelo en `solutions/` usando el mismo nombre por configuración regional (`es.markdown`, `en.markdown`, `pt.markdown`). El repositorio incluye ejemplos trabajados en [`frontend/tests/resources`](https://github.com/omegaup/omegaup/tree/main/frontend/tests/resources) — [`testproblem.zip`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/resources/testproblem.zip) en particular incluye una solución.

## Casos

Cada caso es un par de archivos bajo `cases/`: un `.in` de entrada y su salida esperada `.out`. Los **nombres base deben coincidir** y estar emparejados correctamente (`1.in`/`1.out`, `hola.in`/`hola.out`), pero el nombre específico es irrelevante. omegaUp se ejecuta en Linux, por lo que mayúsculas soporta carga: una carpeta llamada `Cases` o un archivo que termina en `.In` **no se encontrará**. No hay un límite estricto en la cantidad de casos, pero mantenga la carga útil total de casos por debajo de **~100 MB**: cada caso adicional es más trabajo por envío y, en un concurso en vivo, una solución lenta que `TLE` en cien casos puede respaldar la cola de calificación y arruinar la experiencia de todos.

### Casos agrupados

Por defecto, cada caso puntúa de forma independiente. Si, en cambio, desea una puntuación de **todo o nada** (el concursante solo gana los puntos del grupo cuando pasa *todos* los casos), utilice **casos agrupados**. Para agrupar, coloque un `.` (punto) en el nombre del archivo para separar el nombre del grupo del nombre del caso; el nombre del grupo es todo lo que está antes del primer punto. Entonces `grupo1.caso1.in`, `grupo1.caso1.out`, `grupo1.caso2.in`, `grupo1.caso2.out` es un **grupo único con dos casos**. No hay límite en la cantidad de grupos y los grupos pueden contener diferentes cantidades de casos.

Esta es la herramienta adecuada cuando el espacio de respuestas plausibles es pequeño (por ejemplo, un problema de sí o no), donde un concursante podría obtener crédito parcial adivinando casos individuales. Tenga en cuenta la otra cara: **el punto está reservado para agrupar**, así que no coloque puntos sueltos en el nombre de un caso a menos que realmente quiera agruparlo.

### Pesos (`testplan`)

Por defecto, cada caso vale `1 / number-of-cases`, por lo que las puntuaciones suman 100%. Para ponderar los casos de manera diferente, agregue un archivo llamado literalmente **`testplan`** (sin extensión) en la raíz del zip, una línea por caso, siendo cada línea el nombre base del caso (sin extensión) seguido de sus puntos:

```
caso1 5
grupo2.caso1 10
grupo2.caso2 0
```
Asegúrese de que ningún archivo tenga espacios en su nombre. Para asignar puntos a un *grupo* como un todo en lugar de dividirlos entre sus casos, la convención es colocar el valor total de puntos del grupo en su **primer** caso y `0` en todos los demás casos del grupo.

## Límites

Los límites son los que el calificador impone en cada caso. Cada problema comienza desde un bloque de valores predeterminados en `\OmegaUp\Controllers\Problem::getDefaultProblemSettings` ([`Problem.php#L4549`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L4549)):

| Configuración | Predeterminado | Qué hace |
|---|---|---|
| **Límite de tiempo** (`TimeLimit`) | `1s` (1000 ms) | Tiempo máximo de **CPU** que el proceso del concursante puede ejecutar *por caso* antes de que el sistema operativo lo finalice con `TLE`. |
| **Límite de memoria** (`MemoryLimit`) | `64MiB` | RAM máxima (montón + pila) en [kibibytes](https://en.wikipedia.org/wiki/Kibibyte); superándolo es `MLE`. |
| **Límite de tiempo total de pared** (`OverallWallTimeLimit`) | `30s` | Tiempo máximo **real** en el que el calificador espera a que finalice *todo* el problema (todos los casos); de lo contrario, `TLE`. |
| **Tiempo adicional en la pared** (`ExtraWallTime`) | `0s` | Gracia adicional en tiempo real, utilizada principalmente para problemas `libinteractive` donde el proceso del evaluador también debe finalizar. |
| **Límite de salida** (`OutputLimit`) | `10240KiB` | Número máximo de bytes que el proceso puede escribir en stdout/stderr antes de finalizar con `OLE`. |
| **Límite de entrada** (`inputLimit`) | `10240` bytes | Tamaño máximo del *código fuente* del concursante: una palanca para detener las soluciones precalculadas/codificadas. |

Dos sutilezas que vale la pena interiorizar. En primer lugar, **el límite de tiempo es el tiempo de CPU, pero el límite general de tiempo de la pared es el tiempo real**: miden diferentes relojes a propósito. Un envío puede superar el límite general del muro incluso si ningún caso excede su límite de CPU. Cuando eso sucede, cualquier caso que no se haya ejecutado no se califica y, para mantener los resultados reproducibles, el calificador evalúa los casos en **orden lexicográfico**, por lo que qué casos "logran" por debajo de un límite general estricto es determinista, no un lanzamiento de moneda.

En segundo lugar, el **límite de salida normalmente se detecta automáticamente**: omegaUp toma el tamaño del archivo `.out` más grande y agrega **10 KiB** de espacio libre. Solo necesita configurarlo manualmente cuando usa un validador personalizado, porque entonces omegaUp no puede inferir el tamaño de salida esperado; por lo tanto, para problemas con el validador personalizado, proporcione `OutputLimit` explícitamente.

## Validadores

El validador decide *cómo* se compara la salida del concursante con su `.out`. omegaUp envía cinco tipos; las constantes de cadena viven en [`\OmegaUp\ProblemParams`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/ProblemParams.php#L28):

- **`token`**: lee todos los *tokens* (ejecuciones de hasta **4,194,304** caracteres imprimibles contiguos separados por espacios en blanco) de ambos archivos y requiere que las dos secuencias de tokens sean **idénticas**. Este es el valor predeterminado de todos los días y con lo que comienza `getDefaultProblemSettings`. Ignora cuánto espacio en blanco separa los tokens, que es lo que casi siempre desea.
- **`token-caseless`**: igual que `token`, pero todos los tokens se escriben en minúsculas primero, por lo que `Yes` y `yes` coinciden. Úselo cuando la respuesta sea una palabra y no quiera que las mayúsculas y minúsculas importen.
- **`token-numeric`**: lee tokens numéricos, los interpreta como números y requiere que las dos secuencias tengan la misma longitud *y* que cada número correspondiente coincida dentro de un **error absoluto O relativo de 1e-9** (ese es el `Tolerance`, [`Problem.php#L4562`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L4562)). Este es el de las respuestas de punto flotante, donde una coincidencia exacta de cadena rechazaría erróneamente `0.5000000001`.
- **`literal`**: coincidencia exacta byte por byte, sin tokenización. Consíguelo sólo cuando el espacio en blanco sea parte de la respuesta.
- **`custom`**: envía un programa de validación. Vea abajo.

### Validadores personalizados (`validator.<lang>`)

Cuando "comparar estos tokens" no es lo suficientemente expresivo (por ejemplo, cuando un problema tiene **muchas respuestas correctas**), escribes un validador. Coloque un solo archivo llamado `validator.<lang>` en la **raíz** del zip, donde `<lang>` es uno de `c`, `cpp`, `java`, `p` (Pascal) o `py`. Solo necesita un validador independientemente del idioma en el que presente el concursante.

Aquí está el modelo mental de lo que el evaluador le entrega a su validador:

- La salida del concursante llega a la **entrada estándar** del validador; léala normalmente con `scanf`/`cin`/`input()`. Se comporta como si el clasificador ejecutara `./contestant < data.in | ./validator casename`, donde `casename` es el nombre `.in` del caso actual sin la extensión.
- Puede utilizar `open("data.in")` para leer la *entrada del caso original* y `open("data.out")` para leer la *salida esperada* para ese caso, si necesita juzgarlo.
- Su validador **debe imprimir un número de punto flotante en `[0, 1]`** en la salida estándar: la fracción del caso que ganó el concursante. **No imprima nada y obtendrá `JE`.** Un valor inferior a `0` se fija en `0`; El `1` anterior está sujeto al `1`. Todo lo que escriba en *stderr* se ignora en la puntuación, pero es útil para la depuración.

Dos trampas que molestan a la gente: el validador **se ejecuta dentro de la misma zona de pruebas** que el código del concursante, por lo que si * falla o se comporta mal (`WA`, `RFE`, `RTE`,...) toda la presentación se considera como `JE`, no es culpa del concursante; pruebe su validador concienzudamente. Y aunque sus archivos `.out` nunca se comparan cuando usa un validador personalizado, **de todos modos debe enviar un `.out` para cada caso** (pueden ser archivos vacíos) para que se complete el emparejamiento.

Un validador para un problema de "imprimir la suma de `a` y `b`", aceptando la suma literal o el valor recalculado, en C++17:

```cpp
#include <iostream>
#include <fstream>

int main() {
  // Read "data.in" to recover the original case input.
  int64_t a, b;
  {
    std::ifstream original_input("data.in", std::ifstream::in);
    original_input >> a >> b;
  }
  // "data.out" holds the expected output for this case.
  int64_t expected;
  {
    std::ifstream original_output("data.out", std::ifstream::in);
    original_output >> expected;
  }

  // Standard input carries the contestant's output.
  int64_t contestant;
  if (!(std::cin >> contestant)) {
    // stderr is ignored by scoring but useful while debugging.
    std::cerr << "Could not read contestant output\n";
    std::cout << 0.0 << '\n';
    return 0;
  }

  if (expected != contestant && contestant != a + b) {
    std::cerr << "Wrong answer\n";
    std::cout << 0.0 << '\n';
    return 0;
  }

  std::cout << 1.0 << '\n';  // full credit for this case
  return 0;
}
```
Los problemas del validador personalizado también obtienen su **propio** bloque de límites, separado del del concursante, porque su programa de evaluación tiene diferentes necesidades de recursos. Cuando el tipo de validador es `custom` y no los anula, omegaUp completa `TimeLimit` `30s`, `MemoryLimit` `256MiB`, `OverallWallTimeLimit` `5s`, `OutputLimit` `10KiB`, `ExtraWallTime` `0s` ([`Problem.php#L4605`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L4605)). El **límite de tiempo del validador** separado (`validatorTimeLimit`) es el presupuesto en tiempo real que el calificador le da a su validador para emitir un veredicto por caso antes de darse por vencido con `JE`.

### "Salida estándar como puntuación"

Hay un sexto modo que vale la pena conocer: interpretar la salida estándar del concursante directamente como la puntuación. El calificador lee la salida estándar, la analiza como un flotante, la fija en `[0.0, 1.0]` y la utiliza como puntuación final. Esto se usa casi exclusivamente con problemas **interactivos**, donde dejar que el *interactor* (en lugar del concursante) declare la puntuación evita que el concursante simplemente imprima `1.0` para hacer trampa.

## Idiomas y modos de envío

"Idiomas" controla no sólo qué lenguajes de programación están permitidos sino todo el *modo* de envío:

- **Lenguajes normales**: C, C++ (múltiples estándares), Java, Kotlin, Python 2/3, Ruby, C#, Pascal y más. El concursante envía la fuente, omegaUp la compila y ejecuta.
- **Karel** — el lenguaje de bloque/robot, presentado como Karel-Java (`kj`) o Karel-Pascal (`kp`). Los problemas de Karel sólo se pueden crear mediante la ruta ZIP manual; El CDP no los apoya.
- **Solo salida** (`cat`): el concursante carga un `.zip` de respuestas para todos los casos en lugar de código. Si también desea permitir el envío de la respuesta de un solo caso como texto sin formato (sin zip), debe haber exactamente un caso llamado `Main.in`/`Main.out`.
- **Sin envíos**: desactiva el envío por completo. Esto existe sólo para que un "problema" pueda mostrar contenido dentro de un curso sin tener solución.

## Perillas de publicación

Un puñado de campos de metadatos determinan cómo se descubre y administra el problema:

- **Aparece en el listado público** (visibilidad): si el problema puede aparecer públicamente y reutilizarse en concursos y cursos de terceros. Los nuevos problemas son predeterminados **privados** (`VISIBILITY_PRIVATE`), por lo que no se filtra nada de lo que todavía estás redactando.
- **Aclaraciones por correo electrónico**: si omegaUp le envía por correo electrónico las aclaraciones que los concursantes preguntan sobre este problema, para que pueda responder sin tener que acampar en el sitio.
- **Fuente**: atribución del origen del problema (por ejemplo, `OMI 2020`).
- **Etiquetas** — etiquetas de clasificación; También puede elegir si los usuarios pueden agregar sus propias etiquetas.

## Errores comunes

Los dos fallos que hacen tropezar a casi todos los autores de manuales primerizos:

- **`cases/` y `statements/` deben ubicarse en la *raíz* del zip**, sin una carpeta de embalaje; este es un problema de empaquetado de larga data ([problema #310](https://github.com/omegaup/omegaup/issues/310)). Desde el directorio del problema en Linux/macOS, `zip -r myproblem.zip *` genera un archivo con la raíz correcta; comprimir la *carpeta que contiene* no lo hace.
- **Debe ser un `.zip`**, no un `.rar`, `.tar.bz2`, `.7z` o `.zx`. El propio nombre del archivo no importa.

## Documentación relacionada

- **[Formato del problema (ZIP manual)](problem-format.md)** — el diseño exacto del archivo, archivo por archivo
- **[Veredictos](../verdicts.md)**: lo que realmente significan `AC`, `PA`, `WA`, `TLE`, `MLE`, `OLE`, `RTE`, `JE` y el resto.
- **[API de problemas](../../reference/api.md)**: los puntos finales detrás de `apiCreate` y amigos
- **[Manual completo (GitHub)](https://github.com/omegaup/omegaup/blob/main/frontend/www/docs/Manual-for-Zip-File-Creation-for-Problems.md)** — detalle complementario en el repositorio principal
