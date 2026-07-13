---
title: Archivos de datos de documentación GSoC
description: Cómo omegaUp genera páginas del año GSoC a partir de datos JSON
icon: bootstrap/code
---
# Archivos de datos de documentación GSoC {#gsoc-documentation-data-files}

Cada año, omegaUp ejecuta una campaña Google Summer of Code, y cada año los documentos necesitan una página por año: una página "actual" llena de ideas de proyectos y el embudo de aplicaciones mientras la campaña está activa, y una página "pasada" que enumera lo que se envió una vez finalizada. En lugar de escribir esas páginas a mano y dejar que sus títulos se separen, mantenemos el contenido específico del año en un único archivo de datos JSON y eliminamos el Markdown con un pequeño generador de Python. Piense en `scripts/generate-gsoc-pages.py` como un pequeño compilador de plantillas cuyo único lenguaje de plantilla son las cadenas f de Python y cuya única entrada es `_data/gsoc-data.json`: no hay Jinja, ni complemento Zensical, nada más que la biblioteca estándar, por lo que se ejecuta en un `python3` desnudo con cero `pip install`.

Todo es deliberadamente pequeño (alrededor de 180 líneas) porque es una **herramienta de andamiaje, no un renderizador en vivo**. No se ejecuta en el momento de la compilación: `build_all.py` nunca lo llama (búsquelo y no encontrará ninguna referencia). Lo ejecuta a mano cuando agrega o acumula un año, revisa el Markdown que arroja, lo pule a mano y confirma el resultado. Esa distinción es importante, y volveremos a ella a continuación, porque las páginas actualmente comprometidas bajo `docs/en/community/gsoc/` son considerablemente más ricas que cualquier cosa que el generador emita hoy.

## El modelo mental de una línea {#the-one-line-mental-model}

`gsoc-data.json` es la fuente de verdad para el *esqueleto* de la página de cada año; el generador recorre el `data["years"]` y, para cada año, despacha en su campo `type` a una de las dos funciones que construyen el Markdown línea por línea. `type: "current"` recibe el tratamiento completo (ideas de proyectos + un proceso de solicitud de cuatro fases + comunicaciones + preguntas frecuentes + documentos relacionados); todo lo demás obtiene el diseño "pasado" simplificado (proyectos completados con resultados + documentos relacionados).

## Lo que realmente hace el generador, de extremo a extremo {#what-the-generator-actually-does-end-to-end}

El punto de entrada es `main()` en la parte inferior de `scripts/generate-gsoc-pages.py`. En orden:

