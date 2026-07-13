---
title: Referencia de API
description: Cómo llamar a la API REST de omegaUp y dónde reside la referencia autorizada y siempre actualizada del punto final
icon: bootstrap/api
---
# Referencia de API

Todo lo que hace la interfaz web de omegaUp, lo hace llamando a la misma API REST pública que usted
Puedes llamarte a ti mismo. Cada página de la Arena, cada actualización del marcador, cada envío es
una solicitud HTTP a `/api/...`, por lo que no hay nada que la interfaz de usuario pueda hacer que la API no pueda.

!!! tenga en cuenta "Dónde reside la referencia punto por punto"

    Esta página documenta las **reglas transversales** que se aplican a *cada* llamada:
    transporte, autenticación y sobre de respuesta. Deliberadamente **no**
    enumerar puntos finales individuales, porque esa lista se **genera a partir del código fuente** y
    Se pudriría en el momento en que fuera copiado aquí a mano.

    La superficie autoritaria y siempre actual se genera mediante
    [`frontend/server/cmd/APITool.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/cmd/APITool.php)
    - la misma herramienta que emite el cliente frontend escrito
    [`api.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/api.ts)
    y [`api_types.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/api_types.ts).
    Para ver exactamente lo que un controlador acepta y devuelve, lea el controlador en
    [`frontend/server/src/Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers)
    (cada método `apiXxx` es un punto final) o sus documentos generados, en lugar de un
    mesa mantenida a mano.

## Las reglas que se aplican a cada llamada.

**Es HTTP simple, GET o POST, JSON back.** Cada punto final se invoca con un comando normal.
Solicitud HTTP y devuelve un estado HTTP apropiado más un cuerpo JSON. Llamadas de solo lectura que
No se necesitan privilegios, se puede crear con un GET: literalmente puedes pegar la URL en un navegador.
y ver el JSON.

**Solo HTTPS: HTTP se rechaza, no se degrada silenciosamente.** Porque omegaUp se preocupa por
mantener la privacidad de los datos de los usuarios y evitar trampas (alguien husmeando el tráfico del concurso es un
amenaza real, no hipotética), la API se sirve exclusivamente a través de HTTPS. una llamada terminada
HTTP simple no funciona silenciosamente: el servidor responde con una redirección permanente HTTP 301
a la URL segura, y un cliente que no la sigue no obtendrá nada útil.

**Cada URL comienza con el mismo prefijo.** Todos los puntos finales se encuentran bajo
`https://omegaup.com/api/`; el resto de la ruta selecciona el controlador y el método. Por
Por convención nombramos los puntos finales por lo que viene *después* de ese prefijo, por lo que un punto final escrito
aquí como `time/get` es realmente `https://omegaup.com/api/time/get/`.

**La autenticación es un token en una cookie llamada `ouat`.** La mayoría de las llamadas no necesitan especial
privilegio, pero los que actúan en su cuenta requieren que inicie sesión.
llamando al `user/login`, tome el `auth_token` que devuelve y envíelo en cada sesión posterior.
llamar como una cookie denominada **`ouat`** (token de autenticación omegaUp). Una consecuencia importante, nuevamente
impulsado por anti-trampas: **solo puedes tener una sesión activa a la vez.** Si inicias sesión
mediante programación invalidas la sesión de tu navegador y viceversa.

## El sobre de respuesta

Cada respuesta es JSON y lleva un campo `status`. En caso de éxito es `"ok"`; en el fracaso
es `"error"` y el cuerpo también lleva un `errorcode` legible por máquina, un estable
`errorname`, y un mensaje `error` **localizado** legible por humanos adecuado para mostrar a un
usuario en su propio idioma. Maneje las fallas ramificándose en `status`/`errorname`, nunca por
coincidencia en el texto `error` legible por humanos: ese texto se traduce y cambiará.

## Un ejemplo trabajado

La llamada más simple posible recupera el reloj del servidor, lo cual es útil para corregir un
reloj local que puede estar sesgado:

```console
$ curl https://omegaup.com/api/time/get/
{"time":1436577101,"status":"ok"}
```
No necesita privilegios, por lo que no hay ninguna cookie `ouat`, el estado es `HTTP 200 OK` y
`time` es una marca de tiempo UNIX directamente del reloj interno del servidor.

## Ver también

- **[Enlaces útiles](links.md)**: repositorios, guías de contribución y archivos generados automáticamente.
  documentos del controlador.
- **[System Internals](../architecture/internals.md)** — cómo llama una API a
  `run/create` en realidad fluye a través de `\OmegaUp\ApiCaller` hacia un controlador y luego al
  calificador.
