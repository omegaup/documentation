---
title: Comandos úteis de desenvolvimento
description: Comandos e atalhos comuns para desenvolvimento omegaUp
icon: bootstrap/terminal
---
# Comandos úteis de desenvolvimento

Este é o conjunto funcional de comandos que você usará no dia a dia: linting, os conjuntos de testes PHP e Vue, a construção do Webpack e os scripts de banco de dados que mantêm seu esquema local e dados iniciais honestos. Cada comando abaixo é reproduzido exatamente como você deve digitá-lo - os sinalizadores suportam carga, portanto, não os parafraseie.

A coisa mais importante a ser acertada antes de qualquer coisa é **onde** você executa cada comando. O desenvolvimento do omegaUp acontece através de um limite: algumas ferramentas são executadas em sua máquina host (precisam do soquete Docker, da instalação do Node ou de um navegador) e algumas são executadas *dentro* do contêiner `frontend` (precisam do tempo de execução do PHP, da conexão MySQL na porta `13306` e do código montado em `/opt/omegaup`). A execução de um comando no lado errado desse limite é o tropeço inicial mais comum, de modo que cada seção indica seu local de execução e vários scripts se recusam ativamente a executar no local errado, em vez de falharem de forma criptografada.

Para entrar no contêiner em primeiro lugar:

```bash
docker exec -it omegaup-frontend-1 /bin/bash
```
Isso abre um shell bash dentro do contêiner de front-end, deixando você em `/opt/omegaup` (o repositório, montado em ligação do seu host). O contêiner é denominado `omegaup-frontend-1` no Docker Compose V2 (o esquema `<project>-<service>-<n>`, onde o nome do projeto é padronizado como seu diretório `omegaup`). Em instalações mais antigas do Compose V1, o mesmo contêiner é denominado `omegaup_frontend_1` com sublinhados. Se `docker exec` reclamar que o contêiner não existe, execute `docker compose ps` para ver o nome exato que sua configuração produziu.

!!! dica "Como saber de que lado você está"
    Dentro do contêiner, seu prompt fica em `/opt/omegaup`; no host é onde você clonou o repositório (por exemplo, `~/dev/omegaup`). Vários scripts explicam isso: `git rev-parse --show-toplevel` retornando `/opt/omegaup` é exatamente como `lint.sh` e `runtests.sh` detectam que estão dentro do contêiner.

## Linting e validação

### Execute todos os linters omegaUp

```bash
./stuff/lint.sh
```
Execute-o a partir da **raiz do projeto em seu host**, fora do contêiner — ele gera sua própria imagem Docker (`omegaup/hook_tools:v1.0.9`) para executar os linters em um ambiente reproduzível e fixado, por isso precisa de seu soquete Docker. Por causa disso, `lint.sh` se recusa explicitamente a ser executado dentro do contêiner: se `git rev-parse --show-toplevel` voltar como `/opt/omegaup`, ele imprime *"Executar ./stuff/lint.sh dentro de um contêiner não é suportado"* e sai, e se não conseguir encontrar um binário `docker`, ele informa para você instalar o Docker ou sair do contêiner. Ambas as mensagens são o script que protege você de uma execução que silenciosamente faria a coisa errada.

Sem argumentos, `lint.sh` não lint a árvore inteira - ele adivinha o conjunto de arquivos que você realmente alterou comparando com a base de mesclagem de sua ramificação e `upstream/main` (voltando para `origin/main` se você não adicionou o controle remoto `upstream`), e é por isso que uma primeira execução após a clonagem sem um upstream pode se comportar de maneira diferente do que você espera. Porém, você raramente precisa invocá-lo manualmente: ele está conectado ao gancho git `pre-push`, portanto, ele é executado automaticamente em cada `git push` e bloqueia o push se algo estiver sujo.

### Validar estilo sem corrigir

