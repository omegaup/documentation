---
title: Directrices de codificación
description: Estándares de codificación y mejores prácticas para el desarrollo de omegaUp
icon: bootstrap/code
---
# Pautas de codificación

La mayoría de las reglas de esta página no las aplica un revisor humano que lo regaña en un comentario de solicitud de extracción. Se verifican automáticamente en GitHub mediante linters y pruebas de integración, y siempre que podemos, insertamos una regla en esa automatización para que detecte las regresiones por sí sola y libere la revisión del código para centrarse en las partes interesantes de su cambio. Así que piense en esta página menos como una lista de decretos y más como el razonamiento detrás de lo que la máquina ya le dirá, escrito para que comprenda *por qué* antes de que el CI lo haga por usted. La única metarregla de la que desciende todo lo demás: **prefiero explicar _por qué_ las cosas se hacen de la forma en que se hacen** en lugar de reformular _lo_ que_ obviamente hace el código.

Puede verificar su código con casi todo esto localmente, antes de enviarlo, con:

```bash
./stuff/lint.sh validate
```
Ese script no ejecuta las herramientas directamente en su máquina. Se distribuye en una imagen de Docker fijada (actualmente `omegaup/hook_tools:v1.0.9`) para que cada colaborador obtenga resultados idénticos en bytes de `yapf`, `prettier`, `phpcbf`, Psalm y `mypy`, independientemente de lo que esté instalado en su computadora portátil. Ejecútelo *fuera* del contenedor: si `OMEGAUP_ROOT` se resuelve en `/opt/omegaup`, el script se niega y se lo indica, porque esa ruta solo existe dentro del contenedor de desarrollo donde Docker-in-Docker no está disponible. Llamado sin argumentos, adivina el conjunto de archivos que cambió (a diferencia de `upstream/main` o `origin/main` si no ha agregado el control remoto ascendente) y se ejecuta en modo `fix`, editándolos en su lugar; pase `validate` cuando solo quiera que informe.

## Principios generales

