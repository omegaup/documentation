---
title: Componentes Vue
description: Desenvolvimento de componentes Vue.js e integração com Storybook
icon: bootstrap/view-grid
---
# Componentes Vue

Quase toda a UI do omegaUp é Vue. A antiga migração do Smarty para Vue está concluída: o aplicativo atualmente envia **257 componentes `.vue` de arquivo único** em um único modelo do lado do servidor (`frontend/templates/template.tpl`, um shell Twig 3 que apenas envolve um ponto de entrada Vue e injeta sua carga JSON). Portanto, quando você constrói uma página hoje, você quase sempre está construindo — ou conectando — componentes Vue, e não escrevendo HTML renderizado pelo servidor.

Estamos no **Vue 2.7.16 + TypeScript 4.4.4**, usando a API Options por meio de `vue-property-decorator` (componentes de estilo de classe com `@Component`/`@Prop`). Há uma migração separada e lenta para o Vue 3 que reside nos diretórios `vue-upgrade-tool/` e `vue-js-tutorial/` de nível raiz, mas tudo o que você escreve hoje tem como alvo o Vue 2.7, portanto, não procure `<script setup>` ou a API de composição.

## Onde os componentes residem

Cada arquivo `.vue` reside em `frontend/www/js/omegaup/`, e **248 dos 257** ficam especificamente em `frontend/www/js/omegaup/components/`. Não existe `frontend/www/js/components/` – se você procurar lá, não encontrará nada.

Dentro do `components/` a árvore é agrupada pela parte do produto à qual pertence um componente, não por tipo. Um punhado de blocos de construção verdadeiramente genéricos ficam no nível superior (`Markdown.vue`, `CountryFlag.vue`, `ToggleSwitch.vue`, `RadioSwitch.vue`, `Autocomplete.vue`, `DatePicker.vue`), e tudo o que é específico do recurso reside em um subdiretório nomeado: `arena/`, `badge/`, `contest/`, `course/`, `group/`, `problem/`, `user/`, `homepage/`, `notification/`, `submissions/`, `common/` e cerca de uma dúzia mais. Coloque um novo componente próximo a seus irmãos – um novo widget de crachá pertence ao `components/badge/`, não à raiz – para que a pessoa depois de você possa encontrá-lo por recurso.

### Um componente básico

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
Duas regras que irão incomodar você se você ignorá-las, ambas porque elas aparecem sempre na revisão de código:

**Nunca codifique texto voltado para o usuário.** Todas as strings vêm da tabela de tradução `T` (`frontend/www/js/omegaup/lang`), portanto, o mesmo componente é renderizado em espanhol, inglês e português sem reescrever. `<div>Hello</div>` falha na revisão; `{% raw %}{{ T.helloWorld }}{% endraw %}` passa. E quando uma string contém um valor de tempo de execução, não concatene - `{% raw %}{{ T.greeting }} {{ userName }}{% endraw %}` quebra em idiomas onde a ordem das palavras é diferente - use `ui.formatString(T.greeting, { name: userName })` para que o espaço reservado chegue onde quer que o tradutor o coloque.

**Prefira slots a sinalizadores de comportamento.** Um componente que inverte grandes pedaços de sua própria marcação com base em um suporte `mode` ou `variant` se transforma em um emaranhado que ninguém quer tocar. Exponha `<slot>`s nomeados e deixe o chamador fornecer as diferentes partes, para que um componente mantenha um trabalho:

```vue
<template>
  <div>
    <slot name="header"></slot>
    <slot name="content"></slot>
  </div>
</template>
```
O mesmo espírito para estilo: procure as variáveis ​​CSS (`var(--color-primary)`) em vez de um `#ff0000` literal, para que um componente receba alterações de tema gratuitamente, em vez de fixar um valor hexadecimal que alguém terá que procurar mais tarde.

## Livro de histórias

Storybook é onde você desenvolve e observa um componente **isolado**, sem inicializar o aplicativo inteiro. Ele oferece um workshop interativo: renderize um componente por conta própria, vire seus acessórios em uma barra lateral e veja cada estado e variação lado a lado. Essa dissociação é o ponto - você pode construir e revisar um `Badge` ou um `ContestCard` sem um back-end em execução, um usuário conectado ou as linhas corretas do banco de dados, e os revisores podem obter exatamente os estados que você construiu.

