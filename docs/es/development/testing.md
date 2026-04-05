---
title: Guía de prueba
description: Guía de pruebas completa para omegaUp
icon: bootstrap/flask
---
# Guía de prueba

omegaUp utiliza múltiples marcos de prueba para garantizar la calidad del código en diferentes capas.

## Pila de pruebas

| Capa | Marco | Ubicación |
|-------|-----------|----------|
| Pruebas unitarias de PHP | Unidad PHP | `frontend/tests/controllers/` |
| Pruebas de TypeScript/Vue | Broma | `frontend/www/js/` |
| Pruebas E2E | Ciprés | `cypress/e2e/` |
| Pruebas de Python | pytest | `stuff/` |

## Pruebas unitarias de PHP

### Ejecutando todas las pruebas de PHP

```bash
./stuff/runtests.sh
```
Ejecuta pruebas PHPUnit, validación de tipo MySQL y Psalm.

**Ubicación**: Dentro del contenedor Docker

### Ejecutando un archivo de prueba específico

```bash
./stuff/run-php-tests.sh frontend/tests/controllers/MyControllerTest.php
```
Omita el nombre del archivo para ejecutar todas las pruebas.

### Requisitos de prueba

- Todas las pruebas deben pasar el 100% antes de comprometerse.
- La nueva funcionalidad requiere pruebas nuevas/modificadas
- Pruebas ubicadas en `frontend/tests/controllers/`

## Pruebas de TypeScript/Vue

### Ejecución de pruebas de Vue (modo de vigilancia)

```bash
yarn run test:watch
```
Vuelve a ejecutar pruebas automáticamente cuando cambia el código.

**Ubicación**: Dentro del contenedor Docker

### Ejecutando un archivo de prueba específico

```bash
./node_modules/.bin/jest frontend/www/js/omegaup/components/MyComponent.test.ts
```
### Estructura de prueba

Verificación de pruebas de componentes de Vue:
- Visibilidad de los componentes
- Emisión de eventos
- Comportamiento esperado
- Props y estado

## Pruebas E2E con Cypress

Las pruebas de extremo a extremo están en la carpeta `cypress/` en la raíz del repositorio. **Cypress suele ejecutarse en tu máquina anfitriona** (no dentro del contenedor Docker del frontend de omegaUp), así que necesitas Node, dependencias de Yarn y, en Linux, varias bibliotecas del sistema para el ejecutable basado en Electron.

La versión fijada aparece en el `package.json` raíz (campo `cypress`). Tras actualizar dependencias, ejecuta `yarn install` y, si falta el binario:

```bash
./node_modules/.bin/cypress install
```

### Abrir y ejecutar Cypress

```bash
npx cypress open
# o
./node_modules/.bin/cypress open
```

Modo headless:

```bash
npx cypress run
# o
yarn test:e2e
```

`yarn test:e2e` ejecuta `cypress run --browser chrome` (ver scripts en `package.json`).

### Dependencias del sistema en Linux (Ubuntu / Debian)

Lista oficial: [dependencias requeridas](https://on.cypress.io/required-dependencies).

Paquetes habituales:

```bash
sudo apt update
sudo apt install -y libatk1.0-0 libatk-bridge2.0-0 libgdk-pixbuf2.0-0 libgtk-3-0 libgbm-dev libnss3 libxss-dev
```

**Errores `libnss3.so` / NSS** — instale `libnss3` o `libnss3-dev` según la distribución.

**Errores `libasound.so.2`**:

```bash
sudo apt-get install libasound2
```

En **Ubuntu 24.04+** el paquete puede llamarse:

```bash
sudo apt install libasound2t64
```

Si el error persiste, ejecute `sudo apt update` y vuelva a intentar; compare la versión en el mensaje con la ruta bajo `~/.cache/Cypress/<versión>/`.

### Estructura y escritura de pruebas

- Especificaciones: `cypress/e2e/`, patrón `*.cy.ts` (se permiten subcarpetas).
- Comandos personalizados: `cypress/support/commands.js` (y tipos en `cypress/support/cypress.d.ts`).
- Handlers globales / `uncaught:exception`: `cypress/support/e2e.ts`.
- [Comandos personalizados](https://docs.cypress.io/api/cypress-api/custom-commands) y [eventos](https://docs.cypress.io/api/events/catalog-of-events) de Cypress.
- **Cypress Studio** puede grabar interacciones en un spec: [Cypress Studio](https://docs.cypress.io/guides/core-concepts/cypress-studio).

En este repositorio se usan plugins como **cypress-wait-until** y **cypress-file-upload** (ver `package.json`).

### Depurar fallos en CI

Si en GitHub Actions falla y en local pasa, abra la pestaña **Checks** del PR → **CI** y descargue artefactos `cypress-screenshots-<intento>` y `cypress-videos-<intento>` (el número de intento aparece en la URL del workflow, p. ej. `/attempts/3`).

## Pruebas de Python

Las pruebas de Python utilizan pytest y se encuentran en el directorio `stuff/`.

## Cobertura de prueba

Usamos **Codecov** para medir la cobertura:

- **PHP**: Cobertura medida ✅
- **TypeScript**: Cobertura medida ✅
- **Cypress**: Cobertura aún no medida ⚠️

## Mejores prácticas

### Escriba las pruebas primero
Cuando sea posible, escriba pruebas antes de la implementación (TDD).

### Probar rutas críticas
Centrarse en:
- Flujos de autenticación de usuarios.
- Presentación y evaluación de problemas.
- Gestión del concurso
- Puntos finales API

### Mantenga las pruebas rápidas
- Las pruebas unitarias deben ser rápidas (< 1 segundo)
- Las pruebas E2E pueden ser más lentas pero deben completarse en un tiempo razonable

### Prueba de aislamiento
- Cada prueba debe ser independiente.
- Limpiar datos de prueba después de las pruebas.
- Utilice dispositivos de prueba para obtener datos consistentes

## Documentación relacionada

- **[Pautas de codificación](coding-guidelines.md)** - Estándares de código
- **[Comandos útiles](useful-commands.md)** - Comandos de prueba
- **[Configuración de desarrollo](../getting-started/development-setup.md)** — Node, Yarn y Docker antes de ejecutar Cypress
