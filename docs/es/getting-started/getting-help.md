---
title: Obtener ayuda
description: Aprenda cómo hacer preguntas de manera efectiva y obtener ayuda de la comunidad omegaUp
icon: bootstrap/help-circle
---
# Obtener ayuda

Tendrá preguntas: sobre cómo el entorno de desarrollo se niega a aparecer, sobre un seguimiento de pila en lo profundo de `frontend/server/src/Controllers/`, sobre cómo funciona realmente el proceso de solicitud de GSoC en omegaUp. Esto es lo que se espera y se recomienda preguntar. Pero *cómo* preguntas decide qué tan buena respuesta obtienes y qué tan rápido llega, por lo que esta página es menos una lista de enlaces de chat y más una guía para obtener una buena respuesta a tu pregunta. Toda la filosofía detrás de esto es una sola línea: cuanto más contexto pongas al principio, menos idas y venidas gastan todos y es más probable que un voluntario ocupado se detenga para ayudarte.

## Busca antes de preguntar

Casi todas las preguntas que responde un recién llegado han sido respondidas antes, a menudo varias veces, a menudo la misma semana durante la temporada GSoC. Así que el primer paso nunca es "publicar la pregunta": es una búsqueda de dos minutos, porque es muy probable que la respuesta ya esté escrita en algún lugar y la obtendrás instantáneamente en lugar de esperar horas hasta que un humano se despierte en otra zona horaria.

Vale la pena buscar tres lugares, aproximadamente en este orden de utilidad:

