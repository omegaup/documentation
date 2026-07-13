---
title: Guias de desenvolvimento
description: Guias do desenvolvedor, padrões de codificação e práticas recomendadas
icon: bootstrap/code-tags
---
# Quero desenvolver no omegaUp

Obrigado pelo seu interesse em contribuir com o omegaUp. Esta página é a porta de entrada para a base de código: ela informa do que o sistema realmente é feito, em qual repositório cada parte reside, onde na árvore sua mudança provavelmente pertence e qual guia ler a seguir depois de escolher um caminho.

Se você ainda não está familiarizado com o omegaUp como *usuário*, faça isso primeiro. Acesse [omegaup.com](https://omegaup.com/), crie uma conta e resolva um ou dois problemas para que você sinta o ciclo de enviar e obter um veredicto de fora antes de ler o código que o executa. Então [omegaup.org](https://omegaup.org/) irá orientá-lo sobre a organização e as áreas em que atuamos. É muito mais fácil raciocinar sobre `apiCreate` depois de ver seu próprio envio ficar verde.

## O modelo mental de 30 segundos

omegaUp não é um programa, é uma pequena constelação de serviços, e a coisa mais útil para internalizar antes de clonar qualquer coisa é **qual repositório possui o quê**, porque uma mudança na forma como um veredicto é calculado e uma mudança na forma como uma página de concurso é renderizada em bases de código e idiomas completamente diferentes.

- **[omegaup/omegaup](https://github.com/omegaup/omegaup)** é o grande, o PHP + Vue **frontend e API monorepo**. É aqui que você quase certamente deseja começar. Ele renderiza cada página, expõe toda a superfície `/api/`, possui o esquema MySQL e se comunica com todo o resto da rede. Quando as pessoas dizem "a base de código omegaUp" sem qualificação, elas se referem a este repositório.
- **[omegaup/quark](https://github.com/omegaup/quark)** é o **backend de avaliação**, escrito em Go: o *avaliador* (possui a fila de envio e calcula os veredictos), o *runner* (compila e executa o código do usuário), o *broadcaster* (envia atualizações de placar/veredicto ao vivo por meio de WebSockets) e *minijail* (a sandbox que realmente confina um envio em execução). Nada disso está no repositório PHP. O lado do PHP apenas *chama* o avaliador por HTTP.
- **[omegaup/gitserver](https://github.com/omegaup/gitserver)** é um serviço Go que armazena cada problema como seu próprio repositório git, que é como funciona o controle de versão do problema, para que um concurso possa ser fixado em uma revisão exata da declaração de um problema e dos casos de teste.

Uma versão de uma linha para manter em mente: **o monorepo PHP é um aplicativo web bastante distribuído que delega o trabalho perigoso — executar código não confiável — ao classificador Go no quark e armazena problemas como repositórios git no gitserver.** Tudo abaixo é uma consequência dessa divisão.

!!! note "Uma correção na qual o antigo wiki irá te enganar"
    A documentação mais antiga descreve o frontend rodando em HHVM e renderizando com modelos Smarty, e descreve uma migração Smarty→Vue em andamento. Todos os três estão obsoletos. O back-end é **PHP 8.1** padrão (php-fpm por trás do nginx), o shell do lado do servidor é **Twig 3** e a migração Smarty→Vue está *concluída* — o aplicativo atualmente é **257 componentes de arquivo único Vue 2.7** e **414 arquivos TypeScript** contra exatamente **um** modelo de aplicativo (um shell de layout Twig). A única migração ainda ativa é Vue 2 → Vue 3. Se você ler "HHVM" ou "Smarty" em qualquer lugar, trate a reivindicação ao redor como suspeita.

## Visão geral da arquitetura

Estes são os componentes e como eles se conectam. Os codinomes internos temporários são escritos em *itálico*.

| Componente | O que é | Repo / idioma |
| --- | --- | --- |
| *Front-end* | Os controladores e toda a superfície do `/api/`: concursos, problemas, usuários, classificações, placar. Renderiza o site e chama o *Backend* para compilar e executar o código. | [omegaup/omegaup](https://github.com/omegaup/omegaup) — PHP 8.1 + MySQL 8.0 |
| *UX* | Interface de cada página — componentes de arquivo único Vue 2.7 em TypeScript, empacotados pelo Webpack 5 e montados no shell Twig. | [omegaup/omegaup](https://github.com/omegaup/omegaup) — Vue 2.7 + TS 4.4 |
| *Aluno* | Possui a fila de envio, despacha corridas para *Runners*, coleta seus resultados, calcula o veredicto. | [omegaup/quark](https://github.com/omegaup/quark) - Ir |
| *Corredor* | Sabe como compilar, executar e alimentar um envio e verificar se está correto. Essencialmente um frontend bonito e distribuído para *Minijail*. | [omegaup/quark](https://github.com/omegaup/quark) - Ir |
| *Emissora* | Envia atualizações ao vivo (novos veredictos, alterações no placar) para navegadores conectados por meio de WebSockets. | [omegaup/quark](https://github.com/omegaup/quark) - Ir |
| *Minijail* | O sandbox que limita um envio em execução — um fork do sandbox do Linux usado no Chrome OS, reforçado para julgar C/C++/Python/Java/Karel não confiáveis ​​e muito mais. | [omegaup/quark](https://github.com/omegaup/quark) — C |
| *Gitserver* | Armazena cada problema como um repositório git para que os concursos possam fixar uma revisão exata do problema. | [omegaup/gitserver](https://github.com/omegaup/gitserver) — Ir |

Se você deseja um histórico confiável de formato longo, dois artigos foram publicados na revista IOI e ainda são a melhor leitura profunda sobre *por que* o sistema é moldado dessa maneira: [omegaUp: Sistema de gerenciamento de concursos baseado em nuvem e plataforma de treinamento na Olimpíada Mexicana de Informática](http://ioinformatics.org/oi/pdf/v8_2014_169_178.pdf) (Chávez, González, Ponce, 2014) e [libinteractive: A Better Way to Write Interactive Tarefas](https://ioinformatics.org/journal/v9_2015_3_14.pdf) (Chávez, 2015). Para a versão in-repo, leia [Visão geral da arquitetura](../architecture/index.md) e, quando estiver pronto para acompanhar um envio de ponta a ponta, [Interiores do sistema](../architecture/internals.md).

## Siga um pedido real antes de tocar em qualquer coisa

A maneira mais rápida de construir um mapa dessa base de código é rastrear um único envio, porque esse caminho atinge quase todas as camadas que você editará. Quando você clica em “enviar” na Arena, o código é POSTADO em `/api/run/create/`, e aqui é onde ele vai:

1. **`frontend/www/api/ApiEntryPoint.php`** é o ponto de entrada literal. Faz `require_once('../../server/bootstrap.php')` e depois `echo \OmegaUp\ApiCaller::httpEntryPoint()`. Cada solicitação de API que o navegador faz chega aqui primeiro.
2. **`frontend/server/bootstrap.php`** conecta o mundo — configuração, carregamento automático, banco de dados, registro — e passa para **`\OmegaUp\ApiCaller`** (`frontend/server/src/ApiCaller.php`), que analisa a URL, resolve-a para um controlador e despacha para o método `apiXxx` correspondente.
3. Para um envio, esse método é **`\OmegaUp\Controllers\Run::apiCreate`**, em [`frontend/server/src/Controllers/Run.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Run.php) (atualmente próximo à linha 415). Observe que a classe é **`Run`**, não `RunController` — os controladores omegaUp descartam o sufixo `Controller` (`Contest`, `Problem`, `Grader`, `Submission`,…). Dentro, `apiCreate` executa todas as verificações em ordem: se todos os campos obrigatórios estão presentes (problema, concurso, idioma, fonte), se o problema realmente pertence ao concurso, se o limite de tempo do concurso não expirou, se o usuário não está excedendo o limite de taxa de envio e se o concurso é público ou se o usuário foi explicitamente convidado - *antes* de aceitar a corrida. Este é o padrão a ser imitado em qualquer lugar onde você adicionar um endpoint: valide primeiro, em uma varredura legível.
4. Assim que a execução for aceita, `apiCreate` chama **`\OmegaUp\Grader::getInstance()->grade($run, trim($source))`** (atualmente em torno da linha 573). Essa é a fronteira deste repo. **`\OmegaUp\Grader`** (`frontend/server/src/Grader.php`) é um cliente HTTP/curl fino — ele *não* executa nenhum código sozinho. Ele envia a corrida para a niveladora Go em `OMEGAUP_GRADER_URL`, cujo padrão é `https://localhost:21680` (definido em `frontend/server/config.default.php`).
5. A partir daí, a fila, os runners e o minijail vivem em **quark**, em Go, e não estão neste repositório. Quando você quiser entender *essa* metade - as disciplinas da fila, como um runner é despachado, como o minijail finge a ausência de uma rede - leia [Grader Internals](../architecture/grader-internals.md) e [Runner Internals](../architecture/runner-internals.md).

Compreender esse limite - validações e enfileiramentos de PHP, notas Go e sandboxes - informa imediatamente a qual repositório um determinado bug pertence.

## O código e as contas que você obtém

No contêiner de desenvolvimento em execução, tudo está em **`/opt/omegaup`**. A instalação vem com duas contas pré-configuradas para que você não fique preso em uma parede de login na primeira inicialização: **`omegaup` / `omegaup`** (administrador) e **`user` / `user`** (um usuário normal). Sinta-se à vontade para criar quantos mais precisar para teste.

Estes são os diretórios nos quais estamos trabalhando ativamente e *por que* cada um é importante:- **[`frontend/database`](https://github.com/omegaup/omegaup/tree/main/frontend/database)** — o SQL base que cria o esquema, além de todas as migrações adicionadas desde então. Se a sua alteração afetar o formato dos dados, ela chegará aqui como um novo arquivo SQL, não como um arquivo base editado manualmente.
- **[`frontend/server/src`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src)** — todo o PHP, com namespace em `\OmegaUp\` (PSR-4). Este é o servidor. Dentro dele:
    - **[`Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers)** — a lógica de negócios e a superfície `/api/`. Cada método `apiXxx` aqui é um endpoint público. Se você estiver adicionando ou alterando o comportamento que um cliente pode ligar, você está trabalhando aqui.
    - **[`DAO/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/DAO)** — a camada de acesso a dados, dividida deliberadamente. **`DAO/Base/`** contém as classes base geradas automaticamente com o SQL bruto de criação/atualização/exclusão/obtenção para cada tabela, e **`DAO/VO/`** contém os objetos de valor gerados automaticamente (um por formato de linha). *Você não edita manualmente nenhum deles* — eles são gerados. Quando você precisar de consultas personalizadas, adicione-as ao wrapper DAO público no próprio `DAO/`, para que o código gerado possa ser regenerado sem atrapalhar seu trabalho.
    - **[`Template/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Template)** — as extensões personalizadas do Twig 3 (`EntrypointNode`, `JsIncludeNode`, `VersionHashNode` e `Loader`) que permitem que o único shell Twig injete pontos de entrada Vue e hashes de versão que impedem o cache.
- **[`frontend/www`](https://github.com/omegaup/omegaup/tree/main/frontend/www)** — o front-end. Os arquivos TypeScript chamam os controladores e massageiam as respostas; os componentes de arquivo único do Vue renderizam tudo com HTML/CSS. Cada arquivo `.vue` reside em `frontend/www/js/omegaup/`, e a maior parte deles (atualmente 248 de 257) em `frontend/www/js/omegaup/components/`. Dois arquivos aqui são especiais e **não devem ser editados manualmente** — `frontend/www/js/omegaup/api.ts` e `api_types.ts` ambos abertos com `// generated by frontend/server/cmd/APITool.php. DO NOT EDIT.` Eles são a ponte digitada entre PHP e TypeScript: `APITool.php` lê os tipos de Salmo dos controladores e emite o TS correspondente, então o frontend chama a API de uma forma totalmente verificada por tipo. Altere a forma de um controlador, execute novamente o `APITool.php` e os tipos seguem.
- **[`frontend/tests`](https://github.com/omegaup/omegaup/tree/main/frontend/tests)** — os testes do controlador PHPUnit. Existem também testes de unidade Jest localizados com componentes e especificações ponta a ponta do Cypress em `cypress/e2e/`.
- **[`frontend/templates`](https://github.com/omegaup/omegaup/tree/main/frontend/templates)** — os arquivos de internacionalização (inglês, espanhol, português) e `template.tpl`, o único shell Twig que envolve todas as páginas.

## Escolha um caminho em

Para onde você vai a partir daqui depende do que você deseja mudar.

- **Trabalho de front-end/UI** — uma página, um componente, um formulário. Você está morando em `frontend/www/js/omegaup/components/` escrevendo SFCs Vue 2.7 em TypeScript, estilizado com Bootstrap 4.6 + bootstrap-vue 2.21. Leia [Componentes](components.md), e se quiser construir um componente isoladamente, o Storybook está configurado (`yarn storybook`, na porta 6006). Uma regra rígida inicial: **não use jQuery** — este é um aplicativo Vue, faça-o do jeito Vue.
- **Trabalho de backend/API** — um novo endpoint, uma verificação de permissão, uma consulta. Você está no `frontend/server/src/Controllers/` e na camada DAO. Leia a [Arquitetura de backend](../architecture/backend.md), o [padrão MVC](../architecture/mvc-pattern.md) que seguimos e os [Padrões de banco de dados](database-patterns.md) para usar a divisão DAO/VO corretamente em vez de escrever SQL bruto em um controlador.
- **O pipeline de avaliação** — como o código é compilado, colocado em sandbox ou pontuado. Esse trabalho está nos repositórios **quark** e **gitserver** Go, não aqui. Comece com [Modern Internals](../architecture/grader-internals.md), [Runner Internals](../architecture/runner-internals.md) e [Sandbox](../features/sandbox.md).
- **Veredictos, concursos, problemas como conceitos de domínio** — leia a seção [Recursos](../features/index.md) e a [Referência de veredictos](../features/verdicts.md) para saber o que `AC`, `TLE`, `MLE` e amigos realmente significam antes de tocar no código que os emite.

## Antes de escrever uma linha: configuração, testes e regras

Três coisas não são negociáveis e cada uma tem seu próprio guia:

1. **[Configure seu ambiente](../getting-started/development-setup.md)** — desenvolvemos em Docker. Windows e Ubuntu são os caminhos mais conhecidos; O macOS funciona, mas precisa de configuração extra. Seu checkout é montado no contêiner em `/opt/omegaup`, o MySQL 8.0 escuta na porta `13306` e o avaliador em `21680`.
2. **[Leia as diretrizes de codificação](coding-guidelines.md)** — trata-se de julgamento fundamentado de engenharia, não de estilo arbitrário. A meta-regra de suporte: os comentários devem explicar *por que*, não *o quê*. Um representante para lhe dar uma ideia - cada parâmetro `undefined`/`null` dobra as combinações com as quais uma função pode ser chamada e isso cresce exponencialmente, portanto, mantenha a contagem de parâmetros anuláveis ​​**abaixo de 10**. Delegamos a aplicação mecânica a ferramentas (Psalm, PHP_CodeSniffer, Prettier, ESLint, yapf/flake8/mypy no lado Python); execute `./stuff/lint.sh validate` antes de pressionar e ele lhe dirá o que corrigir.
3. **[Escrever testes](testing.md)** — toda alteração de funcionalidade vem com testes, e eles devem estar 100% verdes antes de você confirmar. PHPUnit para controladores, Jest para componentes, Cypress para fluxos ponta a ponta. Execute o pacote com `stuff/runtests.sh`.

Quando sua alteração estiver pronta, siga [Como fazer uma solicitação pull](../getting-started/contributing.md). Uma coisa que vale a pena internalizar desde o início, porque é o erro que os novos contribuidores cometem primeiro: depois de fazer o fork, mantenha seu `main` sincronizado com o `main` do omegaUp e **nunca se comprometa diretamente com ele** - `main` reflete o upstream aprovado pela revisão, portanto, se `git push upstream` falhar, significa que você se comprometeu com `main` por acidente. (A recuperação é `git push upstream -f`, mas a solução real é ramificar para cada alteração.)

## Decisões de design que vale a pena conhecer

Alguns princípios permeiam todo o sistema, e conhecer o raciocínio evita que você “conserte” algo que é deliberado:

- **Criptografar tudo.** *Toda* a comunicação com o omegaUp e entre seus subsistemas é criptografada, de cliente para servidor e de componente para componente. Este não é um dogma de segurança abstrato - em um concurso de programação real, alguém sentou-se e farejou o tráfego, e entre isso e os ataques do tipo Firesheep, a barreira para fazer isso é baixa o suficiente para que não haja desculpa para não fazê-lo. O avaliador é contatado por HTTPS pelo mesmo motivo.
- **Minimizar senhas; identidade federada.** Apoiamos-nos no OAuth2 / OpenID (Facebook, GitHub) porque cada senha que você *não* armazena é aquela que você não pode vazar, e um usuário deve ser capaz de vincular múltiplas identidades - um aluno que se inscreveu como `user@email.com` deve ser capaz de provar que também possui `a0001@school.mx` e mesclar as duas contas.
- **Mantenha os componentes desacoplados.** Espera-se que algumas responsabilidades do *Frontend* migrem para o *Arena* ao longo do tempo, para que as peças sejam mantidas tão independentes quanto possível, em vez de firmemente soldadas entre si. Quando você ficar tentado a ultrapassar os limites de um componente, lembre-se de que ele pode não permanecer como um único componente.

## Você também pode querer

- [Primeiros passos](../getting-started/index.md) — o topo do funil de contribuidor.
- [Comandos úteis](useful-commands.md) — os encantamentos diários para o contêiner de desenvolvimento.
- [Guia de migração](migration-guide.md) — o trabalho atual de atualização do Vue 2 → Vue 3.
- [Visão geral da arquitetura](../architecture/index.md) e [Interiores do sistema](../architecture/internals.md) — a história completa de um envio.
- [Referência de API](../reference/api.md) — a superfície do endpoint e o envelope de solicitação/resposta.
