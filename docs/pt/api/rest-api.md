---
title: Visão geral da API REST
description: Documentação completa da API REST para omegaUp
icon: bootstrap/cloud
---
#API REST omegaUp

omegaUp fornece uma API REST abrangente que pode ser acessada diretamente. Todos os endpoints usam métodos HTTP padrão (`GET` ou `POST`) e retornam respostas no formato JSON.

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

## Formato de resposta

Todas as respostas da API seguem um formato consistente:

### Resposta de sucesso

```json
{
  "status": "ok",
  "data": { ... }
}
```
### Resposta de erro

```json
{
  "status": "error",
  "error": "Error message",
  "errorcode": 400
}
```
## Categorias de API

- **[API de concursos](contests.md)** - Gerenciamento e participação em concursos
- **[API de problemas](problems.md)** - Criação e gerenciamento de problemas
- **[API de usuários](users.md)** - Gerenciamento e autenticação de usuários
- **[Runs API](runs.md)** - Tratamento de envios e resultados
- **[API de esclarecimentos](clarifications.md)** - Esclarecimentos do concurso

## Exemplo: obter horário do servidor

Este é um endpoint público que não requer autenticação:

**Solicitação:**
```bash
GET https://omegaup.com/api/time/get/
```
**Resposta:**
```json
{
  "time": 1436577101,
  "status": "ok"
}
```
### Detalhes do terminal

**`GET time/get/`**

Retorna o carimbo de data/hora atual do UNIX de acordo com o relógio interno do servidor. Útil para sincronizar relógios locais.

| Campo | Tipo | Descrição |
|---------|--------|-------------------------------------------------|
| estado | corda | Retorna `"ok"` se a solicitação foi bem-sucedida |
| tempo | interno | Carimbo de data/hora UNIX representando a hora do servidor |

**Permissões necessárias:** Nenhuma

## Catálogo completo de endpoints

Para uma lista **exaustiva** de métodos agrupados por controlador, veja o **[README dos Controllers](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/README.md)** gerado automaticamente no repositório omegaUp. As páginas aqui (`users.md`, `contests.md`, …) cobrem os fluxos mais comuns; o README é a melhor referência para um nome concreto `apiAlgo`.

## Limitação de taxa

Alguns endpoints têm limites de taxa:

- **Envios**: Um envio por problema a cada 60 segundos
- **Chamadas de API**: varia de acordo com o endpoint

Limite de taxa excedido respostas:

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

**Pronto para usar a API?** Navegue pelas [categorias de API](#api-categories) ou comece com [Autenticação](authentication.md).
