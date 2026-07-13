---
title: Componentes de Vue
description: Desarrollo de componentes Vue.js e integración de Storybook
icon: bootstrap/view-grid
---
# Componentes de Vue

Casi toda la interfaz de usuario de omegaUp es Vue. La antigua migración de Smarty a Vue ya está completa: la aplicación actualmente incluye **257 componentes `.vue` de un solo archivo** en una sola plantilla del lado del servidor (`frontend/templates/template.tpl`, un shell Twig 3 que simplemente envuelve un punto de entrada de Vue e inyecta su carga útil JSON). Entonces, cuando construyes una página hoy, casi siempre estás construyendo (o conectando) componentes de Vue, no escribiendo HTML renderizado por el servidor.

Estamos en **Vue 2.7.16 + TypeScript 4.4.4**, usando la API de Opciones a través de `vue-property-decorator` (componentes estilo clase con `@Component` / `@Prop`). Hay una migración separada y lenta a Vue 3 que se encuentra en los directorios `vue-upgrade-tool/` y `vue-js-tutorial/` de nivel raíz, pero todo lo que escriba hoy apunta a Vue 2.7, así que no busque `<script setup>` o la API de composición.

## Dónde viven los componentes

Cada archivo `.vue` se encuentra en `frontend/www/js/omegaup/`, y **248 de los 257** se encuentran específicamente en `frontend/www/js/omegaup/components/`. No existe ningún `frontend/www/js/components/`; si buscas allí, no encontrarás nada.

Dentro de `components/` el árbol está agrupado por la parte del producto a la que pertenece un componente, no por tipo. Un puñado de bloques de construcción verdaderamente genéricos se encuentran en el nivel superior (`Markdown.vue`, `CountryFlag.vue`, `ToggleSwitch.vue`, `RadioSwitch.vue`, `Autocomplete.vue`, `DatePicker.vue`), y todo lo relacionado con características específicas se encuentra en un subdirectorio con nombre: `arena/`, `badge/`, `contest/`, `course/`, `group/`, `problem/`, `user/`, `homepage/`, `notification/`, `submissions/`, `common/` y alrededor de una docena más. Coloque un nuevo componente junto a sus hermanos (un nuevo widget de insignia pertenece a `components/badge/`, no a la raíz) para que la persona que lo sigue pueda encontrarlo por función.

### Un componente básico

```vue
<template>
  <div class="my-component">
    <h1>{% raw %}{{ title }}{% endraw %}</h1>
    <button @click="handleClick">{% raw %}{{ T.commonSave }}{% endraw %}</button>
  </div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator';
import T from '../../lang';

@Component
export default class MyComponent extends Vue {
  @Prop({ required: true })
  title!: string;

  T = T; // expose the translation table to the template

  handleClick(): void {
    this.$emit('clicked');
  }
}
</script>
```
Dos reglas que te molestarán si las ignoras, ambas porque aparecen en la revisión del código cada vez:

**Nunca codifique texto visible para el usuario.** Todas las cadenas provienen de la tabla de traducción `T` (`frontend/www/js/omegaup/lang`), por lo que el mismo componente se representa en español, inglés y portugués sin necesidad de reescribirlo. `<div>Hello</div>` no pasa la revisión; Pases `{% raw %}{{ T.helloWorld }}{% endraw %}`. Y cuando una cadena tenga un valor de tiempo de ejecución, no la concatene (`{% raw %}{{ T.greeting }} {{ userName }}{% endraw %}` se rompe en idiomas donde el orden de las palabras difiere); use `ui.formatString(T.greeting, { name: userName })` para que el marcador de posición acabe donde lo colocó el traductor.

**Prefiere ranuras a indicadores de comportamiento.** Un componente que voltea grandes porciones de su propio marcado basado en un accesorio `mode` o `variant` se convierte en una maraña que nadie quiere tocar. Exponga los `<slot>` con nombre y permita que la persona que llama proporcione las diferentes partes, de modo que un componente mantenga un trabajo:

```vue
<template>
  <div>
    <slot name="header"></slot>
    <slot name="content"></slot>
  </div>
</template>
```
El mismo espíritu para el estilo: busque las variables CSS (`var(--color-primary)`) en lugar de un `#ff0000` literal, de modo que un componente recoja los cambios de tema de forma gratuita en lugar de fijar un valor hexadecimal que alguien tendrá que buscar más tarde.

## Libro de cuentos

Storybook es donde desarrollas y analizas un componente **de forma aislada**, sin iniciar toda la aplicación. Le brinda un taller interactivo: renderice un componente por sí solo, voltee sus accesorios desde una barra lateral y vea cada estado y variación uno al lado del otro. Ese desacoplamiento es el punto: puede crear y revisar un `Badge` o un `ContestCard` sin un backend en ejecución, un usuario que haya iniciado sesión o las filas correctas de la base de datos, y los revisores pueden obtener exactamente los estados que usted creó.

