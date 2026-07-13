---
title: Solução de problemas
description: Problemas e soluções comuns
icon: bootstrap/tools
---
# Solução de problemas

Esta página coleta as falhas operacionais que as pessoas realmente encontraram ao executar o omegaUp — a pilha não inicializa, a API não consegue acessar o MySQL, suas edições de frontend não aparecem ou o avaliador está inacessível e os envios travam. Para cada um, lideramos com o **erro bruto que você verá**, depois explicamos **o que realmente significa** e, em seguida, fornecemos a **correção** — porque um sintoma que você não consegue interpretar é um sintoma que você não consegue resolver, e o texto do erro é o que nos permite associar seu problema a uma causa conhecida.

Muitos dos tropeços do *tempo de desenvolvimento* (checkout de propriedade da raiz, rastreamentos do MySQL `git push`, redirecionamentos HTTPS forçados, submódulos ausentes) já têm descrições detalhadas em [Configuração do ambiente de desenvolvimento](../getting-started/development-setup.md#troubleshooting). Esta página é a companheira do lado das operações: ela assume que a pilha estava parada em algum ponto e agora está se comportando mal, e faz um link cruzado de volta para a página de configuração sempre que a causa raiz for realmente um erro de configuração.

Antes de você se aprofundar, um modelo mental que economiza muito tempo: **a pilha local não é um processo, é um gráfico de contêineres com uma ordem de inicialização estrita.** Em `docker-compose.yml`, o contêiner `frontend` `depends_on` `mysql`, `gitserver`, `grader` e `redis`; o `grader` espera pelo `mysql:13306` (`wait-for-it mysql:13306`) antes de iniciar; o `runner` espera pelo `grader:11302`; e `gitserver` também espera por `mysql:13306`. Então, quando algo "não aparece", a primeira pergunta é sempre *qual contêiner*, e a segunda é *o que ele estava esperando*. `docker compose ps` responde a primeira; `docker compose logs <service>` responde a segunda.

---

## A pilha não inicializa

**Sintoma**: `docker compose up --no-build` nunca atinge o estado pronto ou um contêiner aparece como `Restarting` / `Exited` em `docker compose ps` em vez de `Up`.

Comece perguntando ao Compose o que ele acha que está em execução e, em seguida, leia o log de qualquer serviço que não esteja íntegro:

```bash
docker compose ps               # which container is Restarting / Exited?
docker compose logs frontend    # then read that specific service's log
docker compose logs grader
```
O sinal normal e íntegro para uma primeira inicialização **não é instantâneo** — uma inicialização a frio leva de **2 a 10 minutos** porque o contêiner `frontend` compila todo o aplicativo Vue 2.7 + TypeScript com Webpack, o MySQL inicializa seu diretório de dados e o avaliador bloqueia no banco de dados. O que indica que ele está realmente pronto é um dump do módulo Webpack terminando com algo como `Child grader: 1131 modules` (a contagem exata varia à medida que a base de código cresce). Se você nunca viu uma inicialização bem-sucedida nesta máquina, não trate uma longa espera como um travamento - consulte a [saída completa do estado de prontidão no guia de configuração] (../getting-started/development-setup.md#step-2-bring-up-the-containers) e aguarde dez minutos completos primeiro.

Depois de isolar o contêiner com falha, os culpados habituais, na ordem aproximada da frequência com que os vemos:

**O contêiner `frontend` reinicia em um loop com `Permission denied`.** Se os logs mostrarem `Permission denied` durante a criação de `phpminiadmin` ou gravação em `stuff/venv/`, a árvore do projeto foi clonada como **root** ou `docker compose` foi executado com `sudo`, portanto, a montagem de ligação em `/opt/omegaup` é de propriedade do root e o usuário não-root do contêiner não pode escreva para ele. Isso é comum o suficiente para ter sua própria seção - [Meu ambiente de desenvolvimento não aparece] (../getting-started/development-setup.md#my-dev-environment-wont-come-up) - e a correção é clonar novamente como um usuário normal em seu diretório inicial, adicionar-se ao grupo `docker` (`sudo usermod -a -G docker $USER`, depois faça logout e login novamente) e nunca `sudo git clone`. Tentar `chown` a árvore de propriedade da raiz de volta ao lugar não vale a pena lutar.

**Um contêiner dependente começa antes do que ele precisa.** Como `grader` e `gitserver` são ambos gate em `wait-for-it mysql:13306`, um MySQL que nunca se torna acessível deixará *eles* presos esperando, o que por sua vez deixa `frontend` esperando em `grader`. Se `docker compose ps` mostrar `grader` ou `gitserver` em estado de espera, não os depure - depure o MySQL primeiro (próxima seção). A ordem importa: consertar a folha raramente conserta a raiz.

**Porta já em uso.** Se um contêiner morrer imediatamente com um erro de ligação como `Error starting userland proxy: listen tcp4 0.0.0.0:8001: bind: address already in use`, alguma outra coisa em seu host já possui essa porta. A pilha publica um conjunto específico e memorável: **`8001`** (HTTP front-end), **`13306`** (MySQL), **`21680`** (API HTTP do avaliador), **`33861`** (gitserver) e **`5672`/`15672`** (RabbitMQ). Encontre e liberte o agressor:

```bash
lsof -i :8001        # or :13306, :21680, :33861
kill -9 <PID>        # or stop whatever service owns it
```
**Você está sem disco ou as imagens estão obsoletas.** Uma compilação em cunha ou um OOM durante a inicialização geralmente remonta a uma raiz de dados completa do Docker. Verifique e recupere:

```bash
docker system df           # how much is images / containers / volumes eating?
docker system prune        # remove stopped containers, dangling images, unused networks
```
Se a falha for "imagem não encontrada" ou uma incompatibilidade após uma grande extração, as imagens fixadas (atualmente `omegaup/dev-php:20231008`, `omegaup/backend:v1.9.35`, `omegaup/runner:v1.9.35`, `omegaup/gitserver:v1.9.13`, `mysql:8.0.34`) precisam ser atualizadas - `docker compose pull` captura o conjunto atual e você só precisa dele na primeira configuração ou quando `up` reclama que uma imagem está faltando ou obsoleta.

Como último recurso – e somente quando você estiver disposto a perder o estado local – você pode apagar e reconstruir do zero. Observe que o `-v` descarta seus **volumes** (incluindo os dados do MySQL e os problemas de armazenamento do git), então você executará novamente o bootstrap do ambiente depois:

```bash
docker compose down -v      # careful: this deletes the MySQL and omegaupdata volumes
docker compose up --no-build
```
---

## MySQL não está acessível

**Sintoma**: a API retorna 500 e o log do PHP ou o navegador mostra um erro de conexão como `SQLSTATE[HY000] [2002]` ou `Can't connect to MySQL server`. Nada que toque no banco de dados funciona, que é basicamente tudo.

O fato de suporte de carga aqui é **onde o MySQL realmente reside e como o PHP se comunica com ele.** O banco de dados é executado no contêiner `mysql` (`mysql:8.0.34`) e o frontend se conecta por TCP — o padrão `OMEGAUP_DB_HOST` é **`mysql:13306`** (consulte `frontend/server/config.default.php`), e `\OmegaUp\MySQLConnection` usa o driver **mysqli** (`mysqli_init()` / `real_connect()`), não DOP. Portanto, "não é possível conectar" quase sempre significa uma de três coisas: o contêiner não está ativo, está ativo, mas ainda está sendo inicializado ou algo está direcionando o cliente para o lugar errado.

Primeiro, confirme se o contêiner está realmente em execução e se a inicialização foi concluída. O MySQL 8.0 funciona de verdade na primeira inicialização, e a API terá a conexão recusada até imprimir sua linha pronta:

```bash
docker compose ps mysql
docker compose logs mysql | tail -50
docker compose logs mysql | grep "ready for connections"
```
Se você ainda não vê o `ready for connections`, essa é a resposta completa - **espere**, não reinicie, porque uma reinicialização apenas executa novamente a mesma inicialização lenta. É também por isso que `grader` e `gitserver` gate em `wait-for-it mysql:13306`: tudo downstream é escrito para assumir que o MySQL vem primeiro.

Se o MySQL *estiver* pronto, mas a API ainda não conseguir acessá-lo, prove a conexão de dentro do contêiner frontend, que é o ambiente em que o PHP realmente é executado:

```bash
docker compose exec frontend /bin/bash
mysql --host=mysql --port=13306 --user=omegaup --password=omegaup omegaup -e "SELECT 1"
```
As credenciais locais padrão são `omegaup`/`omegaup` no banco de dados `omegaup`, correspondendo a `MYSQL_USER`/`MYSQL_PASSWORD`/`MYSQL_DATABASE` no serviço `mysql`. Se esse `SELECT 1` for bem-sucedido dentro do contêiner, mas sua ferramenta falhar no **host**, você se deparará com a confusão mais comum: **o host não tem caminho para MySQL, exceto TCP em `13306`.** Um cliente `mysql` do lado do host padronizado para um soquete Unix falhará com `Can't connect to local MySQL server through socket '/var/run/mysqld/mysqld.sock'` - porque não há servidor local, ele está no Docker. Esse caso exato (ele morde o gancho de política `git push`, que é executado no host) tem uma correção de configuração TCP que pode ser copiada e colada em [git push falha com "Não é possível conectar ao servidor MySQL local"] (../getting-started/development-setup.md#git-push-fails-with-cant-connect-to-local-mysql-server).

Mais duas assinaturas de erro do MySQL que valem a pena interpretar, porque parecem conectividade, mas não são:

- **`ERROR 3024 ... Query execution was interrupted, maximum statement execution time exceeded`.** O contêiner `mysql` é iniciado com `--max_execution_time=30000` (30 segundos), portanto, uma consulta genuinamente lenta é eliminada em vez de ficar suspensa para sempre. Leia isso como "sua consulta está muito lenta", e não como "MySQL está inoperante" - `EXPLAIN` e procure por um índice ausente.
- **`Lock wait timeout exceeded`.** O contêiner também define `--lock_wait_timeout=10` e `--wait_timeout=20`, portanto, uma transação bloqueada em um bloqueio de linha por mais de aproximadamente 10 segundos é abortada deliberadamente, para impedir que um escritor travado prejudique todos. Encontre o titular com `SHOW PROCESSLIST` e deixe-o terminar ou matá-lo, em vez de aumentar o tempo limite.

Se os dados em si estiverem corrompidos após uma falha grave - e não apenas inacessíveis - a opção nuclear é descartar o volume do MySQL e reinicializar. Você perde todos os dados locais, então faça isso apenas em uma caixa de desenvolvimento:

```bash
docker compose down -v
docker compose up -d
```
---

## O aplicativo da web não está mostrando minhas alterações

**Sintoma**: você editou um arquivo `.vue` ou `.ts`, salvou, recarregou o navegador — e ele ainda mostra a IU antiga.

Este confunde as pessoas porque *parece* um bug de cache, mas geralmente não é. **O navegador recebe uma compilação do Webpack, não seus arquivos de origem**, portanto, uma edição que você não reconstruiu fica invisível, não importa quantas vezes você atualize. A UI de cada página é um componente de arquivo único Vue 2.7 em `frontend/www/js/omegaup/components/`, compilado pelo Webpack 5 no pacote que o shell Twig (`frontend/templates/template.tpl`) carrega por meio de suas tags `{% entrypoint %}` / `{% jsInclude %}`. Nada do que você digita chega ao navegador até que o Webpack seja recompilado.

Portanto, a solução é reconstruir, de dentro do contêiner onde reside o conjunto de ferramentas:

```bash
docker compose exec frontend /bin/bash
cd /opt/omegaup && yarn run dev
```
`yarn run dev` executa o Webpack **uma vez** no frontend. Se você estiver iterando e não quiser executá-lo novamente após cada salvamento, use `yarn dev:watch`, que observa a árvore e a reconstrói conforme as alterações. Esta é a mesma orientação do guia de configuração [O aplicativo da Web não mostra minhas alterações!] (../getting-started/development-setup.md#the-web-app-is-not-showing-my-changes) - vale a pena ler lá para obter informações específicas do Windows.

Falando nisso: **no Windows, o observador perde silenciosamente eventos de alteração de arquivo se o seu checkout estiver sob `/mnt/c/...`.** As montagens de ligação do Docker através do limite Windows↔Linux não entregam eventos inotify de forma confiável, então `yarn dev:watch` não vê nada, nunca reconstrói, e você olha para a saída obsoleta sem nenhum erro para explicá-la. A correção não é um sinalizador Webpack – é para manter o repositório dentro do sistema de arquivos WSL2 Linux (por exemplo, `~/omegaup`), conforme abordado no guia de configuração.

Se você reconstruiu com sucesso e ele *ainda* está obsoleto, analise esta pequena lista antes de culpar as ferramentas: confirme se os contêineres estão realmente ativos (`docker compose up --no-build`); faça uma atualização completa (`Ctrl+Shift+R` ou `Cmd+Shift+R` no macOS) ou abra DevTools → Rede → **Desativar cache** para que o navegador pare de servir seu próprio pacote em cache; e se você tocou na assinatura de um controlador PHP, lembre-se de que o cliente API digitado (`api.ts` / `api_types.ts`) é **gerado** — ele não refletirá as alterações do controlador até que seja regenerado pelo `frontend/server/cmd/APITool.php`, não pelo Webpack. Não edite manualmente esses dois arquivos; regenerá-los.

---

## A motoniveladora está inacessível

**Sintoma**: os envios ficam para sempre sem veredicto ou uma ação administrativa que afeta a avaliação retorna 500. No log do PHP, você verá um erro de canal `Grader` — `curl failed` com um URL em `https://localhost:21680` ou a mensagem do terminal `Maximum retry attempts exceeded`.

Aqui está a arquitetura que você deve manter para depurar isso, porque é o que o antigo wiki errou: **o avaliador não faz parte da base de código PHP.** O avaliador, o executor, o transmissor e a sandbox minijail são serviços **Go** separados de [github.com/omegaup/quark](https://github.com/omegaup/quark) (o armazenamento do problema é [github.com/omegaup/gitserver](https://github.com/omegaup/gitserver)), enviados como imagens Docker pré-construídas. O lado PHP é apenas um cliente HTTP fino: `\OmegaUp\Grader` (em [`frontend/server/src/Grader.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Grader.php)) envia solicitações curl para **`OMEGAUP_GRADER_URL`**, cujo padrão é **`https://localhost:21680`** (`frontend/server/config.default.php`). Quando você envia, `\OmegaUp\Controllers\Run::apiCreate` eventualmente chama `\OmegaUp\Grader::getInstance()->grade($run, $source)`, que faz POST para o `/run/new/{run_id}/` do avaliador. Se essa chamada HTTP não puder ser concluída, o envio nunca será avaliado - então "avaliador inacessível" é na verdade "o PHP não pode concluir uma solicitação HTTP para `21680`".

Essa conexão é **autenticada mutuamente por TLS** e é aqui que as configurações locais são interrompidas com mais frequência. A chamada curl em `\OmegaUp\Grader::curlRequestSingle` apresenta um certificado de cliente (`CURLOPT_SSLCERT => /etc/omegaup/frontend/certificate.pem`, `CURLOPT_SSLKEY => /etc/omegaup/frontend/key.pem`), fixa a CA ao mesmo certificado (`CURLOPT_CAINFO`) e - mais importante - verifica o par estritamente (`CURLOPT_SSL_VERIFYPEER => true`, `CURLOPT_SSL_VERIFYHOST => 2`, TLS 1.2). Portanto, um certificado autoassinado ou incompatível não é aprovado silenciosamente; falha no aperto de mão. Se o erro do avaliador `curl failed` mencionar um problema de SSL/certificado em vez de uma conexão recusada, suspeite que os certificados em `/etc/omegaup/frontend/`, e não o avaliador, estejam inativos.

Diagnostice-o na ordem em que a solicitação realmente viaja. Primeiro, o contêiner do avaliador está nivelado e ultrapassou sua própria espera de dependência?

```bash
docker compose ps grader
docker compose logs grader | tail -50
```
Lembre-se do portão `wait-for-it mysql:13306` do avaliador - um avaliador preso esperando é realmente um problema do MySQL, então verifique primeiro se o log mostra que ele nunca foi iniciado. O executor é um contêiner separado que se registra com o avaliador na porta **interna** `11302` (`wait-for-it grader:11302`), que é distinta da API HTTP `21680` com a qual o PHP se comunica; um avaliador que está ativo, mas **não tem corredores** aceitará envios e nunca os terminará, então verifique `docker compose logs runner` para registro e erros também.

Em seguida, pergunte diretamente ao avaliador como ele acha que é a fila. Há um endpoint de primeira classe para isso: **`GET /api/grader/status/`**, servido por `\OmegaUp\Controllers\Grader::apiStatus`, que requer uma sessão de **administrador do sistema** (`\OmegaUp\Authorization::isSystemAdmin`, caso contrário, `ForbiddenAccessException`) e retorna `\OmegaUp\Grader::getInstance()->status()` — um proxy para o `/grader/status/` do próprio aluno. A carga útil (`GraderStatus`) informa exatamente onde reside um backlog:

```json
{
  "grader": {
    "status": "ok",
    "broadcaster_sockets": 0,       // live WebSocket clients on the broadcaster
    "embedded_runner": false,       // is a runner running in-process?
    "queue": {
      "running": [],                // runs currently being judged: [{name, id}]
      "run_queue_length": 0,        // runs waiting to be dispatched
      "runner_queue_length": 0,     // runners idle and waiting for work
      "runners": []                 // names of registered runners
    }
  }
}
```
Leia assim: um `run_queue_length` crescente com uma lista `runners` vazia significa **nenhum corredor está registrado** — o avaliador tem trabalho, mas ninguém para fazê-lo, então olhe para o contêiner do corredor. Um sistema íntegro, mas lento, mostra execuções em movimento através do `running`. Um `runners` vazio *e* zerar tudo geralmente significa que você está conversando com um aluno que acabou de aparecer (ou um falso - veja abaixo).

Quando o PHP realmente não consegue chegar ao `21680`, o cliente não desiste na primeira falha. `\OmegaUp\Grader::curlRequest` **tentativas até 3 vezes** com espera exponencial (`sleep(2^(n-1))`, limitado a 5 segundos), mas *apenas* para erros que classifica como transitórios — a lista atual em `isRetryableError` é `SSL connection timeout`, `HTTP/2 stream`, `SSL routines::unexpected eof`, `INTERNAL_ERROR`, `Connection timed out` e `Operation timed out`. Um `Connection refused` plano (o aluno não escuta) **não** pode ser tentado novamente e falha imediatamente, enquanto um aperto de mão TLS instável recebe três disparos antes de você finalmente ver o `Maximum retry attempts exceeded`. O orçamento por tentativa também é limitado: `CURLOPT_CONNECTTIMEOUT => 5` e `CURLOPT_TIMEOUT => 30`, portanto, uma única chamada suspensa não pode bloquear uma página por mais de aproximadamente 30 segundos. Se você vir `Maximum retry attempts exceeded` nos logs, são três tentativas transitórias com falha - um avaliador intermitentemente insalubre - e não um erro de configuração, que falharia na primeira tentativa.

Uma saída de emergência que vale a pena conhecer para trabalhos apenas de front-end: na verdade, você não precisa de um avaliador ao vivo para desenvolver a maior parte do site. Definir **`OMEGAUP_GRADER_FAKE`** (padrão `false`) faz com que `\OmegaUp\Grader` provoque um curto-circuito em todas as chamadas - `grade()` apenas grava a fonte em `/tmp/{guid}` e retorna, e `status()` retorna um `GraderStatus` vazio, mas bem formado. Se os envios forem "bem-sucedidos", mas nunca produzirem um veredicto real e a fila sempre parecer vazia, verifique se você está executando no modo de avaliação falsa antes de procurar um bug de rede que não existe.

---

## Referência rápida de erros

Estas são as assinaturas que você realmente verá, mapeadas na seção acima que as explica. Ao registrar um problema, cole o texto exato – a string de erro é o que nos permite associar seu sintoma a uma causa conhecida.

| Erro que você vê | O que isso realmente significa | Onde procurar |
|---|---|---|
| `bind: address already in use` (`:8001`, `:13306`, `:21680`) | Outro processo já possui porta publicada | [A pilha não inicializa](#the-stack-wont-boot) |
| `Permission denied` criando `phpminiadmin` / em `stuff/venv/`, loop de reinicialização do contêiner | Repo clonado como root ou `sudo docker compose` – a montagem do bind é de propriedade do root | [Não aparece (configuração)](../getting-started/development-setup.md#my-dev-environment-wont-come-up) |
| `SQLSTATE[HY000] [2002]`/`Can't connect to MySQL server` | Contêiner MySQL inativo, ainda inicializando ou host errado | [MySQL não está acessível](#mysql-is-not-reachable) |
| `Can't connect ... through socket '/var/run/mysqld/mysqld.sock'` | Cliente host usando um soquete Unix; MySQL é somente TCP em `13306` | [git push MySQL correção de soquete (configuração)](../getting-started/development-setup.md#git-push-fails-with-cant-connect-to-local-mysql-server) |
| `maximum statement execution time exceeded` | A consulta excedeu o `--max_execution_time=30000` do contêiner (30s) | [MySQL não está acessível](#mysql-is-not-reachable) |
| `Lock wait timeout exceeded` | Bloqueio de linha realizado após `--lock_wait_timeout=10` (10s), abortado propositalmente | [MySQL não está acessível](#mysql-is-not-reachable) |
| Edições invisíveis após recarregar | O navegador serve a compilação do Webpack, não a sua fonte – precisa de uma reconstrução | [Alterações não exibidas](#the-web-app-is-not-showing-my-changes) |
| Canal `Grader` `curl failed` @ `https://localhost:21680` | PHP não consegue concluir a chamada HTTPS para o avaliador Go | [A motoniveladora está inacessível](#the-grader-is-unreachable) |
| `Maximum retry attempts exceeded` | 3 tentativas transitórias do avaliador, todas com falha – avaliador intermitentemente insalubre | [A motoniveladora está inacessível](#the-grader-is-unreachable) |

---

## Obtendo mais ajuda

Se nada disso resolver:

1. **Pesquise problemas existentes** no [GitHub](https://github.com/omegaup/omegaup/issues) — alguém pode já ter acertado a assinatura exata.
2. **Pergunte no [Discord](https://discord.gg/gMEMX7Mrwe)** e sempre inclua a saída de log relevante; um sintoma sem seu texto de erro é difícil de localizar.
3. **Registre um bug** com suas etapas de reprodução e o erro literal — consulte [Como obter ajuda](../getting-started/getting-help.md) para saber o que constitui um bom relatório.

## Documentação Relacionada

- **[Configuração do ambiente de desenvolvimento](../getting-started/development-setup.md)** — levantando a pilha e a solução de problemas no tempo de configuração para a qual esta página se refere.
- **[Obter ajuda](../getting-started/getting-help.md)** — onde perguntar quando você estiver preso.
- **[Monitoramento](monitoring.md)** — observando a pilha em produção.
- **[Configuração do Docker](docker-setup.md)** — como os contêineres são conectados entre si.
