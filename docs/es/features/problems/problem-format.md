---
title: Formato del problema
description: Estructura ZIP para creación manual de problemas
icon: bootstrap/file-document
---

# Formato del problema (ZIP manual)

Para la mayoría de autores basta el [Problem Creator](https://omegaup.com/problem/creator) (CDP) o el editor en el sitio. Esta página es para empaquetar **manualmente** un `.zip` cuando necesitas control total (por ejemplo **Karel**, tareas **interactivas** o **validadores personalizados**).

!!! tip "Videotutoriales"
    ZIP manual: [parte 1](https://www.youtube.com/watch?v=LfyRSsgrvNc), [parte 2](https://www.youtube.com/watch?v=i2aqXXOW5ic). CDP: [YouTube](https://www.youtube.com/watch?v=cUUP9DqQ1Vg).

## Estructura del ZIP (resumen)

Usa un archivo **`.zip`** (no RAR/7z). El nombre del archivo da igual.

```
problem.zip
├── cases/
├── statements/
├── solutions/
├── interactive/
├── validator.cpp
├── settings.json
├── limits.json
└── testplan
```

Ejemplo de referencia en el repo: [`frontend/tests/resources/testproblem.zip`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/resources/testproblem.zip).

## Qué se configura (idea general)

| Área | Significado |
|------|-------------|
| **Tipo de validador** | Comparación token a token, sin mayúsculas, tolerancia numérica, “stdout como puntaje” (interactivo) o **custom** `validator.<lang>` |
| **Lenguajes** | Modos permitidos: lenguajes normales, **Karel**, **solo salida** (`.zip` de respuestas; un solo caso puede ser `Main.in`/`Main.out` para texto plano), **sin envíos** |
| **Límites** | Tiempo CPU por caso, tiempo total, validador, memoria (KiB), tamaño de salida |
| **Límite de código** | Tamaño máximo del fuente del concursante |
| **Público / etiquetas / fuente** | Visibilidad y atribución |

## `cases/`

- Pares **`.in`** y **`.out`** con la misma base (`1.in` / `1.out`).
- **Casos agrupados**: un **punto** en el nombre separa grupo y caso, p. ej. `grupo1.caso1.in`.
- Evita puntos extra si no quieres agrupar.
- Tamaños enormes hacen lento el jueceo en vivo.

## `statements/`

- Markdown por idioma: `es.markdown`, `en.markdown`, `pt.markdown`.
- Vista previa: [omegaup.com/redaccion.php](https://omegaup.com/redaccion.php).
- Variables tipo `$n$`, `$x_i$`.

## `solutions/`

Opcional, mismo esquema de nombres que statements. Ejemplos en [`frontend/tests/resources`](https://github.com/omegaup/omegaup/tree/main/frontend/tests/resources).

## `interactive/` y libinteractive

Tareas interactivas con [libinteractive](https://omegaup.com/libinteractive/). Ejemplo: [Cave (IOI 2013)](https://omegaup.com/resources/cave.zip).

## Validador personalizado (`validator.<lang>`)

Un solo archivo en la raíz: `validator.c`, `validator.cpp`, `validator.java`, `validator.p` o `validator.py`.

- Comportamiento típico: `./concursante < data.in | ./validator basecaso`.
- Puede leer `data.in` y `data.out`.
- Debe imprimir un flotante en **[0, 1]**; vacío → **JE**.

Manual largo con ejemplos: [`Manual-for-Zip-File-Creation-for-Problems.md`](https://github.com/omegaup/omegaup/blob/main/frontend/www/docs/Manual-for-Zip-File-Creation-for-Problems.md).

## `testplan` y pesos

Si existe, define pesos por grupo; si no, reparto uniforme (coherente con el grader; ver `testproblem.zip`).

## Documentación relacionada

- **[Crear problemas](creating-problems.md)**
- **[Veredictos](../verdicts.md)**
