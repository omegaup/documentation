---
title: Problemas
description: Creación y gestión de problemas de programación en omegaUp.
icon: bootstrap/puzzle
---
# Problemas

omegaUp admite la creación de problemas de programación a través de dos métodos: el Creador de problemas visual (CDP) o la generación manual de archivos ZIP.

## Métodos de creación de problemas

### Creador de problemas omegaUp (CDP)

El [Creador de problemas](https://omegaup.com/problem/creator) es una herramienta visual para crear problemas:

- ✅ Interfaz fácil de usar
- ✅ Flujo de trabajo intuitivo
- ⚠️ Algunas limitaciones (por ejemplo, no hay problemas con Karel)

!!! Consejo "Tutorial"
    Mire [este videotutorial](https://www.youtube.com/watch?v=cUUP9DqQ1Vg) para aprender a utilizar Problem Creator.

### Generación manual de archivos ZIP

Para casos de uso avanzados, puede crear manualmente un archivo `.zip`:

- ✅ Control total sobre la estructura del problema.
- ✅ Admite todo tipo de problemas, incluido Karel
- ✅ Validadores personalizados y casos de prueba.

Consulte [Formato del problema](problem-format.md) para obtener instrucciones detalladas.

## Componentes del problema

Un problema consiste en:

- **Declaración**: Descripción del problema (Markdown)
- **Casos de prueba**: Archivos de entrada/salida (`.in`/`.out`)
- **Validador**: Cómo se comparan los resultados
- **Límites**: limitaciones de tiempo y memoria
- **Idiomas**: lenguajes de programación compatibles

## Documentación relacionada

- **[Creando problemas](creating-problems.md)** - Guía de creación paso a paso
- **[Formato del problema](problem-format.md)** - Estructura y formato del archivo ZIP
- **[API de problemas](../../reference/api.md)** - Puntos finales de API para problemas
