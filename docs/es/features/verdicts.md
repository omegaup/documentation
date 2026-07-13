---
title: Veredictos y puntuación
description: Comprender los veredictos de presentación y los modelos de puntuación
icon: bootstrap/check-circle
---
# Veredictos y puntuación

Cada envío que realiza termina su vida como un **veredicto**: un código corto que dice lo que
sucedió cuando el evaluador ejecutó su programa en los casos de prueba del problema. el veredicto
Lo que ves en la Arena es lo *peor* que pasó en todos los casos en los que el evaluador
ejecutó: omegaUp informa la falla más grave, porque un programa se equivoca en un caso
está mal, no importa cuántos otros hayan acertado.

El veredicto se almacena en cada ejecución en la columna `verdict` de `Runs` y `Submissions`.
tablas, y es uno de exactamente doce valores. Son, aproximadamente de mejor a peor:

| Código | Nombre | Lo que significa |
| ---- | ---- | ------------- |
| `AC` | Aceptado | Todos los casos de la carrera pasaron. La máxima puntuación. |
| `PA` | Aceptado parcialmente | Algunos grupos de casos aprobaron o un validador personalizado otorgó un crédito fraccionario. Su puntuación está estrictamente entre 0 y el máximo. |
| `PE` | Error de presentación | La respuesta es esencialmente correcta, pero su formato está incorrecto. Un veredicto heredado: la mayoría de los problemas ahora utilizan validadores de tokens que ignoran los espacios en blanco, por lo que rara vez los verá. |
| `WA` | Respuesta incorrecta | El programa se ejecutó hasta su finalización pero produjo un resultado que el validador rechazó. |
| `TLE` | Límite de tiempo excedido | El programa no finalizó dentro del `time_limit` del problema (por ejemplo, 1000 ms). También en qué se convierte un punto muerto o una espera infinita en la entrada. |
| `OLE` | Límite de salida excedido | El programa escribió más resultados de los permitidos, generalmente un bucle infinito con un `print` en su interior. |
| `MLE` | Límite de memoria excedido | El programa intentó utilizar más que el `memory_limit` (por ejemplo, 32768 KiB). |
| `RTE` | Error de tiempo de ejecución | El programa falló: un código de salida distinto de cero, una excepción no detectada, un error de segmentación, una señal. |
| `RFE` | Error de función restringida | El programa intentó una llamada al sistema que el sandbox prohíbe (un socket, un fork, un archivo inesperado). Minijail lo atrapó y eliminó el programa. Consulte [Zona de pruebas](sandbox.md). |
| `CE` | Error de compilación | El código no se compiló. Se devuelve el `stderr` del compilador para que pueda ver por qué: el único veredicto decidido antes de que se ejecute cualquier caso. |
| `JE` | Error del juez | Algo salió mal *del lado de omegaUp*, no del suyo: un corredor murió en medio de la evaluación, faltaba un expediente del caso, surgió un error interno. Volver a enviarlo generalmente lo borra; si no es así, dínoslo. |
| `VE` | Error del validador | El propio validador personalizado del problema falló o devolvió tonterías. Un error que plantea problemas, no un error de concursante. |

## Por qué el veredicto es una decisión de grupo, no una decisión de caso

Una sola ejecución es en realidad un lote de muchas ejecuciones (una por archivo `.in`) y cada ejecución
obtiene su propio veredicto por caso dentro de la niveladora (`AC`, `WA`, `TLE`,…). el veredicto que usted
Finalmente vemos que es el agregado, y la regla de agregación es donde se observa el comportamiento interesante.
vidas, porque está directamente relacionado con la **puntuación**.

casos de prueba de grupos omegaUp: todo lo que está antes del primer `.` en el nombre de archivo de un caso es su
**grupo** (por lo que `3.foo.in` y `3.bar.in` pertenecen al grupo `3`; un caso sin punto, como
`5.in`, forma su propio grupo `5`). Un grupo otorga sus puntos sólo si **todos** los casos en él
volvió `AC` o `PA`: el modelo "todo o nada por subtarea" los problemas competitivos dependen
adelante, donde una solución parcialmente correcta para una subtarea no genera nada para esa subtarea.

Los pesos de los casos provienen del archivo `testplan` del problema, si tiene uno (normalizado para que sumen
a 1); de lo contrario, cada caso vale `1 / number-of-cases`. La puntuación de la carrera es la suma de
los pesos de los grupos que aprobaron completamente, multiplicados por los puntos que vale el problema
en el concurso actual (o escalado al 100% en el modo de práctica). Entonces `PA` – una puntuación fraccionaria –
es lo que obtienes cuando algunos grupos pasan y otros no, o cuando un validador personalizado te entrega
devolver una puntuación parcial para un caso.

Para la ruta completa que toma un envío desde `/api/run/create/` a través de las colas, el
corredor, los validadores y de regreso al marcador, consulte [Partes internas del sistema](../architecture/internals.md)
y [Partes internas del clasificador](../architecture/grader-internals.md).

## Validadores: cómo un caso se convierte en AC o WA

El evaluador decide el veredicto de cada caso con un **validador**. Los validadores incorporados
tokenice el resultado esperado y el resultado del concursante en espacios en blanco y luego compare:

- **`token`** — comparar token por token; la primera discrepancia (o una secuencia que termina antes de la
  otro) es un `WA`. El valor predeterminado para la mayoría de los problemas.
- **`token-caseless`**: lo mismo, pero no distingue entre mayúsculas y minúsculas.
- **`token-numeric`**: ignora los tokens no numéricos, analiza el resto como punto flotante y
  comparar con una tolerancia. Esto es lo que permite que un problema acepte `3.14159` donde dice la clave
  `3.14160`.
- **`literal`**: una coincidencia exacta, sin tokenización.
- **`custom`** — el problema incluye su propio programa validador que lee la información del concursante.
  salida (y, para algunos problemas, la entrada) y decide el veredicto en sí, opcionalmente
  otorgar una puntuación parcial. Un fallo aquí es lo que produce `VE`.

!!! nota "El veredicto informado es el más severo"
    Cuando depures un envío, recuerda que el veredicto es el peor de los casos en todo el proceso.
    correr. Una ejecución que muestra `TLE` puede estar resolviendo la mayoría de los casos correctamente y agotando el tiempo en uno grande.
    uno: abra los detalles de la ejecución para ver el desglose por caso antes de concluir todo el proceso.
    El enfoque es incorrecto.
