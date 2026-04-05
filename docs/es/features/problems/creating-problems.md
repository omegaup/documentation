---
title: Creando problemas
description: Guía paso a paso para crear problemas de programación.
icon: bootstrap/plus-circle
---
# Creando problemas

Esta guía le guiará en la creación de problemas de programación en omegaUp.

## Inicio rápido

La forma más sencilla de crear un problema es utilizar el [Creador de problemas (CDP)](https://omegaup.com/problem/creator):

1. Visite [omegaup.com/problem/creator](https://omegaup.com/problem/creator)
2. Complete los detalles del problema
3. Agregar casos de prueba
4. Configurar límites e idiomas
5. Subir y publicar

!!! consejo "Videotutorial"
    Mire [este tutorial](https://www.youtube.com/watch?v=cUUP9DqQ1Vg) para obtener un recorrido visual.

## Componentes del problema

### Elementos requeridos

- **Título**: Nombre del problema
- **Alias**: Identificador corto (usado en URL)
- **Declaración**: descripción del problema (compatible con Markdown)
- **Casos de prueba**: archivos de entrada/salida
- **Validador**: Cómo se comparan los resultados
- **Límites**: limitaciones de tiempo y memoria

### Elementos opcionales

- **Fuente**: origen del problema (p. ej., "OMI 2020")
- **Etiquetas**: etiquetas de categorización
- **Código de validador**: programa de validación personalizado
- **Checker**: Comprobador de salida personalizado

## Tipos de validadores

| Tipo | Descripción |
|------|-------------|
| `literal` | Coincidencia exacta |
| `token` | Comparación token por token |
| `token-caseless` | Comparación de tokens que no distingue entre mayúsculas y minúsculas |
| `token-numeric` | Comparación numérica con tolerancia |
| `custom` | Validador definido por el usuario |

## Límites del problema

Configure los límites apropiados:

- **Límite de tiempo**: tiempo de ejecución por caso de prueba (milisegundos)
- **Límite de memoria**: límite de uso de memoria (KB)
- **Límite de salida**: Tamaño máximo de salida (bytes)

## Idiomas admitidos

omegaUp admite muchos lenguajes de programación:

- C, C++ (varios estándares)
- Java, Kotlin
- Pitón 2/3
- Rubí, Perl
- C#, Pascal
- Karel (Karel.js)
- Y más...

## Avanzado: Creación manual de ZIP

Para casos de uso avanzados, consulte [Formato del problema](problem-format.md) para la creación manual de archivos ZIP.

## Documentación relacionada

- **[Formato del problema](problem-format.md)** - Estructura del archivo ZIP
- **[API de problemas](../../api/problems.md)** - Puntos finales de API
- **[Formato de problema (ZIP)](problem-format.md)** — estructura manual del ZIP
- **[Manual extendido en GitHub](https://github.com/omegaup/omegaup/blob/main/frontend/www/docs/Manual-for-Zip-File-Creation-for-Problems.md)**