Estamos en **Storybook 7.6** (`storybook@^7.6.21`), ejecutando Vue a través de `@storybook/vue` `7.4.6` en el constructor `@storybook/vue-webpack5`: la misma cadena de herramientas de Webpack 5 con la que se construye la aplicación real, por lo que un componente que se representa en Storybook se representa de la misma manera en producción.

### Ejecutándolo

Hay un script dedicado y, a diferencia de la mayoría de omegaUp, **no necesitas Docker up** para usarlo:

```bash
yarn storybook
```
Este ejecuta `storybook dev -p 6006` (consulte la entrada `storybook` en `package.json`), que compila la colección de historias y proporciona un panel en [http://localhost:6006](http://localhost:6006). Déjalo funcionando; se recarga en caliente a medida que edita un componente o su historia.

### Cómo está cableado

La configuración son dos archivos en `.storybook/`:

- **`.storybook/main.ts`** señala Storybook a las historias con el globo `../frontend/www/js/omegaup/**/*.stories.@(js|jsx|ts|tsx)`, en cualquier lugar debajo de `frontend/www/js/omegaup/`, por lo que también captura historias que no son `components/`, como las que están bajo `graderv2/`. Registra tres complementos (`addon-links`, `addon-essentials`, `addon-interactions`), configura `staticDirs: ['../frontend/www']` para que las rutas de recursos relativas se resuelvan exactamente como lo hacen en la aplicación, alias `@` a `frontend/www/` y enseña a la configuración del paquete web compartido cómo cargar `.vue`, `.scss`, `.css` y archivos de imagen. `docs.autodocs` está configurado en `'tag'`, por lo que una historia solo obtiene una página de documentos generada automáticamente si opta por etiquetarla.
- **`.storybook/preview.ts`** carga el CSS global que cada componente supone que está presente: `third_party/bootstrap-4.5.0/css/bootstrap.min.css` (estamos en **Bootstrap 4**, con `bootstrap-vue`, no Bootstrap 5) más FontAwesome 5.15.4 inyectado en el iframe `<head>`. También declara los comparadores `controls` que hacen que Storybook seleccione automáticamente el widget correcto: cualquier argumento que termine en `color`/`background` obtiene un selector de color, cualquier cosa que termine en `Date` obtiene un selector de fecha y una expresión regular `actions` (`^on[A-Z].*`) que registra los controladores coincidentes en el panel Acciones.

Sin `preview.ts` cargando Bootstrap y FontAwesome, su componente se mostraría sin estilo y sin íconos en Storybook a pesar de que se ve bien en la aplicación; esa falta de coincidencia es exactamente lo que este archivo pretende evitar.

### La realidad de la cobertura

Sea honesto consigo mismo sobre el estado de esto: **actualmente solo hay 10 archivos `.stories` para 257 componentes**. Storybook no es un lugar donde ya viven todos los componentes; es un lugar al que los estamos trasladando gradualmente. Si está tocando un componente y no tiene historia, agregar uno es una contribución realmente bienvenida y de bajo riesgo.

### Escribir una historia

La convención es un archivo de historia por componente, con su nombre y ubicado **justo al lado del archivo `.vue`**: para `Badge.vue`, crea `Badge.stories.ts` en la misma carpeta. (Es por eso que el globo es una coincidencia recursiva de `**` en lugar de un único directorio de historias: las historias viven dondequiera que vivan sus componentes).

Escribimos **Formato de historia del componente 3 (CSF3)**: un objeto `meta` exportado de forma predeterminada que describe el componente, luego una exportación con nombre por estado que desea mostrar, cada uno de ellos un `StoryObj`. Aquí está el `ToggleSwitch.stories.ts` real, que es una buena plantilla mínima para copiar:

```ts
import { StoryObj, Meta } from '@storybook/vue';
import ToggleSwitch, { ToggleSwitchSize } from './ToggleSwitch.vue';

const meta: Meta<typeof ToggleSwitch> = {
  component: ToggleSwitch,
  title: 'Components/ToggleSwitch',
  argTypes: {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore FIXME: vue-property-decorator is deprecated, so we can't get prop types from the component
    textDescription: {
      control: 'text',
    },
    checkedValue: {
      control: 'boolean',
    },
    size: {
      control: 'select',
      options: ToggleSwitchSize,
    },
  },
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    textDescription: 'Text for the check',
    checkedValue: false,
    size: ToggleSwitchSize.Large,
  },
  render: (args, { argTypes }) => ({
    components: { ToggleSwitch },
    props: Object.keys(argTypes),
    template:
      '<toggle-switch :text-description="$props.textDescription" :checked-value="$props.checkedValue" :size="$props.size" />',
  }),
};

Default.storyName = 'ToggleSwitch';
```
Leyendo eso de arriba a abajo:

- **`title`** (`'Components/ToggleSwitch'`) es la ruta en la barra lateral de Storybook; la barra diagonal forma una carpeta. Siga la agrupación existente: los componentes genéricos y de nivel superior se encuentran en `Components/...`, los widgets de arena en `Arena/...` (consulte `ContestCardv2.stories.ts` titulado `'Arena/ContestCard'`), y así sucesivamente.
- **`argTypes`** declara cada accesorio y, fundamentalmente, *qué control lo representa* en el tablero: `control: 'text'` proporciona un cuadro de texto, `'boolean'` un interruptor, `'select'` con `options` un menú desplegable. Esto es lo que convierte un renderizado estático en un campo de juego controlado por perillas donde un revisor puede ejercitar cada estado manualmente.
- **Ese `@ts-ignore FIXME`** no es un texto repetitivo que puedas eliminar: soporta carga. Debido a que creamos componentes con el obsoleto `vue-property-decorator`, la escritura de Storybook 7 no puede inferir tipos de accesorios directamente a partir de la clase de componente, por lo que suprimimos el error resultante en `argTypes`. Copie el comentario tal cual; documenta *por qué* el ignorado está ahí para la siguiente persona.
- **`args`** son los valores predeterminados concretos que se introducen en esos controles cuando se representa la historia por primera vez.
- **`render`** crea la instancia de Vue real. La línea `props: Object.keys(argTypes)` reenvía cada argumento declarado al componente contenedor para que los controles estén conectados a accesorios reales, y la cadena `template` monta el componente con esos accesorios vinculados. Solo necesita `render` cuando el montaje predeterminado no es suficiente; para un componente simple, a menudo puede omitirlo y dejar que Storybook monte el componente directamente.
- **`storyName`** anula la etiqueta que se muestra para esa historia individual (de lo contrario, se deriva del nombre de la exportación, por ejemplo, `Default`).

Algunos componentes toman un objeto completo en lugar de accesorios planos, y la función de renderizado es donde lo ensamblas. `Badge.stories.ts` recopila sus argumentos y los pasa como un único objeto vinculado, `template: '<badge :badge="$props" />'`, con `badge_alias` expuesto como un control `select` sobre la lista completa de alias de insignias reales (`'100solvedProblems'`, `'coderOfTheMonth'`, `'problemSetter'`,…) para que pueda hojear cada insignia visualmente.

### Mostrando múltiples estados

El valor real aparece cuando un componente tiene estados significativamente diferentes: cree una exportación con nombre para cada uno. `ContestCardv2.stories.ts` es el modelo: define un `Template` reutilizable, luego exporta `Default`, `Recommended`, `Current`, `Future` y `Past`, cada uno de los cuales distribuye los argumentos base y anula solo los campos que difieren (un indicador recomendado, horas de inicio/finalización hace una hora versus un día fuera) para que los cinco estados del concurso se alineen uno al lado del otro en la barra lateral:

```ts
export const Future = Template.bind({});
Future.args = {
  contest: {
    ...Default.args.contest,
    title: 'Future Contest',
    start_time: new Date(Date.now() + 86400000), // 1 day from now
    finish_time: new Date(Date.now() + 172800000), // 2 days from now
    active: false,
  } as types.ContestListItem,
};
```
Tenga en cuenta el elenco de `as types.ContestListItem`: los datos simulados se escriben con los tipos de API **generados** en `frontend/www/js/omegaup/api_types.ts` (producido por `frontend/server/cmd/APITool.php`, marcado como `DO NOT EDIT`), para que sus dispositivos sean honestos con la forma que realmente envía el backend. Si falta un campo o el tipo es incorrecto, TypeScript se lo informa en la historia antes de llegar a una página.

`ContestCardv2.stories.ts` también está escrito en el estilo CSF2 anterior (`Template.bind({})` con `Story` de `@storybook/vue`) en lugar de CSF3 (ambos funcionan y ambos están en el árbol), pero prefiera el formulario CSF3 `StoryObj` que se muestra arriba para cualquier cosa nueva; es en torno a lo que se construye Storybook 7 y hacia dónde se dirige el ecosistema.

## Pruebas de componentes

Además de las historias, los componentes llevan pruebas unitarias de Jest llamadas `Component.test.ts` en la misma carpeta (verá `Countdown.test.ts`, `Markdown.test.ts`, `ToggleSwitch.test.ts` y amigos junto a sus archivos `.vue`). Utilice `@vue/test-utils` para montar y afirmar:

```ts
import { mount } from '@vue/test-utils';
import MyComponent from './MyComponent.vue';

describe('MyComponent', () => {
  it('renders title', () => {
    const wrapper = mount(MyComponent, {
      propsData: { title: 'Test' },
    });
    expect(wrapper.text()).toContain('Test');
  });
});
```
Piense en los dos como complementarios: la historia es la verificación visual y humana de cómo *se ve* un componente en sus estados; la prueba es la garantía automatizada de cómo *se comporta*. Un componente bien cubierto tiene ambas cosas.

## Documentación relacionada

- **[Pautas de codificación](coding-guidelines.md)**: las reglas completas de Vue/TypeScript (jQuery está prohibido, `T` para todas las cadenas, `ui.formatString` para interpolación)
- **[Guía de pruebas](testing.md)** — Jest, Cypress y cómo ejecutar las suites
- **[Arquitectura de interfaz](../architecture/frontend.md)**: cómo encajan el shell Twig, los puntos de entrada de Webpack y los componentes de Vue