```bash
./stuff/lint.sh validate
```
O modo padrão *corrige* o que pode (ele delega para `yapf`, `prettier`, `phpcbf` e amigos dentro da imagem hook-tools); Em vez disso, o `validate` apenas verifica e relata, sem alterar nada no disco. Faça isso em situações semelhantes às de CI ou quando quiser ver o que há de errado antes de permitir que o autofixer reescreva seus arquivos.

### Gere arquivos de tradução `.lang`

```bash
./stuff/lint.sh --linters=i18n fix --all
```
Isso executa apenas o linter `i18n` e regenera os arquivos `*.lang` em todas as localidades a partir dos três arquivos de fonte da verdade `es.lang`, `en.lang` e `pt.lang`. Execute-o sempre que você adicionar ou alterar uma string voltada ao usuário para que os arquivos gerados por idioma permaneçam sincronizados - caso contrário, o linter i18n falhará no push. Ele também é executado fora do contêiner, na raiz do projeto.

## Teste

### Execute todos os testes e validações de PHP

```bash
./stuff/runtests.sh
```
Este é o portão de back-end completo e deve ser executado **dentro do contêiner**. Ele agrupa quatro verificações distintas que você executaria separadamente: `stuff/db-migrate.py validate` (confirma que suas migrações são consistentes), `stuff/policy-tool.py validate` e `stuff/mysql_types.sh` — que é a mais pesada, executando os controladores e emblemas PHPUnit suites *mais* a verificação de tipo de retorno do MySQL que verifica se seus métodos DAO realmente correspondem às formas que suas consultas retornam — e finalmente Psalm com `--show-info=false`.

`runtests.sh` reconhece localização: execute-o dentro do contêiner e ele invoca essas ferramentas diretamente; execute-o no host e ele será inserido de forma transparente no contêiner com `docker compose exec -T frontend` para cada etapa. De qualquer forma, quando a parte do contêiner termina, ele lembra você de executar as duas verificações no lado do host que *não* pode ser feita internamente - `./stuff/lint.sh` e os testes Selenium/UI via `python3 -m pytest ./frontend/tests/ui/ -s` - porque eles precisam do Docker e de um navegador, respectivamente. Não pule esse lembrete; um `runtests.sh` verde por si só não é uma construção verde.

### Execute testes de unidade PHP para um arquivo específico

```bash
./stuff/run-php-tests.sh frontend/tests/controllers/$MY_FILE.php
```
Quando você está iterando em um controlador, não deseja o conjunto inteiro. Este wrapper executa o PHPUnit apenas no arquivo que você nomeou (omita totalmente o nome do arquivo para executar tudo em `frontend/tests/`). Ele conecta a configuração real do conjunto para você - `--bootstrap frontend/tests/bootstrap.php`, `--configuration frontend/tests/phpunit.xml` e cobertura gravada em `coverage.xml` - e depois passa quaisquer argumentos *extras* diretamente para `phpunit`. Essa passagem é a parte útil: para executar um único método de teste você pode anexar o próprio filtro do PHPUnit, por exemplo.

```bash
./stuff/run-php-tests.sh frontend/tests/controllers/UserRankTest.php --filter testUserRankingClassName
```
Execute isso dentro do contêiner, pois o PHPUnit precisa da conexão MySQL ativa.

### Execute testes ponta a ponta do Cypress (interativo)

```bash
npx cypress open
```
Isso abre o Cypress Test Runner, a GUI onde você escolhe uma especificação, observa-a conduzir um Chrome real e inspeciona falhas passo a passo com instantâneos de viagem no tempo – a maneira mais rápida de depurar um teste e2e instável. Ele é executado no **host**, fora do contêiner (ele precisa de um navegador real e, no Linux, pode precisar do `libasound2` e de outras dependências do X instaladas antes de ser iniciado). As próprias especificações residem no `cypress/e2e/*.cy.ts` - atualmente cerca de dez delas, abrangendo cursos, grupos, IDE, navegação, certificados, concursos e fluxos de criador/coleção de problemas.

