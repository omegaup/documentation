---
title: Glossário
description: Terminologia e definições usadas no omegaUp
icon: bootstrap/book
---
# Glossário {#glossary}

Este é o vocabulário que os mantenedores realmente usam na revisão de código, no rastreador de problemas e quando algo quebra às 2h. Deliberadamente, não é um dicionário alfabético de chavões do MVC: as entradas são agrupadas de acordo com o local em que se encontram na vida de um envio, porque é assim que o sistema é construído e como você acabará depurando-o. Quase todos os termos estão vinculados ao símbolo, arquivo ou chave de configuração exato que o implementa, então você pode ler a verdade em vez de confiar nesta página.

Duas coisas que vale a pena internalizar antes de continuar lendo. Primeiro, omegaUp são **dois repositórios que se comunicam por HTTP**, não um: o monorepo PHP ([`omegaup/omegaup`](https://github.com/omegaup/omegaup)) é o frontend, a API e o aplicativo web; o mecanismo de julgamento real - Grader, Runner, Broadcaster e sandbox - reside no repositório Go [`omegaup/quark`](https://github.com/omegaup/quark), com armazenamento de problemas em [`omegaup/gitserver`](https://github.com/omegaup/gitserver). Quando esta página diz que o lado do PHP "chama o Grader", significa um `curl` literal sobre `OMEGAUP_GRADER_URL`. Em segundo lugar, muitos conhecimentos antigos do wiki (HHVM, Smarty, um avaliador de 8 filas nomeadas) estão mortos; onde a implementação de um termo mudou, a entrada diz isso.

---

## O pipeline de envio {#the-submission-pipeline}

Esses são os componentes pelos quais um único envio passa, aproximadamente na ordem em que os toca. Se você leu apenas uma seção, leia esta - é a espinha dorsal de todo o resto.

### Arena {#arena}

A Arena é a IU do concurso e da prática – a tela de painel dividido onde um competidor lê um problema, escreve o código no editor incorporado, envia e assiste ao placar e aos esclarecimentos atualizados ao vivo. **não** é um serviço separado (foi lançado como um para um hipotético "v2" anos atrás e nunca foi dividido); hoje é simples Vue 2.7 rodando no navegador, com um ponto de entrada TypeScript por modo em `frontend/www/js/omegaup/arena/` - `contest_contestant.ts` para um concurso ao vivo, `contest_practice.ts` para [modo de prática] (#practice-mode) e `contest_virtual.ts` para um [concurso virtual] (#virtual-contest). Tudo o que ele faz é uma chamada de API comum: ele envia código para `/api/run/create/`, pesquisa `/api/contest/scoreboard/` e abre um soquete [Broadcaster](#broadcaster) para atualizações push, para que não seja necessário pesquisar cada veredicto. Consulte [Arena](../features/arena.md) para ver o tour voltado para o usuário e [Arquitetura de front-end](../architecture/frontend.md) para saber como os pontos de entrada do Vue são conectados.

### Executar/Enviar {#run-submission}

Uma **submissão** é o que o concorrente envia (código-fonte + idioma + qual problema e, se aplicável, qual concurso); uma **run** é o artefato graduado que retorna. No banco de dados, essas são realmente duas tabelas - `Submissions` contém o código e os metadados, `Runs` contém o [veredicto](#verdict), pontuação, tempo de execução e memória - porque um único envio pode ser avaliado mais de uma vez (um [rejulgamento](#rejudge) produz uma nova execução para o mesmo envio). A coisa toda é criada por `\OmegaUp\Controllers\Run::apiCreate` (`frontend/server/src/Controllers/Run.php`, por volta da linha 415), que é a função mais instrutiva no backend para ler: em uma passagem ele valida que todos os campos obrigatórios estão presentes, que o problema pertence ao concurso, que o [limite de tempo](#time-limit) não expirou, que o usuário não está excedendo a taxa de envio (`Run::$defaultSubmissionGap = 60` segundos entre envios para o mesmo problema por padrão) e que o concurso é público ou o usuário foi convidado explicitamente. Só depois de tudo isso ele é transferido para a niveladora na linha ~573 via `\OmegaUp\Grader::getInstance()->grade($run, trim($source))`. Cada execução é identificada por um `guid` opaco — esse é o ID que você vê nos URLs e passa para `/api/run/status/`.

Um campo que você vai tropeçar: `submit_delay` é *o número de minutos desde a abertura do problema (ou início do concurso) até o envio do envio*, e é exatamente nisso que o placar se transforma em [penalidade](#penalty). É `0` para [prática](#practice-mode) e para envios de problemas públicos fora de qualquer concurso; `submission_deadline` também é `0` quando você não está em um concurso.

### Motoniveladora {#grader}

O Grader é o cérebro da metade julgadora: um serviço Go em [`omegaup/quark`](https://github.com/omegaup/quark) (`cmd/omegaup-grader/`) que possui a fila de execuções pendentes e as distribui para [Runners](#runner). O back-end do PHP nunca toca a fila diretamente - ele apenas fala HTTP com ela por meio de `\OmegaUp\Grader` (`frontend/server/src/Grader.php`), acessando `OMEGAUP_GRADER_URL` (padrão `https://localhost:21680`) em `/run/new/{run_id}/` para enfileirar uma nova execução, `/run/grade/` para forçar um [rejulgamento] (#rejudge), `/broadcast/` para espalhar uma mensagem através do [Broadcaster](#broadcaster) e `/grader/status/` para ler a integridade da fila. Essa carga útil de status (`run_queue_length`, `runner_queue_length`, `runners`, `broadcaster_sockets`, `embedded_runner`) é o que `\OmegaUp\Controllers\Grader::apiStatus` aparece no painel do administrador.

Dois fatos de implementação que importam e contradizem o antigo wiki. Primeiro, o modelo de fila tem **quatro níveis de prioridade, não oito filas nomeadas**: `grader/queue.go` define `QueuePriorityHigh (0)`, `QueuePriorityNormal (1)`, `QueuePriorityLow (2)` e `QueuePriorityEphemeral (3)` com `QueueCount = 4`; um envio normal de concurso entra em `QueuePriorityNormal`, e a camada efêmera é especial porque deliberadamente *não* persiste os resultados no sistema de arquivos (ele apoia o playground "executar este snippet"). Em segundo lugar, o avaliador assume que os corredores podem morrer: o `InflightMonitor` em `grader/queue.go` arma um `connectTimeout` e um `readyTimeout` de **10 minutos cada**, e se um corredor iniciar uma corrida e ficar em silêncio após esse prazo, ele será considerado morto e a corrida será colocada novamente na fila, repetida até `Config.Grader.MaxGradeRetries` vezes antes de ser abandonada. Consulte [Informações internas do avaliador](../architecture/grader-internals.md) para obter a máquina de estado completa.

### Corredor {#runner}

Um Runner é um trabalhador Go (também em `omegaup/quark`, `cmd/omegaup-runner/`) que faz a compilação e execução reais. Ele **puxa** o trabalho em vez de ser empurrado para: ele pesquisa longamente o endpoint `/run/request/` do Grader e, quando é executado, compila a fonte e a executa em cada [caso de teste](#test-case) dentro da [sandbox](#minijail-omegajail), transmitindo os resultados de volta. O melhor modelo mental, direto das notas de design originais, é que o Runner *sabe como compilar, executar e alimentar entradas para um programa, e verificar se está correto - é basicamente uma interface bonita e distribuída para o sandbox.* Muitos Runners se registram em um Grader e são despachados round-robin (não há afinidade hoje, embora ela existisse em um ponto e não fosse difícil adicionar de volta). Se um Runner receber uma corrida, mas não tiver o conjunto de entrada do problema armazenado em cache localmente, ele informará isso e o Grader reenviará a entrada `.zip`; se a compilação falhar, ele exclui os arquivos temporários e retorna o stderr do compilador como um [CE](#verdict). Consulte [Informações internas do corredor](../architecture/runner-internals.md).

### Minijail/omegajail {#minijail-omegajail}

Esta é a sandbox que torna seguro executar C++ de um estranho em seu servidor. A linhagem: **minijail** é o jailer de processo de baixo nível (o binário enviado em `Dockerfile.minijail` como `minijail-xenial-distrib`), e **omegajail** é o invólucro do omegaUp em torno dele - no Runner é `OmegajailSandbox` (`runner/sandbox.go`), que desembolsa para `bin/omegajail` sob um `omegajailRoot` com sinalizadores como `--root`. Ele impõe o [tempo](#time-limit) e os [limites de memória](#time-limit), bloqueia o acesso à rede e confina o sistema de arquivos, portanto, um envio que tenta abrir um soquete, fork-bomb ou ler `/etc/passwd` simplesmente não consegue. Quando um programa tenta uma syscall proibida, o sandbox o mata e a execução volta [RFE](#verdict) (erro de função restrita). Observe que ele reside inteiramente em `omegaup/quark`, não no repositório PHP - executar o grepping no monorepo para `minijail` retorna zero ocorrências por design, porque o frontend nunca o invoca e apenas vê o veredicto. Consulte [Sandbox](../features/sandbox.md).

### Emissora {#broadcaster}

O Broadcaster é o serviço de distribuição em tempo real (Go, `omegaup/quark`, `broadcaster/`). Quando algo que um competidor deveria ver acontece - um [veredicto](#verdict) chega, um [esclarecimento](#clarification) é respondido, o [placar](#scoreboard) muda - o lado do PHP chama `\OmegaUp\Broadcaster` que faz POST para o `/broadcast/` do avaliador, e o Broadcaster envia essa mensagem para todos os clientes conectados relevantes para que o [Arena](#arena) atualiza sem votação. "Relevante" é decidido por filtros em `broadcaster/filter.go`: um `UserFilter`, `ProblemFilter`, `ProblemsetFilter`, `ContestFilter` e um `AllEventsFilter` abrangente, portanto, uma mensagem para o concurso X atinge apenas os soquetes inscritos no concurso X. Ele fala dois transportes (`broadcaster/transport.go`): `WebSocketTransport` e um substituto `SSETransport`. Consulte [Arquitetura da emissora](../architecture/broadcaster.md) e [Atualizações em tempo real](../features/realtime.md).

### GitServer {#gitserver}

Os problemas são armazenados como **repositórios git**, um repositório por problema, e o GitServer ([`omegaup/gitserver`](https://github.com/omegaup/gitserver), Go) é o que os atende e os versiona. Cada edição em uma instrução, caso de teste ou [validador](#validator) é um commit, e é por isso que um problema tem um histórico completo e é por isso que um concurso pode ser fixado em uma versão específica do problema mesmo depois que o autor continua editando (consulte [Controle de versão do problema](../features/problem-versioning.md)). O lado PHP chega em `OMEGAUP_GITSERVER_URL` (padrão `http://localhost:33861`, de `OMEGAUP_GITSERVER_PORT`) autenticado com `OMEGAUP_GITSERVER_SECRET_TOKEN`. Consulte [Arquitetura GitServer](../architecture/gitserver.md).

---

## Veredictos {#verdicts}

### Veredicto {#verdict}

O resultado de uma palavra de uma corrida. A lista canônica e oficial é `VerdictList` em `common/problemsettings.go` em `omegaup/quark`, e é armazenada **classificada do pior para o melhor** - esta ordem é de suporte de carga, porque quando uma submissão é julgada caso a caso, o veredicto final é o veredicto do *pior* caso, então "as piores classificações primeiro" é como o Runner a escolhe:

`JE` → `CE` → `RFE` → `VE` → `MLE` → `RTE` → `TLE` → `OLE` → `WA` → `PA` → `AC` → `OK`

Cada um:

- **`AC` (Aceito)** — todos os casos são corretos dentro dos limites. Aquele que você deseja.
- **`PA` (parcialmente aceito)** — alguns casos/[grupos](#test-group) foram aprovados, outros não, e o [modo de pontuação](#score-mode) concede crédito parcial.
- **`WA` (Resposta errada)** — a saída estava bem formada, mas errada em pelo menos um caso.
- **`OLE` (Limite de saída excedido)** — o programa imprimiu mais do que o [limite de saída](#time-limit); o Runner também gera isso se um programa em uma configuração interativa fizer com que seu pai estoure.
- **`TLE` (Limite de tempo excedido)** — excedeu o [limite de tempo](#time-limit) por caso.
- **`RTE` (Erro de tempo de execução)** — falha: segfault, exceção não detectada, saída diferente de zero, divisão por zero.
- **`MLE` (Limite de memória excedido)** — ultrapassou o [limite de memória](#time-limit).
- **`VE` (Erro do validador)** — o próprio [validador](#validator) personalizado do problema não conseguiu produzir uma pontuação utilizável (um bug do autor do problema, não um bug do concorrente).
- **`RFE` (Erro de função restrita)** — o [sandbox](#minijail-omegajail) eliminou o programa por tentar uma chamada de sistema proibida, por exemplo. tentando abrir um soquete de rede.
- **`CE` (Erro de Compilação)** — não compilou; o stderr do compilador é retornado para que o competidor possa ver o porquê.
- **`JE` (Erro do Juiz)** — culpa do próprio omegaUp: dados de teste incorretos, validador quebrado ou problema de infraestrutura. Se você vir isso, verifique os registros do Grader, não culpe o competidor.
- **`OK`** — um marcador interno, por caso, "este caso correu bem" usado dentro do Runner, não um veredicto final voltado para o usuário.

O veredicto chega a `Runs.verdict` e leva a [Broadcaster](#broadcaster) até a [Arena](#arena). Consulte [Veredictos](../features/verdicts.md) para exemplos práticos de cada um.

---

## Concursos, cursos e seu encanamento compartilhado {#contests-courses-and-their-shared-plumbing}

### Concurso {#contest}

Uma competição cronometrada sobre um conjunto de [problemas](#problem), de propriedade de `\OmegaUp\Controllers\Contest`. Um concurso tem uma política `start_time`/`finish_time` difícil, um [placar](#scoreboard), um [modo de pontuação](#score-mode) e [penalidade](#penalty), um `admission_mode` (público vs somente por convite) e um `window_length` opcional — o relógio por competidor para "você ganha N minutos a partir de quando *você* começa", que retorna `null` quando o concurso não foi configurado dessa forma. Observe que um concurso não armazena seus problemas diretamente; aponta para um [conjunto de problemas](#problemset).

### Curso {#course}

Um contêiner estruturado e orientado para a aula: uma sequência de tarefas, cada uma das quais é um [conjunto de problemas](#problemset), além de alunos, prazos, acompanhamento de progresso e assistentes de ensino opcionais. Propriedade de `\OmegaUp\Controllers\Course`. A divisão mental é que um **concurso é um evento único** e um **curso é uma aula contínua** - mas como ambos agrupam problemas em conjuntos de problemas, eles compartilham quase todo o mecanismo de envio de execução, placar e esclarecimento subjacente.

### Conjunto de problemas {#problemset}

A abstração que permite que concursos e tarefas de cursos reutilizem o mesmo código. Um **conjunto de problemas** é apenas "um conjunto de problemas contra os quais as pessoas se submetem", identificado por `problemset_id`; um concurso *tem* um conjunto de problemas e cada tarefa do curso *é* um conjunto de problemas (`\OmegaUp\Controllers\Problemset`). É por isso que uma [execução](#run-submission) carrega um `problemset_id` em vez de um `contest_id` — a execução não se importa se está sendo enviada para um concurso ou uma tarefa de casa, apenas qual conjunto de problemas a governa. Se você já ficou confuso sobre por que a lógica do concurso e do curso são tão semelhantes, esta é a resposta: eles são o mesmo conjunto de problemas de encanamento com tampas diferentes.

### Esclarecimento {#clarification}

O canal de perguntas e respostas do concurso. Um competidor faz uma pergunta sobre um problema via `\OmegaUp\Controllers\Clarification::apiCreate` (`frontend/server/src/Controllers/Clarification.php`); ele é armazenado na tabela `Clarifications` com um sinalizador `public`. Quando um organizador responde ou o marca como público, o controlador o envia através do `\OmegaUp\Broadcaster` estático para que ele apareça ao vivo na [Arena](#arena) dos solicitantes (ou de todos, se for pública) sem atualização. A bandeira `public` é a nuance importante: um esclarecimento privado vai apenas para aquele que fez a pergunta, um esclarecimento público é transmitido para todo o concurso para que todos vejam a mesma decisão.

### Placar {#scoreboard}

A classificação ao vivo. Construído em `frontend/server/src/Scoreboard.php` e - esta é a parte que as pessoas esquecem - é **fortemente armazenado em cache** no Redis sob chaves distintas para os dois públicos: `CONTESTANT_SCOREBOARD_PREFIX` (o que os jogadores veem, respeitando [congelar](#scoreboard-freeze)) e `ADMIN_SCOREBOARD_PREFIX` (a verdade descongelada para organizadores), cada um com um `..._EVENTS_PREFIX` paralelo para a linha do tempo animada. A classificação é classificada pelo total de pontos e depois pelo total de [penalidade](#penalty), e como a penalidade é agregada entre os problemas depende de `penalty_calc_policy` (`sum` adiciona a penalidade de cada problema; `max` leva apenas a maior). Como é caro recalcular, a Arena escuta os empurrões da [Broadcaster](#broadcaster) em vez de buscar novamente constantemente.

### Penalidade {#penalty}

O tempo de desempate na pontuação estilo ICPC: com pontos iguais, quem acumulou menos penalidade terá classificação superior. **Quando** a contagem da penalidade começa é definida por `penalty_type`, uma enumeração com exatamente quatro valores (`Contest.php`): `contest_start` (minutos contados a partir do início do concurso), `problem_open` (desde quando *aquele competidor* abriu pela primeira vez *aquele problema*), `runtime` (use o tempo real de execução da solução) e `none` (sem penalidade). — corrida de pontuação pura). **Como** ele agrega os problemas é o `penalty_calc_policy` separado (`sum` vs `max`) descrito em [Placar](#scoreboard). O valor bruto por envio é o `submit_delay` da execução; envios errados antes do aceito adicionam penalidade fixa no topo (convencionalmente 20 minutos cada nas regras do ICPC).

### Modo de pontuação {#score-mode}

Como os resultados por caso de um problema são acumulados em um número, definido por `score_mode` com três valores (`Contest.php`): `all_or_nothing` (você obtém nota máxima apenas se cada caso for [AC](#verdict) — ICPC clássico), `partial` (soma os pesos dos casos/[grupos](#test-group) que você passou — IOI clássico), e `max_per_group` (pegue o melhor resultado por grupo e some-os). Isto é o que decide se uma solução meio certa ganha [PA](#verdict) e alguns pontos ou apenas [WA](#verdict) e zero.

### Placar congelado {#scoreboard-freeze}

O mecanismo de suspense: perto do final de uma competição, o [placar] público (#scoreboard) para de atualizar para os competidores enquanto os organizadores continuam vendo as classificações ao vivo - implementado como a divisão entre os caches `CONTESTANT_SCOREBOARD_PREFIX` e `ADMIN_SCOREBOARD_PREFIX`. As inscrições ainda são julgadas normalmente; apenas a *visão* do público é mantida, então a revelação final é dramática e ninguém pode fazer engenharia reversa de sua posição exata para jogar nos últimos minutos.

### Modo de prática {#practice-mode}

Após o término de um concurso (ou sobre qualquer problema público), você pode continuar enviando para aprendizagem sem riscos. Em `Run::apiCreate`, esta é a ramificação `isPractice`: `submit_delay` é forçado a `0` e nenhuma [penalidade](#penalty) é acumulada, e o acesso é bloqueado por `Problems::getPracticeDeadline` em vez do relógio do concurso - o envio após esse prazo é rejeitado. O ponto de entrada da Arena é `contest_practice.ts`. O objetivo é permitir que as pessoas resolvam problemas antigos sem poluir qualquer classificação ao vivo.

### Concurso virtual {#virtual-contest}

Executar novamente uma competição finalizada em relação ao seu relógio *original* para que você possa experimentá-la como se estivesse competindo – os mesmos problemas, a mesma duração, mas mudado para agora, e pontuado em um placar privado que não afeta os resultados históricos reais. Ponto de entrada `contest_virtual.ts`. É a maneira honesta de “levar” uma competição passada para praticar sob pressão em tempo real.

### Bloqueio {#lockdown}

Uma **switch global de somente leitura em todo o site**, não um recurso anti-cheat por concurso. Quando `OMEGAUP_LOCKDOWN` está ativado, `\OmegaUp\Controllers\Controller::ensureNotInLockdown()` lança `ForbiddenAccessException('lockdown')` de cada endpoint mutante, de modo que o site continua servindo leituras, mas recusa gravações – usadas durante migrações ou incidentes. Possui um companheiro `OMEGAUP_LOCKDOWN_DOMAIN` (padrão `localhost-lockdown`). Não confunda isso com recursos de segurança para exames de concurso; este é um kill switch do operador para gravações.

---

## Anatomia do problema {#problem-anatomy}

### Problema {#problem}

A unidade atômica de conteúdo: uma instrução, especificações de entrada/saída, restrições, [casos de teste](#test-case), limites e um [validador](#validator) opcional, armazenado como um repositório git no [GitServer](#gitserver) e de propriedade do lado PHP de `\OmegaUp\Controllers\Problem`. Todo o resto – concursos, cursos, corridas – existe para fazer as pessoas se submeterem aos problemas.

### Caso de teste {#test-case}

Um arquivo de entrada emparelhado com a saída esperada. Um envio será [AC](#verdict) somente se satisfizer todos os casos de teste dentro dos [limites](#time-limit); o [veredicto](#verdict) do pior caso torna-se o veredicto da corrida.

### Grupo de teste {#test-group}

Um pacote nomeado de casos de teste que pontua em conjunto, usado para avaliação no estilo de subtarefa. A convenção de nomenclatura é mecânica e vale a pena conhecer: o grupo de um caso é *tudo antes do primeiro `.` em seu nome* (portanto, `2.a`, `2.b`, `2.c` pertencem todos ao grupo `2`) e sob `all_or_nothing`/`max_per_group` [pontuação](#score-mode) um grupo atribui os seus pontos apenas se todo o grupo estiver satisfeito. Os pesos são normalizados para que somem 1 ou o padrão seja 1/(número de casos) quando não especificado.

### Validador {#validator}

Para problemas com mais de uma resposta correta (qualquer ordenação, tolerância de ponto flutuante, "imprimir qualquer caminho mais curto"), uma comparação de texto simples não funcionará, então o autor envia um programa **validador** que lê a saída do competidor e decide a pontuação. A estratégia de comparação é o [tipo de validador](#validator-type). Se o próprio validador falhar, a execução será [VE](#verdict), não [WA](#verdict) — essa distinção informa de quem é o bug.

### Validador tipo {#validator-type}

Como a saída é verificada. `token` / `token-caseless` compara token por token (opcionalmente ignorando maiúsculas e minúsculas), `token-numeric` compara números dentro de um épsilon (portanto, `1.0000001` corresponde a `1.0`), `literal` exige uma correspondência exata de bytes e `custom` entrega a decisão ao autor [validador](#validator).

### Limite de tempo / Limite de memória / Limite de saída {#time-limit}

Os três limites máximos de recursos que o [sandbox](#minijail-omegajail) impõe por caso. **Limite de tempo** é o tempo de parede/CPU (violá-lo gera [TLE](#verdict)); **limite de memória** é o limite de espaço de endereço em KiB (violá-lo resulta em [MLE](#verdict)); **limite de saída** limita quantos bytes um programa pode imprimir (violá-lo gera [OLE](#verdict)), que existe para que um `while(true) printf(...)` infinito não possa preencher um disco. Estas são configurações por problema; a aplicação real são sinalizadores omegajail em `runner/sandbox.go`, não em PHP.

---

## Blocos de construção de back-end {#backend-building-blocks}

### Controlador {#controller}

As classes PHP que implementam a API e mantêm a lógica de negócios, em `frontend/server/src/Controllers/` no namespace `\OmegaUp\Controllers`. Uma convenção que afeta os recém-chegados: os nomes das classes **descartam o sufixo `Controller`** — o endpoint de execução reside na classe `Run` (`\OmegaUp\Controllers\Run` totalmente qualificado), não em `RunController`; da mesma forma `Contest`, `Problem`, `Clarification`, `Grader`. Os métodos de API pública têm o prefixo `api…` (`apiCreate`, `apiStatus`).

### ApiCaller / ponto de entrada {#apicaller-entrypoint}

Cada solicitação `/api/...` chega a `frontend/www/api/ApiEntryPoint.php`, que `require`s `frontend/server/bootstrap.php` e depois chama `\OmegaUp\ApiCaller::httpEntryPoint()`. `ApiCaller` (`frontend/server/src/ApiCaller.php`) é o despachante: ele analisa a rota, verifica o [token de autenticação](#authentication-token) e invoca o método `api…` do controlador correto. Essa cadeia – arquivo de entrada → bootstrap → ApiCaller → `Controller::apiXxx` – é a porta de entrada para todo o backend. Consulte [Arquitetura de back-end](../architecture/backend.md).

### DAO (objeto de acesso a dados) {#dao-data-access-object}

A camada de acesso a dados gerada. Cada tabela obtém uma base abstrata gerada automaticamente em `frontend/server/src/DAO/Base/` (por exemplo, `Base/Runs.php`, contendo o SQL `INSERT`/`UPDATE` bruto) além de um wrapper público editável manualmente em `frontend/server/src/DAO/` onde residem consultas personalizadas. A divisão existe, portanto, a regeneração do padrão nunca atrapalha suas consultas personalizadas. O acesso é via `mysqli` no MySQL 8.0 (`MySQLConnection.php`). Consulte [Padrões de banco de dados](../development/database-patterns.md).

### VO (Objeto de Valor) {#vo-value-object}

Os objetos de linha digitados que os DAOs movem, em `frontend/server/src/DAO/VO/` (por exemplo, `VO/Runs.php`). Um VO é um registro com propriedades digitadas e um mapa `FIELD_NAMES` – você busca VOs de um DAO, transforma-os e os devolve ao DAO para persistir. Juntos **DAO + VO** são como a base de código evita a escrita manual de strings SQL nos controladores; a página [padrão MVC](../architecture/mvc-pattern.md) tem a imagem completa.

### Token de autenticação {#authentication-token}

A credencial que identifica um usuário em chamadas de API, transportada no cookie `ouat` e validada por [`ApiCaller`](#apicaller-entrypoint). Nos bastidores, esses são tokens PASETO (`paragonie/paseto`), não as strings ad-hoc descritas pelo antigo wiki. Uma chamada não autenticada para um endpoint protegido retorna com um erro de permissão, não um redirecionamento, porque a API deve ser consumida programaticamente.

### Rejulgar {#rejudge}

Executar novamente um [envio](#run-submission) existente para produzir uma [execução](#run-submission) nova — após um [caso de teste](#test-case) inválido ser corrigido, um [validador](#validator) ser corrigido ou alterar os limites. O lado PHP aciona chamando o endpoint `/run/grade/` do Grader; na [fila](#grader) um rejulgado entra com uma prioridade mais baixa para não privar os envios de concursos ao vivo.

---

## Documentação relacionada {#related-documentation}

- **[Informações internas do avaliador](../architecture/grader-internals.md)** — a máquina de estado de fila, despacho e nova tentativa
- **[Runner internals](../architecture/runner-internals.md)** — compilar/executar o pipeline e a chamada do sandbox
- **[Emissora](../architecture/broadcaster.md)** e **[Atualizações em tempo real](../features/realtime.md)** — como as atualizações ao vivo chegam à Arena
- **[GitServer](../architecture/gitserver.md)** — problemas como repositórios git
- **[Arquitetura de back-end](../architecture/backend.md)** e **[padrão MVC](../architecture/mvc-pattern.md)** — controladores, DAO/VO, o ponto de entrada da API
- **[Veredictos](../features/verdicts.md)** — todos os veredictos com exemplos
- **[Sandbox](../features/sandbox.md)** — isolamento minijail/omegajail
- **[Idiomas](languages.md)** — compiladores e chaves de idioma suportados
