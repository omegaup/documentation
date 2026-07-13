---
title: Bem-vindo
description: Documentação completa para a plataforma de programação educacional omegaUp
icon: bootstrap/home
---
![Logotipo omegaUp](assets/images/omegaup.png){ width="300" style="max-width: 100%; height: auto; object-fit: contain;" }

# Bem-vindo à documentação do omegaUp

omegaUp é uma plataforma educacional gratuita e de código aberto construída em torno de um juiz on-line automático: você escreve uma solução, envia-a e, em segundos, recebe um veredicto - `AC`, `WA`, `TLE` e o resto - porque um avaliador em sandbox compilou e executou seu código em todos os casos de teste. Dezenas de milhares de estudantes e professores em toda a América Latina usam-no todos os dias para praticar, ensinar e competir, desde o treinamento nas olimpíadas nacionais até as crianças dando os primeiros passos no **Karel**, a linguagem de robô em uma grade que o omegaUp suporta especificamente para que uma criança de dez anos possa aprender a programar antes de saber o que é um loop `for` (juntamente com as linguagens que você esperaria: C, C++, Java, Python, C#, Go, Haskell, Lua, Pascal e Ruby).

Esses documentos são para as pessoas que **constroem e executam** essa plataforma — o colaborador que configura seu ambiente pela primeira vez, o desenvolvedor rastreando como um envio realmente flui através do código e o operador que mantém o site ativo em produção. Se você quiser apenas *usar* omegaup.com para resolver problemas ou realizar um concurso para sua escola, ficará mais feliz no próprio site e no [blog](https://blog.omegaup.com/), onde os recursos mais recentes são anunciados primeiro. Tudo abaixo pressupõe que você queira dar uma olhada nos bastidores.

!!! resumo "O modelo mental de um parágrafo"

    omegaUp **não** é um único programa. Este repositório — [`omegaup/omegaup`](https://github.com/omegaup/omegaup) — é o **frontend do PHP 8.1 e API monorepo** (php-fpm por trás do nginx). Ele serve um shell HTML Twig 3 fino que inicializa um aplicativo de página única Vue 2.7 + TypeScript e expõe todos os recursos como um endpoint REST em `/api/`. Ele **não** compila ou executa seu código. Quando você envia, o back-end do PHP entrega a execução via HTTP para um **serviço Go Grader** completamente separado (o projeto [`omegaup/quark`](https://github.com/omegaup/quark) — avaliador, executor, transmissor e sandbox do minijail), e os dados do problema residem em repositórios git gerenciados por um terceiro serviço, [`omegaup/gitserver`](https://github.com/omegaup/gitserver). Saber em qual desses três repositórios uma coisa vive economiza horas; a maior parte desta documentação está organizada em torno dessa divisão.

## Início rápido

Novo no omegaUp? Comece aqui:

<div class="grid cards" markdown>

- :material-rocket-launch:{ .lg .middle } __[Primeiros passos](getting-started/index.md)__

    ---

    Crie um omegaUp local completo com `docker-compose`, crie seus usuários de teste e faça sua primeira solicitação pull. O ambiente é conteinerizado precisamente para que você não precise instalar manualmente PHP, MySQL, Redis e o graduador Go - o primeiro `docker-compose up` pode levar alguns minutos enquanto as imagens são extraídas e o banco de dados é propagado.

    [:octicons-arrow-right-24: Primeiros passos](getting-started/index.md)

- :material-code-tags:{ .lg .middle } __[Arquitetura](architecture/index.md)__

    ---

    Siga um envio real de ponta a ponta - de `OmegaUp.submit` no navegador, passando por `ApiEntryPoint.php` → `bootstrap.php` → `\OmegaUp\ApiCaller`, até `\OmegaUp\Controllers\Run::apiCreate` e saindo por HTTP para a niveladora Go. Este é o mapa de como os três serviços se encaixam.

    [:octicons-arrow-right-24: Saiba mais](architecture/index.md)

- :material-api:{ .lg .middle } __[Referência da API](reference/api.md)__

    ---

    Cada página que o frontend renderiza é apenas uma chamada autenticada para `/api/...`, então a API pode fazer tudo o que a UI pode. Aprenda as regras transversais – autenticação PASETO `auth_token`, transporte JSON e o envelope de resposta `status`/`error`/`errorcode` – e siga a lista de endpoints sempre atual gerada pela fonte.

    [API de navegação :octicons-arrow-right-24:](reference/api.md)

- :material-tools:{ .lg .middle } __[Guias de desenvolvimento](development/index.md)__

    ---

    As regras internas que mantêm 257 componentes Vue e uma grande base de código PHP coerentes: diretrizes de codificação (sim, "Não use jQuery!"), como executar Psalm, PHPUnit, Jest e Cypress localmente e como os clientes `api.ts` / `api_types.ts` gerados mantêm os tipos de front-end e back-end em sincronia.

    [Guias de leitura do :octicons-arrow-right-24:](development/index.md)

</div>

## O que é omegaUp?

omegaUp existe para tornar a prática de programação deliberada gratuita e automática. Tudo na plataforma é construído em torno do juiz online – o mecanismo que decide, de forma objetiva e em segundos, se uma solução é correta e rápida o suficiente:

- **Solução de problemas** — uma grande biblioteca de problemas de programação, cada um com casos de teste ocultos, um `time_limit` (geralmente `1000` ms) e um `memory_limit` (geralmente `32768` KiB), avaliado automaticamente para que ninguém precise verificar manualmente os envios.
- **Concursos** — realize uma competição de programação cronometrada para sua escola, universidade ou clube, com placar ao vivo. Todo o tráfego do concurso é criptografado por um motivo concreto: em um concurso de programação anterior, alguém farejou a rede para trapacear, então *toda* comunicação com o omegaUp passa por TLS.
- **Cursos** — caminhos de aprendizagem estruturados que agrupam problemas em tarefas, para que o professor possa desenvolver práticas avaliadas para um semestre.
- **Treinamento** — pratique problemas organizados por tópico e dificuldade para qualquer um subir de nível por conta própria.

## Seções de documentação

### :material-school:{ .lg } [Primeiros passos](getting-started/index.md)
Tudo o que você precisa para ir de um novo clone a um site local em execução e uma solicitação pull mesclada: a configuração do `docker-compose`, contas de teste propagadas (o administrador `omegaup`/`omegaup` e um `user`/`user` normal, além dos acessórios `test_user_0..9`), o fluxo de trabalho fork-and-PR e onde obter ajuda quando o contêiner não inicializa.

### :material-sitemap:{ .lg } [Arquitetura](architecture/index.md)
Um mergulho profundo em como os três serviços - o frontend/API PHP, o classificador Go (quark) e o gitserver - realmente movem uma solicitação por meio de código real: a camada do controlador em `frontend/server/src/Controllers/`, a camada de acesso a dados DAO/VO gerada automaticamente no MySQL 8.0 e a transferência HTTP para o avaliador em `OMEGAUP_GRADER_URL` (padrão `https://localhost:21680`).

### :material-api:{ .lg } [Referência da API](reference/api.md)
As regras de transporte, autenticação e envelope de resposta que se aplicam a cada terminal, além da referência de terminal gerada pela origem. Como a lista é gerada a partir dos controladores PHP pelo `frontend/server/cmd/APITool.php`, ela não pode ficar fora de sincronia com o que o servidor realmente aceita.

### :material-code-braces:{ .lg } [Desenvolvimento](development/index.md)
Padrões de codificação, o conjunto de ferramentas de linting e análise estática (Psalm para PHP, `prettier`/ESLint para TypeScript), testes em PHPUnit, Jest 26 e Cypress 15.7, bancos de dados e padrões de migração e como construir componentes de arquivo único Vue sem lutar contra as convenções existentes.

### :material-feature-search:{ .lg } [Recursos](features/index.md)
Internos recurso por recurso: como a [Arena](features/arena.md) oferece concursos, como o [avaliador e corredor](features/sandbox.md) compilam e executam uma submissão dentro do minijail, o que cada [veredicto](features/verdicts.md) significa, como o [versionamento de problemas](features/problem-versioning.md) usa o git e como [emblemas](features/badges.md) e [atualizações em tempo real](features/realtime.md) funcionam.

### :material-server:{ .lg } [Operações](operations/index.md)
Executando omegaUp em produção: configuração nginx e php-fpm, a infraestrutura Redis e RabbitMQ 3 da qual o aplicativo depende, observabilidade por meio de Prometheus e Monolog e os manuais de solução de problemas para quando algo quebrar.

### :material-account-group:{ .lg } [Comunidade](community/index.md)
Como se tornar um contribuidor regular, incluindo a participação de longa data da omegaUp no [Google Summer of Code](community/gsoc/index.md).

## Principais fatos

!!! dica "Educativo por design"
    omegaUp foi desenvolvido para salas de aula e competições, não apenas para prática solo - existem cursos, tarefas e placares de concursos para que um professor possa executar um programa inteiro nele. É por isso que apoia Karel: a plataforma atende os alunos onde eles estão, inclusive aqueles que ainda não escreveram código real.

!!! sucesso "Código aberto, três repositórios"
    Contribuições são bem-vindas em todos os três: o frontend/API PHP em [`omegaup/omegaup`](https://github.com/omegaup/omegaup), a pilha de classificadores Go em [`omegaup/quark`](https://github.com/omegaup/quark) e o armazenamento de problemas em [`omegaup/gitserver`](https://github.com/omegaup/gitserver). Verifique em qual repositório um subsistema reside antes de procurar seu código — o avaliador e o sandbox **não** estão no monorepo PHP.

!!! info "Avaliação multilíngue"
    Os envios podem ser escritos em C, C++, Java, Python, C#, Go, Haskell, Lua, Pascal, Ruby e Karel. O avaliador compila cada um deles em uma sandbox isolada e os executa em todos os casos de teste e, em seguida, pontua.

!!! aviso "Tudo está criptografado"
    Toda a comunicação com o omegaUp e seus subsistemas passa por TLS. Isso não é um teatro de segurança: criptografar tudo minimiza a chance de trapaça em concursos (o tráfego *foi* detectado em uma competição real) e com ferramentas como o Firesheep por aí, fazer certo é barato e inegociável.

## Envolva-se

- **Código de contribuição** — comece com o [Guia de contribuição](getting-started/contributing.md); a equipe de manutenção analisa cada PR de acordo com as [Diretrizes de codificação](development/index.md).
- **Relatar problemas** — abra um em [github.com/omegaup/omegaup/issues](https://github.com/omegaup/omegaup/issues).
- **Google Summer of Code** — omegaUp orienta alunos todos os anos; consulte o [programa GSoC](community/gsoc/index.md).

## Recursos- **Site**: [omegaup.com](https://omegaup.com)
- **Blog**: [blog.omegaup.com](https://blog.omegaup.com)
- **Organização**: [omegaup.org](https://omegaup.org)
- **GitHub**: [github.com/omegaup/omegaup](https://github.com/omegaup/omegaup)

---

**Pronto para começar?** Vá para [Introdução](getting-started/index.md) para abrir um omegaUp local com `docker-compose` e fazer sua primeira alteração.
