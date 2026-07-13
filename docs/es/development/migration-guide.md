---
title: Guía de migración
description: El estilo interno para crear una página en Vue + TypeScript encima del shell Twig, más la actualización actual de Vue 2 a Vue 3.
icon: bootstrap/arrow-right
---
# Guía de migración: cómo construimos una página

Érase una vez esta página describía una migración en vuelo: tire de un Smarty `.tpl`
Aparte, entregue los datos a un componente de Vue y elimine la plantilla. Esa migración es
**hecho**. La interfaz ahora son componentes de un solo archivo de Vue de un extremo a otro, a partir de este momento
escribir 257 archivos `.vue` y 414 archivos `.ts` en una sola aplicación
plantilla, `frontend/templates/template.tpl`, y ese único superviviente es un Twig 3
Shell, no Smarty. Smarty se ha ido; HHVM se ha ido; el backend es simple PHP 8.1
ejecutándose bajo php-fpm detrás de nginx.

Así que lea esta página de dos maneras. Primero, el paso a paso a continuación ya no es un
tarea única: es **el estilo de la casa** conectar cualquier página nueva a omegaUp,
porque cada página sigue recorriendo el mismo camino: un controlador PHP ensambla un
escrito `payload`, el shell Twig lo serializa en HTML, un TypeScript
El punto de entrada lo analiza nuevamente y un componente de Vue lo representa. Aprende este camino una vez
y puedes agregar una página sin preguntarle a nadie cómo funciona la plomería. En segundo lugar, el
una migración que *está* aún activa es **Vue 2.7 → Vue 3**; el codemod y el
Los materiales de aprendizaje para ese esfuerzo ya están disponibles en el repositorio, y hay una
sección en la parte inferior sobre dónde dirigir su atención.

## El camino que recorre una página

Antes de la lista de verificación, sostenga todo el proceso en su cabeza, porque cada paso
A continuación se muestra solo una estación. Cuando un navegador solicita, por ejemplo, la página de inicio de sesión,
el método del controlador `\OmegaUp\Controllers\User::apiLoginDetailsForTypeScript`
(en `frontend/server/src/Controllers/User.php`) construye una matriz con dos
claves importantes: un nombre `entrypoint` cuyo paquete TypeScript compilado debería
ejecutar y un `templateProperties` que contiene el `payload` (los datos que necesita la página)
y un `title`. El shell Twig representa esa carga útil palabra por palabra en la página como
`<script type="text/json" id="payload">…</script>`: puedes ver la línea exacta
en `frontend/templates/template.tpl` - y luego `{% entrypoint %}` cae en el
Etiqueta `<script>` para el paquete compilado, seguida de un espacio vacío
`<div id="main-container"></div>` para que Vue lo monte. En el cliente, el
El archivo `.ts` de punto de entrada lee ese JSON a través de un analizador generado, `nuevo
Vue(...)`s a component into `#main-container`, y le entrega la carga útil como accesorios.

Ese es el camino. Observe que el campo es `templateProperties`, **no**
`smartyProperties`: si encuentra el nombre antiguo en una rama con años de antigüedad, ese es el
Ortografía de la era Smarty y ya no existe en el código base. Note también que el
el controlador nunca muestra HTML; devuelve datos y el shell + el punto de entrada
hacer el renderizado. Mantener esa división es el punto: PHP posee los datos y
En sus tipos, Vue posee los píxeles.

## Paso 1: configurar la carga útil de PHP

Comience en el servidor, porque los tipos que define aquí son el contrato completo
desde donde se genera la interfaz.

Encuentre el método de controlador que sirve a su página. La convención es un método.
con el sufijo `ForTypeScript`: para la vista de inicio de sesión que está
`apiLoginDetailsForTypeScript` en `frontend/server/src/Controllers/User.php`. su
El trabajo es recopilar todos los datos que la página necesita y ponerlos bajo
`templateProperties['payload']`. Todo lo que el componente renderice debe vivir
dentro de ese `payload`; todo lo que queda fuera nunca llega al navegador.

