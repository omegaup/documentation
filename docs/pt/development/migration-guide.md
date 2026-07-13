---
title: Guia de migração
description: O estilo inicial para construir uma página em Vue + TypeScript na parte superior do shell Twig, além da atualização atual do Vue 2 para o Vue 3.
icon: bootstrap/arrow-right
---
# Guia de migração: como construímos uma página

Era uma vez esta página descrevia uma migração em vôo: puxe um Smarty `.tpl`
à parte, entregue os dados para um componente Vue e exclua o modelo. Essa migração é
**feito**. O frontend agora é composto por componentes de arquivo único Vue de ponta a ponta - a partir deste momento
gravando 257 arquivos `.vue` e 414 arquivos `.ts` em um único aplicativo
modelo, `frontend/templates/template.tpl`, e aquele único sobrevivente é um Twig 3
concha, não Smarty. Smarty se foi; O HHVM desapareceu; o backend é simples PHP 8.1
rodando em php-fpm atrás do nginx.

Portanto, leia esta página de duas maneiras. Primeiramente, o passo a passo abaixo não é mais um
tarefa única - é **o estilo da casa** para conectar qualquer nova página ao omegaUp,
porque cada página ainda percorre o mesmo caminho: um controlador PHP monta um
digitado `payload`, o shell Twig o serializa no HTML, um TypeScript
o ponto de entrada analisa-o de volta e um componente Vue o renderiza. Aprenda este caminho uma vez
e você pode adicionar uma página sem perguntar a ninguém como funciona o encanamento. Em segundo lugar, o
uma migração que *ainda* está ativa é **Vue 2.7 → Vue 3**; o codemod e o
os materiais de aprendizagem para esse esforço já estão no repositório e há um
seção na parte inferior sobre onde direcionar sua atenção para isso.

## O caminho que uma página percorre

Antes do checklist, tenha em mente todo o pipeline, pois cada etapa
abaixo está apenas uma estação nele. Quando um navegador solicita, digamos, a página de login,
o método do controlador `\OmegaUp\Controllers\User::apiLoginDetailsForTypeScript`
(em `frontend/server/src/Controllers/User.php`) constrói um array com dois
chaves importantes: uma nomenclatura `entrypoint` que compilou o pacote TypeScript deve
executado e um `templateProperties` contendo o `payload` (os dados que a página precisa)
e um `title`. O shell Twig renderiza essa carga literalmente na página como
`<script type="text/json" id="payload">…</script>` — você pode ver a linha exata
em `frontend/templates/template.tpl` - e então `{% entrypoint %}` cai no
Tag `<script>` para o pacote compilado, seguida por um vazio
`<div id="main-container"></div>` para Vue montar. No cliente, o
O arquivo `.ts` do ponto de entrada lê esse JSON de volta por meio de um analisador gerado, `new
Vue(...)`s a component into `#main-container` e entrega a carga como adereços.

Esse é o caminho. Observe que o campo é `templateProperties`, **não**
`smartyProperties` — se você encontrar o nome antigo em uma filial antiga, esse é o
Ortografia da era Smarty e não existe mais na base de código. Observe também que o
o controlador nunca renderiza HTML; ele retorna dados e o shell + o ponto de entrada
faça a renderização. Manter essa divisão é o ponto principal: o PHP possui os dados e
seus tipos, o Vue possui os pixels.

## Etapa 1 — Configurar a carga útil do PHP

Comece no servidor, porque os tipos que você define aqui são o contrato como um todo
front-end é gerado a partir de.

Encontre o método do controlador que atende sua página. A convenção é um método
`ForTypeScript` com sufixo — para a visualização de login que é
`apiLoginDetailsForTypeScript` em `frontend/server/src/Controllers/User.php`. É
trabalho é reunir todos os dados que a página precisa e colocá-los sob
`templateProperties['payload']`. Qualquer coisa que o componente irá renderizar deve funcionar
dentro daquele `payload`; qualquer coisa deixada fora dele nunca chega ao navegador.

Depois que os dados forem reunidos, atribua à carga um **tipo Salmo**. Isto não é
escrituração contábil opcional - é a única fonte de verdade a partir da qual o TypeScript
tipos e o analisador de tempo de execução são gerados automaticamente. Você declara o tipo como um
anotação `@psalm-type` e referenciá-la no docblock `@return` do método. Em
`User.php` o método de login é anotado:

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
`LoginDetailsPayload` é um tipo de Salmo nomeado declarado em outra parte do arquivo e
esse nome é exatamente o que você analisará no cliente - então escolha-o bem.
Mais dois campos nesse formato de retorno ganham seu sustento:

- **`title`** é um `\OmegaUp\TranslationString`, não uma string simples. Deve
  resolver para uma chave `omegaupTitle…` que existe em todos os três `en.lang`,
  `es.lang` e `pt.lang`, porque omegaUp renderiza o título da página em qualquer formato
  idioma para o qual a conta está configurada. Ignore a entrada `.lang` e o título
  renderiza como a chave bruta.