### Execute Cypress sem cabeça

```bash
yarn test:e2e
```
As mesmas especificações sem a GUI: isso se expande para `cypress run --browser chrome`, executando todas as especificações sem cabeça e imprimindo os resultados no terminal. Isso é o que o CI usa e o que você deseja para uma passagem rápida "quebrei algum fluxo e2e", já que não espera que você clique em nada.

### Execute testes de unidade Vue no modo de observação

```bash
yarn run test:watch
```
Isso executa os testes de unidade Jest (Jest 26 via `ts-jest`) para o frontend Vue/TypeScript no modo de observação - nos bastidores, o `cross-env TZ=UTC jest --watchAll --notify` tem como escopo os arquivos correspondentes a `frontend/www/js/.*test\.ts$`. O modo Watch mantém o Jest residente e executa novamente os testes afetados sempre que você salva um componente ou seu teste, para que você obtenha um sinal vermelho/verde contínuo enquanto trabalha, em vez de reativar manualmente. O pino `TZ=UTC` é importante: ele força um fuso horário determinístico para que testes sensíveis à data não sejam aprovados em sua máquina e falhem no CI. Para uma execução única, use `yarn test`; para cobertura use `yarn test:coverage`.

### Execute um arquivo de teste de unidade específico do Vue

```bash
./node_modules/.bin/jest frontend/www/js/omegaup/components/$MY_FILE.test.ts
```
Quando o modo de observação estiver sendo executado com muita frequência, invoque o Jest diretamente em um único arquivo de teste. Todos os componentes de arquivo único do Vue residem em `frontend/www/js/omegaup/components/`, assim como seus vizinhos `.test.ts` também. Este pode ser executado dentro ou fora do contêiner - é Node puro, sem dependência de MySQL.

## Construindo o front-end

O site é um shell Twig 3 que envolve componentes de arquivo único Vue 2.7 + TypeScript, agrupados pelo Webpack 5. Durante o desenvolvimento, você quase sempre deseja que um observador reconstrua os pacotes conforme você edita, em vez de reconstruí-los manualmente.

```bash
yarn dev:watch
```
Este é o loop diário: ele executa o Webpack na configuração do `frontend` no modo de desenvolvimento com `--watch`, portanto, cada salvamento agrupa novamente apenas os pontos de entrada do frontend. Scripts relacionados trocam escopo por velocidade - `yarn dev` é a mesma construção uma vez sem assistir; `yarn dev-all` / `yarn dev-all:watch` cria *todas* as configurações do Webpack (o frontend, mais o estilo e os pacotes secundários) quando uma alteração afeta mais do que o código do aplicativo.

Para um pacote entregável, `yarn build` executa Webpack em `--mode=production` (minificado, sem mapas de origem), enquanto `yarn build-development` produz uma construção de desenvolvimento não minificada. E para navegar pelos componentes isoladamente:

```bash
yarn storybook
```
Isso inicia o Storybook (7.6) na porta `6006` via `storybook dev -p 6006`, oferecendo uma sandbox para renderizar e cutucar componentes individuais do Vue sem inicializar o aplicativo inteiro. A cobertura da história é atualmente escassa – cerca de dez arquivos `.stories` contra mais de 250 componentes – portanto, nem todos os componentes têm uma entrada ainda.

!!! note "O aplicativo da web não está mostrando minhas alterações"
    Se você editar um arquivo `.vue` ou `.ts` e a página parecer inalterada, a causa comum é que nenhum inspetor está em execução para reconstruir o pacote configurável. Certifique-se de que `yarn dev:watch` (ou `yarn dev-all:watch`) esteja em execução e, em seguida, recarregue a página em **http://localhost:8001**. As alterações do PHP, por outro lado, são obtidas diretamente da montagem de ligação, sem reconstrução.

## Banco de dados

### Redefinir o banco de dados para seu estado inicial