Una vez que se hayan reunido los datos, asigne a la carga útil un **tipo de salmo**. esto no es
contabilidad opcional: es la única fuente de verdad a partir de la cual TypeScript
Los tipos y el analizador en tiempo de ejecución se generan automáticamente. Declaras el tipo como
Anotación `@psalm-type` y haga referencia a ella en el bloque de documentación `@return` del método. en
`User.php` el método de inicio de sesión está anotado:

```php
/**
 * @return array{
 *   entrypoint: string,
 *   templateProperties: array{
 *     payload: LoginDetailsPayload,
 *     title: \OmegaUp\TranslationString
 *   }
 * }
 */
```
`LoginDetailsPayload` es un tipo de Salmo con nombre declarado en otra parte del archivo, y
ese nombre es exactamente lo que analizará en el cliente, así que elíjalo bien.
Dos campos más en esa forma de retorno se ganan la vida:

- **`title`** es un `\OmegaUp\TranslationString`, no una cadena simple. debe
  resolver en una clave `omegaupTitle…` que existe en los tres `en.lang`,
  `es.lang` y `pt.lang`, porque omegaUp representa el título de la página en cualquier
  idioma para el que está configurada la cuenta. Salta la entrada `.lang` y el título.
  se representa como la clave sin formato.
- **`entrypoint`** es el nombre del paquete compilado que representará esto
  carga útil: una cadena simple como `'login_signin'`. No es necesario que exista todavía;
  lo creará en el Paso 2. Se asigna a una entrada en la configuración del paquete web (más información sobre
  eso en un momento).

Cuando la carga útil y su tipo estén en su lugar, ejecute `stuff/lint.sh`. haz esto antes
tocas cualquier TypeScript, **porque** el linter es lo que regenera el cliente
definiciones de tipo y el analizador de tiempo de ejecución de su tipo de Salmo: el
Los archivos `.ts` que está a punto de escribir dependen de la salida generada existente. el
Los archivos generados son `frontend/www/js/omegaup/api_types.ts` (el tipo de formas y
el `payloadParsers`) y el `frontend/www/js/omegaup/api.ts` (el tipo
envolvedoras `apiCall<>`); ambos son producidos por `frontend/server/cmd/APITool.php` y
ambos se abren con un banner `// generated by … DO NOT EDIT.`, por lo que nunca los edite manualmente
ellos: arregle el tipo de Salmo y vuelva a ejecutar el linter. También puedes correr
`stuff/runtests.sh` para confirmar que el cambio de su controlador no rompió nada
el lado PHP.

## Paso 2: Conecte el punto de entrada de TypeScript

Gracias al shell Twig unificado, no tocas el `template.tpl` en absoluto: el
shell ya sabe cómo serializar su carga útil e inyectar el punto de entrada
guión. Si el lado de PHP es correcto, todo el trabajo de su cliente ocurre en el
archivo `.ts` de punto de entrada.

!!! nota "¿Viene de un archivo `.js`?"
    Si realmente está convirtiendo un archivo antiguo `.js` a `.ts`, siga estos mismos
    pasos, pero aproveche el hecho de que la mayor parte de la lógica ya existe.
    No lo reescribas desde cero; obtener el comportamiento existente compilando bajo
    Primero escriba TypeScript y luego mejórelo.

Primero, asegúrese de que el nombre `entrypoint` que eligió en el Paso 1 esté registrado en el
Configuración del paquete web y apunta a un archivo real. Las entradas del frontend viven en
`webpack.config-frontend.js` en la raíz del repositorio; la entrada de inicio de sesión es única
línea allí:

```js
login_signin: './frontend/www/js/omegaup/login/signin.ts',
```
Si ese archivo aún no existe, créelo. La forma es repetitiva y puedes copiarla.
desde cualquier punto de entrada vecino: `schools/schoolofthemonth.ts` es un lugar limpio y
ejemplo mínimo. Cada punto de entrada importa los mismos asistentes principales (`OmegaUp` para
el gancho listo, `types` para los analizadores, `api` para llamadas API escritas, `ui`, el
función de traducción `T` de `../lang`, `Vue` y el componente que monta),
espera a que la página esté lista, analiza la carga útil y monta una instancia de Vue
en `#main-container`:

```ts
import { OmegaUp } from '../omegaup';
import { types } from '../api_types';
import Vue from 'vue';
import schoolOfTheMonth_List from '../components/schoolofthemonth/List.vue';

OmegaUp.on('ready', () => {
  const payload = types.payloadParsers.SchoolOfTheMonthPayload();
  new Vue({
    el: '#main-container',
    components: { 'school-of-the-month-list': schoolOfTheMonth_List },
    // …pass payload fields down as props here…
  });
});
```
La línea de carga es `types.payloadParsers.SchoolOfTheMonthPayload()`. eso
El analizador lee el JSON `<script id="payload">` que escribió el shell Twig y lo devuelve.
**escrito** como la forma exacta que definiste en PHP. El nombre del analizador es tu Salmo.
escriba el nombre: `LoginDetailsPayload` en PHP se convierte
`types.payloadParsers.LoginDetailsPayload()` en el punto de entrada. Si el analizador usted
querer no existe, casi siempre es porque el tipo de salmo es incorrecto o
No he vuelto a ejecutar `stuff/lint.sh` desde que lo agregué; regrese al Paso 1, corrija el tipo,
regenerar. No busque `JSON.parse` ni enrolle la forma a mano; todo el punto
del analizador generado es que PHP y TypeScript nunca pueden estar en desacuerdo sobre lo que
contiene la carga útil.

Dos hábitos mantienen limpios los puntos de entrada. Haga sus **llamadas API aquí en el archivo `.ts`**,
no dentro del componente: el punto de entrada busca, el componente se muestra.
`common/navbar.ts` es el ejemplo canónico de un punto de entrada que llama a una API
y envía el resultado a su componente. E importa solo lo que uses; la pelusa
señalará el resto.

## Paso 3: construir el componente Vue (Bootstrap 4)

El componente recibe, como accesorios, los datos que analizó su punto de entrada, y esos
Los accesorios llevan los tipos exactos generados desde el Paso 1. Importarlos desde
`api_types.ts` y escriba sus `@Prop` contra ellos para que se produzca un cambio en la forma de la carga útil.
PHP aparece como un error de compilación en el componente, no como una sorpresa en tiempo de ejecución.
producción:

```vue
<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator';
import { types } from '../../api_types';

@Component
export default class SchoolOfTheMonthList extends Vue {
  @Prop({ required: true })
  schools!: types.SchoolOfTheMonthPayload['schools'];
}
</script>
```
Algunas reglas aquí no son negociables y cada una tiene una razón:

- **Bootstrap 4, no 3 y no 5.** omegaUp está en `bootstrap ^4.6.0` con
  `bootstrap-vue ^2.21.2`, y el shell carga Bootstrap 4 CSS. cada clase que
  el uso debe ser una clase BS4. Si está tocando un archivo `.vue` anterior al
  migración y todavía lleva el marcado BS3, migrelo a BS4 en el mismo cambio:
  **si no lo haces, no funcionará**, porque el shell unificado sólo incluye el BS4
  Las hojas de estilo y los nombres de clases BS3 se mostrarán silenciosamente sin estilo.
- **Evitar atributos `id`** dentro de los componentes. Se puede montar el mismo componente
  más de una vez en una página y los `id` duplicados son HTML no válidos que se rompen.
  `document.getElementById` y herramientas de accesibilidad. Llegar a una clase o un
  atributo `data-` en su lugar. Si realmente debe configurar un `id` (algunos fabricantes de terceros)
  El widget exige uno), hay una trampilla de escape: una bandera de componente existente que
  suprime la verificación de atributos reservados del linter, pero trata su necesidad como una
  olor.

El resto de las reglas internas para el código de componentes son lo suficientemente breves como para indicar
directamente, y existen en todos los SFC del árbol:

- **No uses jQuery.** Ahora somos un marco de componentes reactivos; llegando a
  el DOM lucha manualmente contra el marco y desincroniza el DOM virtual de Vue de
  lo que hay en la pantalla.
- **Prefiera el patrón de cláusula de guardia**: regrese temprano en los casos excepcionales para que
  el camino feliz se lee de arriba a abajo sin un anidamiento profundo.
- **Nombres de elementos y atributos HTML en kebab-case; nombres de métodos en camelCase.**
  La coherencia aquí es lo que te permite explorar el código base y encontrar cosas.
