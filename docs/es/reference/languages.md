---
title: Idiomas admitidos
description: Lenguajes de programación soportados por omegaUp
icon: bootstrap/code-tags
---
# Idiomas admitidos

omegaUp acepta envíos en un conjunto fijo de idiomas: la columna `language` en una ejecución es
una enumeración, por lo que un envío es siempre uno de los identificadores siguientes y nada más. la lista
a continuación se muestra esa enumeración, exactamente como la define la base de datos. Cuando envías a través del
[API](api.md), pasa uno de estos identificadores cortos (por ejemplo, `cpp17-gcc`), no un
nombre legible por humanos.

Se aplican dos convenciones en cada lenguaje compilado, y hacen tropezar a las personas si no las hacen.
conocerlos:

- **Su punto de entrada debe llamarse `Main`.** No existe una configuración de compilación por problema;
  el corredor compila por convención. El archivo fuente principal (y, para los idiomas que lo necesitan,
  la clase principal) debe llamarse `Main` — `Main.java` con `public class Main`, un `Main`
  ejecutable para C/C++, etc. Consulte [Partes internas del corredor](../architecture/runner-internals.md)
  para saber cómo ocurre realmente la compilación dentro del sandbox.
- **Cuando un idioma ofrece tanto GCC como Clang**, el identificador nombra la cadena de herramientas
  explícitamente (`-gcc` vs `-clang`), porque los dos ocasionalmente no están de acuerdo en límites
  cumplimiento de estándares y quien planteó el problema puede haberlo probado contra uno de ellos.

## Los idiomas

### C y C++

Los caballos de batalla de la programación competitiva y la razón por la que la lista de C++ es tan larga: cada uno
La revisión estándar es un identificador separado, por lo que un problema anterior sigue compilándose de la misma manera.
siempre lo hizo:

| Identificador | Idioma |
| ---------- | -------- |
| `c` | C (CCG heredado) |
| `c11-gcc`, `c11-clang` | C11 |
| `cpp` | C++ (CCG heredado) |
| `cpp11`, `cpp11-gcc`, `cpp11-clang` | C++11 |
| `cpp17-gcc`, `cpp17-clang` | C++17 |
| `cpp20-gcc`, `cpp20-clang` | C++20 |

Para nuevos envíos de C++ casi siempre querrás `cpp17-gcc` o `cpp20-gcc`.

### Otros lenguajes de propósito general

| Identificador | Idioma |
| ---------- | -------- |
| `java` | Java |
| `kt` | Kotlin |
| `py3` | Pitón 3 |
| `py2` | Pitón 2 |
| `py` | Python (alias heredado) |
| `cs` | C# |
| `rb` | Rubí |
| `pl` | Perla |
| `pas` | Pascal |
| `hs` | Haskel |
| `lua` | Lúa |
| `go` | Ir |
| `rs` | Óxido |
| `js` | JavaScript |

### Los especiales

Tres identificadores no son lenguajes de propósito general, y saber cuáles son explica una
Mucho sobre para quién está diseñado omegaUp:

- **`kp` y `kj` — Karel.** omegaUp surgió de la Olimpiada Mexicana de Informática, cuyo
  La pista de nivel básico utiliza **Karel the Robot**, un lenguaje de enseñanza en el que se programa un robot.
  en una cuadrícula. `kp` es Karel con sintaxis con sabor a Pascal y `kj` es Karel con sintaxis con sabor a Java
  sintaxis: el mismo lenguaje, dos gramáticas superficiales, por lo que un principiante puede usar cualquiera que sea su
  clase impartida. Los problemas de Karel son un ciudadano de primera, no una novedad.
- **`cat`: solo salida.** Para problemas en los que no envía ningún programa, envía
  la *respuesta*. El "lenguaje" `cat` significa que el corredor simplemente trata su envío como el
  resultado que se va a validar con el resultado esperado. Así es como solo salida y
  Los problemas con archivos de datos funcionan.

!!! nota "El conjunto cambia con el tiempo"
    Se agregan nuevos estándares y cadenas de herramientas a medida que maduran (la lista de C++ es la más clara).
    constancia de ello). Trate la tabla anterior como actual; la fuente autorizada es la
    Enumeración `language` en [`frontend/database/schema.sql`](https://github.com/omegaup/omegaup/blob/main/frontend/database/schema.sql)
    y las versiones del compilador configuradas en el ejecutor ([omegaup/quark](https://github.com/omegaup/quark)).
