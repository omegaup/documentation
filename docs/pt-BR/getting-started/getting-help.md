---
title: Obtendo ajuda
description: Aprenda como fazer perguntas de maneira eficaz e obter ajuda da comunidade omegaUp
icon: bootstrap/help-circle
---
# Obtendo ajuda

Você terá perguntas - sobre como o ambiente de desenvolvimento se recusa a aparecer, sobre um rastreamento de pilha nas profundezas do `frontend/server/src/Controllers/`, sobre como o processo de aplicação GSoC realmente funciona no omegaUp. Isso é esperado e perguntar é incentivado. Mas *como* você pergunta decide quão boa será sua resposta e quão rápido ela chegará, então esta página é menos uma lista de links de bate-papo e mais um guia para obter uma boa resposta para sua pergunta. Toda a filosofia por trás disso é uma linha: quanto mais contexto você coloca antecipadamente, menos idas e vindas todos gastam e maior a probabilidade de um voluntário ocupado parar para ajudá-lo.

## Pesquise antes de perguntar

Quase todas as perguntas que um novato responde já foram respondidas antes, muitas vezes várias vezes, muitas vezes na mesma semana durante a temporada GSoC. Portanto, o primeiro passo nunca é “postar a pergunta” – é uma pesquisa de dois minutos, porque a resposta muito provavelmente já está escrita em algum lugar e você a obterá instantaneamente, em vez de esperar horas até que um humano acorde em outro fuso horário.

Vale a pena pesquisar três lugares, aproximadamente nesta ordem de utilidade:

- **Este site de documentação.** Use a caixa de pesquisa na parte superior. Se o seu problema for configuração do ambiente, a página [Configuração de desenvolvimento](development-setup.md) percorre todo o fluxo `docker compose`; se for sobre abrir uma solicitação pull, [Contributing to omegaUp](contributing.md) cobre o fluxo de trabalho git; se for "como *este* subsistema funciona", a seção [Arquitetura](../architecture/index.md) rastreia os caminhos reais do código de ponta a ponta. Se sua pergunta for em formato de API, a [referência de API](../reference/api.md) gerada listará todos os endpoints.
- **Histórico de mensagens do Discord.** Nossa comunidade reside no [servidor omegaUp Discord](https://discord.com/invite/K3JFd9d3wk), e o canal de trabalho para contribuidores é **#dev_training**. A barra de pesquisa do Discord é genuinamente poderosa – pesquise uma palavra-chave do seu erro (`port already allocated`, `wait-for-it`, o nome de um serviço com falha) e muitas vezes você chegará a um tópico onde alguém perguntou exatamente isso, este ano ou no ano passado, com a correção já postada abaixo. É por isso que insistimos que todos postem publicamente (mais sobre isso abaixo): o arquivo pesquisável só existe porque perguntas anteriores foram feitas onde todos pudessem vê-las.
- **Google.** Se sua dúvida for sobre Git, Docker, PHP 8.1, TypeScript ou qualquer coisa que não seja específica do omegaUp, o Google quase sempre superará a espera por um mantenedor. Reserve os canais humanos para as partes específicas do omegaUp que ninguém mais conhece na Internet.

Se você estiver se inscrevendo por meio do Google Summer of Code, leia a página de ideias e perguntas frequentes do GSoC para esse ano (link na seção [Community/GSoC](../community/gsoc/index.md)) *antes* de perguntar sobre o processo. Ele responde diretamente à maioria das perguntas do processo de inscrição, e o FAQ cobre especificamente as recorrentes sobre cronogramas, propostas e como os candidatos são avaliados.

!!! dica "A pesquisa amplia, não restringe"
    Se a sua primeira palavra-chave não retornar nada, tente uma frase *diferente* em vez de uma mais específica - copie a linha distinta da mensagem de erro, elimine as partes que são exclusivas da sua máquina (caminhos, IDs de contêiner) e pesquise no meio. O sinal geralmente é uma ou duas palavras, como `port is already allocated`, e não o rastreamento completo.

## Onde perguntar: #dev_training, publicamente

Quando a pesquisa não der certo, poste sua pergunta no canal **#dev_training** do [servidor Discord](https://discord.com/invite/K3JFd9d3wk). omegaUp coordena no Discord em vez de uma lista de discussão tradicional, então #dev_training *é* a lista de discussão - trate-a como o registro público que ela se tornará.

Duas regras aqui, e ambas existem pela mesma razão – uma questão pública ajuda muito mais pessoas do que uma questão privada:

- **Postagem no canal, nunca em mensagem direta.** Uma DM para um mantenedor atinge exatamente uma pessoa, que pode estar dormindo, ocupada ou simplesmente não saber a resposta. A mesma pergunta em #dev_training chega a todos, então a pessoa mais rápida disponível responde, *e* a resposta se torna pesquisável para a próxima pessoa que atingir sua parede exata. Se você não encontrou nada na pesquisa, é quase certo que você não será a última pessoa que precisará disso.
- **Não marque pessoas específicas.** Nós deliberadamente administramos uma cultura inclusiva, onde qualquer um pode participar, e @-ing um mantenedor sinaliza "isso é entre você e eu" e silenciosamente desencoraja todos os outros de responder. Pergunte à sala, não a uma pessoa.

!!! importante "O GitHub é para bugs confirmados e discussão de design, não para ajuda de configuração"
    A discórdia é onde você fica *desbloqueado*. GitHub é onde as coisas são *rastreadas*. Depois de confirmar um bug reproduzível no código (não é um problema com sua própria máquina), abra um problema em [omegaup/omegaup/issues](https://github.com/omegaup/omegaup/issues) com as etapas de reprodução. Para ideias de recursos e conversas de design mais longas, use [Discussões no GitHub](https://github.com/omegaup/omegaup/discussions). Não abra um problema no GitHub porque `docker compose up` falhou em seu laptop - essa é uma questão #dev_training até que você tenha provado que o bug existe no repositório e não em seu ambiente.

## Como perguntar para que você realmente seja atendido

Uma boa pergunta antecipa tudo o que um ajudante precisa para diagnosticar você sem um único acompanhamento. Perguntas vagas obtêm respostas vagas ou silêncio; perguntas específicas recebem soluções específicas, porque você fez as três primeiras perguntas do auxiliar para elas. Incluir, antecipadamente:

- **O que você estava tentando fazer** e o comando exato que você executou.
- **O que você esperava** que acontecesse versus **o que realmente** aconteceu.
- **A mensagem de erro ou log completo**, copiado e colado como texto (não uma captura de tela do seu terminal – ninguém pode pesquisar ou copiar de uma captura de tela).
- **O que você já tentou**, então ninguém desperdiça uma resposta sugerindo o que você fez há uma hora.
- **Detalhes relevantes do ambiente** quando podem ser importantes: seu sistema operacional e versão, versão do Docker e — especificamente para omegaUp — se os contêineres terminaram a inicialização (a pilha de desenvolvimento pode levar de **2 a 10 minutos** para ficar totalmente ativa na primeira vez, e muitos "está quebrado" acabam sendo "ainda não estava pronto").

### Uma pergunta que é respondida

```markdown
Setting up the dev environment on Ubuntu 22.04. `docker compose up` fails.

Expected: all containers start and I can open the frontend on localhost:8001.
Actual: the frontend container never binds; I get a port-conflict error.

Error:
ERROR: for frontend  Cannot start service frontend: driver failed programming
external connectivity on endpoint omegaup-frontend-1:
Bind for 0.0.0.0:8001 failed: port is already allocated

What I've tried:
- `lsof -i :8001` showed a leftover process; I killed it and re-ran — same error.
- Waited ~10 min in case it was still booting.
- Searched Discord for "port already allocated", found one thread but it was
  about port 13306 (MySQL), not 8001.
```
Essa pergunta nomeia a porta que o omegaUp realmente publica para o frontend (**8001**), mostra o erro literal do Docker, prova que o solicitante já descartou o atraso no tempo de inicialização e um processo obsoleto e até cita o thread quase perdido que encontraram - para que quem o pegar possa ir direto para a causa real, em vez de perguntar novamente o óbvio. Um ajudante que conhece a pilha reconhecerá imediatamente as portas em jogo (frontend em **8001**, MySQL em **13306**, o Go Grader em **21680**) e poderá zerar rapidamente.

### Uma pergunta que é ignorada

```markdown
docker not working help pls
```
!!! fracasso "Por que este morre sem resposta"
    Não há nada para agir: nenhum comando, nenhum texto de erro, nenhum sistema operacional, nenhum sinal do que significa “não está funcionando” ou do que já foi tentado. Responder requer quatro rodadas de "qual sistema operacional?", "qual comando?", "colar o erro", "o que você tentou?" - e a maioria das pessoas simplesmente passa a página em vez de iniciar o interrogatório. A solução não é mais educação; é mais informação.

Para um tratamento mais profundo dessa mesma ideia, recomendamos o pequeno ensaio de Mike Ash [*Obtendo Respostas*](https://www.mikeash.com/getting_answers.html) — é o artigo canônico de como fazer uma pergunta técnica que as pessoas desejam responder.

## Responda ao tópico existente, não inicie um novo

Se sua pesquisa encontrou um tópico *fechado*, mas a resposta não resolveu seu caso, responda nesse tópico em vez de abrir um novo. Duas razões, ambas sobre a próxima pessoa: ele mantém tudo sobre um problema em um só lugar, e significa que quem o corrige o conserta *para registro*, de modo que o leitor que acertar isso em seis meses encontrará a história inteira - sintoma original, tentativas fracassadas, solução funcional - em um único pergaminho, em vez de espalhado por três tópicos sem respostas pela metade. Repostar a mesma pergunta em um novo tópico divide o conhecimento e torna mais provável que ninguém anote a resposta real.

## Fecha o loop quando estiver resolvido

Este é o passo que todos esquecem e é mais importante do que parece. Quando o seu problema for resolvido — quer alguém tenha ajudado você ou você mesmo o tenha solucionado — **volte ao tópico e diga como você o resolveu.**

O motivo é concreto e um pouco egoísta por parte da comunidade: se você deixar o tópico aberto, as pessoas que não viram sua última mensagem continuarão lendo, pensando e gastando seu tempo tentando ajudar alguém que já está perdido. Um tópico não fechado desperdiça silenciosamente exatamente o esforço voluntário pelo qual você estava grato. E quando a próxima pessoa encontrar o mesmo erro, a correção postada será o tópico que a barra de pesquisa entrega a ela. Diga o que funcionou, agradeça a quem ajudou e, se a correção for diferente do sugerido, explique a diferença – esse delta costuma ser a frase mais útil em todo o tópico.

## Ajude a próxima pessoa

Obter ajuda e dar ajuda são o mesmo ciclo visto de dois lados, então, quando você estiver preparado, leia as perguntas que outros colaboradores postam em #dev_training e responda as que puder. Isso não é apenas boa cidadania — **nós levamos isso em consideração ao selecionar candidatos ao GSoC.** Um colaborador que ajuda colegas de maneira confiável demonstra exatamente a colaboração em que o projeto é executado e isso aparece na forma como avaliamos as inscrições. Na prática, você raramente precisa ser um especialista: apontar a alguém a página correta do documento, reconhecer um erro que você enfrentou pessoalmente na semana passada ou apenas confirmar "sim, essa inicialização de 2 a 10 minutos é normal, espere" geralmente é a resposta completa. Explicar algo que você acabou de aprender também é a maneira mais rápida de ter certeza de que você realmente entendeu.

## A versão curta

Se você não se lembra de mais nada: ** pesquise primeiro ** (documentos, histórico do Discord, Google), ** pergunte em #dev_training publicamente ** com seu comando, seu erro literal e o que você já tentou, ** responda aos tópicos existentes ** em vez de iniciar novos, ** publique sua correção ** quando for resolvido para que ninguém continue perseguindo um problema resolvido e ** ajude seus colegas ** porque o arquivo pesquisável que acabou de salvar você foi construído por pessoas fazendo exatamente isso.

---

**Ainda travado?** Entre no [omegaUp Discord](https://discord.com/invite/K3JFd9d3wk) e pergunte em **#dev_training** — com seu erro colado e seu sistema operacional nomeado, você geralmente terá uma resposta antes de terminar seu café.
