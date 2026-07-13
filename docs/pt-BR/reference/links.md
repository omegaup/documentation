---
title: Links úteis
description: Os repositórios que compõem o omegaUp, onde começar a contribuir e um ponteiro para a API
icon: bootstrap/link
---
# Links úteis

omegaUp não é um programa único - é um punhado de serviços que se comunicam entre si
HTTP, espalhado por vários repositórios. Se você apenas já viu
[`omegaup/omegaup`](https://github.com/omegaup/omegaup) você viu o frontend do PHP e
a API, mas não o Go Grader que realmente compila e executa os envios, nem o git
servidor que armazena problemas como repositórios controlados por versão. Esta página é o mapa: qual repositório
contém o quê, por onde começar se você quiser contribuir e onde a API sempre atual
vidas de referência. Quando um link aponta para o código, ele aponta para o repositório que *possui* esse código,
não o monorepo, então você chega onde a mudança realmente precisa ser feita.

## Os repositórios

Existem três que importam para quase tudo, além de alguns satélites. A razão pela qual
existe divisão é que as peças são escritas em idiomas diferentes e evoluem em
relógios diferentes: o frontend é PHP + Vue e é enviado em cada mesclagem para `main`, enquanto o
grader é Go e é enviado como um binário versionado que o frontend chama pela rede. Manter
esse limite em mente - é por isso que "consertar a fila" e "consertar o formulário de envio" estão presentes
repositórios diferentes.

### omegaup/omegaup — o frontend e a API

[`github.com/omegaup/omegaup`](https://github.com/omegaup/omegaup) é o grande e o
aquele em que você passará a maior parte do tempo. É o back-end do PHP 8.1 (php-fpm por trás do nginx, o
código `\OmegaUp\...` com namespace em
[`frontend/server/src`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src)),
os componentes de arquivo único Vue 2.7 + TypeScript em
[`frontend/www/js/omegaup/components`](https://github.com/omegaup/omegaup/tree/main/frontend/www/js/omegaup/components),
e toda a API REST pública. Todo controlador vive em
[`frontend/server/src/Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers),
e cada método `apiXxx` em um controlador é exatamente um ponto final - então
[`Run.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Run.php)
`apiCreate` *é* `/api/run/create/`. O que este repositório **não** contém é o avaliador, o
runner ou sandbox: quando um envio precisa ser julgado, a classe PHP
[`\OmegaUp\Grader`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Grader.php)
apenas faz uma chamada curl para `OMEGAUP_GRADER_URL` (padrão `https://localhost:21680`) e permite
o serviço Go faz o verdadeiro trabalho.

### omegaup/quark — avaliador, corredor, locutor

[`github.com/omegaup/quark`](https://github.com/omegaup/quark) é o backend propriamente dito, escrito
in Go, e seu próprio README o descreve em três partes:

- **avaliador** — gerencia a fila de execução/envio. Notavelmente, ele *não executa nada*;
  apenas mantém a fila e as mãos trabalham. Quando você POSTA um envio, é isso que
  `\OmegaUp\Grader` está conversando.
- **runner** — solicita ao avaliador novos envios, depois compila e executa o código dentro do
  [omegajail sandbox](https://github.com/omegaup/omegajail) com cada entrada, compara o
  saída para a resposta esperada (executando um validador se o problema precisar de um) e atribui um
  pontuação por caso. É basicamente um frontend bonito e distribuído para o sandbox.
- **emissora** — envia notificações ao vivo para todos em um concurso ou curso: corridas ficando
  classificação, mudança de placares, novos esclarecimentos e assim por diante.

Se você está procurando um bug sobre *por que um veredicto deu errado* ou *por que a fila parou*,
este é o repositório, não o PHP. O sandbox em si é mais um repositório desativado -
[`omegaup/omegajail`](https://github.com/omegaup/omegajail) — porque isolando não confiáveis
o código concorrente é um problema difícil o suficiente para merecer seu próprio projeto.

### omegaup/gitserver — problemas como repositórios git

[`github.com/omegaup/gitserver`](https://github.com/omegaup/gitserver) é o serviço Go que
armazena cada problema como seu próprio repositório git – instruções, casos de teste, validadores, configurações,
tudo versionado. É por isso que editar um problema produz um histórico real de commits que você pode reverter:
o "banco de dados" para o problema *content* é git, não MySQL. O frontend fala com ele sempre que um
o problema é criado ou editado e o executor lê os casos de teste dele durante a avaliação.

### Os satélites

Eles aparecem com menos frequência, mas vale a pena saber que existem:

| Repositório | Para que serve |
|------------|---------------|
| [omegaup/libinterativo](https://github.com/omegaup/libinteractive) | Gera o padrão que permite que um problema seja *interativo* (o código do competidor e o processo do juiz trocam mensagens). Escrito no artigo do jornal IOI de 2015 abaixo. |
| [omegaup/omegajail](https://github.com/omegaup/omegajail) | A caixa de areia que o corredor usa. Isola envios não confiáveis ​​no nível do syscall. |
| [omegaup/implantar](https://github.com/omegaup/deploy) | Scripts de implantação e configuração de produção. |
| [omegaup/problemsetter-toolkit](https://github.com/omegaup/omegaup/wiki) | Ferramentas para solucionar problemas de autoria (consulte o wiki para obter o ponto de entrada atual). |

## Por onde começar a contribuir

O fluxo de trabalho reside no repositório principal e a única fonte da verdade é
[`CONTRIBUTING.md`](https://github.com/omegaup/omegaup/blob/main/CONTRIBUTING.md) — leia
antes de seu primeiro PR, porque as regras de atribuição são aplicadas por automação, não por boa vontade.
Algumas coisas que vale a pena saber com antecedência para não se surpreender:

- **Reivindicar um problema com `/assign`.** Você pode reter até **2 atribuições ativas** por vez,
  e `/assign` só funciona quando o problema foi aberto por alguém com associação de repositório
  `OWNER`, `MEMBER` ou `COLLABORATOR` — esse filtro existe para que o bot de atribuição não entregue
  resolver problemas que usuários aleatórios registraram. Se você é um colaborador iniciante, não pode autoatribuir
  até que você tenha pelo menos um PR mesclado aqui; até então, comente e um mantenedor ajudará.
- **Configure o ambiente antes de qualquer coisa.** O passo a passo completo do Docker — trazendo o
  contêineres, executando os testes, propagando usuários de teste e a solução de problemas para quando o
  o contêiner não inicializa - vive em
  [`frontend/www/docs/Development-Environment-Setup-Process.md`](https://github.com/omegaup/omegaup/blob/main/frontend/www/docs/Development-Environment-Setup-Process.md),
  ou no próprio guia [Configuração de desenvolvimento](../getting-started/development-setup.md) deste site.
- **Siga as diretrizes de codificação.** Elas não são pedantismo de estilo por si só; a meta-regra
  toda a base de código é *explicar por que, não o quê*. Veja
  [Diretrizes de codificação](../development/coding-guidelines.md) aqui ou o código canônico
  [versão wiki](https://github.com/omegaup/omegaup/wiki/Coding-guidelines-(English-version)).

Para o dia-a-dia, estas são as páginas para as quais os mantenedores realmente apontam novos contribuidores:

| Guia | O que cobre |
|-------|----------------|
| [Contribuindo](../getting-started/contributing.md) | O fork → branch → PR loop e por que você nunca se compromete com `main`. |
| [Obtendo ajuda](../getting-started/getting-help.md) | Onde perguntar quando você estiver preso (e o [wiki "Como obter ajuda"](https://github.com/omegaup/omegaup/wiki/How-to-Get-Help)). |
| [Comandos úteis](../development/useful-commands.md) | As invocações exatas de `docker-compose`, lint e teste que você executará todos os dias. |
| [Teste](../development/testing.md) | PHPUnit, Jest e Cypress — como executá-los e como escrever um. |
| [Guia de migração](../development/migration-guide.md) | A migração ao vivo do Vue 2.7 → Vue 3 (a antiga do Smarty → Vue está concluída). |
| [Página inicial do Wiki](https://github.com/omegaup/omegaup/wiki) | O wiki original de notas de trabalho, ainda a fonte mais profunda para casos extremos de configuração. |

E as superfícies do GitHub nas quais você viverá:

| Recurso | Ligação |
|----------|------|
| Rastreador de problemas | [omegaup/omegaup/problemas](https://github.com/omegaup/omegaup/issues) |
| Boas primeiras edições | [Etiqueta `Good first issue`](https://github.com/omegaup/omegaup/labels/Good%20first%20issue) |
| Solicitações pull abertas | [omegaup/omegaup/pulls](https://github.com/omegaup/omegaup/pulls) |
| Código de Conduta | [`CODE_OF_CONDUCT.md`](https://github.com/omegaup/omegaup/blob/main/CODE_OF_CONDUCT.md) |
| Discord (canal principal) | [discord.gg/gMEMX7Mrwe](https://discord.gg/gMEMX7Mrwe) |

## Um ponteiro para a API

Tudo o que o front-end da web faz é chamando a mesma API REST pública que você pode chamar
você mesmo - cada atualização do placar, cada envio, cada login é apenas uma solicitação HTTP para
`/api/...`. As regras são as mesmas para todos eles: HTTP simples GET ou POST, JSON back, **HTTPS
apenas ** (uma chamada HTTP simples obtém um redirecionamento `301`, não um sucesso silencioso, porque cheirar
o tráfego do concurso é um verdadeiro vetor de trapaça), cada URL em `https://omegaup.com/api/` e
autenticação por meio de um token obtido de `user/login` e enviado de volta em um cookie chamado `ouat`.
Uma consequência que vale a pena lembrar: você só pode ter **uma sessão ativa por vez**, então
fazer login programaticamente interromperá a sessão do navegador e vice-versa.

!!! dica "Leia isto primeiro"

    As regras transversais completas – transporte, o token de autenticação `ouat` e o
    Envelope de resposta `status`/`errorcode`/`errorname`/`error` — estão escritos no
    **[Referência de API](api.md)** página, com um exemplo `curl` funcional.

A única coisa que deliberadamente **não** mantemos aqui é uma lista de endpoints mantida manualmente,
porque apodreceria no momento em que alguém editasse um controlador. O autoritário e sempre atual
superfície é *gerada a partir da fonte* por
[`frontend/server/cmd/APITool.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/cmd/APITool.php)
— a mesma ferramenta que emite o cliente frontend digitado
[`api.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/api.ts) e
[`api_types.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/api_types.ts).
Para ver exatamente o que uma chamada aceita e retorna, leia o método `apiXxx` em seu controlador em
[`frontend/server/src/Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers)
em vez de confiar em qualquer mesa.

## Sites oficiais

| Recurso | URL | O que é |
|----------|-----|-----------|
| Plataforma | [omegaup.com](https://omegaup.com) | O juiz ao vivo e o sistema de competição. |
| Organização | [omegaup.org](https://omegaup.org) | A organização sem fins lucrativos, nossa missão e impacto. |
| Blogue | [blog.omegaup.com](https://blog.omegaup.com) | Anúncios, tutoriais, notas de lançamento. |
| Estado | [status.omegaup.com](https://status.omegaup.com) | Status do sistema ao vivo e histórico de incidentes. |

## Formação acadêmicaDois artigos da revista IOI são o pano de fundo confiável sobre por que o sistema é construído da maneira que é
é - vale a pena ler se você quiser a intenção do design por trás da arquitetura, não apenas a atual
código:

- [omegaUp: Cloud-Based Contest Management System](http://www.ioinformatics.org/oi/pdf/v8_2014_169_178.pdf) (IOI Journal, 2014) — o artigo de arquitetura original.
- [libinteractive: A Better Way to Write Interactive Tasks](https://ioinformatics.org/journal/v9_2015_3_14.pdf) (IOI Journal, 2015) — o design por trás de [`omegaup/libinteractive`](https://github.com/omegaup/libinteractive).

O local mais amplo é o [IOI Journal em ioinformatics.org](https://ioinformatics.org/), e
O próprio omegaUp surgiu da [Olimpíada Mexicana de Informática (OMI)](https://www.olimpiadadeinformatica.org.mx/).

## Veja também

- **[Referência da API](api.md)** — as regras transversais para chamar qualquer endpoint.
- **[Interiores do sistema](../architecture/internals.md)** — como uma chamada `run/create` realmente flui do `\OmegaUp\ApiCaller` através de um controlador e sai para a niveladora Go.
- **[Grader Internals](../architecture/grader-internals.md)** e **[Runner Internals](../architecture/runner-internals.md)** — o que acontece dentro do quark quando o frontend entrega um envio.

---

!!! dica "Perdeu um link?"
    Se você souber de um recurso que pertence aqui, [abra um PR](https://github.com/omegaup/omegaup/pulls) nos documentos.