```bash
./stuff/bootstrap-environment.py --purge
```
Execute isso dentro do contêiner quando seus dados locais entrarem em um estado inutilizável ou quando você quiser apenas uma lista limpa para testar. O sinalizador `--purge` elimina e recria o banco de dados do zero; o script então reproduz uma série de solicitações reais de API para preenchê-lo, apresentando concursos, cursos, problemas e os usuários de teste necessários para testes manuais. A definição do que é criado reside no `stuff/bootstrap.json`, então se você quiser equipamentos extras, esse é o arquivo a ser editado. Sinta-se à vontade para executá-lo quantas vezes precisar - um novo bootstrap é a maneira mais rápida de sair de "meu banco de dados local está quebrado".

### Aplicar migrações de banco de dados localmente

```bash
./stuff/db-migrate.py migrate --databases=omegaup,omegaup-test
```
Depois de adicionar um novo arquivo de migração `.sql`, isso aplica as alterações de esquema pendentes aos seus bancos de dados locais. Nomear **ambos** `omegaup` e `omegaup-test` é deliberado e importante: o segundo é o banco de dados no qual o conjunto PHPUnit é executado, portanto, se você migrar apenas `omegaup`, seu aplicativo funcionará, mas `runtests.sh` falhará em um esquema de teste obsoleto (e sua própria etapa `db-migrate.py validate` sinalizará a incompatibilidade). Execute-o dentro do contêiner.

### Gere novamente o `schema.sql` e os DAOs da sua migração

```bash
./stuff/update-dao.sh
```
As migrações descrevem *mudanças*; `schema.sql` e as classes DAO/VO geradas descrevem o formato *atual* do banco de dados e não se atualizam. Este script copia `frontend/database/schema.sql` para `frontend/database/dao_schema.sql` para acionar a regeneração e, em seguida, executa `stuff/update-dao.py` para reescrever as classes base DAO geradas automaticamente e objetos de valor para corresponder às suas novas colunas. Execute-o dentro do contêiner após adicionar uma migração - e observe o problema de ordenação: ele se regenera no esquema confirmado, portanto, ele faz seu trabalho assim que o arquivo de migração estiver em vigor.

## Validação de tipo PHP

### Execute o Psalm no código-fonte PHP

```bash
find frontend/ \
    -name *.php \
    -and -not -wholename 'frontend/server/libs/third_party/*' \
    -and -not -wholename 'frontend/tests/badges/*' \
    -and -not -wholename 'frontend/tests/controllers/*' \
    -and -not -wholename 'frontend/tests/runfiles/*' \
    -and -not -wholename 'frontend/www/preguntas/*' \
  | xargs ./vendor/bin/psalm \
    --long-progress \
    --show-info=false
```
Isso executa o Psalm (o verificador de tipo estático configurado por `psalm.xml`) sobre o PHP original, usando `find` para entregar todos os arquivos `.php` *exceto* os caminhos excluídos - bibliotecas de terceiros em `frontend/server/libs/third_party/`, vários diretórios de acessórios de teste e a árvore herdada `frontend/www/preguntas/` - porque esses não são nossos para verificação de tipo ou afogariam a execução em ruído. `--long-progress` fornece uma barra de progresso ao vivo para o que é uma passagem lenta de árvore inteira, e `--show-info=false` suprime avisos informativos para que apenas erros de tipo genuínos apareçam. Execute-o dentro do contêiner. Se você deseja apenas a mesma verificação que o portão CI é executado, o `runtests.sh` já invoca o `./vendor/bin/psalm --show-info=false` para você.

## Docker

### Inicie o ambiente de desenvolvimento

