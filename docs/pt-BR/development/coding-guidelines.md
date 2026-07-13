---
title: Diretrizes de codificação
description: Padrões de codificação e práticas recomendadas para desenvolvimento do omegaUp
icon: bootstrap/code
---
# Diretrizes de codificação

A maioria das regras nesta página não são aplicadas por um revisor humano repreendendo você em um comentário de pull request. Eles são verificados automaticamente no GitHub por linters e testes de integração e, sempre que possível, inserimos uma regra nessa automação para que ela capture as regressões por conta própria e libere a revisão do código para se concentrar nas partes interessantes da sua mudança. Portanto, pense nesta página menos como uma lista de decretos e mais como o raciocínio por trás do que a máquina já vai lhe dizer, escrito para que você entenda o *porquê* antes que o CI faça isso por você. A única meta-regra da qual todo o resto descende: **prefira explicar _por que_ as coisas são feitas da maneira como são feitas** em vez de reafirmar _o que_ o código obviamente faz.

Você pode verificar seu código em quase tudo isso localmente, antes de enviar por push, com:

```bash
./stuff/lint.sh validate
```
Esse script não executa as ferramentas diretamente na sua máquina. Ele é distribuído em uma imagem Docker fixada (atualmente `omegaup/hook_tools:v1.0.9`) para que cada contribuidor obtenha resultados idênticos em bytes de `yapf`, `prettier`, `phpcbf`, Psalm e `mypy`, independentemente do que estiver instalado em seu laptop. Execute-o *fora* do contêiner - se `OMEGAUP_ROOT` resolver para `/opt/omegaup`, o script se recusará e informará isso, porque esse caminho só existe dentro do contêiner de desenvolvimento onde o Docker-in-Docker não está disponível. Chamado sem argumentos, ele adivinha o conjunto de arquivos que você alterou (diferentemente de `upstream/main` ou `origin/main` se você não adicionou o controle remoto upstream) e executa no modo `fix`, editando-os no lugar; passe `validate` quando quiser apenas reportar.

## Princípios gerais