- **Utilice la interpolación literal de plantilla de ES6** en lugar de la concatenación de cadenas.
  es más corto y hay menos errores.
- **`let` y `const`, nunca `var`.** El alcance del bloque elimina una categoría completa de
  chinches de elevación.
- **Elimine el registro de depuración antes de confirmar.** `console.log` dejado en un componente
  se envía a la consola de cada usuario.

## Paso 4: Pruebe el componente en Jest

Un componente nuevo o modificado necesita una prueba y Codecov señalará el lugar exacto
líneas que su cambio dejó al descubierto. Las pruebas de componentes utilizan `@vue/test-utils`'
`shallowMount`, que representa el componente en un nivel de profundidad (componentes secundarios
se convierten en resguardos), por lo que está probando este componente de forma aislada en lugar de en su totalidad.
subárbol. El patrón, tomado de
`frontend/www/js/omegaup/components/arena/Arena.test.ts`, es para montar con
`propsData`, luego afirmar en el texto representado:

```ts
import { shallowMount } from '@vue/test-utils';
import arena_Arena from './Arena.vue';

describe('Arena.vue', () => {
  it('Should handle details for a contest', () => {
    const wrapper = shallowMount(arena_Arena, {
      propsData: { title: 'Hello omegaUp', activeTab: 'problems' },
    });
    expect(wrapper.find('.clock').text()).toBe('∞');
    expect(wrapper.find('div[data-arena-wrapper]>div>h2>span').text()).toBe(
      'Hello omegaUp',
    );
  });
});
```
Tenga en cuenta que las afirmaciones apuntan a `.clock` y a un selector `[data-arena-wrapper]`, no
un `id`, que es exactamente la razón por la que el Paso 3 le indica que evite los `id`: clase y
Los selectores `data-` son a lo que se aferran sus pruebas. Copiar una prueba vecina como
punto de partida; la forma apenas varía entre los componentes.

## La migración en vivo: Vue 2 → Vue 3

Todo lo anterior describe la construcción sobre la pila actual: **Vue 2.7.16** con
TypeScript 4.4.4, la API de opciones a través de `vue-property-decorator`, Vuex 3, Webpack
5. Eso es lo que se produce hoy en día. La única migración que aún está en movimiento es
levantando toda la parte frontal de Vue 2.7 a Vue 3, y las herramientas para ello ya
se encuentra en la raíz del repositorio:

- **`vue-upgrade-tool/`** es un codemod suministrado (basado en `vue-metamorph`) que
  transforma mecánicamente el código de Vue 2 a Vue 3: archivos JS/TS, SFC y unidades
  pruebas por igual. Preste atención a su propia advertencia: **no se garantiza que los resultados sean perfectos,
  y debes verificar manualmente cada cambio que realiza.** Tampoco formatea
  su salida es agradable, así que ejecute Prettier/ESLint sobre cualquier cosa que toque para traer el
  código nuevamente en línea con nuestras convenciones.
- **`vue-js-tutorial/`** contiene el material de aprendizaje para sentirse cómodo con
  los modismos de Vue 3 antes de comenzar a convertir componentes reales.

Debido a que 2.7 es la versión final de Vue 2, gran parte del código 2.7 existente (el
SFC `<script lang="ts">`, los accesorios escritos, el apretón de manos `payloadParsers`, es
ya está cerca de la forma de Vue 3, que es exactamente la razón por la cual la canalización en los Pasos 1 a 4
permanece válido durante la actualización. El controlador/carga útil/punto de entrada/carretera componente
no cambia; lo que cambia debajo es el tiempo de ejecución del componente. cuando tu
convertir un componente, ejecutar el codemod, verificarlo manualmente, volver a ejecutar su prueba Jest,
y reformatearlo antes de comprometerse.

## Documentación relacionada

- [Pautas de codificación](coding-guidelines.md): el conjunto completo de Vue y TypeScript
  estándares en los que se basan estos pasos.
- [Guía de componentes](components.md): convenciones más profundas para la estructura de componentes.
- [Arquitectura frontend](../architecture/frontend.md): cómo funciona el shell Twig, el
  puntos de entrada y los componentes encajan en general.
