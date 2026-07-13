---
title: Recrutamento
description: Como se juntar à equipe de engenharia omegaUp
icon: bootstrap/briefcase
---
# Juntando-se à equipe omegaUp

omegaUp é administrado por voluntários, e toda a plataforma - o frontend PHP 8.1, a UI Vue 2.7, o classificador Go em [omegaup/quark](https://github.com/omegaup/quark), o armazenamento de problemas [gitserver](https://github.com/omegaup/gitserver), os milhares de problemas e cursos - existe porque as pessoas que começaram exatamente onde você decidiu permanecer. Esta página é sobre a segunda etapa: não como abrir sua primeira solicitação pull (o [guia de contribuição](../getting-started/contributing.md) cobre isso de ponta a ponta), mas como passar de contribuidor único a alguém que a equipe de manutenção conhece pelo nome e convida formalmente para a equipe de engenharia. Não há entrevista nem tela de currículo. A única moeda é o trabalho mesclado, e o caminho para isso está totalmente aberto.

## Não há nada para solicitar

O processo de treinamento está aberto a qualquer pessoa que queira – você não envia um e-mail para um mantenedor, preenche um formulário ou espera para entrar. Você clona o repositório, reivindica um problema e começa. A razão pela qual funciona dessa maneira é a mesma razão pela qual todo o projeto está aberto no GitHub: as pessoas que se tornam membros da equipe são aquelas que contribuiriam, quer alguém estivesse assistindo ou não, então o processo simplesmente sai do seu caminho e mede o resultado.

O que isso significa na prática é que “ser recrutado” é um efeito colateral de fazer o trabalho, e não um caminho separado para o qual você muda. Tudo abaixo é o trabalho.

## As funções nas quais você pode crescer

Escrever código de back-end e front-end é a forma mais visível de entrada, mas está longe de ser a única, e a equipe realmente trabalha com todas elas:

- **Desenvolvedores** carregam o código - controladores sob `frontend/server/src/Controllers/`, componentes de arquivo único Vue sob `frontend/www/js/omegaup/components/`, além de revisar as solicitações pull de outras pessoas, o que é por si só uma das maneiras mais rápidas de ganhar a confiança da equipe porque uma boa revisão economiza o recurso mais escasso do mantenedor, seu tempo.
- **Os criadores de problemas** criam os problemas de programação competitiva e seus casos de teste — o conteúdo educacional que o juiz realmente executa. Você não precisa mexer na base de código para ser indispensável aqui.
- **Tradutores** mantêm o omegaUp utilizável em mais de um idioma; a plataforma atende uma comunidade que prioriza o espanhol e abrange muitos países, e o envelope de erro em si está localizado "en el idioma que se tenga definido la cuenta", portanto a tradução é de suporte, não cosmética.
- **Educadores** executam o omegaUp em salas de aula e competições reais, e o ciclo de feedback de um professor real usando cursos com carga horária vale mais do que a maioria das solicitações de recursos.
- **Mentores** ajudam a próxima onda de recém-chegados a se libertar do **#dev_training**, e esta é silenciosamente uma das funções de maior aproveitamento: o arquivo pesquisável do Discord que economizará uma tarde para o próximo colaborador só existe porque alguém respondeu publicamente.

Se você não tem certeza de qual destes é você, tudo bem – a maioria dos frequentadores acaba fazendo dois ou três. Comece com qualquer um em que você possa agir hoje.

## Como se envolver além de um único PR

A mecânica do rastreador de problemas é deliberadamente construída para recompensar o envolvimento *sustentado* em uma única solução, e compreendê-la lhe dirá exatamente como se tornar um cliente regular:

Cada solicitação pull deve estar vinculada a um problema do GitHub que é **atribuído a você** — isso é imposto pela automação, portanto, um PR sem nenhum problema atribuído por trás dele não pode ser mesclado, não importa quão bom seja o código. Você reivindica um problema comentando `/assign` sobre ele (o bot [`takanome-dev/assign-issue-action`](https://github.com/takanome-dev/assign-issue-action) cuida disso para que você nunca espere por um humano) e você pode resolver no máximo **5** problemas de uma vez. Esse limite é o primeiro empurrãozinho em direção à consistência: você deve terminar e entregar, e não acumular o backlog. Depois de reivindicar um problema, você tem **7 dias** para abrir uma solicitação de pull — um **rascunho** PR conta — ou o bot automaticamente cancela a atribuição de você (um lembrete chega aproximadamente na metade do caminho, **3,5 dias**, então uma semana agitada não lhe custará o problema de surpresa). O ritmo que isso cria - reivindicar, enviar dentro de uma semana, reivindicar novamente - *é* o que significa ser um contribuidor regular.

O sistema também possui um marco de confiança integrado que você pode atingir. Depois de ter **10 PRs mesclados** no repositório, os problemas de sua autoria podem ser auto-atribuídos sem contar com seu limite de 5 atribuições ativas — um sinal pequeno, mas real, de que o projeto agora trata você de maneira diferente do que no primeiro dia. Chegar a dez PRs mesclados é uma meta concreta e contável, e é aproximadamente o ponto em que os mantenedores param de pensar em você como um recém-chegado.

Vale a pena conhecer mais dois ciclos de feedback porque é assim que a equipe realmente percebe você. Primeiro, **ajudar colegas em #dev_training conta.** Levamos isso em consideração ao selecionar candidatos ao GSoC - um contribuidor que responde de forma confiável às perguntas de outras pessoas demonstra exatamente a colaboração em que o projeto é executado, e você raramente precisa ser um especialista para fazê-lo (apontar alguém para a página de documento correta ou confirmar "sim, aquela primeira inicialização de 2 a 10 minutos é normal, espere", geralmente é a resposta completa). Em segundo lugar, lembre-se de que os PRs mesclados vão para produção na **implantação no fim de semana**, e não no instante em que são mesclados — portanto, a parte satisfatória, ver sua mudança ao vivo no omegaup.com, chega depois do próximo fim de semana, e ver isso acontecer é parte do que faz as pessoas voltarem.

## O que é necessário para um convite formal

Existe uma barreira concreta para ser formalmente convidado para a equipe de engenharia, e é exatamente o tipo de alvo contável que o projeto prefere a um julgamento subjetivo:

1. Leia a documentação - este site, além do antigo [omegaUp Wiki](https://github.com/omegaup/omegaup/wiki), para conhecer o sistema antes de alterá-lo.
2. Resolva **5** problemas rotulados como [**Bom primeiro problema**](https://github.com/omegaup/omegaup/issues?q=is%3Aissue+is%3Aopen+label%3A%22Good+first+issue%22) — a rampa de acesso selecionada para seus primeiros patches.
3. Resolva **5** problemas rotulados como [**Bom segundo problema**](https://github.com/omegaup/omegaup/issues?q=is%3Aissue+is%3Aopen+label%3A%22Good+second+issue%22) — o próximo nível deliberadamente mais difícil, destinado a provar que você pode navegar pela base de código sem precisar segurar as mãos.

Limpe esses dez e você será **formalmente convidado a se juntar à equipe de engenharia** e **oferecerá uma conta de e-mail `@omegaup.com`** se desejar. A estrutura de duas camadas é intencional: cinco *primeiros* problemas mostram que você pode realizar uma mudança em todo o pipeline (fork, branch, lint com `./stuff/lint.sh`, PR, revisão, mesclagem, implantação de fim de semana) e cinco *segundos* problemas mostram que você pode fazer isso em problemas que ninguém pré-mastigou para você.

!!! note "Algumas pessoas pulam o caminho das dez questões"
    Existe o requisito de construir e demonstrar confiança, para que as pessoas que já a estabeleceram através de outro canal não sejam obrigadas a insistir novamente. Duas exceções permanentes: **estagiários com contrato assinado** e **ex-voluntários com histórico de contribuição reconhecido** que estão retornando. Se você acha que se enquadra em um desses, aumente-o em **#dev_training** em vez de assumir.

## Por onde começar hoje

O primeiro passo concreto mais rápido é o vídeo de configuração e uma boa primeira edição, nesta ordem:

- Assista ao [passo a passo de configuração do ambiente de desenvolvimento](https://www.youtube.com/watch?v=H1PG4Dvje88) e siga o guia escrito [Configuração de desenvolvimento](../getting-started/development-setup.md) — a pilha de desenvolvimento pode levar de **2 a 10 minutos** para ficar totalmente operacional na primeira vez, então não entre em pânico se parecer travada.
- Entre no [servidor Discord](https://discord.com/invite/K3JFd9d3wk) e diga olá em **#dev_training**; é aqui que toda a comunidade de colaboradores se coordena e onde você se desvencilhará mais rápido.
- Escolha um [**Bom primeiro problema**](https://github.com/omegaup/omegaup/issues?q=is%3Aissue+is%3Aopen+label%3A%22Good+first+issue%22), comente `/assign` e abra um rascunho de PR no mesmo dia para garantir sua janela de 7 dias.

## Documentação Relacionada

- **[Contribuindo para omegaUp](../getting-started/contributing.md)** — o fluxo de trabalho completo de pull-request, desde a bifurcação até a implantação no fim de semana.
- **[Configuração de desenvolvimento](../getting-started/development-setup.md)** — faça a pilha funcionar localmente.
- **[Obtendo ajuda](../getting-started/getting-help.md)** — como perguntar em #dev_training para que você realmente receba uma resposta.
- **[Comunidade](index.md)** — o cenário mais amplo: GSoC, canais de comunicação e todas as formas de envolvimento.
