---
title: Gerenciando concursos
description: Guia para criar e gerenciar concursos de programação
icon: bootstrap/cog
---
# Gerenciando concursos

Esta página mostra tudo o que você faz como pessoa que *conduz* um concurso - o professor configurando um treino semanal para uma aula, o organizador do clube organizando uma seleção regional, o treinador reproduzindo o IOI do ano passado como uma sessão de treinamento. Traçamos o fluxo real: criar o concurso, pendurar problemas nele, decidir quem entra, ajustar o placar e escolher a modalidade que mais se adapta à sua sala. Cada botão aqui é mapeado para um campo em `\OmegaUp\DAO\VO\Contests` e um ponto final em `\OmegaUp\Controllers\Contest` (`frontend/server/src/Controllers/Contest.php`), portanto, quando a UI ocultar algo, você saberá exatamente qual parâmetro procurar.

## Criando um concurso

O formulário do concurso que você preenche no site é o componente Vue `frontend/www/js/omegaup/components/contest/Form.vue`; quando você o envia, ele faz um POST para `Contest::apiCreate` (`Contest.php:2941`). Dois portões disparam antes que qualquer coisa seja escrita: `Controller::ensureNotInLockdown()` (você não pode criar concursos a partir do host de bloqueio `arena.omegaup.com` – mais sobre isso abaixo) e `ensureMainUserIdentityIsOver13()`, porque a criação do concurso está vinculada a uma conta completa e o omegaUp não permite que identidades menores de 13 anos possuam uma.

A coisa mais surpreendente sobre o `apiCreate` é que **todo concurso nasce privado**, não importa o que você peça. O controlador codifica `'admission_mode' => 'private'` e, se você passar qualquer `admission_mode` diferente de `'private'`, ele lançará `contestMustBeCreatedInPrivateMode` em vez de honrá-lo silenciosamente. Isso é deliberado: você cria o concurso em uma sala silenciosa - adiciona problemas, verifica o relógio, convida um coadministrador - e só *então* torna-o público por meio do `apiUpdate`. Ninguém tropeça em um concurso incompleto.

### Os campos básicos

Estes quatro são a identidade do concurso e são obrigatórios:

- **`title`** — o nome humano mostrado nas listagens (por exemplo, "Selectivo Regional 2026").
- **`alias`** — o slug curto que fica na URL. O concurso pode ser acessado em `/arena/<alias>`, portanto, mantenha-o em letras minúsculas e com URL seguro; `Validators::alias` impõe isso.
- **`description`** — texto livre mostrado na página de introdução do concurso antes da entrada do competidor.
- **`start_time` / `finish_time`** — ambos são carimbos de data/hora. `finish_time` deve ser *estritamente* maior que `start_time` ou `validateCommonCreateOrUpdate` gera `contestNewInvalidStartTime`. Os dois juntos definem a duração do concurso, e essa duração é limitada: `MAX_CONTEST_LENGTH_SECONDS` é `60 * 60 * 24 * 31`, ou seja, **31 dias** para um organizador normal; administradores de sistema recebem `MAX_CONTEST_LENGTH_SYSADMIN_SECONDS` = **60 dias**. Solicite um concurso de 40 dias como professor e você receberá o `contestLengthTooLong` de volta com o `max_days` permitido.

### Os botões de sintonia (e o que eles realmente fazem)

Tudo que vai além do básico tem um padrão sensato, então você pode deixá-los em paz para um primeiro concurso e voltar quando souber o que quer. Os padrões abaixo são aqueles escritos em `VO/Contests`:

- **`window_length`** (minutos `int`, padrão `null`) — este é o cronômetro pessoal estilo USACO. `null` significa "você pode enviar para todo o período entre `start_time` e `finish_time`" — um relógio compartilhado para todos. Defina-o como, digamos, `180`, e cada competidor terá sua própria janela de 180 minutos que começa a contar no momento em que *eles* abrem o concurso. Isso é o que permite que uma turma de 30 pessoas se sente em horários escalonados e ainda assim cada uma tenha as mesmas três horas. Nota `apiCreate` armazena `$r['window_length'] ?: null`, então um `0` volta a ser "sem janela".
- **`submissions_gap`** (`int` segundos, padrão `60`) — a espera mínima que um competidor deve cumprir entre duas submissões em qualquer problema. O padrão 60 existe para atenuar o comportamento de força bruta de "enviar e ver" e para evitar que uma pessoa inunde a fila do juiz; abandone-o para uma prática descontraída, aumente-o para uma seleção de apostas altas.
- **`scoreboard`** (`int` 0–100, padrão `1`) — leia como *a porcentagem do tempo decorrido do concurso durante o qual o placar ao vivo fica visível para os competidores*. `100` significa que a placa está ativa o tempo todo; `0` significa que está escuro durante todo o concurso. Este é o seu placar **congelamento**: configure-o para `80` e a classificação parará de ser atualizada silenciosamente para os 20% finais do concurso, para que o drama da última hora permaneça em segredo. (Consulte a seção [Placar](#the-scoreboard) para saber como isso se compõe com `show_scoreboard_after`.)
- **`points_decay_factor`** (`float`, padrão `0.00`) — quanto o valor de um problema desaparece à medida que o tempo passa, recompensando as soluções antecipadas. `0` significa sem deterioração: um problema vale o mesmo no minuto 1 e no minuto 179. Para calibração, **TopCoder usa `0.7`**. A maioria dos concursos escolares deixa isso em 0.
- **`penalty`** (minutos `int`, padrão `1`) e **`penalty_type`** (enum `'contest_start' | 'problem_open' | 'runtime' | 'none'`) — o mecanismo de desempate. `penalty` é quantos minutos cada envio *rejeitado* adiciona ao seu tempo; `penalty_type` decide o que o relógio mede - minutos desde o início da competição (`contest_start`, a convenção ICPC), minutos desde que *você abriu pessoalmente* esse problema (`problem_open`, que emparelha naturalmente com `window_length`), o tempo de execução real do programa em milissegundos (`runtime`) ou nada (`none`). **`penalty_calc_policy`** (enum `'sum' | 'max'`) então diz se a penalidade do competidor é a soma dos problemas ou apenas o pior.
- **`score_mode`** (enum `'partial' | 'all_or_nothing' | 'max_per_group'`, validado por `ensureOptionalEnum`) — pontuação de uma solução parcialmente correta. `partial` dá crédito proporcional aos casos de teste aprovados; `all_or_nothing` dá nota máxima para um problema somente quando *todos* os casos são AC e zero caso contrário (estilo clássico de olimpíada); `max_per_group` obtém a melhor pontuação alcançada em cada grupo de teste. Há um `partial_score` booleano mais antigo (padrão `true`) que antecede esta enumeração e expressa a mesma intenção parcial versus tudo ou nada.
- **`feedback`** (enum `'none' | 'summary' | 'detailed'`, padrão `'none'`) — quanto o competidor aprende com uma inscrição. `none` esconde totalmente o veredicto (eles se submetem ao estilo IOI final sombrio); `summary` mostra a porcentagem de casos aprovados mais o veredicto do pior caso; `detailed` revela o veredicto caso a caso. As sessões práticas precisam de `detailed`; uma seleção real geralmente precisa de `none` ou `summary`.
- **`show_scoreboard_after`** (`bool`, padrão `true`) — se o placar completo será revelado a todos quando a competição terminar, independentemente do que `scoreboard` fez durante a corrida.
- **`languages`** (filtro opcional) — restringe quais linguagens de programação são permitidas. Deixe `null` para permitir todos os idiomas suportados pelo omegaUp; configure-o para bloquear um concurso para iniciantes, digamos, apenas em Python.
- **`contest_for_teams`** (`bool`, padrão `false`) mais **`teams_group_alias`** — transforme o concurso em um evento de equipe cujos participantes vêm de um grupo de equipes em vez de convites individuais. Este sinalizador altera a forma como você adiciona participantes (veja abaixo), então decida com antecedência.
- **`check_plagiarism`** (`bool`, padrão `false`) — execute o detector de plágio do omegaUp nos envios após o concurso.

## Gerenciando problemas

Um concurso começa vazio; você tem problemas com `Contest::apiAddProblem` (`Contest.php:3461`), que o componente `contest/AddProblem.vue` aciona. Somente um administrador de concurso pode fazer isso — `validateContestAdmin` é executado primeiro — e é **proibido em um concurso virtual** (`forbiddenInVirtual`), já que um concurso virtual é uma repetição congelada de um conjunto de problemas existente, e não um problema novo que você edita.

Dois parâmetros moldam cada adição. **`points`** é `ensureFloat('points', 0, INF)` — qualquer peso não negativo, então você pode fazer com que o problema difícil valha 300 e o aquecimento valha 50. **`order_in_contest`** (padrão `1`) corrige onde o problema aparece na lista. Há um teto rígido: `MAX_PROBLEMS_IN_CONTEST` é **30** (definido em `frontend/server/config.default.php:176`), e o 31º `apiAddProblem` lança `contestAddproblemTooManyProblems`.

Uma sutileza que vale a pena internalizar: adicionar um problema fixa-o em um **commit git específico** desse problema (via `Problem::resolveCommit`, que resolve o parâmetro opcional `commit` ou o commit mestre do problema). Isso congela os dados exatos do teste e a declaração que seus competidores verão, de modo que um autor que edite a versão ao vivo do problema no meio da competição não possa mudar o terreno em um evento em execução. Após a gravação, `apiAddProblem` invalida dois caches – `Cache::CONTEST_INFO` para o alias e o cache do placar via `Scoreboard::invalidateScoreboardCache` – então a alteração aparece imediatamente em vez de exibir uma página de concurso obsoleta. Para resolver um problema, `apiRemoveProblem` é a imagem espelhada.

## Gerenciando Participantes

Como todo concurso é privado até que você diga o contrário, a lista de participantes *é* a lista de controle de acesso. Como você o preenche depende de `admission_mode`, que você define por meio de `apiUpdate` (a enumeração é `'private' | 'public' | 'registration'`):

- **`private`** — somente as identidades que você convidar explicitamente podem entrar. Este é o padrão e a escolha certa para uma sala de aula.
- **`public`** — qualquer pessoa no omegaUp pode entrar sem convite. `is_invited` é o que distingue alguém que você adicionou deliberadamente de alguém que simplesmente entrou em um concurso público, o que é importante quando você lê mais tarde a lista de participantes.
- **`registration`** — os concorrentes *solicitam* acesso e você os aprova. Suas solicitações surgem por meio do `apiRequests`, e você aceita ou rejeita cada uma delas com o `apiArbitrateRequest`. Este é o meio termo para um evento aberto, mas aprovado.Para um concurso privado você convida uma pessoa de cada vez com `Contest::apiAddUser` (`Contest.php:3859`), passando por um `usernameOrEmail`. Ele grava uma linha `ProblemsetIdentities` com `is_invited => true` (e `score`/`time` zerado, `end_time` nulo para que sua janela pessoal não tenha iniciado). Uma pegadinha está aqui: se o concurso foi criado com `contest_for_teams`, `apiAddUser` recusa com `usersCanNotBeAddedInContestForTeams` – um concurso de equipe extrai sua escalação de um grupo, então você usa `apiAddGroup` (ou `apiReplaceTeamsGroup`) em vez de adicionar indivíduos. E uma conveniência: se o concurso estiver no modo `registration`, convidar alguém através do `apiAddUser` também **pré-aceita** sua solicitação de acesso via `preAcceptAccessRequest`, para que ele pule totalmente a fila de solicitações.

Convidar uma turma inteira com um nome de usuário por vez envelhece rapidamente, e é por isso que `apiAddGroup` existe: crie um grupo uma vez (sua lista do "Período 3 CS") e adicione o grupo inteiro a qualquer concurso em uma única chamada. Para entregar as funções de co-organização, `apiAddAdmin` e `apiAddGroupAdmin` concedem direitos de administrador no próprio concurso.

## O placar

As classificações ao vivo são veiculadas pelo `apiScoreboard`, com um feed de evento incremental do `apiScoreboardEvents` que o front end reproduz para animar as mudanças de classificação. Dois campos que você define na criação controlam a visibilidade e eles compõem: **`scoreboard`** (0–100) controla quanto do concurso *em execução* o tabuleiro está ativo — seu congelamento — enquanto **`show_scoreboard_after`** decide se ele será totalmente revelado quando o concurso terminar. Uma configuração comum é `scoreboard: 100, show_scoreboard_after: true` para uma prática transparente, versus `scoreboard: 0, show_scoreboard_after: true` para uma seleção "somente resultados no final". `default_show_all_contestants_in_scoreboard` controla se administradores e não participantes são listados junto com os concorrentes por padrão.

As atualizações chegam em tempo real pelo **Broadcaster** WebSocket em `wss://omegaup.com/events/` — um serviço Go separado no repositório [`omegaup/quark`](https://github.com/omegaup/quark), que não faz parte do back-end do PHP — portanto, um problema resolvido sobe sem ninguém recarregar. Se sua rede estiver bloqueada, esse WebSocket precisa estar acessível (veja a lista de verificação abaixo) ou a placa voltará silenciosamente para uma pesquisa mais lenta. Quando você realiza duas sessões do mesmo evento e deseja uma classificação combinada – uma seção matinal e outra vespertina, digamos – o `apiScoreboardMerge` reúne várias competições em um único placar.

## Modos de concurso

Além dos botões por campo, três modos amplos cobrem quase todos os eventos reais:

**Padrão (relógio compartilhado).** O padrão: um `start_time`, um `finish_time`, `window_length` deixou `null`. Todos competem no mesmo relógio de parede. Este é o formato ICPC/sala de aula.

**Virtual (replay no estilo USACO).** `Contest::apiCreateVirtual` (`Contest.php:2735`) clona um concurso *terminado* em um novo que você pode fazer como um exame simulado - o original já deve ter terminado ou lançará `originalContestHasNotEnded`. Combinado com o `window_length`, é assim que um aluno “dirige” a olimpíada nacional do ano passado às 19h de uma terça-feira e ainda recebe a autêntica pressão do tempo: seu cronômetro pessoal inicia quando ele o abre. Lembre-se de que os problemas em um concurso virtual ficam congelados — `forbiddenInVirtual` bloqueia a edição.

**Lockdown.** Um modo de integridade que você escolhe apenas por *qual nome de host* por meio do qual seus concorrentes se conectam – abordado a seguir, porque em uma escola é realmente uma decisão de networking.

## Realizando um concurso em uma escola (lista de verificação de rede)

Se os participantes estiverem em um **laboratório escolar** ou em uma rede bloqueada, permita **HTTPS (porta 443)** de saída para o omegaUp e os poucos serviços dos quais ele depende. Tudo é HTTPS – uma solicitação para a porta 80 apenas é redirecionada para 443 – então a porta 443 é tudo que você precisa para abrir.

**Obrigatório:**

- **`https://omegaup.com`** — modo de competição padrão.
- **`https://arena.omegaup.com`** — *somente* se você usar intencionalmente o **modo de bloqueio** (abaixo). Se você usar o bloqueio, deverá **bloquear** o `omegaup.com` para os competidores, ou eles podem simplesmente mudar para o host normal e contornar todas as restrições.
- **`https://ssl.google-analytics.com`** — usado pelo site.

**Opcional (cada um degrada uma conveniência se bloqueado, nada quebra):**

- **`https://secure.gravatar.com`** — o avatar no canto superior direito.
- **`https://accounts.google.com`** — "Faça login com o Google."
- **`https://connect.facebook.net`** e **`https://s-static.*.facebook.com`** — "Entrar com o Facebook."

Existe uma regra de firewall não óbvia que salvará seu evento: configure hosts bloqueados para **REJECT/DENY com uma resposta explícita**, nunca **DROP**. Em um DROP, o navegador não recebe resposta e continua esperando. Ele trava por aproximadamente **20 a 30 segundos** por domínio bloqueado antes de desistir e, para uma sala cheia de alunos, a página inteira parece congelada. Uma rejeição explícita falha rapidamente e a IU permanece responsiva.

### Modo de bloqueio (`arena.omegaup.com`)

Aponte os concorrentes para `https://arena.omegaup.com/` em vez do host normal e eles entrarão no **modo de bloqueio**, criado para quando você precisar de garantias mais fortes de que os alunos não poderão transmitir informações uns aos outros por meio da plataforma. Grande parte da funcionalidade do site é deliberadamente desativada e **nenhuma exceção por concurso é possível** — o valor do bloqueio é que ele não pode ser desbloqueado seletivamente. Os recursos mais comumente perdidos durante o bloqueio são:

- **Modo administrador.**
- **Modo de prática.**
- **Visualizando a origem dos envios anteriores** — onde o site normal mostra seu código antigo, o bloqueio mostra uma mensagem de erro.

Se a sua situação realmente precisa de uma das coisas que o bloqueio bloqueia, a resposta não é abrir um buraco nela - é não usar o bloqueio e, em vez disso, conectar-se por meio do `https://omegaup.com`.

### Ambiente do concorrente (laboratório do Windows vs. o juiz)

As inscrições são avaliadas em **Linux**, portanto, qualquer distribuição Linux razoavelmente recente nas máquinas do laboratório corresponde exatamente ao ambiente de avaliação. O Windows é onde vivem os papercuts: o código que extrai o cabeçalho `conio.h` somente do Windows não será compilado no juiz, e as cadeias de ferramentas mais antigas do Windows imprimem `long long` com `%I64d` em vez do `%lld` portátil. Treine seus concorrentes em relação a E/S compatível com POSIX — `%lld` (ou fluxos C++) e cabeçalhos padrão — para que um programa executado no PC do laboratório não morra ao ser enviado.

### Grandes eventos (mais de 100 participantes)

Se você estiver planejando um grande concurso — **100 ou mais** participantes simultâneos — envie um e-mail para **hello@omegaup.com** com bastante antecedência para que a equipe possa confirmar a capacidade para o seu encontro. É uma cortesia que evita uma surpresa ruim no dia.

## Documentação relacionada

- **[Referência da API](../../reference/api.md)** — a referência completa do endpoint por trás de tudo aqui.
- **[Arena](../arena.md)** — a interface que os competidores realmente veem.
- **[Atualizações em tempo real](../realtime.md)** — como o Broadcaster WebSocket conduz o placar ao vivo.