```bash
docker compose up --no-build
```
É assim que você eleva toda a pilha: o contêiner `frontend` (php-fpm por trás do nginx, servindo em **http://localhost:8001**), MySQL 8.0 na porta `13306`, Redis e os serviços Go pré-construídos — `gitserver`, `grader`, `broadcaster` e `runner` — extraídos das imagens `omegaup/*`. `--no-build` pula a reconstrução das imagens e apenas executa o que você já tem, que é o que você deseja em um dia normal; solte-o (`docker compose up`) na primeira execução ou após as alterações da imagem, para que o Compose construa/puxe primeiro. O frontend PHP backend se comunica com o Go `grader` por HTTP em `OMEGAUP_GRADER_URL` (padrão `https://localhost:21680`), enquanto as mãos do avaliador trabalham com os executores internamente na porta `11302` - esses serviços residem nos repositórios `omegaup/quark` e `omegaup/gitserver` separados, não neste.

!!! observe "`docker compose` vs `docker-compose`"
    Docker Compose V2 é o plugin do formato `docker compose` (com espaço); configurações mais antigas possuem o binário `docker-compose` independente. Qualquer um deles funciona desde que sua instalação forneça um deles; os exemplos aqui usam o formulário V2.

### Reinicie o serviço Docker

```bash
systemctl restart docker.service
```
Execute isso em seu **host** (Linux) quando o próprio Docker entrar em um estado ruim - especificamente, se `docker exec` começar a falhar com:

```bash
OCI runtime exec failed: exec failed: unable to start container process: open /dev/pts/0: operation not permitted: unknown
```
Esse erro não é um problema do omegaUp; é o tempo de execução do daemon Docker que perdeu a capacidade de alocar um pseudoterminal para seu `exec`. Reiniciar o daemon `docker.service` o limpa, após o que `docker exec -it omegaup-frontend-1 /bin/bash` funciona novamente. (No macOS ou Windows, o equivalente é reiniciar o Docker Desktop.)

## Referência rápida

Cada comando, com o lado do limite do contêiner ao qual pertence:

| Tarefa | Comando | Onde correr |
|------|---------|-------------|
| Execute todos os linters (autofix) | `./stuff/lint.sh` | Host, raiz do projeto |
| Verifique o estilo sem consertar | `./stuff/lint.sh validate` | Host, raiz do projeto |
| Gerar novamente arquivos `.lang` | `./stuff/lint.sh --linters=i18n fix --all` | Host, raiz do projeto |
| Teste PHP completo + portão de validação | `./stuff/runtests.sh` | Dentro do recipiente |
| Um arquivo de teste PHP | `./stuff/run-php-tests.sh frontend/tests/controllers/$MY_FILE.php` | Dentro do recipiente |
| GUI Cipreste | `npx cypress open` | Anfitrião |
| Cipreste sem cabeça | `yarn test:e2e` | Anfitrião |
| Testes de unidade Vue (assistir) | `yarn run test:watch` | Qualquer lado |
| Um arquivo de teste Vue | `./node_modules/.bin/jest frontend/www/js/omegaup/components/$MY_FILE.test.ts` | Qualquer lado |
| Observador de construção de front-end | `yarn dev:watch` | Anfitrião |
| Pacote de produção | `yarn build` | Anfitrião |
| Caixa de areia de componentes | `yarn storybook` (porta 6006) | Anfitrião |
| Redefinir e propagar o banco de dados | `./stuff/bootstrap-environment.py --purge` | Dentro do recipiente |
| Aplicar migrações | `./stuff/db-migrate.py migrate --databases=omegaup,omegaup-test` | Dentro do recipiente |
| Regenerar esquema + DAOs | `./stuff/update-dao.sh` | Dentro do recipiente |
| Abra um shell de contêiner | `docker exec -it omegaup-frontend-1 /bin/bash` | Anfitrião |
| Inicie a pilha | `docker compose up --no-build` | Anfitrião |

## Documentação Relacionada

- **[Guia de teste](testing.md)** — a imagem completa sobre PHPUnit, Jest e Cypress
- **[Diretrizes de codificação](coding-guidelines.md)** — os padrões que os linters impõem
- **[Configuração de desenvolvimento](../getting-started/development-setup.md)** — colocar o ambiente em execução em primeiro lugar
