---
title: Descripción general de la API REST
description: Documentación completa de la API REST para omegaUp
icon: bootstrap/cloud
---
# API REST omegaUp

omegaUp proporciona una API REST completa a la que se puede acceder directamente. Todos los puntos finales utilizan métodos HTTP estándar (`GET` o `POST`) y devuelven respuestas con formato JSON.

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

## Formato de respuesta

Todas las respuestas de API siguen un formato consistente:

### Respuesta exitosa

```json
{
  "status": "ok",
  "data": { ... }
}
```
### Respuesta de error

```json
{
  "status": "error",
  "error": "Error message",
  "errorcode": 400
}
```
## Categorías API

- **[API de concursos](contests.md)** - Gestión y participación del concurso
- **[API de problemas](problems.md)** - Creación y gestión de problemas
- **[API de usuarios](users.md)** - Gestión y autenticación de usuarios
- **[Ejecuta API](runs.md)** - Manejo de envíos y resultados
- **[API de Aclaraciones](clarifications.md)** - Aclaraciones del concurso

## Ejemplo: Obtener la hora del servidor

Este es un punto final público que no requiere autenticación:

**Solicitud:**
```bash
GET https://omegaup.com/api/time/get/
```
**Respuesta:**
```json
{
  "time": 1436577101,
  "status": "ok"
}
```
### Detalles del punto final

**`GET time/get/`**

Devuelve la marca de tiempo actual de UNIX según el reloj interno del servidor. Útil para sincronizar relojes locales.

| Campo | Tipo | Descripción |
|---------|--------|--------------------------------------------------|
| estado | cadena | Devuelve `"ok"` si la solicitud fue exitosa |
| tiempo | entero | Marca de tiempo UNIX que representa la hora del servidor |

**Permisos requeridos:** Ninguno

## Catálogo completo de endpoints

Para una lista **exhaustiva** de métodos agrupados por controlador, consulte el **[README de Controllers](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/README.md)** generado automáticamente en el repositorio omegaUp. Las páginas aquí (`users.md`, `contests.md`, …) cubren los flujos más frecuentes; el README es la mejor referencia para un nombre concreto de `apiAlgo`.

## Limitación de velocidad

Algunos puntos finales tienen límites de velocidad:

- **Envíos**: un envío por problema cada 60 segundos
- **Llamadas API**: varía según el punto final

Límite de tasa excedido respuestas:

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

**¿Listo para usar la API?** Explore las [categorías de API](#api-categories) o comience con [Autenticación](authentication.md).
