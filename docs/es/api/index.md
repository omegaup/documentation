---
title: Referencia de API
description: Documentación completa de la API REST para omegaUp
icon: bootstrap/api
---
# Referencia de API

omegaUp proporciona una API REST completa a la que se puede acceder directamente. Todos los puntos finales utilizan métodos HTTP estándar (`GET` o `POST`) y devuelven respuestas JSON.

## URL base

Todos los puntos finales de API tienen el prefijo:

```
https://omegaup.com/api/
```
En esta documentación, solo se muestra la parte de la URL **después** de este prefijo.

## Autenticación

!!! advertencia "Se requiere HTTPS"
    Sólo se permiten conexiones HTTPS. Las solicitudes HTTP devolverán `HTTP 301 Permanent Redirect`.

Algunos puntos finales son públicos y no requieren autenticación. Los puntos finales protegidos requieren autenticación a través de un `auth_token` obtenido del punto final [`user/login`](users.md#login).

El token debe incluirse en una cookie denominada `ouat` (token de autenticación omegaUp) para solicitudes autenticadas.

!!! importante "Sesión única"
    omegaUp solo admite una sesión activa a la vez. Iniciar sesión mediante programación invalidará la sesión de su navegador y viceversa.

## Categorías API

<div class="grid cards" markdown>

- :material-trophy:{ .lg .middle } __[API de concursos](contests.md)__

    ---

    Crear, gestionar y participar en concursos de programación.

    [:octicons-arrow-right-24: Explorar](contests.md)

- :material-puzzle:{ .lg .middle } __[API de problemas](problems.md)__

    ---

    Crear, actualizar y gestionar problemas de programación.

    [:octicons-arrow-right-24: Explorar](problems.md)

- :material-account:{ .lg .middle } __[API de usuarios](users.md)__

    ---

    Gestión de usuarios, autenticación y operaciones de perfiles.

    [:octicons-arrow-right-24: Explorar](users.md)

- :material-code-braces:{ .lg .middle } __[Ejecuta API](runs.md)__

    ---

    Envíe el código, verifique el estado y recupere los resultados del envío.

    [:octicons-arrow-right-24: Explorar](runs.md)

- :material-message-text:{ .lg .middle } __[API de aclaraciones](clarifications.md)__

    ---

    Hacer y responder preguntas durante los concursos.

    [:octicons-arrow-right-24: Explorar](clarifications.md)

</div>

## Ejemplo rápido

Obtenga la hora actual del servidor (punto final público):

```bash
curl https://omegaup.com/api/time/get/
```
Respuesta:

```json
{
  "time": 1436577101,
  "status": "ok"
}
```
## Formato de respuesta

Todas las respuestas de API siguen un formato consistente:

```json
{
  "status": "ok",
  "data": { ... }
}
```
Respuestas de error:

```json
{
  "status": "error",
  "error": "Error message",
  "errorcode": 400
}
```
## Catálogo completo de endpoints

Este sitio documenta las **categorías** principales de la API. El índice **generado y autoritativo** de controladores y rutas está en el repositorio principal:

**[frontend/server/src/Controllers/README.md](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/README.md)**

Convención: una petición a `/api/<segmento>/<acción>/` la maneja `<Segmento>Controller::api<Acción>` en `frontend/server/src/Controllers/` (con los ajustes de nombre habituales en PHP).

## Limitación de velocidad

Algunos puntos finales tienen límites de velocidad para evitar abusos:

- **Envíos**: un envío por problema cada 60 segundos
- **Llamadas API**: varía según el punto final

Las respuestas sobre el límite de velocidad excedido incluyen:

```json
{
  "status": "error",
  "error": "Rate limit exceeded",
  "errorcode": 429
}
```
## Documentación relacionada

- **[Guía de autenticación](authentication.md)** - Flujo de autenticación detallado
- **[Descripción general de la arquitectura](../architecture/index.md)** - Arquitectura del sistema
- **[Guías de desarrollo](../development/index.md)** - Uso de la API en desarrollo

---

**¿Listo para usar la API?** Comience con [Autenticación](authentication.md) o explore las [categorías de API](#api-categories) arriba.
