---
title: Configuração do ambiente de desenvolvimento
description: Guia completo para configurar seu ambiente de desenvolvimento local omegaUp
icon: bootstrap/tools
---
# Configuração do ambiente de desenvolvimento

Esta página orienta você na criação de um omegaUp local completo - frontend, API PHP, MySQL e Go grader/runner/gitserver - em sua própria máquina com Docker. A pilha inteira reside em alguns contêineres descritos por `docker-compose.yml`, então você não instala PHP 8.1, MySQL 8.0, Redis ou RabbitMQ manualmente; você extrai imagens pré-construídas e as traz à tona. Preferimos Docker para todos agora - a antiga VM Vagrant/VirtualBox provisionada de [omegaup/deploy](https://github.com/omegaup/deploy) está obsoleta e não é mais o caminho suportado, então se você encontrar uma página wiki informando para `vagrant up`, pule-a.

!!! dica "Vídeo Tutorial"
    Se você preferir assistir a ler, temos um [vídeo tutorial](http://www.youtube.com/watch?v=H1PG4Dvje88) que percorre a mesma configuração de ponta a ponta.

## Pré-requisitos

Antes de mais nada, instale as duas peças de ferramentas Docker e Git:

- **Docker Engine** — [instale](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository). Isto é o que realmente executa os contêineres.
- **Docker Compose v2** — [instale o plugin](https://docs.docker.com/compose/install/linux/#install-the-plugin-manually). Compose é o que lê `docker-compose.yml` e reúne toda a pilha. Se você ainda estiver no Compose v1, poderá [migrar para v2](https://docs.docker.com/compose/install/linux/#install-using-the-repository); as grafias `docker compose` (espaço) e `docker-compose` (hífen) funcionam e este guia as utiliza de forma intercambiável.
- **Git** — para clonar o repositório e porque todo o fluxo de trabalho de contribuição é construído nele.

!!! aviso "Novo no Git?"
    Se você ainda não está confiante com o Git, leia [este tutorial do Git](https://github.com/shekhargulati/git-the-missing-tutorial) antes de começar. Tudo após o clone – ramificações, solicitações pull, manutenção do `main` sincronizado – pressupõe que você possa se movimentar confortavelmente no Git.

### Linux: adicione-se ao grupo `docker`

No Linux, execute isto uma vez para poder invocar `docker` sem `sudo`:

```bash
sudo usermod -a -G docker $USER
```
Em seguida, **saia e faça login novamente** para que a nova associação ao grupo entre em vigor. Isso é mais importante do que parece: se você ignorá-lo e começar a buscar `sudo docker compose up`, a árvore do projeto montada em bind acabará sendo propriedade de `root`, e o usuário não-root do contêiner não poderá mais gravar nele - o que surge mais tarde como um loop de reinicialização desconcertante (consulte [Meu ambiente de desenvolvimento não aparece](#my-dev-environment-wont-come-up)). Faça isso da maneira certa uma vez e você evitará todo o tipo de problema.

!!! observe "Windows: desenvolva dentro do WSL2"
    No Windows, execute tudo por meio de [WSL2](https://docs.docker.com/desktop/features/wsl) com a integração WSL do Docker Desktop habilitada e - esta é a parte de suporte de carga - **clone o repositório no sistema de arquivos Linux** (em algum lugar na sua casa WSL, por exemplo, `~/omegaup`), *não* em `/mnt/c/...`. As montagens de ligação do Docker que cruzam o limite do Windows↔Linux são lentas e, pior, o `webpack --watch` dentro do contêiner perde silenciosamente eventos de alteração de arquivo no `/mnt/c`, para que suas edições nunca acionem uma reconstrução e você fique olhando para uma saída obsoleta. Manter o checkout no lado do Linux é o substituto moderno para a antiga dança de sincronização de arquivos WinSCP/Xming da era Vagrant.

## Etapa 1: bifurcar e clonar

Fork [omegaup/omegaup](https://github.com/omegaup/omegaup) no GitHub primeiro - você envia para seu fork, não para o repositório principal - depois clona seu fork em um diretório vazio. O sinalizador `--recurse-submodules` é importante: várias dependências de front-end de terceiros (`pagedown` para o editor Markdown, `iso-3166-2.js` para códigos de país, `mathjax` para renderização matemática e muito mais) residem em submódulos Git e a construção é interrompida sem eles.

```bash
git clone --recurse-submodules https://github.com/YOURUSERNAME/omegaup
cd omegaup
```
Se você clonou sem `--recurse-submodules`, ou um submódulo parece vazio, extraia-os explicitamente da raiz do repositório:

```bash
git submodule update --init --recursive
```
## Etapa 2: Abra os contêineres

Na raiz do repositório (`omegaup/`), extraia as imagens e inicie a pilha:

```bash
docker-compose pull       # only needed the first time, or when the next command complains
docker-compose up --no-build
```
O `pull` captura as imagens pré-construídas que o Compose precisa – o frontend PHP/nginx, MySQL 8.0, Redis, RabbitMQ e os serviços Go separados (`omegaup/backend`, `omegaup/runner`, `omegaup/gitserver`) que fornecem o avaliador, o executor e o armazenamento de problemas. Você só precisa extrair novamente quando configurar pela primeira vez ou quando `docker-compose up` reclamar que uma imagem está faltando ou obsoleta. O sinalizador `--no-build` diz ao Compose para executar essas imagens pré-construídas como estão, em vez de reconstruí-las do zero, o que reduz a inicialização a minutos, em vez de um longo intervalo para o café.

**A primeira inicialização leva de 2 a 10 minutos.** Após essa espera, o contêiner front-end está executando o Webpack para compilar todo o front-end Vue 2.7 + TypeScript, o MySQL está inicializando e o avaliador está aguardando no banco de dados (`wait-for-it mysql:13306`). O que sinaliza que ele está realmente pronto é um dump do módulo Webpack semelhante a este:

```
frontend_1     | Child frontend:
frontend_1     |        1550 modules
frontend_1     |     Child HtmlWebpackCompiler:
frontend_1     |            1 module
frontend_1     | Child style:
frontend_1     |        1 module
frontend_1     |     Child extract-text-webpack-plugin node_modules/extract-text-webpack-plugin/dist node_modules/css-loader/dist/cjs.js!node_modules/sass-loader/dist/cjs.js!frontend/www/sass/main.scss:
frontend_1     |            2 modules
frontend_1     | Child grader:
frontend_1     |        1131 modules
frontend_1     |     Child vs/editor/editor:
frontend_1     |            36 modules
frontend_1     |     Child vs/language/typescript/tsWorker:
frontend_1     |            41 modules
```
Depois de ver isso, o front-end concluiu sua construção e o site está ativo. O módulo exato conta o desvio à medida que o frontend cresce - trate-os como um sinal de "terminamos a compilação", não como uma soma de verificação.

Em execuções posteriores você pode pular o `pull` e apenas iniciar a pilha:

```bash
docker compose up --no-build
```
## Etapa 3: abra sua instância local

Com os contêineres em execução, seu omegaUp local está em:

**[http://localhost:8001](http://localhost:8001)**

Essa é a porta `8001`, publicada a partir do contêiner frontend em `docker-compose.yml`. Observe que é `http` simples - consulte [a correção do redirecionamento HTTPS do navegador] (#my-browser-keeps-forcing-https) se o seu navegador insistir em reescrevê-lo.

## Etapa 4: coloque um shell dentro do contêiner

Quase todos os comandos dev - executando testes, invocando scripts `stuff/`, vasculhando o banco de dados - são executados *dentro* do contêiner frontend, porque é onde o PHP 8.1, o Node, o Yarn e as ferramentas realmente residem. Abra um shell com um destes (eles são equivalentes):

```bash
docker compose exec frontend /bin/bash
# or, by container name:
docker exec -it omegaup-frontend-1 /bin/bash
```
O nome exato do contêiner depende da versão do Compose - a v2 o nomeia como `omegaup-frontend-1` (hífenes), o `docker-compose` mais antigo usava `omegaup_frontend_1` (sublinhados). Se você não tiver certeza do que possui, `docker compose ps` lista os nomes reais. Dentro do contêiner, a base de código é montada em **`/opt/omegaup`** — os mesmos arquivos que você edita em seu host, portanto, um salvamento em sua máquina fica instantaneamente visível no contêiner.

## Contas de Desenvolvimento

Sua nova instalação vem com duas contas já propagadas, para que você possa fazer login imediatamente sem registrar nada:

- **`omegaup`** / senha **`omegaup`** — um usuário com privilégios de administrador de sistema. Use isto quando precisar tocar na interface do usuário somente para administrador.
- **`user`** / senha **`user`** — um usuário comum simples, para testar a experiência do usuário normal.

Além disso, o conjunto de testes gera uma lista estável de contas nas quais você pode fazer login. A senha é sempre idêntica ao nome de usuário, o que torna fácil lembrar:

| Nome de usuário | Senha |
| -- | -- |
| `test_user_0` | `test_user_0` |
| `test_user_1` | `test_user_1` |
| `test_user_2` | `test_user_2` |
| `test_user_3` | `test_user_3` |
| `test_user_4` | `test_user_4` |
| `test_user_5` | `test_user_5` |
| `test_user_6` | `test_user_6` |
| `test_user_7` | `test_user_7` |
| `test_user_8` | `test_user_8` |
| `test_user_9` | `test_user_9` |
| `course_test_user_0` | `course_test_user_0` |
| `course_test_user_1` | `course_test_user_1` |
| `course_test_user_2` | `course_test_user_2` |

**Sinta-se à vontade para criar quantos usuários precisar** para testar suas alterações. No modo de desenvolvimento, a verificação de e-mail está desativada, portanto qualquer endereço fictício funciona — você nunca precisa verificar uma caixa de entrada para ativar uma conta.

## Estrutura da base de código

O código omegaUp reside em `/opt/omegaup` dentro do contêiner (e em seu clone no host - é a mesma árvore montada em ligação). Estes são os diretórios nos quais trabalhamos ativamente no dia a dia:

- **[`frontend/server/src/Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers)** — os controladores, com namespace `\OmegaUp\Controllers`, que mantêm a lógica de negócios e expõem a API do servidor. Cada método estático `apiXxx` é um endpoint de API; por exemplo, `\OmegaUp\Controllers\Run::apiCreate` (em [`Run.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Run.php)) é o que trata de um envio. Observe que a classe é `Run`, não `RunController` – os controladores omegaUp eliminam o sufixo `Controller`.
- **[`frontend/server/src/DAO/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/DAO)** — a camada de acesso a dados. Ele é dividido propositalmente: classes base abstratas geradas automaticamente em `DAO/Base/` carregam o SQL bruto, objetos de valor simples em `DAO/VO/` espelham as linhas do banco de dados e wrappers escritos à mão diretamente em `DAO/` adicionam as consultas que os controladores realmente chamam. Você edita os wrappers e os VOs, não as bases geradas.
- **[`frontend/server/src/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src)** — o restante das bibliotecas e utilitários do servidor, incluindo `ApiCaller.php` (o despachante de solicitação) e `Grader.php` (o cliente HTTP fino que se comunica com o classificador Go).
- **[`frontend/templates/`](https://github.com/omegaup/omegaup/tree/main/frontend/templates)** — o shell HTML renderizado pelo servidor mais os arquivos de internacionalização para inglês, espanhol e português. Há um único modelo aqui, `template.tpl`, e apesar da extensão `.tpl` é **Twig 3**, não Smarty – Smarty se foi. Suas tags personalizadas (`{% entrypoint %}`, `{% jsInclude %}`) são implementadas por nossas próprias extensões Twig em `frontend/server/src/Template/`, e tudo o que elas fazem é inicializar um aplicativo Vue e entregar a ele uma carga JSON.
- **[`frontend/www/`](https://github.com/omegaup/omegaup/tree/main/frontend/www)** — todo o aplicativo voltado para o navegador. A UI de cada página é um componente de arquivo único do Vue 2.7; os componentes residem em `frontend/www/js/omegaup/components/`, e o cliente API digitado (`api.ts`, `api_types.ts`) é gerado a partir dos controladores PHP por `frontend/server/cmd/APITool.php` - não edite manualmente esses dois, regenere-os.

Uma coisa que confunde as pessoas: **avaliador, corredor, locutor e sandbox minijail não estão neste repositório**. Eles são serviços Go separados em [github.com/omegaup/quark](https://github.com/omegaup/quark) (e o armazenamento de problemas reside em [github.com/omegaup/gitserver](https://github.com/omegaup/gitserver)). O Docker os executa como binários pré-construídos, e o backend do PHP apenas *conversa* com o avaliador por HTTP por meio de `\OmegaUp\Grader`, em `OMEGAUP_GRADER_URL` (padrão `https://localhost:21680`). Se você está perseguindo um bug de avaliação, esse é o repositório para o qual seu editor deve apontar - não este.

Para um tour mais detalhado, consulte [Visão geral da arquitetura](../architecture/index.md) e [Arquitetura de front-end](../architecture/frontend.md). O fluxo de trabalho de solicitação branch-and-pull reside em [Contribuindo](contributing.md).

## Edição com código do Visual Studio

Você pode editar em seu host com [Visual Studio Code](https://code.visualstudio.com/) enquanto a pilha continua em execução no Docker. Como seu clone é montado em `/opt/omegaup`, um salvamento no host é um salvamento no contêiner - recarregamento a quente e Webpack dentro do contêiner o coletam sem nenhuma etapa de cópia, que é exatamente o atrito que a antiga configuração do Vagrant-plus-WinSCP existia para contornar e não precisa mais.

Duas maneiras de trabalhar, dependendo de quanto você deseja que as próprias ferramentas do VS Code (PHP IntelliSense, o terminal integrado, extensões) sejam executadas no sistema de arquivos do contêiner:

1. **Edite no host, execute no Docker.** Basta abrir seu clone como uma pasta e editar normalmente. Caminho mais simples; seus salvamentos fluem para o contêiner por meio da montagem de ligação.
2. **Anexe o código VS ao contêiner em execução.** Instale a extensão [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) (ou a extensão [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)). Com a pilha (`docker compose up --no-build`), abra a paleta de comandos e escolha **Anexar ao contêiner em execução**, escolha o contêiner frontend (nomeado como `omegaup-frontend-1`; confirme com `docker compose ps`) e, em seguida, **Arquivo → Abrir pasta** em **`/opt/omegaup`**. Agora o terminal e os servidores de linguagem do VS Code são executados *dentro* do contêiner, no mesmo PHP 8.1 e Node que o aplicativo usa.

Adicione as extensões PHP, Vue e ESLint conforme os arquivos que você toca as exigem.

## GitHub OAuth (local "Entrar com GitHub")

Para fazer o botão **Entrar com GitHub** funcionar em **`http://localhost:8001/`**, registre um aplicativo OAuth no GitHub e entregue suas credenciais à sua configuração local.

### 1. Crie o aplicativo OAuth no GitHub

Abra [Configurações do desenvolvedor do GitHub](https://github.com/settings/developers), vá para **Aplicativos OAuth → Novo aplicativo OAuth** e defina:

- **Nome do aplicativo**: qualquer coisa, por exemplo. `omegaUp local`
- **URL da página inicial**: `http://localhost:8001/`
- **URL de retorno de chamada de autorização**: `http://localhost:8001/login?third_party_login=github`

Registre-o, copie o **ID do cliente** e, em seguida, gere e copie o **Segredo do cliente** — o GitHub mostra o segredo apenas uma vez, então pegue-o agora.

### 2. Configure o omegaUp localmente

Coloque as credenciais em **`frontend/server/config.php`**, o arquivo de substituições locais (crie-o se não existir). Este arquivo é apenas para *sua* máquina — nunca envie-o e nunca coloque segredos no `config.default.php` com versão controlada.

```php
<?php
define('OMEGAUP_GITHUB_CLIENT_ID', 'your_real_client_id_here');
define('OMEGAUP_GITHUB_CLIENT_SECRET', 'your_real_client_secret_here');
```
Geralmente, não é necessária uma reinicialização completa do Compose para que um novo PHP `define` tenha efeito, mas se o botão permanecer acinzentado, reinicie o contêiner de front-end uma vez.

!!! falha "Nunca confirme segredos OAuth"
    Reverta ou exclua `config.php` antes de enviar e mantenha seu ID/segredo de cliente em um gerenciador de senhas - se o contêiner for recriado e levar `config.php` com ele, você os desejará à mão. Se o botão de login permanecer inativo, o ID do Cliente está faltando ou errado no `config.php`; se você alterar o host ou a porta, atualize o URL de retorno de chamada no aplicativo GitHub OAuth para corresponder ou o redirecionamento falhará.

Consulte [Segurança → OAuth](../architecture/security.md#oauth-integration) para saber como o login de terceiros se encaixa na plataforma.

## Solução de problemas

Aqui estão os problemas que as pessoas realmente enfrentam, aproximadamente na ordem em que os atingem – primeiro o erro bruto, depois o que ele significa e depois a correção.

### O aplicativo da web não está mostrando minhas alterações!

Você editou um arquivo `.vue` ou `.ts`, salvou, recarregou – e o navegador mostra o antigo. O frontend é servido a partir de um *build* do Webpack, portanto, uma edição não construída fica invisível, não importa quantas vezes você atualize. Reconstrua-o de dentro do contêiner:

```bash
docker compose exec frontend /bin/bash
cd /opt/omegaup && yarn run dev
```
`yarn run dev` executa o Webpack uma vez no frontend; se você estiver iterando e não quiser executá-lo novamente manualmente após cada salvamento, use `yarn dev:watch`, que observa a árvore e a reconstrói conforme as alterações. (No Windows, é exatamente por isso que seu checkout deve estar no sistema de arquivos WSL2 Linux e não no `/mnt/c` — o observador perde eventos de mudança além desse limite.) Se ainda não estiver atualizando após uma compilação bem-sucedida, certifique-se de que os contêineres estejam realmente em execução (`docker compose up --no-build`) e, caso contrário, pergunte em nossos [canais de comunicação] (getting-help.md).

### Meu ambiente de desenvolvimento não aparece :(

**Sintomas**: os logs mostram `Permission denied` ao criar `phpminiadmin` ou gravar em `stuff/venv/`, o contêiner `developer-environment` sai e reinicia em um loop e o site nunca é veiculado em `http://localhost:8001`.

**Causa**: o repositório foi clonado como **root** ou `docker compose` foi executado com `sudo`, portanto o diretório do projeto pertence a `root`. A montagem de ligação mapeia seu diretório host para `/opt/omegaup`, e uma árvore de propriedade do root impede que o usuário não-root do contêiner grave nele - então ele falha, morre e o Compose o reinicia para sempre.

**Consertar**: não tente "consertar" a árvore de propriedade da raiz no local; não vale a pena lutar. Como um usuário normal, clone novamente em seu diretório inicial, certifique-se de ter se adicionado ao grupo `docker` (`sudo usermod -a -G docker $USER`, depois efetue logout e login novamente) e execute **`docker compose` sem `sudo`**. Nunca `sudo git clone`.

### Meu navegador continua forçando HTTPS

Se o seu navegador reescrever `http://localhost:8001` para `https://` e não conseguir se conectar, esse é o comportamento HSTS/HTTPS forçado do navegador, não omegaUp - a instância local fala apenas HTTP simples. Desative a política HTTPS forçada para `localhost` seguindo [este guia](https://hmheng.medium.com/exclude-localhost-from-chrome-chromium-browsers-forced-https-redirection-642c8befa9b).

---

### `git push` falha com um rastreamento do MySQL

Quando você envia push, os ganchos de política do omegaUp executam `stuff/policy-tool.py`, que precisa consultar o banco de dados. Em muitas máquinas, o primeiro push termina com um longo traceback do Python terminando em:

```
Traceback (most recent call last):
  File "/home/ubuntu/dev/omegaup/stuff/policy-tool.py", line 124, in <module>
    main()
  ...
  File "/home/ubuntu/dev/omegaup/stuff/database_utils.py", line 75, in mysql
    return subprocess.check_output(args, universal_newlines=True)
  ...
FileNotFoundError: [Errno 2] No such file or directory: '/usr/bin/mysql'
error: failed to push some refs to 'https://github.com/user/omegaup'
```
Esse `FileNotFoundError: ... '/usr/bin/mysql'` significa que não há binário do cliente `mysql` na máquina que executa o gancho. O problema: `git push` é executado em seu **host**, fora do contêiner, portanto, mesmo que o MySQL 8.0 esteja rodando *no* Docker, o host não tem nenhum cliente para conversar com ele. Instale o cliente **fora do contêiner**:

```bash
sudo apt-get install mysql-client
```
### `git push` falha com "Não é possível conectar ao servidor MySQL local"

Às vezes, o cliente é instalado, mas o push ainda falha, desta vez com um erro de soquete antes do mesmo rastreamento:

```
mysql: [Warning] Using a password on the command line interface can be insecure.
ERROR 2002 (HY000): Can't connect to local MySQL server through socket '/var/run/mysqld/mysqld.sock' (2)
Traceback (most recent call last):
  File "/home/ubuntu/dev/omegaup/stuff/policy-tool.py", line 124, in <module>
    main()
  ...
subprocess.CalledProcessError: Command '['/usr/bin/mysql', '--user=root', '--password=omegaup', 'omegaup', '-NBe', 'SELECT COUNT(*) FROM `PrivacyStatements` WHERE ...']' returned non-zero exit status 1.
error: failed to push some refs to 'https://github.com/user/omegaup'
```
`Can't connect ... through socket '/var/run/mysqld/mysqld.sock'` é a oferta: o cliente está padronizando um **socket Unix local**, mas seu MySQL não é local — está em um contêiner, acessível apenas por **TCP na porta 13306** (publicado do contêiner em `docker-compose.yml`). A correção é entregar ao cliente host uma configuração TCP apontando para essa porta e, em seguida, vinculá-la como o `.my.cnf` padrão, o gancho diz:

```bash
cat > ~/.mysql.docker.cnf <<EOF
[client]
port=13306
host=127.0.0.1
protocol=tcp
user=root
password=omegaup
EOF
ln -sf ~/.mysql.docker.cnf .my.cnf
```
Depois disso, a ferramenta de política se conecta via TCP ao MySQL Dockerizado e o push é executado. Este é o mesmo padrão TCP-config documentado no [Guia de contribuição](contributing.md).

---

### A saída de erros de script `stuff/`

Se você executar um dos scripts `stuff/` diretamente em seu host e obter o mesmo rastreamento `/usr/bin/mysql` mostrado acima, a causa comum é que **você o executou fora do contêiner**. A maioria desses scripts assume as ferramentas e o acesso ao banco de dados que existem apenas dentro do contêiner front-end. Abra um shell no contêiner (`docker compose exec frontend /bin/bash`) e execute-o lá. (Os ganchos `git push` acima são a exceção deliberada - aqueles *fazem* execução no host, e é por isso que eles precisam do cliente MySQL do lado do host e da configuração TCP.)

### Módulos de terceiros ausentes

Se a construção ou os testes falharem, reclamando de módulos ausentes em `frontend/www/third_party/js/`, seus submódulos não serão verificados. Puxe-os para dentro:

```bash
git submodule update --init --recursive
```
### Erros de nó/fio após realizar grandes alterações

Se o Node ou o Yarn começarem a gerar erros logo após você obter um grande aumento de dependência, a imagem de front-end pré-construída pode estar fora de sintonia com o novo `package.json`. Reconstrua:

```bash
docker compose build frontend
docker compose up
```
---

Se você encontrar algo não abordado aqui, registre um problema em [omegaup/deploy/issues](https://github.com/omegaup/deploy/issues) com suas etapas de reprodução e a mensagem de erro exata — o texto do erro é o que nos permite associar seu sintoma a um sintoma conhecido.

## Próximas etapas

- **[Aprenda como contribuir](contributing.md)** — filiais, controles remotos e envio de pull request.
- **[Revise as diretrizes de codificação](../development/coding-guidelines.md)** — as convenções às quais mantemos o código.
- **[Explore a arquitetura](../architecture/index.md)** — como as peças que você acabou de inicializar se encaixam.

## Obtendo ajuda

Se você estiver preso em algo que esta página não cobre:

1. Verifique o [Guia de ajuda](getting-help.md).
2. Pesquise os [problemas do GitHub](https://github.com/omegaup/deploy/issues) existentes.
3. Pergunte em nosso [servidor Discord](https://discord.gg/gMEMX7Mrwe).

---

**Pronto para começar a codificar?** Acesse o [Guia de contribuição](contributing.md) para enviar sua primeira solicitação pull.
