---
title: Guia de teste
description: Guia de teste abrangente para omegaUp
icon: bootstrap/flask
---
# Guia de teste

omegaUp é testado em três camadas, e cada uma vive em algum lugar diferente por um
razão. Os controladores PHP e a API são cobertos pelos testes **PHPUnit 9** que são executados
_dentro_ do contêiner Docker `frontend` (eles precisam de um MySQL 8.0 real, um verdadeiro
gitserver e toda a cadeia de carregamento automático `\OmegaUp\`). Os componentes do Vue 2.7 e
o TypeScript em `frontend/www/js` é coberto pelos testes de unidade **Jest 26**,
que também roda dentro do contêiner, mas só precisa de jsdom. E o completo
jornadas de cliques do usuário – registre-se, faça login, crie um concurso, envie uma corrida –
são cobertos pelos testes completos do **Cypress 15.7** que são executados _no seu host_,
dirigindo um Chrome real contra o contêiner por meio de `http://127.0.0.1:8001`.

A regra que obrigamos a todos: os testes devem estar verdes antes de você abrir um pull
solicitação, e qualquer novo comportamento é enviado com um teste que o exercita. CI será executado
todas as três suítes novamente em seu PR, então uma suíte que só passa em sua máquina
não está passando.

| Camada | Estrutura | Onde mora | Onde funciona |
|-------|-----------|----------------|---------------|
| Controladores PHP + API | PHPUnit 9 | `frontend/tests/controllers/`, `frontend/tests/badges/` | Dentro do contêiner `frontend` |
| Unidades TypeScript/Vue | Brincadeira 26 (jsdom) | `frontend/www/js/**/*.test.ts` | Dentro do contêiner `frontend` |
| Viagens de ponta a ponta | Cipreste 15.7 | `cypress/e2e/*.cy.ts` | No seu host, contra `127.0.0.1:8001` |

## Testes de unidade PHP (PHPUnit)

### O único comando: `./stuff/runtests.sh`

O script que realmente executamos antes de enviar é
[`stuff/runtests.sh`](https://github.com/omegaup/omegaup/blob/main/stuff/runtests.sh),
e é deliberadamente mais do que "apenas PHPUnit". Ele primeiro decide se é
dentro do Docker, verificando se a raiz do repositório é `/opt/omegaup` (é onde
o contêiner monta a fonte); se assim for, ele é executado diretamente, caso contrário, ele dispara
no contêiner com `docker compose exec -T frontend`. A partir daí, em
ordem:

1. Valida as migrações de esquema com `stuff/db-migrate.py validate` e o
   políticas de autorização com `stuff/policy-tool.py validate`, porque um teste
   executado em um esquema ou política obsoleto não diz nada de útil.
2. Executa [`stuff/mysql_types.sh`](https://github.com/omegaup/omegaup/blob/main/stuff/mysql_types.sh),
   qual é a parte interessante – veja abaixo.
3. Executa o Salmo em toda a árvore com `vendor/bin/psalm --show-info=false`
   (suprimimos o ruído no nível de informação para que apenas erros de tipo real falhem na execução).
4. Verifica se os hashes de ação do GitHub fixados são consistentes por meio de
   `hack/gha-reversemap.sh verify-mapusage`, mas somente se `yq` e `jq` forem
   instalado — caso contrário, ele imprime um aviso de salto em vez de falhar.

Quando você executa dentro do container ele termina lembrando você de executar
`./stuff/lint.sh` e os testes de IU do Python (`python3 -m pytest ./frontend/tests/ui/ -s`)
_fora_ do container, pois precisam de ferramentas que o container não carrega.

### Por que o `mysql_types.sh` existe (a parte inteligente)

`mysql_types.sh` não roda apenas o conjunto PHPUnit — ele roda com MySQL
**log de consulta geral** ativado (`SET GLOBAL general_log = 'ON'` gravando em um
`TABLE`), captura todas as consultas que os testes realmente emitiram e, em seguida, as alimenta
`stuff/process_mysql_return_types.py`. O objetivo é verificar se
As anotações `@psalm-type` que escrevemos à mão na camada DAO correspondem ao que o MySQL
_realmente_ retorna para essas colunas. Se você adicionar uma consulta cujo formato de resultado
não corresponde ao tipo de Salmo declarado, esta é a etapa que o detecta - longo
antes que se torne uma surpresa em tempo de execução em um controlador. Também funciona
`process_mysql_explain_logs.py` para verificar a integridade dos planos de consulta. Então, "o tipo
check" a menção dos documentos mais antigos não é uma suposição estática; está fundamentado no
consultas que seus testes realmente executaram.

### Executando o conjunto (ou um teste)

Nos bastidores, [`stuff/run-php-tests.sh`](https://github.com/omegaup/omegaup/blob/main/stuff/run-php-tests.sh)
é o que realmente invoca o PHPUnit. Sem argumentos, ele executa tudo sob
`frontend/tests/`; com argumentos ele os passa diretamente para `phpunit`,
então você obtém a filtragem do PHPUnit gratuitamente. Para iterar em um único teste de controlador:

```bash
# From inside the container (or via docker compose exec -T frontend ...)
./stuff/run-php-tests.sh frontend/tests/controllers/UserRankTest.php \
    --filter testUserRankingClassName
```
Ele sempre conecta as mesmas três coisas: `--bootstrap frontend/tests/bootstrap.php`,
`--configuration frontend/tests/phpunit.xml` e
`--coverage-clover coverage.xml` (esse arquivo Clover é o que o Codecov lê mais tarde).

As próprias suítes são declaradas em
[`frontend/tests/phpunit.xml`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/phpunit.xml):
um conjunto de **controladores** sobre `frontend/tests/controllers/` (atualmente ~129 unidades de teste
arquivos — esta é a maior parte da cobertura) e um pacote de **Selos**
`frontend/tests/badges/`. A cobertura é medida em `../server/`, mas deliberadamente
exclui o código gerado (`server/libs/dao/base/`), a configuração, o `cmd/`
scripts e as fontes do plug-in Psalm, porque a medição de arquivos gerados automaticamente
apenas diluiria o número.

!!! note "Os testes precisam de um gitserver e o ouvinte o fornece"
    `phpunit.xml` registra `\OmegaUp\Test\GitServerTestSuiteListener`
    ([`GitServerTestSuiteListener.php`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/GitServerTestSuiteListener.php)).
    Os testes de criação e envio de problemas precisam de um back-end git real para o problema
    armazenamento, para que o ouvinte se prepare para a execução do teste. É por isso que você
    não é possível executar esses testes de forma significativa fora do contêiner - as partes móveis
    eles tocam (MySQL 8.0, gitserver) são serviços de contêiner, não simulações.

Ajudantes nos quais você contará ao escrever novos testes ao vivo junto com as suítes:
`frontend/tests/Utils.php`, o diretório `frontend/tests/Factories/` para
construindo usuários/concursos/problemas e `ControllerTestCase.php` /
`BadgesTestCase.php` como classes base. Há também um `ApiCallerMock.php` para
conduzindo a camada API sem passar pelo HTTP.

## Testes de unidade TypeScript/Vue (Jest)

O conjunto Jest cobre cerca de 180 arquivos `*.test.ts` em `frontend/www/js`,
variando de lógica pura (`omegaup.test.ts`, `markdown.test.ts`, `csv.test.ts`)
para componentes de arquivo único Vue montados com `@vue/test-utils`. Os scripts npm em
[`package.json`](https://github.com/omegaup/omegaup/blob/main/package.json) todos
forçar `TZ=UTC` via `cross-env`, caso contrário, asserções de formatação de data
passar em uma máquina em um fuso horário e falhar no CI - fixar o UTC mantém todos
resultados idênticos:

```bash
yarn test            # cross-env TZ=UTC jest 'frontend/www/js/.*test\.ts$'
yarn test:watch      # same, but --watchAll --notify — reruns on save
yarn test:coverage   # same, with --coverage=true
```
Para executar um único arquivo durante a iteração, pule o wrapper e acesse o binário
diretamente:

```bash
./node_modules/.bin/jest frontend/www/js/omegaup/components/RadioSwitch.test.ts
```
Os testes de componentes são assim - monte o SFC com adereços e, em seguida, afirme
texto renderizado ou eventos emitidos. Observe a convenção de importação de traduções
(`T`) em vez de codificar strings de UI, para que um teste sobreviva a uma alteração de cópia:

```typescript
import { shallowMount } from '@vue/test-utils';
import T from '../lang';
import omegaup_RadioSwitch from './RadioSwitch.vue';

describe('RadioSwitch.vue', () => {
  it('Should render a simple radio switch with default descriptions', () => {
    const wrapper = shallowMount(omegaup_RadioSwitch, {
      propsData: { selectedValue: true },
    });
    expect(wrapper.text()).toContain(T.wordsYes);
    expect(wrapper.text()).toContain(T.wordsNo);
  });
});
```
Prefira `shallowMount` a `mount`, a menos que você precise especificamente de componentes filhos
para renderizar - ele stupa os filhos, o que mantém o teste rápido e interrompe um
bug de criança não relacionado seja reprovado no teste. A configuração do Jest
([`jest.config.js`](https://github.com/omegaup/omegaup/blob/main/jest.config.js))
faz o encanamento em que você tropeçaria: `testEnvironment: 'jsdom'`, um
`testURL` de `http://localhost:8001/` então código que lê `window.location`
se comporta, `vue-jest` para arquivos `.vue` e entradas `moduleNameMapper` que simulam
eliminar as dependências pesadas ou apenas do navegador - `monaco-editor`, importações CSS/LESS,
e `sugar` resolvem stubs em
`frontend/www/js/omegaup/__mocks__/` e `@/` são mapeados para `frontend/www/`. Compartilhado
a configuração é executada a partir do `frontend/www/js/omegaup/test.setup.ts` via
`setupFilesAfterEnv`.

## Testes ponta a ponta do Cypress

As 10 especificações abaixo
[`cypress/e2e/`](https://github.com/omegaup/omegaup/tree/main/cypress/e2e) —
`basic_commands`, `certificate`, `contest`, `course`, `course_2Part`, `group`,
`ide`, `navigation`, `problem_collection` e `problem_creator`, todos nomeados
`*.cy.ts` — conduza um navegador real por todo o produto. Ao contrário do PHPUnit e
Brincadeira, **Cypress é executado em seu host, não dentro do contêiner Docker.** O
contêiner atende o aplicativo em `http://127.0.0.1:8001` e Cypress
(`baseUrl` em [`cypress.config.ts`](https://github.com/omegaup/omegaup/blob/main/cypress.config.ts))
aponta o Chrome para esse endereço. Então você precisa do Node, suas dependências do Yarn
instalado e - no Linux - várias bibliotecas de sistema que o Electron/Chrome
link do corredor contra.

### Instalando o Cypress

Depois de um `yarn install`, se o próprio binário do navegador estiver faltando, você verá
algo como:

```text
No version of Cypress is installed in: ~/.cache/Cypress/15.7.0/Cypress

Please reinstall Cypress by running: cypress install
```
Isso não é um problema de dependência — o pacote npm está lá, mas o real
O binário Cypress que reside em `~/.cache/Cypress/<version>/` não foi baixado.
Corrija com:

```bash
./node_modules/.bin/cypress install
```
A versão fixada é `cypress` em `package.json` (atualmente **15.7.0**); o
path em qualquer mensagem de erro informa qual versão binária do Cypress está procurando
para, que é a maneira mais rápida de detectar uma incompatibilidade de versão/cache após uma atualização.

### Bibliotecas do sistema Linux

Cypress falha rapidamente – antes de executar um único teste – se uma biblioteca compartilhada for
necessidades estão faltando e o erro nomeia o `.so` exato. Dois aparecem constantemente.
Se você ver:

```text
~/.cache/Cypress/15.7.0/Cypress/Cypress: error while loading shared libraries:
libnss3.so: cannot open shared object file: No such file or directory
```
essa é a biblioteca criptográfica NSS. E:

```text
error while loading shared libraries: libasound.so.2: cannot open shared object
file: No such file or directory
```
é ALSA (áudio). Instale todo o conjunto de documentos Cypress como
[dependências necessárias](https://on.cypress.io/required-dependencies):

```bash
sudo apt update
sudo apt install -y libgtk-3-0 libgbm-dev libnss3 libatk1.0-0 \
    libatk-bridge2.0-0 libgdk-pixbuf2.0-0 libxss-dev libasound2
```
No **Ubuntu 24.04+** ALSA foi renomeado para a transição time_t de 64 bits, então
`libasound2` não será encontrado – instale `libasound2t64`. Se uma biblioteca
o erro persiste após a instalação, execute `sudo apt update` e tente novamente; um velho
o índice do pacote é o culpado usual.

### Executando os testes

A GUI é a maneira agradável de desenvolver uma especificação — ela mostra cada comando conforme
é executado e permite que você passe o mouse sobre qualquer etapa para ver um instantâneo DOM da página exatamente naquele
momento, além de uma ferramenta seletora que escreve o `cy.get(...)` para qualquer elemento
você clica:

```bash
npx cypress open
# or
./node_modules/.bin/cypress open
```
Headless é o que o CI faz e o que `yarn test:e2e` mapeia:

```bash
yarn test:e2e        # cypress run --browser chrome
```
Fixamos `--browser chrome` propositalmente, em vez de deixá-lo padrão para o
Electron empacotado, então as execuções locais correspondem ao CI. Uma corrida grava um vídeo em
`cypress/videos/` e, em caso de falha, uma captura de tela do `cypress/screenshots/`, então
você pode observar o que o teste viu, mesmo em caso de falha sem cabeça.

Vale a pena conhecer algumas configurações no `cypress.config.ts` porque elas
mudar a forma como os testes se comportam: `chromeWebSecurity: false` (para coisas de origem cruzada como
Os iframes OAuth não são bloqueados no desenvolvedor local), `experimentalStudio: true`
(ativa o Studio, abaixo) e `experimentalMemoryManagement: true` com
`numTestsKeptInMemory: 0` — mantemos zero testes anteriores na memória porque estes
as viagens são longas e, caso contrário, o Chrome inflaria e travaria no meio da corrida.

### Comandos personalizados

O recurso Cypress mais útil aqui são os **comandos personalizados**: um recurso reutilizável
Função Cypress para que você não reescreva o login (ou criação de concurso, ou problema
criação) em todas as especificações. Eles são declarados em
[`cypress/support/commands.ts`](https://github.com/omegaup/omegaup/blob/main/cypress/support/commands.ts).
`login` efetua login de um usuário fazendo POST diretamente na API, em vez de direcionar o
forma, que é mais rápida e menos escamosa:

```typescript
Cypress.Commands.add('login', ({ username, password }: LoginOptions) => {
  cy.request({
    method: 'POST',
    url: '/api/user/login/',
    form: true,
    body: { usernameOrEmail: username, password },
  }).then((response) => {
    expect(response.status).to.equal(200);
    cy.reload();
  });
});
```
Há um irmão `loginAdmin` que codifica a conta de administrador propagada
(`omegaup` / `omegaup`), mais `register`, `logout`, `logoutUsingApi`,
`createProblem`, `createCourse`, `createRun`, `createContest`,
`addProblemsToContest`, `createGroup` e muito mais – a configuração completa do concurso/curso
vocabulário, então uma especificação parece uma história em vez de uma parede de cliques.

Como estamos no TypeScript, adicionar um comando leva duas etapas e pular a
o segundo é o erro clássico: **declare seu tipo**, ou o TypeScript não saberá
`cy.myCommand()` existe. A interface `Chainable` reside em
[`cypress/support/cypress.d.ts`](https://github.com/omegaup/omegaup/blob/main/cypress/support/cypress.d.ts),
e os tipos de opções (`LoginOptions`, `CourseOptions`, `ProblemOptions`, …) em
`cypress/support/types.d.ts`:

```typescript
declare global {
  namespace Cypress {
    interface Chainable {
      login(loginOptions: LoginOptions): void;
      loginAdmin(): void;
      register(loginOptions: LoginOptions): void;
      createProblem(problemOptions: ProblemOptions): void;
      // ...add your new command's signature here
    }
  }
}
```
### Eventos: não deixe que uma exceção de terceiros interrompa a execução

Às vezes você quer que um teste continue mesmo quando uma exceção não detectada é acionada
do código que você não controla. O caso concreto que forçou isso: ao executar
Cypress, a API do Google Sign-In recusou-se a reconhecer `127.0.0.1` (o Docker IP)
como um host permitido e lançou `idpiframe_initialization_failed`, que por padrão
aborta todo o teste. A correção é um manipulador `uncaught:exception` global em
[`cypress/support/e2e.ts`](https://github.com/omegaup/omegaup/blob/main/cypress/support/e2e.ts)
que retorna `false` exatamente para aqueles erros inofensivos conhecidos, então o teste
continua:

```typescript
import './commands';

Cypress.on('uncaught:exception', (err, runnable) => {
  if (
    (err as any).message?.includes('idpiframe_initialization_failed') ||
    (err as any).error?.includes('idpiframe_initialization_failed') ||
    (err as any).message?.includes(
      'ResizeObserver loop completed with undelivered notifications',
    )
  ) {
    // Google API sign-in error, and a benign ResizeObserver warning
    return false;
  }
});
```
Observe que ele também engole o loop `ResizeObserver concluído com não entregue
aviso de notificações - um ruído benigno do navegador que, de outra forma, prejudicaria seu
testes. Coloque os manipuladores que você deseja apenas para uma especificação dentro desse arquivo de especificações, em vez de
aqui; `e2e.ts` é global e se aplica a todos os testes.

### Cypress Studio e os plug-ins

Como o `experimentalStudio` está ativado, abrir uma especificação na GUI fornece um botão
para **gravar** suas interações diretamente nas especificações como comandos — clique
através do fluxo e o Studio grava as chamadas `cy.*` para você, estendendo um
teste existente ou estruturar um novo. Uma propriedade legal: o Studio faz
_não_ registre o tempo entre as ações, para não ter pressa; demore tanto tempo
como quiser entre cliques.

Dois plug-ins são conectados e importados na parte superior do `commands.ts`:
**cypress-wait-until** (`cy.waitUntil(...)`, para sondagem até que uma condição seja mantida
- usado, por ex. em `logout` para aguardar a resolução do URL) e
**cypress-file-upload** (para `.attachFile(...)` nos fluxos de upload de problemas).
O gancho `setupNodeEvents` em cargas `cypress.config.ts`
`cypress/plugins/index.js`, que registra uma tarefa `log` para que um teste possa ser impresso
o terminal executando o Cypress.

### Quando passa localmente, mas falha no CI

CI executa as especificações fragmentadas em uma matriz (veja o trabalho `cypress` em
[`.github/workflows/ci.yml`](https://github.com/omegaup/omegaup/blob/main/.github/workflows/ci.yml)),
cada fragmento executando `./node_modules/.bin/cypress run --browser chrome --spec '<specs>'`.
Quando um teste é verde na sua máquina, mas vermelho no PR, não adivinhe – observe o que
o navegador CI viu. Abra a guia **Verificações** do PR e selecione o **cypress** com falha
job e baixe os artefatos da execução:

- `cypress-videos-shard-<shard>-<run_attempt>` — o vídeo da execução real.
- `cypress-screenshots-shard-<shard>-<run_attempt>` — capturas de tela no momento
  de fracasso.
- `frontend-test-logs-<run_attempt>` — logs do lado do contêiner, quando a falha é
  na verdade, o back-end está se comportando mal, e não o teste.

O sufixo `<run_attempt>` é o número da tentativa da execução do fluxo de trabalho (visível
no URL de execução, por exemplo. `/attempts/3`), portanto, se você executou novamente um trabalho instável, certifique-se de
pegue os artefatos da tentativa que realmente falhou.

## Testes de IU em Python

Há um conjunto menor de UI estilo Selenium no `frontend/tests/ui/` executado com
`python3 -m pytest ./frontend/tests/ui/ -s`. Como `runtests.sh` lembra você, é
é executado **fora** do contêiner, e é por isso que não faz parte do contêiner
Fluxo PHPUnit.

## Cobertura de teste

Enviamos a cobertura para **Codecov**. A cobertura do PHP vem do relatório Clover
(`coverage.xml`) que `run-php-tests.sh` emite e cobertura TypeScript de
`yarn test:coverage`. As execuções do Cypress **não** estão conectadas à cobertura ainda – elas
provar que as viagens funcionam de ponta a ponta, mas não contam para a cobertura
número, então não confie em um teste e2e para "cobrir" uma unidade de lógica que um Jest ou
O teste PHPUnit deve possuir.

## Alguns hábitos que vale a pena manter

Mantenha os testes unitários genuinamente rápidos e genuinamente isolados — cada teste PHPUnit é construído
seus próprios equipamentos através dos auxiliares `Factories/` e cada teste Jest monta seu
próprio componente, portanto os testes nunca dependem do estado restante um do outro ou de
ordem de execução. Procure a camada que corresponde ao que você está testando: pura
funções e componentes únicos pertencem a Jest, controlador/permissão/API
comportamento pertence ao PHPUnit contra um MySQL real, e apenas o completo
a jornada do usuário entre páginas ganha uma especificação Cypress (eles são os mais lentos e os
mais esquisito, então gaste-os deliberadamente). E quando você toca no comportamento, escreve ou
atualize o teste na mesma mudança - um PR que muda o que o código faz, mas
não o que os testes afirmam é o que os revisores enviarão de volta.

## Documentação relacionada

- **[Diretrizes de codificação](coding-guidelines.md)** — os padrões que os linters e o Salmo impõem
- **[Comandos úteis](useful-commands.md)** — a folha de dicas dos comandos do dia a dia
- **[Configuração de desenvolvimento](../getting-started/development-setup.md)** — instale o Node, o Yarn e o Docker antes de executar qualquer um destes
