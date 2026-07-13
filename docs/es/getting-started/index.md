---
title: Empezando
description: Comienza tu viaje contribuyendo a omegaUp
icon: bootstrap/rocket-launch
---
# Primeros pasos con el desarrollo de omegaUp

¡Bienvenido! Esta guía lo ayudará a comenzar a contribuir con omegaUp, una plataforma educativa gratuita que ayuda a mejorar las habilidades de programación.

## ¿Qué es omegaUp?

omegaUp es una plataforma de programación educativa utilizada por decenas de miles de estudiantes y profesores en América Latina. Proporciona:

- **Resolución de problemas**: Miles de problemas de programación con evaluación automática
- **Concursos**: organizar concursos de programación.
- **Cursos**: rutas de aprendizaje estructuradas
- **Entrenamiento**: Practicar problemas organizados por tema y dificultad

## Antes de comenzar

Si eres nuevo en omegaUp, te recomendamos:

1. **Experimente la plataforma**: visite [omegaUp.com](https://omegaup.com/), cree una cuenta y resuelva algunos problemas
2. **Más información sobre nosotros**: Explore [omegaup.org](https://omegaup.org/) para obtener más información sobre nuestra organización
3. **Comprenda el código base**: revise la [Descripción general de la arquitectura](../architecture/index.md) para comprender cómo funciona omegaUp.

## Ruta de inicio rápido

<div class="grid cards" markdown>

- :material-docker:{ .lg .middle } __[Configuración de desarrollo](development-setup.md)__

    ---

    Configure su entorno de desarrollo local utilizando Docker. Este es el primer paso para empezar a contribuir.

    [Guía de configuración de :octicons-arrow-right-24:](development-setup.md)

- :material-source-branch:{ .lg .middle } __[Guía contribuyente](contributing.md)__

    ---

    Aprenda a bifurcar el repositorio, crear ramas y enviar solicitudes de extracción.

    [Contribución :octicons-arrow-right-24:](contributing.md)

- :material-help-circle:{ .lg .middle } __[Obteniendo ayuda](getting-help.md)__

    ---

    ¿Atascado? Aprenda a hacer preguntas de manera efectiva y obtenga ayuda de la comunidad.

    [:octicons-arrow-right-24: Obtenga ayuda](getting-help.md)

</div>

## Descripción general del entorno de desarrollo

omegaUp utiliza Docker para el desarrollo local. A alto nivel:

- **Web + API**: **controladores PHP 8.1** y DAO sobre **MySQL 8** (MVC clásico; API JSON)
- **Juez**: **Go** calificador, corredores y **minijail** sandbox: un servicio separado (`omegaup/quark`) al que el backend llama a través de HTTP
- **UI del navegador**: **Vue 2.7** componentes de un solo archivo, **TypeScript**, **Bootstrap 4**, renderizados dentro de un shell de servidor **Twig 3**
- **Problema de almacenamiento**: **gitserver** y diseño zip/case como se documenta en [Características → Problemas](../features/problems/index.md)

### Dónde viven las cosas en el repositorio (mapa rápido)

| Área | Ruta (en el repositorio principal) |
|------|--------------------------------|
| API HTTP/reglas comerciales | `frontend/server/src/Controllers/` |
| Acceso a la base de datos | `frontend/server/src/DAO/` |
| Migraciones | `frontend/database/` |
| Mecanografiado/Vue | `frontend/www/js/` |
| Plantillas heredadas / i18n | `frontend/templates/` |
| Pruebas de API PHPUnit | `frontend/tests/controllers/` |
| Ciprés E2E | `cypress/e2e/` |

### Artículos (contexto arquitectónico)

- [omegaUp: sistema de gestión de concursos basado en la nube](http://www.ioinformatics.org/oi/pdf/v8_2014_169_178.pdf) (IOI Journal, 2014)
- [libinteractive](https://ioinformatics.org/journal/v9_2015_3_14.pdf) — tareas interactivas

## Navegadores compatibles (colaboradores y concursantes)

Utilice un navegador **actual y actual** (**Chrome**, **Firefox**, **Safari** o **Edge**). El sitio es **solo HTTPS**. Las versiones muy antiguas de Internet Explorer **no** son compatibles.

## Cuentas de Desarrollo

Cuando configure su entorno local, tendrá acceso a dos cuentas preconfiguradas:

| Nombre de usuario | Contraseña | Rol |
|----------|----------|------|
| `omegaup` | `omegaup` | Administrador |
| `user` | `user` | Usuario habitual |

## Próximos pasos

1. **[Configura tu entorno de desarrollo](development-setup.md)** - Ejecuta Docker y clona el repositorio
2. **[Lea la guía de contribución](contributing.md)** - Conozca el flujo de trabajo para enviar cambios
3. **[Explora la arquitectura](../architecture/index.md)** - Comprenda cómo está estructurado omegaUp
4. **[Revisar las pautas de codificación](../development/coding-guidelines.md)** - Conozca nuestros estándares de codificación

## Recursos

- **Sitio web**: [omegaup.com](https://omegaup.com)
- **GitHub**: [github.com/omegaup/omegaup](https://github.com/omegaup/omegaup)
- **Discord**: [Únase a nuestro servidor de Discord](https://discord.gg/gMEMX7Mrwe) para obtener apoyo de la comunidad
- **Problemas**: [Informar errores o solicitar funciones](https://github.com/omegaup/omegaup/issues)

---

¿Listo para empezar? Dirígete a [Configuración de desarrollo](development-setup.md) para comenzar.