**Declarar tipos en cada interfaz.** Cada función debe declarar los tipos de sus parámetros y su valor de retorno; esto no es opcional y los analizadores estáticos fallarán en la compilación sin esto. Usamos [TypeScript](https://www.typescriptlang.org/) (actualmente 4.4.4) en la interfaz, [Psalm](https://psalm.dev/) (actualmente 4.29, configurado en `psalm.xml`) para PHP en `frontend/server/` y [mypy](https://mypy-lang.org/) para las herramientas Python en `stuff/`. Más allá de la interfaz, también se prefiere anotar los tipos de matrices y mapas declarados *dentro* de una función, porque un `[]` o `array()` simple no le dice nada al siguiente lector sobre lo que debe contener.

**Escribe todo en inglés**: código, identificadores y comentarios por igual. omegaUp es un proyecto con colaboradores en muchos países, y el inglés es el único idioma que se supone que leen todos los que tocan el código.

**El comportamiento nuevo o modificado se envía con las pruebas.** Cualquier cambio en la funcionalidad (una corrección de errores, una característica nueva, un caso extremo modificado) debe venir con las pruebas nuevas o modificadas que lo identifiquen. Esta es una regla estricta, no una sutileza, y se verifica en CI.

**Evita `null` y `undefined` siempre que puedas**, y especialmente en los parámetros de función; aquí es donde hacen más daño y merece su propia sección a continuación.

**Evite funciones (y componentes de Vue) que bifurcan su comportamiento en una bandera.** Un parámetro booleano que hace que una función haga una cosa sustancialmente diferente cuando `true` y otra cuando `false` son en realidad dos funciones que llevan una gabardina. Divídalos en dos funciones con nombres claros y llame a la correcta en el sitio de llamada; en Vue, abstraiga el comportamiento diferente en un [`slot`](https://vuejs.org/v2/guide/components-slots.html) para que la persona que llama lo proporcione. Esto mantiene a cada unidad haciendo algo comprensible.

**Utilice el [Patrón de cláusula de protección](https://refactoring.com/catalog/replaceNestedConditionalWithGuardClauses.html)** siempre que sea posible; regrese temprano en los casos excepcionales para que el camino feliz no quede enterrado bajo `if` anidados.

**Elimine el código inactivo, nunca lo comente.** No debe haber bloques comentados persistentes "por si acaso". Si lo necesita de vuelta, está en el historial de git; para eso es exactamente el control de versiones, y un bloque comentado es solo ruido que pudre y engaña.

**Minimizar la distancia entre el lugar donde se declara una variable y el lugar donde se usa por primera vez.** El punto es reducir la cantidad de código irrelevante que un lector tiene que tener en su cabeza para saber qué contiene actualmente una variable; Declarar cosas en la parte superior de una función larga y usarlas cincuenta líneas hacia abajo obliga a todos a seguir desplazándose.

**Comente el _por qué_, no el _qué_.** Un comentario que diga `// increment counter` encima de `counter++` es peor que ningún comentario, porque es un desorden que puede volverse obsoleto silenciosamente. Los comentarios ganan su lugar al explicar lo que no es obvio: el razonamiento, la restricción, el problema histórico que hizo que el código pareciera extraño.

```php
// Bad — restates what the code plainly does:
// Increment counter
$counter++;

// Better — explains why this line exists at all:
// Count retries so we can back off once we exceed the rate-limit threshold.
$counter++;
```
### La regla `null`/`undefined` y por qué existe

Esto merece más que una bala, porque es la regla que la gente más a menudo se equivoca. `null` solo debería significar "el usuario no proporcionó esto" y `undefined` solo debería aparecer en la declaración de parámetros opcionales de TypeScript. No declares un tipo que pueda ser *ambos* `null` y `undefined` a la vez; elige el que tenga significado. 

Aquí está el razonamiento que hace que la regla no sea negociable en lugar de estilística: **cada parámetro que puede ser independientemente `null` o `undefined` duplica el número de combinaciones de entrada distintas que la función debe manejar correctamente, y ese recuento crece exponencialmente.** Dos parámetros que aceptan valores NULL son cuatro combinaciones; cuatro son dieciséis; diez son más de mil estados en los que implícitamente afirmas haber pensado y probado. **Mantenga el número de combinaciones de este tipo por debajo de 10.**

Y cuando la capacidad de nulidad *es* legítima, los campos que aceptan valores anulables deben poder ser nulos *independientemente uno de otro*. Si descubre que un subconjunto de parámetros siempre debe pasarse juntos (todos presentes o ausentes), es una señal de que pertenecen a su propio tipo, no como argumentos opcionales sueltos. Por ejemplo, un validador personalizado necesita un idioma y un tiempo de espera, pero solo cuando la validación personalizada está activada:

```php
// Bad — validatorLanguage and validatorTimeout are secretly coupled to
// customValidator, but nothing in the signature says so, and they multiply
// the combination count:
function myFunc(
    \OmegaUp\DAO\VO\Problems $problem,
    bool $customValidator,
    ?string $validatorLanguage = null,
    ?int $validatorTimeout = null,
): void {
```
Agrupe los campos acoplados en un tipo intermedio, de modo que "la validación personalizada está activada" y "aquí están sus dos configuraciones requeridas" se conviertan en una sola e indivisible parte del estado:

```php
/**
 * @psalm-type ValidatorOptions=array{language: string, timeout: int}
 */
// ...
/**
 * @param null|ValidatorOptions $customValidatorOptions
 */
function myFunc(
    \OmegaUp\DAO\VO\Problems $problem,
    ?array $customValidatorOptions = null,
): void {
```
Ahora hay exactamente un parámetro que acepta valores NULL en lugar de tres, `null` significa sin ambigüedades "sin validación personalizada" y es imposible representar el estado sin sentido de un idioma sin un tiempo de espera.

### Nombrar

Utilice [camelCase](https://en.wikipedia.org/wiki/Camel_case) para nombres de funciones, variables y clases. Las excepciones donde [snake_case](https://en.wikipedia.org/wiki/Snake_case) es correcto son todos los lugares donde el nombre lo dicta algo fuera de nuestro mundo PHP/TypeScript:

- Nombres de columnas de MySQL
- Variables y parámetros de Python (snake_case es la norma de la comunidad Python, y `yapf`/`pylint` lo esperan)
- Parámetros API (cruzan el cable y aparecen en `api_types.ts`, por lo que su carcasa es un contrato)

Y **evite abreviaturas** tanto en los identificadores como en los comentarios. `cnt`, `usr`, `tmp` ahorran algunas pulsaciones de teclas al autor y le cuestan a cada futuro lector un momento de "espera, ¿qué es eso?"; una abreviatura que es obvia para ti, rara vez lo es para todos.

## Formato

Deliberadamente no discutimos sobre el formato; Delegamos toda la pregunta a herramientas automatizadas para que nadie dedique una revisión del código a la colocación de llaves. [`yapf`](https://github.com/google/yapf) formatea Python, [`prettier`](https://prettier.io/) formatea TypeScript y Vue, y [`phpcbf`](https://github.com/squizlabs/PHP_CodeSniffer) (la mitad de reparación automática de PHP_CodeSniffer) formatea PHP. Al ejecutar `./stuff/lint.sh` sin argumentos, se aplican los tres a los archivos modificados en su lugar.

Las reglas que aplican esas herramientas, como referencia:

- 2 o 4 espacios de sangría según el tipo de archivo, nunca tabulaciones.
- Finales de línea de Unix (`\n`), no de Windows (`\r\n`).
- Llave de apertura en la misma línea que el enunciado que la introduce.
- Un espacio entre una palabra clave y su paréntesis para `if`, `else`, `while`, `switch`, `catch` y `function`, pero *sin* espacio antes del paréntesis de una función *llamada*.
- No hay espacios dentro de paréntesis.
- Un espacio después de cada coma, ninguno antes.
- Un espacio a ambos lados de cada operador binario.
- Como máximo una línea en blanco seguida.
- No hay comentarios vacíos.
- Sólo comentarios de línea `//`; Nunca el `/* ... */` bloquea comentarios.

```php
if (condition) {
    stuff;
}
```
##PHP

**Las pruebas pasan el 100% antes de confirmar, sin excepciones.** Ejecútelas localmente; una suite roja nunca es "probablemente buena".

**Evite viajes de ida y vuelta de la base de datos O(n).** Un bucle que llama a un método DAO una vez por elemento, incluido todo lo que toque los DAO generados automáticamente en `frontend/server/src/DAO/`, convierte una operación lógica en *n* viajes de ida y vuelta de red a MySQL, y esa es la forma clásica en que un punto final que es ágil con datos de prueba cae en producción. En su lugar, escriba una única consulta manual que haga todo el trabajo en un solo viaje.

```php
// Bad — one query per user, N round trips to MySQL:
foreach ($users as $user) {
    $runs = \OmegaUp\DAO\Runs::getByUserId($user->user_id);
}

// Better — one query for all of them:
$runs = \OmegaUp\DAO\Runs::getByUserIds(
    array_map(fn ($u) => $u->user_id, $users)
);
```
**Solo las funciones API pueden recibir `\OmegaUp\Request`.** Los métodos `apiXxx` en los controladores bajo `frontend/server/src/Controllers/` (en el espacio de nombres `\OmegaUp\Controllers`) son el límite donde una solicitud sin tipo proporcionada por el usuario ingresa al sistema; por ejemplo, `\OmegaUp\Controllers\Run::apiCreate(\OmegaUp\Request $r)`, que valida la solicitud y luego, una vez que todo está comprobado, entrega el trabajo a `\OmegaUp\Grader::getInstance()->grade(...)`. Cada función *detrás* de ese límite debe tomar parámetros escritos. Entonces, el trabajo de cada método `apiXxx` es validar la solicitud, extraer cada campo en una variable local escrita correctamente y luego llamar a las funciones internas con esas variables, nunca para pasar `$r` más profundamente en el código. Esto mantiene el núcleo tipado del sistema genuinamente escrito y limita toda la incertidumbre de "¿el usuario realmente envió este campo" a una capa delgada?

**Documente cada función** en el estilo de comentario en bloque Salmo y los revisores esperan: un resumen de una línea, una breve explicación de *por qué* existe cuando eso no es obvio y anotaciones `@param`/`@return`:

```php
/**
 * set
 *
 * If cache is on, save the value under key with the given timeout.
 *
 * @param string $value
 * @param int $timeout
 * @return boolean
 */
public function set($value, $timeout) { ... }
```
**Informar errores con excepciones**, no valores de retorno centinela. Una función que devuelve `true`/`false` está bien cuando el valor booleano es una respuesta genuinamente esperada ("¿existe este usuario?"), pero "algo salió mal" es para lo que sirven las excepciones.

**Todas las API devuelven matrices asociativas.** Esto es lo que `\OmegaUp\ApiCaller` serializa al cliente y lo que `frontend/server/cmd/APITool.php` lee para generar el cliente frontend escrito, por lo que la forma es un contrato, no una conveniencia.

**Utilice [RAII](https://en.wikipedia.org/wiki/Resource_Acquisition_Is_Initialization)** cuando sea necesario, principalmente para la gestión de recursos (archivos, bloqueos y similares): vincule la vida útil de un recurso con la de un objeto para que la limpieza no se pueda olvidar en una devolución anticipada o en una excepción.

## Vista

La interfaz de usuario de omegaUp son componentes de un solo archivo de Vue 2.7.16 (actualmente en mitad de la migración a Vue 3, rastreados en los directorios raíz `vue-upgrade-tool/` y `vue-js-tutorial/`) en `frontend/www/js/omegaup/components/`. Algunas reglas mantienen esos componentes mantenibles y traducibles.

**Prefiera `slot` a los indicadores de comportamiento**, por la misma razón que las funciones: un componente que cambia radicalmente lo que representa en función de un accesorio booleano son dos componentes fusionados. Exponga la parte variable como [`slot`](https://vuejs.org/v2/guide/components-slots.html) y deje que la persona que llama la complete. Si varios sitios de llamadas quieren la misma variante, envuélvala en *otro* componente que proporcione esa ranura.

**Nunca codifique el texto de cara al usuario.** Toda la interfaz debe representarse en varios idiomas, por lo que cada cadena que ve el usuario proviene de una clave de traducción (`T.someKey`), no de un literal. Y **no concatene cadenas de traducción**: el orden de las palabras difiere entre idiomas, por lo que pegar fragmentos produce basura en algunos de ellos. Utilice `ui.formatString` con parámetros con nombre para que la traducción misma controle el orden:

```html
<!-- Bad — the fixed word order can't survive translation:
     contestRanking = "Contest ranking: "
-->
<div>{{ T.contestRanking }} {{ user.rank }} {{ user.username }}</div>

<!-- Better — the whole sentence, with slots, lives in the translation string:
     contestRanking = "Contest ranking: %(rank) %(username)"
-->
<div>{{ ui.formatString(T.contestRanking, { rank: user.rank, username: user.username }) }}</div>
```
**No codifique los colores** como hexadecimal o `rgb(...)`. Declarelos como variables CSS y haga referencia a ellas, porque el modo oscuro funciona intercambiando los valores de las variables: un `#ffffff` literal es un cuadrado blanco que el modo oscuro no puede alcanzar.

**Evite los ganchos del ciclo de vida a menos que el componente realmente toque el DOM** y trate de evitar tocar el DOM en primer lugar. En un marco reactivo, alcanzar `mounted()` para tocar un elemento suele ser una señal de que algún estado debería haber sido reactivo. Que es la otra mitad de esto: **prefiero [observadores y propiedades calculadas](https://vuejs.org/v2/guide/computed.html)** a recalcular y reasignar variables manualmente. Deje que la reactividad de Vue rastree las dependencias por usted en lugar de hacerlo a mano y equivocarse sutilmente.

**Agregue una historia de Storybook para cada componente nuevo** y actualice la historia cuando cambie los accesorios o estados de un componente. Storybook (actualmente 7.6) le permite desarrollar y observar un componente de forma aislada, desacoplado del resto de la aplicación, lo que es bueno para reutilizarlo y para revisores que desean ver cada estado sin hacer clic en el sitio en vivo. Ni siquiera necesitas Docker para ejecutarlo:

```bash
yarn storybook
```
Eso inicia el panel en [localhost:6006](http://localhost:6006). Para agregar una historia, coloque un archivo `Component.stories.ts` al lado del componente (por ejemplo, `Badge.stories.ts` al lado de `Badge.vue`), importe el componente y exporte un `meta` más un `StoryObj` por estado que desee mostrar:

```ts
import { StoryObj, Meta } from '@storybook/vue';
import Badge from './Badge.vue';

const meta: Meta<typeof Badge> = {
  component: Badge,
  // argTypes turns props into interactive controls in the dashboard.
  argTypes: {},
};
export default meta;

type Story = StoryObj<typeof meta>;

export const Unlocked: Story = {
  // args are the props passed to the component for this story.
  args: {
    badge_alias: '100solvedProblems',
    unlocked: true,
  },
};
```
La cobertura aquí aún es escasa (actualmente alrededor de 10 archivos de historias contra 257 componentes), por lo que una nueva historia es casi siempre una adición neta, no un duplicado.

## Mecanografiado

**Cuando una función supera los 2 o 3 parámetros**, y *especialmente* si varias comparten el mismo tipo, y *definitivamente* si varias son opcionales, cambie a un solo parámetro de objeto. Los argumentos posicionales del mismo tipo son un error a punto de ocurrir (`updateProblem(problem, currentVersion, previousVersion)` intercambia silenciosamente dos cadenas y realiza comprobaciones de tipos correctamente); Los campos de objeto con nombre hacen que la llamada sea autodocumentada e independiente del pedido:

```ts
// Bad — four positional params, two of them interchangeable strings:
function updateProblem(
  problem: Problem,
  previousVersion: string,
  currentVersion: string,
  points?: number,
): void { ... }

// Better — one object, every argument named at the call site:
function updateProblem({
  problem,
  previousVersion,
  currentVersion,
  points,
}: {
  problem: Problem;
  previousVersion: string;
  currentVersion: string;
  points?: number;
}): void { ... }
```
**Evite [aserciones de tipo](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-assertions).** Una conversión `as` consiste en anular el compilador, por lo que solo se permite cuando el compilador realmente no puede conocer el tipo:

- interactuar con el DOM (`document.querySelector` y amigos);
- anotar un literal vacío, p. `null as null | string` o `[] as Foo[]`;
- en pruebas, declarar `params` en el constructor Vue.

**No toque el cliente API generado con la mano.** `frontend/www/js/omegaup/api.ts` y `frontend/www/js/omegaup/api_types.ts` comienzan con `// generated by frontend/server/cmd/APITool.php. DO NOT EDIT.`; se regeneran a partir de las anotaciones `@omegaup-request-param` y los tipos de DAO de los controladores PHP, por lo que una edición que realice allí está a una ejecución de `APITool.php` de ser sobrescrita silenciosamente. Cambie el PHP, luego regenere.

**¡No uses jQuery!** Ha quedado obsoleto y ya no se puede usar en ninguna parte del código base. Busque el marco (reactividad de Vue, referencias) o API DOM simples.

## Pitón

El Python aquí son los ~24 scripts de herramientas en `stuff/`, verificados por `mypy`, `flake8` y `pylint` y formateados por `yapf`.

**Después de 2 o 3 parámetros, conviértalos solo en palabras clave**: el mismo razonamiento que la regla del objeto TypeScript, expresado de forma Pythonic con un simple `*` en la firma, de modo que quienes llaman *deben* nombrar cada argumento:

```python
# Bad — positional, and previous/current are easy to swap:
def update_problem(problem: Problem, previous_version: str,
                   current_version: str, points: Optional[int] = None) -> None: ...

# Better — the leading * forces every caller to name its arguments:
def update_problem(
    *,
    problem: Problem,
    previous_version: str,
    current_version: str,
    points: Optional[int] = None,
) -> None: ...
```
**Utilice Snake_case para funciones y variables, CamelCase para clases**: estilo estándar de Python, que `pylint` aplica.

**Importar módulos, no nombres.** Evite `from module import function`; importe el módulo y use el acceso con puntos, de modo que en cada sitio de llamadas sea obvio de dónde vino `function` y no haya ambigüedad sobre a qué `function` se refiere:

```python
# Bad — where did function come from three screens later?
from module import function
function()

# Better — the origin travels with every call:
import module
module.function()
```
La única excepción es el módulo `typing`, donde `from typing import Optional, List` es idiomático y se entiende universalmente.

## Documentación relacionada

- **[Guía de pruebas](testing.md)**: cómo escribir las pruebas que requiere cada cambio funcional
- **[Comandos útiles](useful-commands.md)**: los comandos de desarrollo diarios
- **[Guía de componentes](components.md)** — creación de componentes de Vue en profundidad

---

**Recuerde:** casi todo lo anterior se aplica mediante automatización, así que ejecute `./stuff/lint.sh validate` antes de confirmar y deje que las herramientas lo detecten primero.
