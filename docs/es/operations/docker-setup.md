---
title: Configuración de la ventana acoplable
description: Configuración detallada de Docker Compose para desarrollo local
icon: bootstrap/tools
---
# Configuración de la ventana acoplable

omegaUp no es un solo programa: es una aplicación web PHP más un puñado de servicios Go más
sus almacenes de datos, y la única forma sensata de ejecutarlos todos en su máquina es Docker
Componga la pila en el [`docker-compose.yml`](https://github.com/omegaup/omegaup/blob/main/docker-compose.yml) del repositorio.
Esta página explica cómo comienza realmente esa pila y por qué, de modo que cuando algo se comporte mal
ya sabes qué contenedor mirar.

Si su objetivo es *contribuir* (clonar, iniciar, iniciar sesión, editar código), comience con
[Configuración de desarrollo](../getting-started/development-setup.md), que recorre el camino feliz.
Esta página es el mapa debajo de ella.

## Los servicios

Al levantar la pila (`docker-compose up`), se inician estos contenedores, cada uno de ellos fijado a un
imagen específica para que todos ejecuten las mismas versiones:

| Servicio | Imagen | Qué es |
| ------- | ----- | ---------- |
| `frontend` | `omegaup/dev-php` | La aplicación web PHP 8.1 (php-fpm detrás de nginx): la aplicación [MVC](../architecture/mvc-pattern.md) que sirve a cada página y los puntos finales `/api/`. Este es el contenedor en el que ejecuta pruebas, paquetes web y herramientas PHP. |
| `mysql` | `mysql:8.0.34` | La base de datos. Expuesto al host en el puerto **13306** (no el 3306 predeterminado, por lo que no colisionará con un MySQL que ya esté ejecutando). |
| `redis` | `redis` | Cache. |
| `rabbitmq` | `rabbitmq:3-management-alpine` | Cola de mensajes utilizada para trabajo asincrónico; la imagen del `-management` también te ofrece su consola web. |
| `gitserver` | `omegaup/gitserver:v1.9.13` | El servicio Go que almacena cada problema como un repositorio git. Consulte [Gitserver](../architecture/gitserver.md). |
| `grader` | `omegaup/backend` | El clasificador Go: recibe carreras, las pone en cola y las envía a los corredores. La interfaz lo alcanza a través de HTTP en `OMEGAUP_GRADER_URL` (`https://localhost:21680` predeterminado). |
| `runner` | `omegaup/runner` | The Go runner: compila y ejecuta envíos dentro de la minijail. |
| `broadcaster` | `omegaup/backend` | El servicio Go que envía actualizaciones de marcadores/veredictos al navegador a través de WebSockets. |
| `init-omegaupdata` | `alpine` | Un contenedor de inicio de corta duración que genera el volumen compartido de datos de problemas antes de que comiencen los servicios de larga ejecución. |

Grader, runner, broadcaster y gitserver son **binarios prediseñados** que se envían como Docker.
imágenes: no se crean a partir de este repositorio, que no contiene ninguna fuente de Go. ellos vienen
del [omegaup/quark](https://github.com/omegaup/quark) separado y
proyectos [omegaup/gitserver](https://github.com/omegaup/gitserver); ver
[Infraestructura](../architecture/infrastructure.md) para ver cómo encajan las piezas
producción.

## Volúmenes

Algunos volúmenes con nombre persisten en su estado después de los reinicios para que no vuelvas a inicializar todo cada vez:
`dbdata` (MySQL), `omegaupdata` (los datos del problema compartidos entre frontend, grader y gitserver
todo leído), además de `rabbitmq` y `redis`. Si la pila alguna vez se atasca genuinamente
estado, eliminar estos volúmenes y volver a sembrar es el gran martillo - ver
[Solución de problemas](troubleshooting.md).

## Producción versus desarrollo

`docker-compose.yml` es la pila de desarrollo. La producción ejecuta los mismos servicios en
Kubernetes de [`docker-compose.k8s.yml`](https://github.com/omegaup/omegaup/blob/main/docker-compose.k8s.yml)
con las imágenes `omegaup/php` y `omegaup/nginx` en lugar del `dev-php` todo en uno
imagen. La topología del servicio es la misma; el embalaje y el tamaño difieren. Ver
[Implementación](deployment.md).
