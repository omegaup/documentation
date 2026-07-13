---
title: Emblemas
description: Implementação do sistema de conquistas
icon: bootstrap/award
---
# Emblemas

Os emblemas são pequenas conquistas que o omegaUp concede aos usuários - "resolveu 100 problemas",
"codificador do mês", "administrador do concurso". O que os torna agradáveis de trabalhar é
que um selo é quase inteiramente **declarativo**: você não escreve código que decide quem
ganha, você escreve uma consulta SQL que *seleciona* quem o ganhou, coloca-o em uma pasta e
omegaUp faz o resto. Implementar um é um caminho bastante conhecido.

## Adicionando um selo, passo a passo

1. **Escolha um alias.** Ele deve ser exclusivo e ter no máximo **32 caracteres**. Todo o resto é
   nomeado após isso.

2. **Crie sua pasta.** Crie um diretório em
   [`frontend/badges/`](https://github.com/omegaup/omegaup/tree/main/frontend/badges) cujo
   name é exatamente o alias. A partir daqui este é o seu `badgeFolder`.

3. **Adicione um ícone (opcional).** Se o emblema tiver um ícone personalizado, coloque seu SVG em `badgeFolder`
   como `icon.svg`.

4. **Escreva a consulta de premiação.** Crie `badgeFolder/query.sql` contendo um único MySQL
   `SELECT` que retorna os `user_id`s de cada usuário que deverá receber o crachá. Isto
   consulta *é* a lógica do emblema, então você precisa saber a forma dos dados - mantenha o
   [esquema de banco de dados](https://github.com/omegaup/omegaup/blob/main/frontend/database/schema.sql)
   abra enquanto você o escreve e busque algo simples e armazenável em cache, em vez de inteligente.

5. **Adicione localizações.** Crie
   [`badgeFolder/localizations.json`](https://github.com/omegaup/omegaup/blob/main/frontend/badges/legacyUser/localizations.json)
   com o nome e a descrição do crachá traduzidos para espanhol (`es`), inglês (`en`) e
   Português (`pt`). O nome pode ter no máximo **50 caracteres**.

6. **Carregue as localizações.** Execute `./stuff/lint.sh` para que as strings em `localizations.json`
   são propagados nos arquivos de mensagens correspondentes.

7. **Escreva o teste.** Crie `badgeFolder/test.json`. Seu campo `testType` escolhe como o
   execuções de teste de unidade do emblema:

    - **`"testType": "apicall"`** — construa o cenário chamando APIs do controlador para criar
      os dados dos quais o crachá depende (problemas, usuários, concursos, corridas,…). Você descreve isso
      com um array `actions`, cujas entradas podem ser:
        - `changeTime` — mova o relógio do sistema para poder testar crachás dependentes do tempo.
        - `apicalls` — chama uma API específica, fornecendo o nome de usuário e a senha do usuário chamador
          e os parâmetros. As APIs são todos os métodos `api…` estáticos públicos no
          controladores em
          [`frontend/server/src/Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers).
        - `scripts` — execute um dos scripts cron do omegaUp (`aggregateFeedback`, `assignBadges`,
          `updateUserRank`), que vivem em
          [`stuff/cron/`](https://github.com/omegaup/omegaup/tree/main/stuff/cron).

      Finalize um teste `apicall` com um campo `expectedResults` listando os nomes de usuário que
      deveria receber o crachá. Veja
      [`coderOfTheMonth/test.json`](https://github.com/omegaup/omegaup/blob/main/frontend/badges/coderOfTheMonth/test.json)
      para um exemplo trabalhado.

    - **`"testType": "phpunit"`** — escreva um teste PHPUnit clássico chamado `<alias>Test.php`,
      salvo em
      [`frontend/tests/badges/`](https://github.com/omegaup/omegaup/tree/main/frontend/tests/badges),
      seguindo a mesma estrutura dos outros testes unitários do omegaUp (e livre para usar o
      [fábricas](https://github.com/omegaup/omegaup/tree/main/frontend/tests/factories)).

    Cada um tem suas vantagens: prefira `phpunit` para um emblema que, de outra forma, precisaria de muitos
    chamadas de API quase idênticas; caso contrário, `apicalls` é a opção mais leve.

8. **Execute os testes** para confirmar sua consulta e teste e realmente conceda o selo à direita
   pessoas:

    ```bash
    ./vendor/bin/phpunit --bootstrap frontend/tests/bootstrap.php \
      --configuration frontend/tests/phpunit.xml frontend/tests/badges/ --debug
    # or simply
    ./stuff/runtests.sh
    ```
9. **Abra a solicitação pull.** Se nada der errado, seu crachá está pronto – envie-o.

Para referência, dois PRs de emblemas mesclados são bons modelos a serem seguidos:
[Administrador do concurso](https://github.com/omegaup/omegaup/pull/2602/files) e
[Administrador do Concurso Virtual](https://github.com/omegaup/omegaup/pull/2603/files).

Se algo não estiver claro enquanto você constrói um, não hesite em entrar em contato - consulte
[Obtendo ajuda](../getting-started/getting-help.md).
