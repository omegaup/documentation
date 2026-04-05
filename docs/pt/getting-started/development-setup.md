---
title: Configuração do ambiente de desenvolvimento
description: Guia completo para configurar seu ambiente de desenvolvimento local omegaUp
icon: bootstrap/tools
---
# Configuração do ambiente de desenvolvimento

Este guia orientará você na configuração de um ambiente de desenvolvimento local para omegaUp usando Docker.

!!! dica "Vídeo Tutorial"
    Temos um [vídeo tutorial](http://www.youtube.com/watch?v=H1PG4Dvje88) que demonstra visualmente o processo de configuração.

## Pré-requisitos

Antes de começar, certifique-se de ter o seguinte instalado:

- **Docker Engine**: [Instalar Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
- **Docker Compose 2**: [Instalar Docker Compose](https://docs.docker.com/compose/install/linux/#install-the-plugin-manually)
- **Git**: Para clonar o repositório

!!! observe "Usuários WSL"
    Se você estiver usando WSL (subsistema Windows para Linux), siga o [guia oficial de integração WSL do Docker Desktop](https://docs.docker.com/desktop/features/wsl).

### Configuração específica do Linux

Se você estiver executando o Linux, após instalar o Docker, adicione seu usuário ao grupo docker:

```bash
sudo usermod -a -G docker $USER
```
Saia e faça login novamente para que as alterações tenham efeito.

!!! aviso "Git Conhecimento"
    Se você não tiver confiança no uso do Git, recomendamos a leitura [este tutorial do Git](https://github.com/shekhargulati/git-the-missing-tutorial) primeiro.

## Etapa 1: bifurcar e clonar o repositório

1. **Fork do repositório**: Visite [github.com/omegaup/omegaup](https://github.com/omegaup/omegaup) e clique no botão "Fork"

2. **Clone seu garfo**:
   ```bash
   git clone --recurse-submodules https://github.com/YOURUSERNAME/omegaup
   cd omegaup
   ```
3. **Inicializar submódulos** (se necessário):
   ```bash
   git submodule update --init --recursive
   ```
## Etapa 2: iniciar contêineres Docker

### Configuração pela primeira vez

Na primeira execução, extraia as imagens do Docker e inicie os contêineres:

```bash
docker-compose pull
docker-compose up --no-build
```
Isso levará de 2 a 10 minutos. Você saberá que está pronto quando vir uma saída semelhante a:

```
frontend_1     | Child frontend:
frontend_1     |        1550 modules
frontend_1     |     Child HtmlWebpackCompiler:
frontend_1     |            1 module
...
```
### Execuções subsequentes

Após a primeira execução, você pode iniciar contêineres mais rapidamente com:

```bash
docker compose up --no-build
```
O sinalizador `--no-build` evita reconstruir tudo, acelerando significativamente a inicialização.

!!! nota "`docker compose` versus `docker-compose`"
    O Docker Compose V2 usa o comando `docker compose` (com espaço). Instalações antigas podem ter o binário `docker-compose`; ambos funcionam se o seu Docker suportar. Este guia usa `docker compose`.

## Etapa 3: acesse sua instância local

Assim que os contêineres estiverem em execução, acesse sua instância local do omegaUp em:

**http://localhost:8001**

## Etapa 4: acessar o console do contêiner

Para executar comandos dentro do contêiner:

```bash
docker exec -it omegaup-frontend-1 /bin/bash
```
A base de código está localizada em `/opt/omegaup` dentro do contêiner.

## Contas de Desenvolvimento

Sua instalação local inclui contas pré-configuradas:

### Conta de administrador
- **Nome de usuário**: `omegaup`
- **Senha**: `omegaup`
- **Função**: Administrador (privilégios de administrador de sistema)

### Conta de usuário normal
- **Nome de usuário**: `user`
- **Senha**: `user`
- **Função**: usuário regular

### Contas de teste

Para fins de teste, você pode usar estas contas de teste:

| Nome de usuário | Senha |
|----------|----------|
| `test_user_0` | `test_user_0` |
| `test_user_1` | `test_user_1` |
| ... | ... |
| `course_test_user_0` | `course_test_user_0` |

!!! informações "Verificação de e-mail"
    No modo de desenvolvimento, a verificação de e-mail está desabilitada. Você pode usar endereços de e-mail fictícios ao criar novas contas.

## Executando testes localmente

Se você deseja executar testes JavaScript/TypeScript fora do Docker:

### Pré-requisitos

1. **Node.js**: versão 16 ou superior
2. **Yarn**: Gerenciador de pacotes

### Etapas de configuração

1. **Inicializar submódulos Git**:
   ```bash
   git submodule update --init --recursive
   ```
Isso baixa as dependências necessárias:
   - `pagedown` - Editor de redução
   - `iso-3166-2.js` - Códigos de país/região
   - `csv.js` - análise CSV
   - `mathjax` - Renderização matemática

2. **Instalar dependências**:
   ```bash
   yarn install
   ```
3. **Executar testes**:
   ```bash
   yarn test
   ```
### Início rápido (novo clone)

Para um novo clone, use este único comando:

```bash
git clone --recurse-submodules https://github.com/YOURUSERNAME/omegaup
cd omegaup
yarn install
yarn test
```
## Estrutura da base de código

A base de código omegaUp é organizada da seguinte forma:

```
omegaup/
├── frontend/
│   ├── server/
│   │   └── src/
│   │       ├── Controllers/    # Business logic & API endpoints
│   │       ├── DAO/            # Data Access Objects
│   │       └── libs/           # Libraries & utilities
│   ├── www/                    # Frontend assets (TypeScript, Vue.js)
│   ├── templates/              # Smarty templates & i18n files
│   ├── database/               # Database migrations
│   └── tests/                  # Test files
```
Para mais detalhes, consulte a [Visão geral da arquitetura](../architecture/index.md) e a [arquitetura de frontend](../architecture/frontend.md).

O fluxo de contribuição (branches, PRs, remotos) está em [Contribuindo](contributing.md).

## Visual Studio Code com Docker

Você pode editar no host com [Visual Studio Code](https://code.visualstudio.com/) enquanto o Docker executa o stack.

### Extensões recomendadas

- [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) ou [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) para anexar a um contêiner em execução
- Extensões PHP, Vue e ESLint conforme necessário

### Anexar ao contêiner frontend

1. Inicie o ambiente: `docker compose up --no-build` (ou `docker compose up` na primeira vez).
2. No VS Code, use **Attach to Running Container** e escolha o contêiner do frontend (muitas vezes `omegaup-frontend-1`; veja `docker compose ps`).
3. Na janela anexada, abra a pasta **`/opt/omegaup`**.

Você também pode editar o clone no host: o mesmo diretório é montado em `/opt/omegaup`.

!!! dica "Vagrant / SSH legado"
    Se usar VM com [omegaup/deploy](https://github.com/omegaup/deploy), use **Remote - SSH** com a saída de `vagrant ssh-config`, como na [documentação Remote SSH do VS Code](https://code.visualstudio.com/docs/remote/ssh). Para novos colaboradores, prefira Docker quando possível.

## GitHub OAuth (login local com GitHub)

### 1. Criar o OAuth App no GitHub

1. Abra [GitHub Developer Settings](https://github.com/settings/developers).
2. **OAuth Apps → New OAuth App**.
3. Defina **Homepage URL** `http://localhost:8001/` e **Authorization callback URL** `http://localhost:8001/login?third_party_login=github`.
4. Registre e copie **Client ID** e **Client Secret**.

### 2. Configurar o omegaUp

Crie ou edite **`frontend/server/config.php`**:

```php
<?php
define('OMEGAUP_GITHUB_CLIENT_ID', 'your_real_client_id_here');
define('OMEGAUP_GITHUB_CLIENT_SECRET', 'your_real_client_secret_here');
```

!!! falha "Nunca faça commit de segredos OAuth"
    Não envie `config.php` com credenciais. Não use `config.default.php` para segredos.

Consulte também [Segurança → OAuth](../architecture/security.md#oauth-integration).

## Problemas comuns

### O aplicativo da web não está mostrando minhas alterações

Certifique-se de que o Docker esteja em execução:

```bash
docker compose up --no-build
```
Caso o problema persista, peça ajuda nos canais de comunicação da omegaUp.

### Navegador redireciona HTTP para HTTPS

Se o seu navegador continuar mudando `http` para `https` para localhost, você poderá desabilitar as políticas de segurança para `localhost`. [Veja este guia](https://hmheng.medium.com/exclude-localhost-from-chrome-chromium-browsers-forced-https-redirection-642c8befa9b).

### Erro MySQL não encontrado

Se você encontrar esse erro ao enviar para o GitHub:

```
FileNotFoundError: [Errno 2] No such file or directory: '/usr/bin/mysql'
```
Instale o cliente MySQL fora do contêiner:

```bash
sudo apt-get install mysql-client mysql-server
```
Em seguida, configure a conexão MySQL:

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
### Erro de conexão MySQL

Se o MySQL estiver instalado, mas aparecer erro de socket, os hooks em `git push` esperam cliente **TCP** na porta **13306**. Use `~/.mysql.docker.cnf` e o link `.my.cnf` como em [Contribuindo](contributing.md).

### Submódulos Git

```bash
git submodule update --init --recursive
```

### Reconstruir imagem frontend

```bash
docker compose build frontend
docker compose up
```

### Permissões: `phpminiadmin`, `venv` ou loop de reinício

**Causa**: clone ou `docker compose` como **root**.

**Solução**: clone de novo como usuário normal, grupo `docker`, sem `sudo` em `git clone` nem em `docker compose`.

### `policy-tool` / `mysql` ao fazer push

Instale o cliente MySQL no **host** e configure TCP como acima. Ambiente de deploy: [omegaup/deploy/issues](https://github.com/omegaup/deploy/issues).

## Próximas etapas

- **[Aprenda como contribuir](contributing.md)** - Crie ramificações e envie solicitações pull
- **[Revise as diretrizes de codificação](../development/coding-guidelines.md)** - Entenda nossos padrões de codificação
- **[Explore a arquitetura](../architecture/index.md)** - Entenda como o omegaUp funciona

## Obtendo ajuda

Se você encontrar problemas não abordados aqui:

1. Verifique o [Guia de ajuda](getting-help.md)
2. Pesquise [issues existentes no GitHub](https://github.com/omegaup/deploy/issues)
3. Pergunte em nosso [servidor Discord](https://discord.gg/gMEMX7Mrwe)

---

**Pronto para começar a codificar?** Acesse o [Guia de contribuição](contributing.md) para saber como enviar sua primeira solicitação pull!
