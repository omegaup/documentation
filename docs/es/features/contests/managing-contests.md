---
title: Gestión de concursos
description: Guía para crear y gestionar concursos de programación
icon: bootstrap/cog
---
# Gestión de concursos

Guía completa para crear y gestionar concursos de programación en omegaUp.

## Creando un concurso

### Información básica

- **Título**: Nombre del concurso
- **Alias**: Identificador corto (usado en URL)
- **Descripción**: descripción del concurso
- **Hora de inicio**: Cuando comienza el concurso
- **Hora de finalización**: cuando finaliza el concurso.
- **Público/Privado**: configuración de visibilidad

### Configuración avanzada

- **Duración de la ventana**: temporizadores individuales estilo USACO
- **Visibilidad del marcador**: porcentaje de tiempo que el marcador está visible
- **Disminución de puntos**: factor de disminución de puntuación basado en el tiempo
- **Política de sanciones**: cómo se calculan las sanciones
- **Brecha de envío**: segundos entre envíos

## Tipos de concurso

### Concurso estándar
- Hora de inicio y finalización fija.
- Temporizador compartido para todos los participantes.
- Formato de concurso tradicional

### Concurso Virtual (estilo USACO)
- Temporizador individual por participante
- Comienza cuando el participante ingresa.
- Duración basada en ventana

## Manejo de problemas

Añade problemas a tu concurso:

1. Crear o seleccionar problemas
2. Valores de punto de ajuste
3. Problemas de pedido
4. Configurar ajustes específicos del problema

## Gestión de participantes

### Concursos públicos
- Abierto a todos los usuarios.
- No se necesita invitación

### Concursos privados
- Invitar a usuarios específicos
- Administrar la lista de participantes
- Controlar el acceso

## Configuración del marcador

- **Visibilidad**: controla cuándo está visible el marcador
- **Freeze**: congela el marcador antes de que termine el concurso.
- **Actualizar**: actualizaciones en tiempo real a través de WebSocket

## Concurso en una escuela (red y laboratorio)

Permita **HTTPS (443)** hacia omegaUp y servicios relacionados desde las PCs de los concursantes.

- **`https://omegaup.com`** — modo normal.
- **`https://arena.omegaup.com`** — solo si usa **modo lockdown**; en ese caso bloquee el dominio normal para que no se pueda eludir.
- **`https://ssl.google-analytics.com`** — uso del sitio. Opcional: Gravatar, Google OAuth.

Evite reglas de firewall que **descarten** paquetes sin respuesta (**DROP**) para dominios necesarios: el navegador puede esperar ~20–30 s por conexión. **Lockdown** restringe práctica, código de envíos previos, etc.; si lo necesita, no use lockdown.

Los envíos se califican en **Linux**; código solo Windows puede fallar. Eventos grandes (100+): contacte **hello@omegaup.com** con antelación.

## Documentación relacionada

- **[API de concursos](../../api/contests.md)** — Endpoints
- **[Arena](../arena.md)** — Interfaz del concurso