- **`entrypoint`** é o nome do pacote compilado que irá renderizar este
  carga útil — uma string simples como `'login_signin'`. Ainda não precisa existir;
  você o criará na Etapa 2. Ele mapeia para uma entrada na configuração do Webpack (mais sobre
  isso em um momento).

Quando a carga útil e seu tipo estiverem definidos, execute `stuff/lint.sh`. Faça isso antes
você toca em qualquer TypeScript, **porque** o linter é o que regenera o cliente
definições de tipo e o analisador de tempo de execução do seu tipo de Salmo - o
Os arquivos `.ts` que você está prestes a gravar dependem da saída gerada existente. O
os arquivos gerados são `frontend/www/js/omegaup/api_types.ts` (o tipo formas e
o `payloadParsers`) e `frontend/www/js/omegaup/api.ts` (o digitado
Invólucros `apiCall<>`); ambos são produzidos pela `frontend/server/cmd/APITool.php` e
ambos abrem com um banner `// generated by … DO NOT EDIT.`, portanto, nunca edite manualmente
eles - corrija o tipo de Salmo e execute novamente o linter. Você também pode correr
`stuff/runtests.sh` para confirmar se a alteração do seu controlador não quebrou nada
o lado do PHP.

## Etapa 2 — Conecte o ponto de entrada TypeScript

Graças ao shell Twig unificado, você nem toca no `template.tpl` - o
shell já sabe como serializar sua carga útil e injetar o ponto de entrada
roteiro. Se o lado do PHP estiver correto, todo o trabalho do seu cliente acontecerá no
arquivo `.ts` do ponto de entrada.

!!! note "Vindo de um arquivo `.js`?"
    Se você estiver convertendo um arquivo `.js` antigo para `.ts`, siga estas mesmas instruções
    etapas - mas aproveite o fato de que a maior parte da lógica já existe.
    Não reescreva do zero; obter o comportamento existente compilando em
    TypeScript primeiro, depois melhore-o.

Primeiro, certifique-se de que o nome `entrypoint` escolhido na Etapa 1 esteja registrado no
Configuração do Webpack e aponta para um arquivo real. As entradas de frontend residem em
`webpack.config-frontend.js` na raiz do repositório; a entrada de login é única
linha aí:

```js
login_signin: './frontend/www/js/omegaup/login/signin.ts',
```
Se esse arquivo ainda não existir, crie-o. A forma é padrão que você pode copiar
de qualquer ponto de entrada vizinho - `schools/schoolofthemonth.ts` é um ponto de entrada limpo e
exemplo mínimo. Cada ponto de entrada importa os mesmos auxiliares principais (`OmegaUp` para
o gancho pronto, `types` para os analisadores, `api` para chamadas de API digitadas, `ui`, o
função de tradução `T` de `../lang`, `Vue` e o componente que ele monta),
espera a página estar pronta, analisa a carga útil e monta uma instância Vue
em `#main-container`:

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
A linha de suporte de carga é `types.payloadParsers.SchoolOfTheMonthPayload()`. Isso
o analisador lê o JSON `<script id="payload">` que o shell Twig escreveu e o retorna
**digitado** como a forma exata que você definiu em PHP. O nome do analisador é o seu Salmo
nome do tipo — `LoginDetailsPayload` em PHP torna-se
`types.payloadParsers.LoginDetailsPayload()` no ponto de entrada. Se o analisador você
querer não existe, é quase sempre porque o tipo de Salmo está errado ou você
não executei novamente o `stuff/lint.sh` desde que o adicionei - volte para a Etapa 1, corrija o tipo,
regenerar. Não pegue `JSON.parse` ou role a forma manualmente; todo o ponto
do analisador gerado é que PHP e TypeScript nunca podem discordar sobre o que
a carga útil contém.

Dois hábitos mantêm os pontos de entrada limpos. Faça suas **chamadas de API aqui no arquivo `.ts`**,
não dentro do componente — o ponto de entrada é buscado, o componente é exibido.
`common/navbar.ts` é o exemplo canônico de um ponto de entrada que chama uma API
e alimenta o resultado ao seu componente. E importe apenas o que você usa; o linter
sinalizará o resto.

## Etapa 3 — Construa o componente Vue (Bootstrap 4)

O componente recebe, como adereços, os dados que seu ponto de entrada analisou - e aqueles
props carregam os tipos exatos gerados na Etapa 1. Importe-os de
`api_types.ts` e digite seus `@Prop`s contra eles para que uma mudança no formato da carga útil
O PHP aparece como um erro de compilação no componente, não como uma surpresa em tempo de execução.
produção:

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
Algumas regras aqui não são negociáveis e cada uma tem um motivo:

- **Bootstrap 4, não 3 e não 5.** omegaUp está em `bootstrap ^4.6.0` com
  `bootstrap-vue ^2.21.2`, e o shell carrega Bootstrap 4 CSS. Cada aula que você
  o uso deve ser uma classe BS4. Se você estiver tocando em um arquivo `.vue` anterior ao
  migração e ainda carrega marcação BS3, migre-o para BS4 na mesma mudança -
  **caso contrário, não funcionará**, porque o shell unificado envia apenas o BS4
  a folha de estilo e os nomes das classes BS3 serão renderizados silenciosamente sem estilo.
- **Evite atributos `id`** dentro dos componentes. O mesmo componente pode ser montado
  mais de uma vez em uma página e `id`s duplicados são HTML inválidos que quebram
  `document.getElementById` e ferramentas de acessibilidade. Procure uma aula ou um
  Atributo `data-` em vez disso. Se você realmente precisa definir um `id` (alguns terceiros
  widget exige uma), há uma saída de emergência - um sinalizador de componente existente que
  suprime a verificação de atributos reservados do linter - mas trata a necessidade dele como um
  cheiro.

O resto das regras internas para o código do componente são curtas o suficiente para indicar
de uma vez, e eles existem em todos os SFC da árvore:

- **Não use jQuery.** Agora somos uma estrutura de componentes reativos; alcançando
  o DOM combate manualmente a estrutura e dessincroniza o DOM virtual do Vue de
  o que está na tela.
- **Prefira o padrão de cláusula de guarda** — retorne mais cedo nos casos excepcionais para
  o caminho feliz é lido de cima para baixo, sem aninhamento profundo.
- **Elementos HTML e nomes de atributos em kebab-case; nomes de métodos em camelCase.**
  Consistência aqui é o que permite que você acesse a base de código e realmente encontre as coisas.
- **Use interpolação literal de modelo ES6** em vez de concatenação de strings —
  é mais curto e há menos erros.
- **`let` e `const`, nunca `var`.** O escopo do bloco remove uma categoria inteira de
  içando insetos.
- **Retire o registro de depuração antes de confirmar.** `console.log` deixado em um componente
  é enviado para o console de todos os usuários.

## Passo 4 — Teste o componente no Jest

Um componente novo ou modificado precisa de um teste, e o Codecov apontará para o exato
linhas que sua mudança deixou descoberta. Os testes de componentes usam `@vue/test-utils`'
`shallowMount`, que renderiza o componente com um nível de profundidade (componentes filhos
tornam-se stubs), então você está testando este componente isoladamente, em vez de todo o seu
subárvore. O padrão, retirado de
`frontend/www/js/omegaup/components/arena/Arena.test.ts`, é para montar com
`propsData` e afirme no texto renderizado:

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
Observe que as asserções têm como alvo `.clock` e um seletor `[data-arena-wrapper]` - não
um `id` - e é exatamente por isso que a Etapa 3 diz para você evitar `id`s: classe e
Os seletores `data-` são onde seus testes se baseiam. Copie um teste vizinho como um
ponto de partida; a forma quase não varia entre os componentes.

## A migração ao vivo: Vue 2 → Vue 3

Tudo acima descreve a construção da pilha atual — **Vue 2.7.16** com
TypeScript 4.4.4, a API de opções via `vue-property-decorator`, Vuex 3, Webpack
5. Isso é o que está em produção hoje. A única migração ainda em movimento é
levantando todo o front-end do Vue 2.7 para o Vue 3, e as ferramentas para isso já
fica na raiz do repositório:

- **`vue-upgrade-tool/`** é um codemod vendido (construído em `vue-metamorph`) que
  transforma mecanicamente o código Vue 2 em Vue 3 - arquivos JS/TS, SFCs e unidade
  testes iguais. Preste atenção ao seu próprio aviso: **os resultados não são garantidos como perfeitos,
  e você deve verificar manualmente cada alteração feita.** Ele também não formata
  sua saída bem, então execute o Prettier/ESLint sobre qualquer coisa que ele tocar para trazer o
  código novamente alinhado com nossas convenções.
- **`vue-js-tutorial/`** contém o material de aprendizagem para você se sentir confortável
  os idiomas do Vue 3 antes de começar a converter componentes reais.

Como a versão 2.7 é a versão final do Vue 2, grande parte do seu código 2.7 existente — o
SFCs `<script lang="ts">`, os adereços digitados, o handshake `payloadParsers` - é
já está próximo do formato Vue 3, e é exatamente por isso que o pipeline nas Etapas 1–4
permanece válido durante a atualização. O controlador/carga útil/ponto de entrada/estrada do componente
não muda; o que muda por baixo é o tempo de execução do componente. Quando você
converter um componente, executar o codemod, verificá-lo manualmente, executar novamente o teste Jest,
e reformate antes de confirmar.

## Documentação Relacionada

- [Diretrizes de codificação](coding-guidelines.md) — o conjunto completo de Vue e TypeScript
  padrões nos quais essas etapas se baseiam.
- [Guia de Componentes](components.md) — convenções mais profundas para estrutura de componentes.
- [Arquitetura Frontend](../architecture/frontend.md) — como o shell Twig, o
  pontos de entrada e os componentes se encaixam amplamente.