Estamos no **Storybook 7.6** (`storybook@^7.6.21`), conduzindo Vue por meio de `@storybook/vue` `7.4.6` no construtor `@storybook/vue-webpack5` — o mesmo conjunto de ferramentas Webpack 5 com o qual o aplicativo real é construído, portanto, um componente que é renderizado no Storybook é renderizado da mesma maneira na produção.

### Executando

Há um script dedicado e - diferentemente da maioria do omegaUp - **você não precisa do Docker up** para usá-lo:

```bash
yarn storybook
```
Isso executa `storybook dev -p 6006` (consulte a entrada `storybook` em `package.json`), que compila a coleção de histórias e exibe um painel em [http://localhost:6006](http://localhost:6006). Deixe funcionando; ele é recarregado conforme você edita um componente ou sua história.

### Como está conectado

A configuração consiste em dois arquivos em `.storybook/`:

- **`.storybook/main.ts`** aponta o Storybook para as histórias com o glob `../frontend/www/js/omegaup/**/*.stories.@(js|jsx|ts|tsx)` — em qualquer lugar sob `frontend/www/js/omegaup/`, então ele também captura histórias não-`components/` como aquelas sob `graderv2/`. Ele registra três complementos (`addon-links`, `addon-essentials`, `addon-interactions`), define `staticDirs: ['../frontend/www']` para que os caminhos de ativos relativos sejam resolvidos exatamente como no aplicativo, alias de `@` a `frontend/www/` e ensina a configuração compartilhada do Webpack como carregar `.vue`, `.scss`, `.css` e arquivos de imagem. `docs.autodocs` está definido como `'tag'`, portanto, uma história só recebe uma página de documentos gerada automaticamente se você ativar marcando-a.
- **`.storybook/preview.ts`** carrega o CSS global que cada componente assume estar presente: `third_party/bootstrap-4.5.0/css/bootstrap.min.css` (estamos no **Bootstrap 4**, com `bootstrap-vue`, não Bootstrap 5) mais FontAwesome 5.15.4 injetado no iframe `<head>`. Ele também declara os matchers `controls` que fazem o Storybook escolher automaticamente o widget certo - qualquer argumento que termine em `color`/`background` recebe um seletor de cores, qualquer coisa que termine em `Date` recebe um seletor de data - e um regex `actions` (`^on[A-Z].*`) que registra manipuladores correspondentes no painel Ações.

Sem `preview.ts` carregando Bootstrap e FontAwesome, seu componente seria renderizado sem estilo e sem ícone no Storybook, mesmo que parecesse bom no aplicativo - essa incompatibilidade é exatamente o que este arquivo existe para evitar.

### A realidade da cobertura

Seja honesto consigo mesmo sobre o estado disso: **atualmente existem apenas 10 arquivos `.stories` para 257 componentes**. O Storybook não é um lugar onde todos os componentes já vivem; é um lugar para onde estamos gradualmente mudando-os. Se você estiver tocando em um componente e ele não tiver história, adicionar um é uma contribuição genuinamente bem-vinda e de baixo risco.

### Escrevendo uma história

A convenção é um arquivo de história por componente, com o nome dele e localizado **ao lado do arquivo `.vue`**: para `Badge.vue` você cria `Badge.stories.ts` na mesma pasta. (É por isso que o glob é uma correspondência recursiva `**` em vez de um único diretório de histórias - as histórias vivem onde quer que seus componentes estejam.)

Escrevemos **Component Story Format 3 (CSF3)**: um objeto `meta` exportado por padrão que descreve o componente e, em seguida, uma exportação nomeada por estado que você deseja mostrar, cada um `StoryObj`. Aqui está o `ToggleSwitch.stories.ts` real, que é um bom modelo mínimo para copiar:

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
Lendo isso de cima a baixo:

- **`title`** (`'Components/ToggleSwitch'`) é o caminho na barra lateral do Storybook — a barra cria uma pasta. Siga o agrupamento existente: componentes de nível superior e genéricos vão em `Components/...`, widgets de arena em `Arena/...` (veja `ContestCardv2.stories.ts` intitulado `'Arena/ContestCard'`) e assim por diante.
- **`argTypes`** declara cada prop e, crucialmente, *qual controle o renderiza* no painel: `control: 'text'` fornece uma caixa de texto, `'boolean'` uma alternância, `'select'` com `options` um menu suspenso. Isso é o que transforma uma renderização estática em um playground controlado por botões, onde um revisor pode exercitar cada estado manualmente.
- **Esse `@ts-ignore FIXME`** não é padrão que você pode excluir - é resistente. Como criamos componentes com o `vue-property-decorator` obsoleto, a digitação do Storybook 7 não pode inferir os tipos de objetos diretamente da classe do componente, portanto, suprimimos o erro resultante em `argTypes`. Copie o comentário como está; documenta *por que* o ignorar existe para a próxima pessoa.
- **`args`** são os valores padrão concretos inseridos nesses controles quando a história é renderizada pela primeira vez.
- **`render`** constrói a instância real do Vue. A linha `props: Object.keys(argTypes)` encaminha cada argumento declarado para o componente wrapper para que os controles sejam conectados a adereços reais, e a string `template` monta o componente com esses adereços vinculados. Você só precisa do `render` quando a montagem padrão não é suficiente - para um componente simples, muitas vezes você pode omiti-lo e deixar o Storybook montar o componente diretamente.
- **`storyName`** substitui o rótulo mostrado para aquela história individual (caso contrário, é derivado do nome de exportação, por exemplo, `Default`).

Alguns componentes pegam um objeto inteiro em vez de objetos planos, e a função de renderização é onde você o monta. `Badge.stories.ts` coleta seus argumentos e os transmite como um único objeto vinculado - `template: '<badge :badge="$props" />'` - com `badge_alias` exposto como um controle `select` sobre a lista completa de aliases de crachás reais (`'100solvedProblems'`, `'coderOfTheMonth'`, `'problemSetter'`,…) para que você possa percorrer cada crachá visualmente.

### Mostrando vários estados

O valor real aparece quando um componente tem estados significativamente diferentes — crie uma exportação nomeada para cada um. `ContestCardv2.stories.ts` é o modelo: ele define um `Template` reutilizável e, em seguida, exporta `Default`, `Recommended`, `Current`, `Future` e `Past`, cada um espalhando os argumentos básicos e substituindo apenas os campos que diferem (um sinalizador recomendado, horários de início/término há uma hora versus um dia antes) para que todos os cinco estados do concurso se alinhem lado a lado na barra lateral:

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
Observe a conversão de `as types.ContestListItem`: os dados simulados são digitados em relação aos tipos de API **gerados** em `frontend/www/js/omegaup/api_types.ts` (produzido por `frontend/server/cmd/APITool.php`, marcado como `DO NOT EDIT`), para que seus fixtures permaneçam honestos com a forma que o backend realmente envia. Se um campo estiver faltando ou for do tipo errado, o TypeScript conta a história antes mesmo de chegar a uma página.

`ContestCardv2.stories.ts` também é escrito no estilo CSF2 antigo (`Template.bind({})` com `Story` de `@storybook/vue`) em vez de CSF3 - ambos funcionam e ambos estão na árvore - mas prefira o formato CSF3 `StoryObj` mostrado acima para qualquer coisa nova; é em torno disso que o Storybook 7 foi construído e para onde o ecossistema está se dirigindo.

## Teste de componentes

Juntamente com as histórias, os componentes carregam testes de unidade Jest chamados `Component.test.ts` na mesma pasta (você verá `Countdown.test.ts`, `Markdown.test.ts`, `ToggleSwitch.test.ts` e amigos sentados ao lado de seus arquivos `.vue`). Use `@vue/test-utils` para montar e afirmar:

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
Pense nos dois como complementares: a história é a verificação visual e humana de como um componente *aparece* em seus estados; o teste é a garantia automatizada de como ele *se comporta*. Um componente bem coberto possui ambos.

## Documentação Relacionada

- **[Diretrizes de codificação](coding-guidelines.md)** — as regras completas do Vue/TypeScript (jQuery foi banido, `T` para todas as strings, `ui.formatString` para interpolação)
- **[Guia de teste](testing.md)** — Jest, Cypress e como executar as suítes
- **[Arquitetura Frontend](../architecture/frontend.md)** — como o shell Twig, os pontos de entrada do Webpack e os componentes Vue se encaixam
