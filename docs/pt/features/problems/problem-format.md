---
title: Formato do problema
description: Estrutura ZIP para criação manual de problemas
icon: bootstrap/file-document
---

# Formato do problema (ZIP manual)

Para a maioria dos autores, o [Problem Creator](https://omegaup.com/problem/creator) (CDP) ou o editor no site basta. Esta página é para empacotar **manualmente** um `.zip` quando você precisa de controle total (por exemplo **Karel**, tarefas **interativas** ou **validadores personalizados**).

!!! dica "Vídeos"
    ZIP manual: [parte 1](https://www.youtube.com/watch?v=LfyRSsgrvNc), [parte 2](https://www.youtube.com/watch?v=i2aqXXOW5ic). CDP: [YouTube](https://www.youtube.com/watch?v=cUUP9DqQ1Vg).

## Layout do ZIP (resumo)

Use **`.zip`** (não RAR/7z). O nome do arquivo é arbitrário.

```
problem.zip
├── cases/
├── statements/
├── solutions/
├── interactive/
├── validator.cpp
├── settings.json
├── limits.json
└── testplan
```

Referência no repositório: [`frontend/tests/resources/testproblem.zip`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/resources/testproblem.zip).

## O que se configura

| Área | Significado |
|------|-------------|
| **Tipo de validador** | token, sem maiúsculas, tolerância numérica, “stdout como pontuação” (interativo) ou **custom** `validator.<lang>` |
| **Linguagens** | Modos: linguagens normais, **Karel**, **somente saída** (`.zip` de respostas; caso único pode ser `Main.in`/`Main.out`), **sem envios** |
| **Limites** | Tempo CPU, tempo total, validador, memória (KiB), tamanho de saída |
| **Limite de código** | Tamanho máximo do fonte |
| **Público / tags / fonte** | Visibilidade e atribuição |

## `cases/`

- Pares **`.in`** / **`.out`** com o mesmo prefixo.
- **Agrupamento**: ponto no nome, ex. `grupo1.casoa.in`.
- ZIPs muito grandes deixam o julgamento lento.

## `statements/`

- Markdown por idioma. Pré-visualização: [omegaup.com/redaccion.php](https://omegaup.com/redaccion.php).

## `solutions/`

Opcional. Exemplos em [`frontend/tests/resources`](https://github.com/omegaup/omegaup/tree/main/frontend/tests/resources).

## `interactive/` e libinteractive

[libinteractive](https://omegaup.com/libinteractive/). Exemplo: [Cave (IOI 2013)](https://omegaup.com/resources/cave.zip).

## Validador customizado (`validator.<lang>`)

Um arquivo na raiz entre `validator.c`, `validator.cpp`, `validator.java`, `validator.p`, `validator.py`. Deve imprimir float em **[0, 1]**; vazio → **JE**.

Manual longo: [`Manual-for-Zip-File-Creation-for-Problems.md`](https://github.com/omegaup/omegaup/blob/main/frontend/www/docs/Manual-for-Zip-File-Creation-for-Problems.md).

## `testplan`

Pesos por grupo ou repartição uniforme; ver `testproblem.zip`.

## Documentação relacionada

- **[Criar problemas](creating-problems.md)**
- **[Veredictos](../verdicts.md)**
