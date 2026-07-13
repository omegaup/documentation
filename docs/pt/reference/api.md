---
title: Referência de API
description: Como chamar a API REST omegaUp e onde reside a referência de endpoint confiável e sempre atual
icon: bootstrap/api
---
# Referência de API

Tudo o que o frontend web do omegaUp faz, ele faz chamando a mesma API REST pública que você
pode ligar para si mesmo. Cada página na Arena, cada atualização do placar, cada envio é
uma solicitação HTTP para `/api/...` — portanto, não há nada que a UI possa fazer que a API não possa.

!!! observe "Onde reside a referência ponto por ponto"

    Esta página documenta as **regras transversais** que se aplicam a *todas* chamadas —
    transporte, autenticação e envelope de resposta. Deliberadamente **não**
    listar endpoints individuais, porque essa lista é **gerada a partir do código-fonte** e
    apodreceria no momento em que fosse copiado aqui à mão.

    A superfície oficial e sempre atual é gerada por
    [`frontend/server/cmd/APITool.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/cmd/APITool.php)
    — a mesma ferramenta que emite o cliente frontend digitado
    [`api.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/api.ts)
    e [`api_types.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/api_types.ts).
    Para ver exatamente o que um controlador aceita e retorna, leia o controlador em
    [`frontend/server/src/Controllers/`](https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers)
    (cada método `apiXxx` é um endpoint) ou seus documentos gerados, em vez de um
    mesa mantida à mão.

## As regras que se aplicam a todas as chamadas

**É simples HTTP, GET ou POST, JSON de volta.** Cada endpoint é invocado com um
Solicitação HTTP e retorna um status HTTP apropriado mais um corpo JSON. Chamadas somente leitura que
não precisa de privilégios pode ser feito com um GET - você pode literalmente colar o URL em um navegador
e veja o JSON.

**Somente HTTPS — HTTP é recusado, não é rebaixado silenciosamente.** Porque omegaUp se preocupa com
manter os dados dos usuários privados e evitar trapaças (alguém que fareja o tráfego do concurso é um
ameaça real, não hipotética), a API é servida exclusivamente por HTTPS. Uma chamada acabou
HTTP simples não é bem-sucedido silenciosamente: o servidor responde com um redirecionamento permanente HTTP 301
para o URL seguro, e um cliente que não o segue não obtém nada de útil.

**Cada URL começa com o mesmo prefixo.** Todos os endpoints residem em
`https://omegaup.com/api/`; o resto do caminho seleciona o controlador e o método. Por
convenção, nomeamos os pontos finais pelo que vem *depois* desse prefixo - portanto, um ponto final escrito
aqui como `time/get` é realmente `https://omegaup.com/api/time/get/`.

**A autenticação é um token em um cookie chamado `ouat`.** A maioria das chamadas não precisa de nenhum
privilégio, mas aqueles que atuam em sua conta exigem que você esteja logado.
chamando `user/login`, pegue o `auth_token` que ele retorna e envie-o em cada
chame como um cookie chamado **`ouat`** (omegaUp Auth Token). Uma consequência importante, novamente
impulsionado pelo anti-trapaça: **você só pode ter uma sessão ativa por vez.** Se você fizer login
programaticamente você invalida a sessão do seu navegador e vice-versa.

## O envelope de resposta

Cada resposta é JSON e carrega um campo `status`. Em caso de sucesso, é `"ok"`; em caso de falha
é `"error"` e o corpo também carrega um `errorcode` legível por máquina, um estável
`errorname` e uma mensagem `error` legível por humanos, **localizada**, adequada para exibição a um
usuário em seu próprio idioma. Lide com falhas ramificando em `status`/`errorname`, nunca
correspondência no texto `error` legível por humanos - esse texto é traduzido e mudará.

## Um exemplo prático

A chamada mais simples possível busca o relógio do servidor, o que é útil para corrigir um problema.
relógio local que pode estar distorcido:

```console
$ curl https://omegaup.com/api/time/get/
{"time":1436577101,"status":"ok"}
```
Não precisa de privilégios, portanto não há cookie `ouat`, o status é `HTTP 200 OK` e
`time` é um carimbo de data/hora UNIX direto do relógio interno do servidor.

## Veja também

- **[Links úteis](links.md)** — repositórios, guias de contribuição e arquivos gerados automaticamente
  documentos do controlador.
- **[System Internals](../architecture/internals.md)** — como uma chamada de API para
  `run/create` na verdade flui através de `\OmegaUp\ApiCaller` para um controlador e para o
  nivelador.
