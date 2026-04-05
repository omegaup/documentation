---
title: Referência de API
description: Documentação completa da API REST para omegaUp
icon: bootstrap/api
---
# Referência de API

omegaUp fornece uma API REST abrangente que pode ser acessada diretamente. Todos os endpoints usam métodos HTTP padrão (`GET` ou `POST`) e retornam respostas JSON.

##URL base

Todos os endpoints da API são prefixados com:

```
https://omegaup.com/api/
```
Nesta documentação, apenas a parte da URL **após** esse prefixo é mostrada.

## Autenticação

!!! aviso "HTTPS obrigatório"
    Somente conexões HTTPS são permitidas. As solicitações HTTP retornarão `HTTP 301 Permanent Redirect`.

Alguns endpoints são públicos e não requerem autenticação. Os endpoints protegidos exigem autenticação por meio de um `auth_token` obtido do endpoint [`user/login`](users.md#login).

O token deve ser incluído em um cookie chamado `ouat` (omegaUp Auth Token) para solicitações autenticadas.

!!! importante "Sessão Única"
    omegaUp suporta apenas uma sessão ativa por vez. O login programaticamente invalidará a sessão do navegador e vice-versa.

## Categorias de API

<div class="grid cards" markdown>

- :material-trophy:{ .lg .middle } __[API de concursos](contests.md)__

    ---

    Crie, gerencie e participe de concursos de programação.

    [Navegar :octicons-arrow-right-24:](contests.md)

- :material-puzzle:{ .lg .middle } __[API de problemas](problems.md)__

    ---

    Crie, atualize e gerencie problemas de programação.

    [Navegar :octicons-arrow-right-24:](problems.md)

- :material-account:{ .lg .middle } __[API de usuários](users.md)__

    ---

    Gerenciamento de usuários, autenticação e operações de perfil.

    [Navegar :octicons-arrow-right-24:](users.md)

- :material-code-braces:{ .lg .middle } __[Executa API](runs.md)__

    ---

    Envie o código, verifique o status e recupere os resultados do envio.

    [Navegar :octicons-arrow-right-24:](runs.md)

- :material-message-text:{ .lg .middle } __[API de esclarecimentos](clarifications.md)__

    ---

    Faça e responda perguntas durante concursos.

    [Navegar :octicons-arrow-right-24:](clarifications.md)

</div>

## Exemplo rápido

Obtenha o horário atual do servidor (endpoint público):

```bash
curl https://omegaup.com/api/time/get/
```
Resposta:

```json
{
  "time": 1436577101,
  "status": "ok"
}
```
## Formato de resposta

Todas as respostas da API seguem um formato consistente:

```json
{
  "status": "ok",
  "data": { ... }
}
```
Respostas de erro:

```json
{
  "status": "error",
  "error": "Error message",
  "errorcode": 400
}
```
## Catálogo completo de endpoints

Este site documenta as **categorias** principais da API. O índice **gerado e autoritativo** de controladores e rotas está no repositório principal:

**[frontend/server/src/Controllers/README.md](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/README.md)**

Convenção: um pedido a `/api/<segmento>/<ação>/` é tratado por `<Segmento>Controller::api<Ação>` em `frontend/server/src/Controllers/` (com os ajustes de nome usuais em PHP).

## Limitação de taxa

Alguns endpoints têm limites de taxa para evitar abusos:

- **Envios**: Um envio por problema a cada 60 segundos
- **Chamadas de API**: varia de acordo com o endpoint

As respostas do limite de taxa excedido incluem:

```json
{
  "status": "error",
  "error": "Rate limit exceeded",
  "errorcode": 429
}
```
## Documentação Relacionada

- **[Guia de autenticação](authentication.md)** - Fluxo de autenticação detalhado
- **[Visão geral da arquitetura](../architecture/index.md)** - Arquitetura do sistema
- **[Guias de desenvolvimento](../development/index.md)** - Uso da API no desenvolvimento

---

**Pronto para usar a API?** Comece com [Autenticação](authentication.md) ou navegue pelas [categorias de API](#api-categories) acima.
