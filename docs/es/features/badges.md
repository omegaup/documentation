---
title: Insignias
description: Implementación del sistema de logros
icon: bootstrap/award
---
# Insignias

Las insignias son los pequeños logros que omegaUp otorga a los usuarios: "resolvió 100 problemas",
"codificador del mes", "administrador del concurso". Lo que hace que sea agradable trabajar con ellos es
que una insignia es casi enteramente **declarativa**: no se escribe código que decida quién
lo gana, escribes una consulta SQL que *selecciona* quién se lo ganó, la colocas en una carpeta y
omegaUp hace el resto. Implementar uno es un camino muy transitado.

## Agregar una insignia, paso a paso

1. **Elija un alias.** Debe ser único y tener como máximo **32 caracteres**. Todo lo demás es
   lleva su nombre.

2. **Crea su carpeta.** Crea un directorio en
   [`frontend/badges/`](https://github.com/omegaup/omegaup/tree/main/frontend/badges) cuyo
   El nombre es exactamente el alias. De aquí en adelante este es tu `badgeFolder`.

3. **Agregue un ícono (opcional).** Si la insignia tiene un ícono personalizado, coloque su SVG en `badgeFolder`
   como `icon.svg`.

4. **Escriba la consulta de adjudicación.** Cree `badgeFolder/query.sql` que contenga un solo MySQL
   `SELECT` que devuelve los `user_id` de cada usuario que debería recibir la insignia. esto
   La consulta *es* la lógica de la insignia, por lo que necesita conocer la forma de los datos; mantenga la
   [esquema de base de datos](https://github.com/omegaup/omegaup/blob/main/frontend/database/schema.sql)
   ábralo mientras lo escribe y busque algo simple y que se pueda almacenar en caché en lugar de algo inteligente.

5. **Agregar localizaciones.** Crear
   [`badgeFolder/localizations.json`](https://github.com/omegaup/omegaup/blob/main/frontend/badges/legacyUser/localizations.json)
   con el nombre y la descripción de la insignia traducidos al español (`es`), inglés (`en`) y
   Portugués (`pt`). El nombre puede tener como máximo **50 caracteres**.

6. **Cargue las localizaciones.** Ejecute `./stuff/lint.sh` para que las cadenas en `localizations.json`
   se propagan a los archivos de mensajes correspondientes.

7. **Escribe la prueba.** Crea `badgeFolder/test.json`. Su campo `testType` elige cómo
   La prueba unitaria de la insignia se ejecuta:

    - **`"testType": "apicall"`**: cree el escenario llamando a las API del controlador para crear
      los datos de los que depende la insignia (problemas, usuarios, concursos, tiradas,…). tu lo describe
      con un arreglo `actions`, cuyas entradas pueden ser:
        - `changeTime`: mueve el reloj del sistema para que puedas probar insignias dependientes del tiempo.
        - `apicalls`: llama a una API específica y proporciona el nombre de usuario y la contraseña del usuario que llama.
          y los parámetros. Las API son todos los métodos públicos estáticos `api…` en el
          controladores en
          [`frontend/server/src/Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers).
        - `scripts`: ejecuta uno de los scripts cron de omegaUp (`aggregateFeedback`, `assignBadges`,
          `updateUserRank`), que viven en
          [`stuff/cron/`](https://github.com/omegaup/omegaup/tree/main/stuff/cron).

      Finalice una prueba `apicall` con un campo `expectedResults` que enumere los nombres de usuario que
      debería recibir la insignia. Ver
      [`coderOfTheMonth/test.json`](https://github.com/omegaup/omegaup/blob/main/frontend/badges/coderOfTheMonth/test.json)
      para un ejemplo trabajado.

    - **`"testType": "phpunit"`** — escribe una prueba PHPUnit clásica llamada `<alias>Test.php`,
      guardado bajo
      [`frontend/tests/badges/`](https://github.com/omegaup/omegaup/tree/main/frontend/tests/badges),
      siguiendo la misma estructura que las otras pruebas unitarias de omegaUp (y de uso gratuito
      [fábricas](https://github.com/omegaup/omegaup/tree/main/frontend/tests/factories)).

    Cada uno tiene sus ventajas y desventajas: prefiera `phpunit` para una insignia que de otro modo necesitaría muchas
    llamadas API casi idénticas; de lo contrario, `apicalls` es la opción más ligera.

8. **Ejecute las pruebas** para confirmar su consulta y la prueba otorgará la insignia a la derecha.
   gente:

    ```bash
    ./vendor/bin/phpunit --bootstrap frontend/tests/bootstrap.php \
      --configuration frontend/tests/phpunit.xml frontend/tests/badges/ --debug
    # or simply
    ./stuff/runtests.sh
    ```
9. **Abra la solicitud de extracción.** Si no hay ningún error, su credencial está lista: envíela.

Como referencia, dos RP de insignia fusionados son buenas plantillas a seguir:
[Administrador del concurso](https://github.com/omegaup/omegaup/pull/2602/files) y
[Administrador del concurso virtual](https://github.com/omegaup/omegaup/pull/2603/files).

Si algo no queda claro mientras crea uno, no dude en comunicarse; consulte
[Obteniendo ayuda](../getting-started/getting-help.md).
