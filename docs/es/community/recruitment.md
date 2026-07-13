---
title: Reclutamiento
description: Cómo unirse al equipo de ingeniería de omegaUp
icon: bootstrap/briefcase
---
# Unirse al equipo omegaUp

omegaUp está dirigido por voluntarios, y toda la plataforma (la interfaz PHP 8.1, la interfaz de usuario Vue 2.7, el evaluador Go en [omegaup/quark](https://github.com/omegaup/quark), el [gitserver] de almacenamiento de problemas (https://github.com/omegaup/gitserver), los miles de problemas y cursos—existe porque las personas que comenzaron exactamente donde usted decidió quedarse. Esta página trata sobre ese segundo paso: no sobre cómo abrir su primera solicitud de extracción (la [Guía de contribución](../getting-started/contributing.md) cubre eso de principio a fin), sino sobre cómo pasar de colaborador único a alguien que el equipo de mantenimiento conoce por su nombre e invita formalmente al equipo de ingeniería. No hay entrevista ni pantalla de currículum. La única moneda es el trabajo fusionado y el camino hacia él está completamente abierto.

## No hay nada que solicitar

El proceso de capacitación está abierto a cualquiera que lo desee: no envía un correo electrónico a un encargado de mantenimiento, no completa un formulario ni espera a que le permitan ingresar. Clona el repositorio, reclama un problema y comienza. La razón por la que funciona de esta manera es la misma por la que todo el proyecto está abierto en GitHub: las personas que se convierten en miembros del equipo son las que iban a contribuir independientemente de que alguien estuviera mirando o no, por lo que el proceso simplemente se sale de su camino y mide el resultado.

Lo que eso significa en la práctica es que "ser contratado" es un efecto secundario de hacer el trabajo, no un camino separado al que cambiar. Todo lo que aparece a continuación es el trabajo.

## Los roles en los que puedes crecer

Escribir código de backend y frontend es la forma más visible de ingresar, pero está lejos de ser la única, y el equipo realmente se ejecuta en todos estos:

- **Los desarrolladores** llevan el código: controladores bajo `frontend/server/src/Controllers/`, componentes de archivo único de Vue bajo `frontend/www/js/omegaup/components/`, además de revisar las solicitudes de extracción de otras personas, que es en sí misma una de las formas más rápidas de ganarse la confianza del equipo porque una buena revisión ahorra el recurso más escaso del mantenedor: su tiempo.
- **Los creadores de problemas** crean los problemas de programación competitiva y sus casos de prueba: el contenido educativo que el juez realmente ejecuta. No es necesario tocar el código base en absoluto para ser indispensable aquí.
- **Los traductores** mantienen omegaUp utilizable en más de un idioma; la plataforma sirve a una comunidad que habla principalmente español y se extiende por muchos países, y el sobre de error en sí está localizado "en el idioma que se tenga configurado la cuenta", por lo que la traducción es de carga, no cosmética.
- **Los educadores** ejecutan omegaUp en aulas y competencias reales, y el ciclo de retroalimentación de un maestro real que usa cursos bajo carga vale más que la mayoría de las solicitudes de funciones.
- Los **Mentores** ayudan a la próxima ola de recién llegados a despegarse en **#dev_training**, y este es silenciosamente uno de los roles de mayor influencia: el archivo de Discord con capacidad de búsqueda que le ahorrará una tarde al próximo colaborador solo existe porque alguien respondió públicamente.

Si no está seguro de cuál de estos es usted, está bien: la mayoría de los clientes habituales terminan haciendo dos o tres. Comience con aquel en el que pueda actuar hoy.

## Cómo involucrarse más allá de un solo RP

Las mecánicas del rastreador de problemas están diseñadas deliberadamente para recompensar la participación *sostenida* en lugar de una única solución inmediata, y comprenderlas le indicará exactamente cómo convertirse en un cliente habitual:

Cada solicitud de extracción debe estar vinculada a un problema de GitHub que esté **asignado a usted**; esto se aplica mediante la automatización, por lo que un PR sin un problema asignado detrás no puede fusionarse sin importar qué tan bueno sea el código. Usted reclama un problema comentando `/assign` sobre él (el bot [`takanome-dev/assign-issue-action`](https://github.com/takanome-dev/assign-issue-action) lo maneja para que nunca espere a un humano) y puede retener como máximo **5** problemas a la vez. Ese límite es el primer empujón hacia la coherencia: se supone que usted debe terminar y enviar, no acumular el trabajo pendiente. Después de reclamar un problema, tiene **7 días** para abrir una solicitud de extracción (un PR **borrador** cuenta) o el bot lo desasignará automáticamente (un recordatorio llega aproximadamente a la mitad del camino, **3,5 días**, por lo que una semana ocupada no le costará el problema por sorpresa). El ritmo que esto crea (reclamar, enviar dentro de la semana, reclamar nuevamente) *es* lo que significa ser un colaborador habitual.

El sistema también tiene un hito de confianza incorporado al que puede aspirar. Una vez que tenga **10 RP combinados** en el repositorio, los problemas que *usted* haya creado se pueden autoasignar sin contar contra su límite de 5 asignaciones activas, una pequeña pero real señal de que el proyecto ahora lo trata de manera diferente que el primer día. Llegar a diez RP fusionados es un objetivo concreto y contable, y es aproximadamente el punto en el que los mantenedores dejan de pensar en usted como un recién llegado.

Vale la pena conocer dos ciclos de retroalimentación más porque son la forma en que el equipo realmente te nota. En primer lugar, **ayudar a los compañeros en #dev_training cuenta.** Lo tenemos en cuenta al seleccionar candidatos de GSoC: un colaborador que responde de manera confiable a las preguntas de otras personas demuestra exactamente la colaboración en la que se ejecuta el proyecto, y rara vez es necesario ser un experto para hacerlo (señalar a alguien la página del documento correcta o confirmar "sí, ese primer arranque de 2 a 10 minutos es normal, espere", suele ser la respuesta completa). En segundo lugar, recuerde que los RP fusionados pasan a producción en la **implementación del fin de semana**, no en el instante en que se fusionan, por lo que la parte satisfactoria, ver su cambio en vivo en omegaup.com, llega después del próximo fin de semana, y verlo suceder es parte de lo que engancha a las personas para que regresen.

## Lo que se necesita para una invitación formal

Hay una barrera concreta para ser invitado formalmente al equipo de ingeniería, y es exactamente el tipo de objetivo contable que el proyecto prefiere a un juicio subjetivo:

1. Lea la documentación: este sitio, además del [omegaUp Wiki] anterior (https://github.com/omegaup/omegaup/wiki), para conocer el sistema antes de cambiarlo.
2. Resuelva **5** problemas etiquetados [**Buen primer problema**](https://github.com/omegaup/omegaup/issues?q=is%3Aissue+is%3Aopen+label%3A%22Good+first+issue%22): la vía de acceso seleccionada para sus primeros parches.
3. Resuelva **5** problemas etiquetados [**Buen segundo problema**](https://github.com/omegaup/omegaup/issues?q=is%3Aissue+is%3Aopen+label%3A%22Good+second+issue%22): el siguiente nivel deliberadamente más difícil, destinado a demostrar que puede navegar por el código base sin que lo tomen de la mano.

Borre esos diez y estará **formalmente invitado a unirse al equipo de ingeniería** y **se le ofrecerá una cuenta de correo electrónico `@omegaup.com`** si desea una. La estructura de dos niveles es intencional: cinco *primeros* problemas muestran que puede realizar un cambio en todo el proceso (bifurcación, rama, pelusa con `./stuff/lint.sh`, relaciones públicas, revisión, fusión, implementación de fin de semana) y cinco *segundos* problemas muestran que puede hacerlo en problemas que nadie ha analizado previamente.

!!! nota "Algunas personas se saltan el camino de los diez temas"
    El requisito existe para generar y demostrar confianza, de modo que las personas que ya la han establecido a través de otro canal no tengan que esforzarse nuevamente. Dos excepciones permanentes: **pasantes con contrato firmado** y **ex voluntarios con trayectoria de contribución reconocida** que regresan. Si crees que caes en uno de estos, infórmalo en **#dev_training** en lugar de asumirlo.

## Por dónde empezar hoy

El primer paso concreto más rápido es el vídeo de instalación y un buen primer paso, en ese orden:

- Mire el [tutorial de configuración del entorno de desarrollo](https://www.youtube.com/watch?v=H1PG4Dvje88), luego siga la guía escrita de [Configuración de desarrollo](../getting-started/development-setup.md): la pila de desarrollo puede tardar **entre 2 y 10 minutos** en funcionar por completo la primera vez, así que no entre en pánico si parece atascado.
- Únete al [servidor de Discord](https://discord.com/invite/K3JFd9d3wk) y saluda en **#dev_training**; aquí es donde se coordina toda la comunidad de contribuyentes y donde usted se despegará más rápido.
- Elija un [**Buen primer número**](https://github.com/omegaup/omegaup/issues?q=is%3Aissue+is%3Aopen+label%3A%22Good+first+issue%22), comente `/assign` y abra un borrador de PR el mismo día para bloquear su ventana de 7 días.

## Documentación relacionada

- **[Contribuyendo a omegaUp](../getting-started/contributing.md)**: el flujo de trabajo completo de solicitud de extracción, desde la bifurcación hasta la implementación del fin de semana.
- **[Configuración de desarrollo](../getting-started/development-setup.md)**: haga que la pila se ejecute localmente.
- **[Obtener ayuda](../getting-started/getting-help.md)**: cómo preguntar en #dev_training para obtener una respuesta.
- **[Comunidad](index.md)** — el panorama más amplio: GSoC, canales de comunicación y todas las formas de participar.