1. **Resuelve rutas relativas al propio script**, no al directorio de trabajo de su shell. `PROJECT_ROOT = Path(__file__).parent.parent` (la raíz del repositorio, un nivel por encima de `scripts/`), y luego codifica `DATA_FILE = PROJECT_ROOT / "docs" / "community" / "gsoc" / "_data" / "gsoc-data.json"` y `OUTPUT_DIR = PROJECT_ROOT / "docs" / "community" / "gsoc"`. **Lea esas dos rutas con atención**: ya no coinciden con el repositorio y eso es lo primero que le molestará. Más sobre eso en [El camino obsoleto te atrapó](#the-stale-path-gotcha-read-this-before-you-run-it).

2. **Falla ruidosamente si falta el archivo de datos.** Antes de hacer cualquier cosa, `main()` verifica `DATA_FILE.exists()`; si no, imprime `Error: Data file not found: <path>` más `Please create the data file first.` y llama a `sys.exit(1)`. Por lo tanto, un archivo de datos faltante o extraviado es una parada difícil, no una operación silenciosa.

3. **Analiza JSON, y solo JSON.** `load_data()` realiza un `json.load()` simple en `DATA_FILE`. Si el JSON tiene un formato incorrecto, `main()` detecta el `json.JSONDecodeError` e imprime el `Error: Invalid JSON in data file: <message>` antes de salir del `1`, por lo que una coma al final le brinda un diagnóstico real en lugar de un rastreo. Tenga en cuenta lo que *no* lee: el hermano `gsoc-data.yaml`. Ese archivo YAML es un espejo amigable para los humanos que guardamos para facilitar la edición (está comentado, es diferenciable), pero el generador nunca lo toca; no hay ningún `import yaml` en ninguna parte del script, precisamente por eso la herramienta permanece solo como biblioteca estándar. Si edita el YAML y olvida el JSON, nada cambia. **El JSON es la entrada; el YAML es una copia de cortesía.**

4. **Genera el año más nuevo primero.** `main()` itera `sorted(data["years"].keys(), reverse=True)`, por lo tanto, `"2025"`, luego `"2024"` y luego `"2023"`. Se trata de una clasificación de cadenas sobre las claves de año, que resulta ser correcta para años de cuatro dígitos; sólo afecta el orden de la consola, no los archivos de salida en sí.

5. **Para cada año, `generate_page()` se despacha en `type`.** Extrae `year_data = data["years"][year]` y se bifurca: `if year_data["type"] == "current"` llama `generate_current_year_page()`, `else` llama `generate_past_year_page()`. Tenga en cuenta el `else`: el despacho es "actual versus *todo lo que no está actual*". Entonces, `"type": "past"` y un error tipográfico como `"type": "pastt"` aterrizan en el diseño anterior. No existe ninguna validación que detecte un tipo mal escrito; simplemente obtienes silenciosamente una página pasada. Escribe el resultado en `OUTPUT_DIR / f"{year}.md"` e imprime `✓ Generated <path>`.

Cuando termina, imprime `✓ All GSoC pages generated successfully!` y un recordatorio para revisar y confirmar los archivos. Nada se organiza en git para ti, eso depende de ti.

## Los dos diseños, campo por campo {#the-two-layouts-field-by-field}

El verdadero valor didáctico es saber exactamente qué clave JSON se convierte en qué parte de Markdown, porque eso es lo que estás editando a ciegas cuando tocas el archivo de datos.

### Página del año actual: `generate_current_year_page()` {#current-year-page-generate_current_year_page}

Dado un año `type: "current"`, la función emite, en este orden fijo:

- **Frontmatter** creado a partir de tres claves: `title`, `description` y un `icon: material/school` codificado. (Observe ese ícono; consulte [Desviación de íconos](#icon-drift) a continuación; las páginas confirmadas no usan `material/school`).
- **`# {title}`** como H1, luego una línea en blanco, luego la cadena `intro` sin formato palabra por palabra. El `intro` es Markdown-passthrough, por lo que los enlaces y el énfasis en su interior sobreviven.
- **`## Project Ideas`** — siempre emitido, incluso si no hay ideas. Las ideas en sí provienen de `year_data.get("project_ideas", [])`, por lo que una clave faltante genera una sección vacía en lugar de un bloqueo. Cada objeto de idea se convierte en:
    ```
    ### {name}
    {description}

    **Skills**: {skills}
    **Size**: {size}
    **Level**: {level}
    ```
Aquí hay un problema de representación sutil: `**Skills**`, `**Size**` y `**Level**` se emiten en tres líneas consecutivas sin **ninguna línea en blanco entre ellas**, por lo que Markdown los colapsa en un párrafo ajustado. Es por eso que los datos de origen mantienen cada uno de esos valores breves (`"350 hours"`, `"Advanced"`, `"Vue.js, TypeScript, PHP"`) en lugar de intentar convertirlos en filas visuales separadas.
- **`## Application Process`** — construido a partir de `year_data.get("application_process", {})`. La función recorre la lista fija literal `["phase1", "phase2", "phase3", "phase4"]` y emite solo las fases que están presentes, en ese orden. Dos consecuencias que vale la pena internalizar: una clave `phase5` sería **ignorada silenciosamente** (el bucle nunca la busca), y las fases se representan en el orden `phase1..phase4` independientemente del orden en que aparecen en el JSON. Dentro de cada fase emite `### {title}`, luego, si la fase tiene una matriz `steps`, una lista numerada (`enumerate(..., 1)`) y/o, si tiene una cadena `description`, esa descripción como un párrafo. Ambos pueden coexistir; una fase en la que ninguno apenas aporta su título. Esta es la razón por la que las fases 1 a 3 de los datos en vivo utilizan `steps` (listas de verificación concretas), mientras que `phase4` usa un único `description` (la propaganda de la entrevista).
- **`## Communications`**: se emite solo `if "communications" in year_data`, como una lista con viñetas donde cada entrada de la matriz se imprime palabra por palabra después de `- `. Las entradas ya son Markdown (`"**Discord**: [Join our Discord server](...)"`), por lo que las negritas y los enlaces son suyos para escribir en los datos.
- **`## FAQ`** — emitido solo `if "faq" in year_data`. Cada elemento se convierte en `**{question}**` en una línea y `{answer}` en la siguiente, nuevamente sin una línea en blanco entre ellos, por lo que la pregunta y la respuesta se representan como un párrafo, con la pregunta en negrita.
- **`## Related Documentation`**: emitido solo `if "related_docs" in year_data`, cada entrada como `- **{doc}**`. Debido a que toda la cadena `doc` está envuelta en `**...**`, la entrada *completa* (texto del enlace *y* la "- descripción" final) aparece en negrita. Esa es una peculiaridad del modelo actual, no una elección de diseño que valga la pena defender.

### Página del año pasado: `generate_past_year_page()` {#past-year-page-generate_past_year_page}

Todo lo que no sea `current` obtiene el diseño simplificado: el mismo frontmatter de tres teclas y el encabezado `# {title}` / `intro`, luego **`## Projects`** construido a partir de `year_data.get("projects", [])`. Cada objeto del proyecto es solo:

```
### {name}
{description}

**Result**: {result}
```
Luego el mismo bloque opcional **`## Related Documentation`**. Esa es toda la plantilla anterior: sin habilidades, sin fases, sin preguntas frecuentes. La división mental es: una página *actual* es un embudo de reclutamiento, una página *pasada* es un currículum.

## El esquema de datos {#the-data-schema}

Todo cuelga de un objeto `years` de nivel superior codificado por cadenas de años de cuatro dígitos. Cada año tiene una de dos formas.

Un año **actual** (ver `2025` en los datos en vivo):

```json
"2025": {
  "type": "current",
  "title": "GSoC 2025",
  "description": "Google Summer of Code 2025 program at omegaUp",
  "intro": "omegaUp is participating in Google Summer of Code 2025! ...",
  "project_ideas": [
    {
      "name": "AI Teaching Assistant",
      "description": "Create a bot that can answer clarifications ...",
      "skills": "Python, PHP, MySQL, LLM Prompt Engineering, REST APIs",
      "size": "350 hours",          // free text; GSoC sizes are 90 / 175 / 350 hours
      "level": "Advanced"           // free text; e.g. "Medium", "High", "Medium to Advanced"
    }
  ],
  "application_process": {
    "phase1": { "title": "...", "steps": ["...", "..."] },   // steps -> numbered list
    "phase4": { "title": "...", "description": "..." }         // description -> paragraph
  },
  "communications": ["**Discord**: [...](...)"],   // verbatim Markdown bullets, optional
  "faq": [ { "question": "...", "answer": "..." } ], // optional
  "related_docs": ["[Getting Started](../getting-started/index.md) - Development setup"]
}
```
Un año **pasado** (ver `2023` / `2024`):

```json
"2024": {
  "type": "past",
  "title": "GSoC 2024",
  "description": "Google Summer of Code 2024 projects",
  "intro": "Projects completed during GSoC 2024.",
  "projects": [
    {
      "name": "Migrate Problem Creator to Vue.js + TypeScript",
      "description": "Migrated the Problem Creator ...",
      "result": "Problem Creator can now be used directly on omegaUp.com ..."
    }
  ],
  "related_docs": ["[GSoC 2025](../community/gsoc/2025.md) - Current year program"]
}
```
`type`, `title`, `description` y `intro` son las únicas claves que el generador elimina directamente (`year_data['title']`, etc.), por lo que esas cuatro son efectivamente **requeridas**: omita una y obtendrá un `KeyError`. Todo lo demás (`project_ideas`, `application_process`, `communications`, `faq`, `related_docs`, `projects`) se lee a través de `.get(...)` o está protegido por un `if ... in year_data`, por lo que todo es opcional y se degrada a una sección vacía (o ausente).

Una cosa que el esquema *no* codifica: los enlaces relativos dentro de los pasos `related_docs`, `application_process` y `communications` están escritos desde la perspectiva del propio directorio de la página del año (`../getting-started/...`, `../index.md` y hermano `2025.md`). Si se mueve donde se generan las páginas, esos enlaces se mueven con ellos y pueden romperse; verifíquelos con `scripts/verify_docs_nav.py` después de la regeneración.

## Agregando un nuevo año {#adding-a-new-year}

Cuando se abre una nueva campaña, realiza dos ediciones y pasa un año:

1. **Agregue el nuevo año actual** a `gsoc-data.json`. Déle `"type": "current"`, complete `title`/`description`/`intro` y complete `project_ideas`, `application_process` (fases `phase1`–`phase4`), `communications`, `faq` y `related_docs`. Mantenga los valores de `skills`/`size`/`level` cortos (se pegan entre sí en el renderizado).
2. **Degradar la página del año pasado al pasado.** Cambie el `"type"` del año anterior de `"current"` a `"past"` y cambie su `project_ideas` por una matriz `projects` donde cada objeto lleva `name` / `description` / `result` que describe lo que realmente se envió. La plantilla anterior ignora por completo `project_ideas`, por lo que dejar la matriz anterior en su lugar simplemente la convierte en información muerta; elimínela.
3. **Refleje el cambio en `gsoc-data.yaml`** para que la copia editable por humanos no se pudra. Esta es una cortesía manual (el generador no lo hará y no lo leerá), pero la siguiente persona que lo edite buscará primero el YAML.
4. **Regenerar**, luego revisar la diferencia. Consulte la advertencia de ruta inmediatamente debajo antes de ejecutar cualquier cosa.
5. **Pulir a mano y confirmar los archivos `YYYY.md`.** La salida del generador es un esqueleto inicial; las páginas comprometidas contienen secciones adicionales (tablas de estadísticas, listas de logros, comparaciones de beneficios) que no existen en el archivo de datos. No espere que la regeneración los reproduzca.

Debido a que omegaUp mantiene cuatro configuraciones regionales (`docs/en`, `docs/es`, `docs/pt`, `docs/pt-BR`), cada una con su propio `_data/gsoc-data.json`, "agregar un año" significa repetir los pasos 1 a 5 por configuración regional que mantenga; el generador no tiene noción de configuración regional, simplemente se ejecuta contra cualquier JSON único al que apunte su `DATA_FILE`. `scripts/translate_docs.py` maneja la traducción masiva de prosa, pero los datos estructurados del año se editan manualmente por localidad.

## La ruta obsoleta te pilló: lee esto antes de ejecutarla {#the-stale-path-gotcha-read-this-before-you-run-it}

Aquí está el filo. El `DATA_FILE` del script está codificado para:

```
docs/community/gsoc/_data/gsoc-data.json
```
Pero el árbol de documentos se reorganizó en raíces por configuración regional (`docs/en/…`, `docs/es/…`, `docs/pt/…`, `docs/pt-BR/…`) y `docs/community/` **ya no existe**. Entonces, ejecutar el script como está comprometido, desde cualquier lugar, le brinda:

```
$ python3 scripts/generate-gsoc-pages.py
Error: Data file not found: /…/ou-documentation/docs/community/gsoc/_data/gsoc-data.json
Please create the data file first.
```
Ese error no es "olvidó crear el archivo", sino "el generador se escribió antes de que los documentos se dividieran por idioma y sus dos constantes de ruta nunca se actualizaron". Los archivos reales se encuentran en `docs/<lang>/community/gsoc/_data/gsoc-data.json`. Para utilizar realmente el generador hoy, debe redirigir tanto `DATA_FILE` como `OUTPUT_DIR` a una ubicación específica, por ejemplo:

```python
DATA_FILE  = PROJECT_ROOT / "docs" / "en" / "community" / "gsoc" / "_data" / "gsoc-data.json"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "en" / "community" / "gsoc"
```
y ejecútelo una vez por ubicación. Una solución adecuada tomaría la configuración regional como argumento y bucle, pero al momento de escribir este artículo, el script sigue siendo de ruta única y ciego a la configuración regional. Trate las constantes comprometidas como un error que hay que solucionar, no como un diseño en el que confiar.

## Dos derivas más para saber sobre {#two-more-drifts-to-know-about}

### Deriva del icono {#icon-drift}

El generador codifica `icon: material/school` en la portada de cada página que emite. Las páginas realmente confirmadas bajo `docs/en/community/gsoc/` usan `icon: bootstrap/school`: todo el sitio de documentos estandarizado en el conjunto de íconos `bootstrap/…` (consulte cualquier hermano en `docs/en/development/`, por ejemplo, `icon: bootstrap/terminal`). Por lo tanto, las páginas recién generadas aparecen con el espacio de nombres de ícono incorrecto y necesitan una corrección de una sola línea, o la cadena de texto frontal del generador necesita actualizarse a `bootstrap/school`. Hasta que alguien haga esto último, espere corregirlo manualmente en cada regeneración.

### Las páginas comprometidas son más ricas que el generador {#the-committed-pages-are-richer-than-the-generator}

Si compara una página comprometida con lo que produciría el generador, no coinciden, y eso es lo esperado. Tome `docs/en/community/gsoc/2023.md`: el diseño anterior del generador le daría dos bloques `### {name}` con una descripción de una línea y un `**Result**:` cada uno. En cambio, la página comprometida tiene un análisis profundo de **Cumplimiento de COPPA**, listas de viñetas de "Logros clave" e "Implementación técnica", una tabla de beneficios de Selenium-vs-Cypress, una sección de "Ideas de proyectos (2023)" y una tabla de estadísticas; ninguna de las cuales existe en `gsoc-data.json`. Del mismo modo, `2026.md` está comprometido y activo a pesar de que el año más nuevo del archivo de datos sigue siendo `2025`.

La conclusión: el generador es una **herramienta de arranque para el esqueleto inicial de una página de un año**, no el renderizador autorizado de las páginas que ves en el sitio. La regeneración *sobrescribirá* esas secciones hechas a mano con la plantilla básica. Entonces, antes de volver a ejecutarlo en un año que ya ha sido enriquecido manualmente, asegúrese de estar preparado para volver a aplicar (o restaurar con git) el contenido más rico o, mejor, solo regenerar años genuinamente nuevos.

## Diseño de archivo {#file-layout}

```
docs/<lang>/community/gsoc/
├── _data/
│   ├── gsoc-data.json   # the generator's input (JSON only)
│   └── gsoc-data.yaml   # human-editable mirror; NOT read by the generator
├── index.md             # public hub (cards + links) — hand-written, not generated
├── 2023.md              # generated skeleton, then hand-enriched
├── 2024.md
├── 2025.md
├── 2026.md
└── …
```
Una regla permanente para esta carpeta: **nunca coloque un `README.md` junto a `index.md`.** Zensical trata a `README.md` como el índice de sección, por lo que reclamaría la URL de `/community/gsoc/` y ocultaría el centro `index.md` real. Si la página de destino alguna vez "desaparece", lo primero que debe verificar es un `README.md` perdido.

## Notas {#notes}

- El generador es una biblioteca estándar pura (`json`, `sys`, `pathlib`): no necesita dependencias ni virtualenv. Esa restricción es la razón por la que lee JSON y no el espejo YAML más amigable.
- No se ejecuta durante `build_all.py`; La regeneración es siempre un paso manual y deliberado que se revisa antes de comprometerse.
- Confirme los archivos `YYYY.md` generados (y pulidos a mano) junto con el cambio de datos para que el sitio y su fuente permanezcan sincronizados.
</content>
</invoke>