**Declarar tipos em cada interface.** Toda função deve declarar os tipos de seus parâmetros e seu valor de retorno — isso não é opcional e os analisadores estáticos falharão na construção sem ele. Usamos [TypeScript](https://www.typescriptlang.org/) (atualmente 4.4.4) no frontend, [Psalm](https://psalm.dev/) (atualmente 4.29, configurado em `psalm.xml`) para PHP em `frontend/server/` e [mypy](https://mypy-lang.org/) para as ferramentas Python em `stuff/`. Além da interface, também é preferível anotar os tipos de arrays e mapas declarados *dentro* de uma função, porque um `[]` ou `array()` simples não diz nada ao próximo leitor sobre o que ele deve conter.

**Escreva tudo em inglês** — códigos, identificadores e comentários. omegaUp é um projeto com colaboradores em vários países, e o inglês é o idioma que todos que tocam no código devem ler.

**Comportamento novo ou alterado vem com testes.** Qualquer alteração na funcionalidade – uma correção de bug, um novo recurso, um caso extremo alterado – deve vir com os testes novos ou modificados que o definem. Esta é uma regra rígida, não uma sutileza, e é verificada no CI.

**Evite `null` e `undefined` sempre que puder**, e especialmente em parâmetros de função - é aqui que eles causam mais danos e merece sua própria seção abaixo.

**Evite funções (e componentes Vue) que bifurcam seu comportamento em um sinalizador.** Um parâmetro booleano que faz uma função fazer uma coisa substancialmente diferente quando `true` e outra quando `false` são na verdade duas funções vestindo um sobretudo. Divida-as em duas funções claramente nomeadas e chame a correta no local da chamada; no Vue, abstraia o comportamento diferente em um [`slot`](https://vuejs.org/v2/guide/components-slots.html) para que o chamador o forneça. Isso mantém cada unidade fazendo uma coisa compreensível.

**Use o [padrão de cláusula de proteção](https://refactoring.com/catalog/replaceNestedConditionalWithGuardClauses.html)** sempre que possível — retorne mais cedo nos casos excepcionais para que o caminho feliz não fique enterrado sob `if`s aninhados.

**Exclua o código morto, nunca comente-o.** Não deve haver blocos comentados remanescentes "por precaução". Se você precisar dele de volta, está no histórico do git - é exatamente para isso que serve o controle de versão, e um bloco comentado é apenas um ruído que apodrece e engana.

**Minimize a distância entre o local onde uma variável é declarada e o local onde ela é usada pela primeira vez.** O objetivo é reduzir a quantidade de código irrelevante que um leitor precisa manter em mente para saber o que uma variável contém atualmente; declarar coisas no topo de uma função longa e usá-las cinquenta linhas abaixo força todos a continuar rolando novamente.

**Comente o _porquê_, não o _o que_.** Um comentário que diz `// increment counter` acima de `counter++` é pior do que nenhum comentário, porque é uma desordem que pode ficar silenciosamente obsoleta. Os comentários ganham seu lugar explicando o que não é óbvio: o raciocínio, a restrição, a pegadinha histórica que fez o código parecer estranho.

```php
// Bad — restates what the code plainly does:
// Increment counter
$counter++;

// Better — explains why this line exists at all:
// Count retries so we can back off once we exceed the rate-limit threshold.
$counter++;
```
### A regra `null`/`undefined` e por que ela existe

Isso merece mais do que uma bala, porque é a regra que as pessoas erram com mais frequência. `null` deve significar apenas "o usuário não forneceu isso" e `undefined` deve aparecer apenas na declaração de parâmetros TypeScript opcionais. Não declare um tipo que possa ser *ambos* `null` e `undefined` ao mesmo tempo — escolha aquele que carrega significado. 

Aqui está o raciocínio que torna a regra não negociável em vez de estilística: **cada parâmetro que pode ser independentemente `null` ou `undefined` dobra o número de combinações de entrada distintas que a função deve manipular corretamente, e essa contagem cresce exponencialmente.** Dois parâmetros anuláveis ​​são quatro combinações; quatro são dezesseis; dez são mais de mil estados que você afirma implicitamente ter pensado e testado. **Mantenha o número dessas combinações abaixo de 10.**

E quando a nulidade *é* legítima, os campos anuláveis devem poder ser nulos *independentemente um do outro*. Se você achar que um subconjunto de parâmetros deve sempre ser passado junto — todos presentes ou todos ausentes — isso é um sinal de que eles pertencem ao seu próprio tipo, e não como argumentos opcionais soltos. Por exemplo, um validador personalizado precisa de um idioma e de um tempo limite, mas apenas quando a validação personalizada está ativada:

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
Agrupe os campos acoplados em um tipo intermediário, para que "a validação personalizada esteja ativada" e "aqui estão as duas configurações obrigatórias" se tornem uma parte única e indivisível do estado:

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
Agora há exatamente um parâmetro anulável em vez de três, `null` significa inequivocamente "sem validação personalizada" e é impossível representar o estado absurdo de uma linguagem sem um tempo limite.

### Nomenclatura

Use [camelCase](https://en.wikipedia.org/wiki/Camel_case) para nomes de funções, variáveis e classes. As exceções onde [snake_case](https://en.wikipedia.org/wiki/Snake_case) está correto são todos os lugares onde o nome é ditado por algo fora do nosso mundo PHP/TypeScript:

- Nomes de colunas MySQL
- Variáveis e parâmetros Python (snake_case é a norma da comunidade Python, e `yapf`/`pylint` espera isso)
- Parâmetros API (eles cruzam o fio e aparecem no `api_types.ts`, então seu invólucro é um contrato)

E **evite abreviações** tanto nos identificadores quanto nos comentários. `cnt`, `usr`, `tmp` economizam algumas teclas para o autor e custam a cada futuro leitor um momento de "espere, o que é isso" - uma abreviatura que é óbvia para você raramente é óbvia para todos.

## Formatação

Deliberadamente não discutimos sobre formatação; delegamos toda a questão a ferramentas automatizadas para que ninguém gaste uma revisão de código na colocação de chaves. [`yapf`](https://github.com/google/yapf) formata Python, [`prettier`](https://prettier.io/) formata TypeScript e Vue, e [`phpcbf`](https://github.com/squizlabs/PHP_CodeSniffer) (a metade de correção automática do PHP_CodeSniffer) formata PHP. Executar `./stuff/lint.sh` sem argumentos aplica todos os três aos arquivos alterados no lugar.

As regras que essas ferramentas impõem, para referência:

- 2 ou 4 espaços de recuo dependendo do tipo de arquivo — nunca tabulações.
- Finais de linha Unix (`\n`), não Windows (`\r\n`).
- Chave de abertura na mesma linha da instrução que a apresenta.
- Um espaço entre uma palavra-chave e seu parêntese para `if`, `else`, `while`, `switch`, `catch` e `function` — mas *nenhum* espaço antes do parêntese de uma *chamada* de função.
- Sem espaços apenas entre parênteses.
- Um espaço depois de cada vírgula, nenhum antes.
- Um espaço em ambos os lados de cada operador binário.
- No máximo uma linha em branco seguida.
- Sem comentários vazios.
- Somente comentários da linha `//`; nunca `/* ... */` bloqueia comentários.

```php
if (condition) {
    stuff;
}
```
##PHP

**Os testes passam 100% antes de você confirmar — sem exceções.** Execute-os localmente; uma suíte vermelha nunca é "provavelmente boa".

**Evite O(n) viagens de ida e volta do banco de dados.** Um loop que chama um método DAO uma vez por elemento - incluindo qualquer coisa que toque os DAOs gerados automaticamente em `frontend/server/src/DAO/` - transforma uma operação lógica em *n* viagens de ida e volta da rede para o MySQL, e essa é a maneira clássica pela qual um endpoint que é ágil com dados de teste falha na produção. Escreva uma única consulta manual que faça todo o trabalho em uma viagem.

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
**Apenas funções de API podem receber `\OmegaUp\Request`.** Os métodos `apiXxx` nos controladores em `frontend/server/src/Controllers/` (no namespace `\OmegaUp\Controllers`) são o limite onde uma solicitação não digitada fornecida pelo usuário entra no sistema - por exemplo, `\OmegaUp\Controllers\Run::apiCreate(\OmegaUp\Request $r)`, que valida a solicitação e, depois que tudo for verificado, entrega o trabalho com `\OmegaUp\Grader::getInstance()->grade(...)`. Cada função *atrás* desse limite deve receber parâmetros digitados. Portanto, o trabalho de cada método `apiXxx` é validar a solicitação, extrair cada campo em uma variável local digitada corretamente e, em seguida, chamar as funções internas com essas variáveis ​​- para nunca passar `$r` mais profundamente no código. Isso mantém o núcleo digitado do sistema genuinamente digitado e limita toda a incerteza "o usuário realmente enviou este campo" a uma camada fina.

**Documente cada função** no estilo de comentário em bloco que o Salmo e os revisores esperam - um resumo de uma linha, uma breve explicação de *por que* ela existe quando isso não é óbvio e anotações `@param`/`@return`:

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
**Relatar erros com exceções**, não com valores de retorno sentinela. Uma função que retorna `true`/`false` é adequada quando o booleano é uma resposta genuinamente esperada ("este usuário existe?"), mas "algo deu errado" é para que servem as exceções.

**Todas as APIs retornam matrizes associativas.** Isso é o que `\OmegaUp\ApiCaller` serializa de volta para o cliente e o que `frontend/server/cmd/APITool.php` lê para gerar o cliente front-end digitado, portanto, a forma é um contrato, não uma conveniência.

**Use [RAII](https://en.wikipedia.org/wiki/Resource_Acquisition_Is_Initialization)** quando for necessário, principalmente para gerenciamento de recursos (arquivos, bloqueios e similares) — vincule o tempo de vida de um recurso ao de um objeto para que a limpeza não possa ser esquecida em um retorno antecipado ou em uma exceção.

## Vista

A UI do omegaUp consiste em componentes de arquivo único Vue 2.7.16 (atualmente no meio da migração para Vue 3, rastreados nos diretórios raiz `vue-upgrade-tool/` e `vue-js-tutorial/`) em `frontend/www/js/omegaup/components/`. Algumas regras mantêm esses componentes passíveis de manutenção e tradução.

**Prefira `slot`s a sinalizadores de comportamento**, pelo mesmo motivo das funções: um componente que muda radicalmente o que é renderizado com base em uma propriedade booleana são dois componentes fundidos. Exponha a parte variável como [`slot`](https://vuejs.org/v2/guide/components-slots.html) e deixe o chamador preenchê-la. Se vários sites de chamada desejarem a mesma variante, envolva-a em *outro* componente que forneça esse slot.

**Nunca codifique o texto voltado para o usuário.** Toda a interface precisa ser renderizada em vários idiomas, portanto, cada string que o usuário vê vem de uma chave de tradução (`T.someKey`), não de um literal. E **não concatene strings de tradução** — a ordem das palavras difere entre os idiomas, então colar fragmentos produz lixo em alguns deles. Use `ui.formatString` com parâmetros nomeados para que a própria tradução controle a ordem:

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
**Não codifique cores** como hexadecimal ou `rgb(...)`. Declare-as como variáveis ​​CSS e faça referência a elas, porque o modo escuro funciona trocando os valores das variáveis ​​- um `#ffffff` literal é um quadrado branco que o modo escuro não consegue alcançar.

**Evite ganchos de ciclo de vida, a menos que o componente realmente toque no DOM** — e tente evitar tocar no DOM em primeiro lugar. Em uma estrutura reativa, usar `mounted()` para cutucar um elemento geralmente é um sinal de que algum estado deveria ter sido reativo. Qual é a outra metade disso: **prefira [propriedades computadas e observadores](https://vuejs.org/v2/guide/computed.html)** em vez de recalcular e reatribuir variáveis ​​manualmente. Deixe a reatividade do Vue rastrear as dependências para você, em vez de fazer isso manualmente e errar sutilmente.

**Adicione uma história do Storybook para cada novo componente** e atualize a história quando você alterar as propriedades ou estados de um componente. O Storybook (atualmente 7.6) permite desenvolver e observar um componente isoladamente, desacoplado do resto do aplicativo – bom para reutilização e para revisores que desejam ver todos os estados sem clicar no site ativo. Você nem precisa do Docker para executá-lo:

```bash
yarn storybook
```
Isso inicia o painel em [localhost:6006](http://localhost:6006). Para adicionar uma história, solte um arquivo `Component.stories.ts` próximo ao componente (por exemplo, `Badge.stories.ts` ao lado de `Badge.vue`), importe o componente e exporte um `meta` mais um `StoryObj` por estado que você deseja exibir:

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
A cobertura aqui ainda é escassa – atualmente em torno de 10 arquivos de histórias contra 257 componentes – então uma nova história é quase sempre uma adição líquida, não uma duplicata.

## Datilografado

**Quando uma função ultrapassa 2–3 parâmetros** — e *especialmente* se vários compartilham o mesmo tipo, e *definitivamente* se vários são opcionais — mude para um único parâmetro de objeto. Argumentos posicionais do mesmo tipo são um bug esperando para acontecer (`updateProblem(problem, currentVersion, previousVersion)` troca silenciosamente duas strings e verifica corretamente); campos de objetos nomeados tornam a chamada autodocumentada e independente do pedido:

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
**Evite [afirmações de tipo](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-assertions).** Uma conversão `as` consiste em substituir o compilador, portanto, só é permitido quando o compilador realmente não consegue saber o tipo:

- interagindo com o DOM (`document.querySelector` e amigos);
- anotando um literal vazio, por ex. `null as null | string` ou `[] as Foo[]`;
- em testes, declarar `params` no construtor Vue.

**Não toque no cliente API gerado manualmente.** `frontend/www/js/omegaup/api.ts` e `frontend/www/js/omegaup/api_types.ts` começam com `// generated by frontend/server/cmd/APITool.php. DO NOT EDIT.` — eles são regenerados a partir das anotações `@omegaup-request-param` e tipos DAO dos controladores PHP, portanto, uma edição que você faz há um `APITool.php` que foge de ser sobrescrito silenciosamente. Altere o PHP e depois regenere.

**Não use jQuery!** Ele foi descontinuado e não pode mais ser usado em nenhum lugar da base de código. Em vez disso, use a estrutura (reatividade Vue, refs) ou APIs DOM simples.

##Píton

O Python aqui são os ~24 scripts de ferramentas em `stuff/`, verificados por `mypy`, `flake8` e `pylint` e formatados por `yapf`.

**Depois de 2 a 3 parâmetros, torne-os apenas com palavras-chave** - o mesmo raciocínio da regra de objeto TypeScript, expressa da maneira Pythonic com um `*` simples na assinatura, então os chamadores *devem* nomear cada argumento:

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
**Use Snake_case para funções e variáveis, CamelCase para classes** — estilo Python padrão, que `pylint` impõe.

**Importe módulos, não nomes.** Evite `from module import function`; importe o módulo e use o acesso pontilhado, para que em cada site de chamada seja óbvio de onde veio o `function` e não haja ambigüidade sobre qual `function` você quis dizer:

```python
# Bad — where did function come from three screens later?
from module import function
function()

# Better — the origin travels with every call:
import module
module.function()
```
A única exceção é o módulo `typing`, onde `from typing import Optional, List` é idiomático e universalmente compreendido.

## Documentação relacionada

- **[Guia de testes](testing.md)** — como escrever os testes que cada mudança funcional exige
- **[Comandos úteis](useful-commands.md)** — os comandos de desenvolvimento diários
- **[Guia de componentes](components.md)** — construção detalhada de componentes Vue

---

**Lembre-se:** quase tudo acima é aplicado por automação, então execute `./stuff/lint.sh validate` antes de confirmar e deixe as ferramentas detectá-lo primeiro.