- **Este sitio de documentación.** Utilice el cuadro de búsqueda en la parte superior. Si su problema es la configuración del entorno, la página [Configuración de desarrollo](development-setup.md) recorre todo el flujo de `docker compose`; si se trata de abrir una solicitud de extracción, [Contribuyendo a omegaUp](contributing.md) cubre el flujo de trabajo de git; si se trata de "cómo funciona *este* subsistema", la sección [Arquitectura](../architecture/index.md) rastrea las rutas del código real de extremo a extremo. Si su pregunta tiene forma de API, la [referencia de API](../reference/api.md) generada enumera todos los puntos finales.
- **Historial de mensajes de Discord.** Nuestra comunidad vive en el [servidor omegaUp Discord](https://discord.com/invite/K3JFd9d3wk), y el canal de trabajo para los contribuyentes es **#dev_training**. La barra de búsqueda de Discord es realmente poderosa: busque una palabra clave de su error (`port already allocated`, `wait-for-it`, el nombre de un servicio que falla) y muy a menudo llegará a un hilo donde alguien preguntó exactamente esto, este año o el año pasado, con la solución ya publicada debajo. Es por eso que insistimos en que todos publiquen públicamente (más sobre esto a continuación): el archivo con capacidad de búsqueda solo existe porque las preguntas anteriores se hicieron donde todos podían verlas.
- **Google.** Si su pregunta es sobre Git, Docker, PHP 8.1, TypeScript o cualquier cosa que no sea específica de omegaUp, Google casi siempre será mejor que esperar a un mantenedor. Reserve los canales humanos para las partes específicas de omegaUp que nadie más en Internet conoce.

Si presenta su solicitud a través de Google Summer of Code, lea la página de ideas y preguntas frecuentes de GSoC para ese año (vinculada desde la sección [Comunidad/GSoC](../community/gsoc/index.md)) *antes* de preguntar sobre el proceso. Responde directamente a la mayoría de las preguntas sobre el proceso de solicitud, y las preguntas frecuentes cubren específicamente las preguntas recurrentes sobre cronogramas, propuestas y cómo se evalúan los candidatos.

!!! consejo "La búsqueda se amplía, no se reduce"
    Si su primera palabra clave no devuelve nada, pruebe con una redacción *diferente* en lugar de una más específica: copie la línea distintiva del mensaje de error, elimine las partes que son exclusivas de su máquina (rutas, ID de contenedor) y busque en el medio. La señal suele ser una o dos palabras, como `port is already allocated`, no el rastreo completo.

## Dónde preguntar: #dev_training, públicamente

Cuando la búsqueda no salga, publique su pregunta en el canal **#dev_training** del [servidor de Discord](https://discord.com/invite/K3JFd9d3wk). omegaUp coordina en Discord en lugar de una lista de correo tradicional, por lo que #dev_training *es* la lista de correo; trátela como el registro público en el que se convertirá.

Aquí hay dos reglas, y ambas existen por la misma razón: una pregunta pública ayuda a muchas más personas que una privada:

- **Publicar en el canal, nunca en un mensaje directo.** Un DM a un mantenedor llega exactamente a una persona, que puede estar dormida, ocupada o simplemente no es la que sabe la respuesta. La misma pregunta en #dev_training llega a todos, por lo que la persona disponible más rápida responde, *y* la respuesta se puede buscar para la siguiente persona que llegue a tu muro exacto. Si no encontró nada en la búsqueda, es casi seguro que no sea la última persona que lo necesitará.
- **No etiquetes a personas específicas.** Manejamos deliberadamente una cultura inclusiva en la que cualquiera puede participar, y @-ing a un responsable indica "esto es entre tú y yo" y disuade silenciosamente a todos los demás de responder. Pregúntale a la habitación, no a una persona.

!!! importante "GitHub es para errores confirmados y discusión de diseño, no para ayuda con la configuración"
    La discordia es donde te *despegas*. GitHub es donde se *siguen* las cosas. Una vez que haya confirmado un error reproducible en el código (no un problema con su propia máquina), abra un problema en [omegaup/omegaup/issues](https://github.com/omegaup/omegaup/issues) con los pasos de reproducción. Para ideas sobre funciones y conversaciones de diseño más extensas, utilice [Discusiones de GitHub](https://github.com/omegaup/omegaup/discussions). No abra un problema de GitHub porque `docker compose up` falló en su computadora portátil; esa es una pregunta #dev_training hasta que haya demostrado que el error se encuentra en el repositorio y no en su entorno.

## Cómo preguntar para que realmente te respondan

Una buena pregunta concentra todo lo que un ayudante necesita para diagnosticarlo sin un solo seguimiento. Las preguntas vagas obtienen respuestas vagas o silencio; Las preguntas específicas obtienen correcciones específicas, porque usted ha respondido las primeras tres preguntas del ayudante. Incluya, por adelantado:

- **Lo que intentabas hacer** y el comando exacto que ejecutaste.
- **Lo que esperabas** que sucediera versus **lo que realmente** sucedió.
- **El mensaje de error completo o el registro**, copiado y pegado como texto (no una captura de pantalla de su terminal; nadie puede buscar ni copiar una captura de pantalla).
- **Lo que ya has probado**, para que nadie desperdicie una respuesta sugiriendo lo que hiciste hace una hora.
- **Detalles relevantes del entorno** cuando podrían importar: su sistema operativo y su versión, la versión de Docker y, específicamente para omegaUp, si los contenedores terminaron de iniciarse (la pila de desarrollo puede tardar **entre 2 y 10 minutos** en funcionar por completo la primera vez, y muchos de los "está roto" resultan ser "aún no estaba listo").

### Una pregunta que tiene respuesta

```markdown
Setting up the dev environment on Ubuntu 22.04. `docker compose up` fails.

Expected: all containers start and I can open the frontend on localhost:8001.
Actual: the frontend container never binds; I get a port-conflict error.

Error:
ERROR: for frontend  Cannot start service frontend: driver failed programming
external connectivity on endpoint omegaup-frontend-1:
Bind for 0.0.0.0:8001 failed: port is already allocated

What I've tried:
- `lsof -i :8001` showed a leftover process; I killed it and re-ran — same error.
- Waited ~10 min in case it was still booting.
- Searched Discord for "port already allocated", found one thread but it was
  about port 13306 (MySQL), not 8001.
```
Esa pregunta nombra el puerto que omegaUp realmente publica para la interfaz (**8001**), muestra el error literal de Docker, demuestra que el autor de la pregunta ya descartó el retraso en el tiempo de arranque y un proceso obsoleto, e incluso cita el hilo que casi falló que encontraron, por lo que quien lo conteste puede ir directamente a la causa real en lugar de volver a preguntar lo obvio. Un ayudante que conozca la pila reconocerá inmediatamente los puertos en juego (frontend en **8001**, MySQL en **13306**, Go Grader en **21680**) y podrá concentrarse rápidamente.

### Una pregunta que se ignora

```markdown
docker not working help pls
```
!!! fracaso "¿Por qué éste muere sin respuesta?"
    No hay nada sobre lo que actuar: ningún comando, ningún texto de error, ningún sistema operativo, ninguna señal de lo que significa "no funciona" o de lo que ya se intentó. Responderlo requiere cuatro rondas de "¿qué sistema operativo?", "¿qué comando?", "pegue el error", "¿qué ha probado?" – y la mayoría de la gente simplemente pasará de largo en lugar de comenzar ese interrogatorio. La solución no es más cortesía; es más información.

Para un tratamiento más profundo de esta misma idea, recomendamos el ensayo breve de Mike Ash [*Getting Answers*](https://www.mikeash.com/getting_answers.html): es el artículo canónico sobre cómo formular una pregunta técnica que la gente quiere responder.

## Responder al hilo existente, no iniciar uno nuevo

Si su búsqueda encontró un hilo *cerrado* pero la respuesta allí no resolvió su caso, responda en ese hilo en lugar de abrir uno nuevo. Dos razones, ambas sobre la siguiente persona: mantiene todo lo relacionado con un problema en un solo lugar, y significa que quien lo soluciona lo arregla *para que conste*, por lo que el lector que llega a esto en seis meses encuentra la historia completa (síntoma original, intentos fallidos, solución funcional) en un solo pergamino en lugar de dispersarse en tres hilos a medio responder. Volver a publicar la misma pregunta en un hilo nuevo divide el conocimiento y hace que sea más probable que nadie escriba la respuesta real.

## Cierra el ciclo cuando esté resuelto.

Este es el paso que todos olvidan y es más importante de lo que parece. Cuando se resuelva su problema, ya sea que alguien lo haya ayudado o usted mismo lo haya resuelto, **regrese al hilo y diga cómo lo resolvió.**

La razón es concreta y un poco egoísta por parte de la comunidad: si dejas el hilo abierto, las personas que no vieron tu último mensaje seguirán leyéndolo, seguirán pensando y seguirán dedicando su tiempo a intentar ayudar a alguien que ya se ha despegado. Un hilo sin cerrar desperdicia silenciosamente el esfuerzo voluntario exacto por el que estabas agradecido. Y cuando la siguiente persona encuentre su error idéntico, la solución publicada será el hilo que le entrega la barra de búsqueda. Diga qué funcionó, agradezca a quien ayudó y, si la solución difirió de lo sugerido, explique la diferencia: esa delta suele ser la oración más útil de todo el hilo.

## Ayuda a la siguiente persona

Obtener ayuda y brindar ayuda son el mismo ciclo visto desde dos lados, así que una vez que tenga equilibrio, lea las preguntas que otros colaboradores publican en #dev_training y responda las que pueda. Esto no es solo buena ciudadanía: **lo tenemos en cuenta al seleccionar candidatos de GSoC.** Un colaborador que ayuda de manera confiable a sus pares demuestra exactamente la colaboración en la que se ejecuta el proyecto y se refleja en la forma en que evaluamos las solicitudes. En la práctica, rara vez es necesario ser un experto: señalar a alguien la página del documento correcta, reconocer un error con el que luchó personalmente la semana pasada o simplemente confirmar "sí, ese arranque de 2 a 10 minutos es normal, espere" es a menudo la respuesta completa. Explicar algo que acabas de aprender también es la forma más rápida de asegurarte de que realmente lo entiendes.

## La versión corta

Si no recuerdas nada más: **busca primero** (docs, historial de Discord, Google), **pregunta en #dev_training públicamente** con tu comando, tu error textual y lo que ya intentaste, **responde a los hilos existentes** en lugar de iniciar otros nuevos, **publica tu solución** cuando esté resuelta para que nadie siga persiguiendo un problema cerrado, y **ayuda a tus compañeros** porque el archivo de búsqueda que acaba de salvarte fue creado por personas que hicieron exactamente eso.

---

**¿Aún estás atascado?** Ingresa a [omegaUp Discord](https://discord.com/invite/K3JFd9d3wk) y pregunta en **#dev_training**. Con tu error pegado y tu sistema operativo nombrado, generalmente tendrás una respuesta antes de terminar tu café.
