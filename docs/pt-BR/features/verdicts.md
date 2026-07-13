---
title: Veredictos e pontuação
description: Noções básicas sobre veredictos de envio e modelos de pontuação
icon: bootstrap/check-circle
---
# Veredictos e pontuação

Cada envio que você faz termina como um **veredicto**: um pequeno código que diz o que
aconteceu quando o avaliador executou seu programa nos casos de teste do problema. O veredicto
que você vê na Arena é a *pior* coisa que aconteceu em todos os casos que o aluno
correu — omegaUp relata a falha mais grave, porque um programa que errou um caso
está errado, não importa quantos outros acertou.

O veredicto é armazenado em cada execução na coluna `verdict` do `Runs` e `Submissions`
tabelas, e é um dos exatamente doze valores. Eles são, aproximadamente do melhor ao pior:

| Código | Nome | O que significa |
| ---- | ---- | ------------- |
| `AC` | Aceito | Todos os casos na corrida foram aprovados. Nota máxima. |
| `PA` | Parcialmente aceito | Alguns grupos de casos foram aprovados ou um validador personalizado recebeu crédito fracionário. Sua pontuação está estritamente entre 0 e o máximo. |
| `PE` | Erro de apresentação | A resposta está essencialmente correta, mas sua formatação está desativada. Um veredicto legado – a maioria dos problemas agora usa validadores de token que ignoram espaços em branco, então você raramente os verá. |
| `WA` | Resposta errada | O programa foi concluído, mas produziu uma saída que o validador rejeitou. |
| `TLE` | Prazo excedido | O programa não terminou dentro do `time_limit` do problema (por exemplo, 1000 ms). Além disso, o que se torna um impasse ou uma espera infinita na entrada. |
| `OLE` | Limite de saída excedido | O programa gravou mais saída do que o permitido — geralmente um loop infinito com um `print` dentro dele. |
| `MLE` | Limite de memória excedido | O programa tentou usar mais do que o `memory_limit` (por exemplo, 32.768 KiB). |
| `RTE` | Erro de tempo de execução | O programa travou – um código de saída diferente de zero, uma exceção não detectada, uma falha de segurança, um sinal. |
| `RFE` | Erro de função restrita | O programa tentou uma chamada de sistema que proíbe a sandbox (um soquete, um fork, um arquivo inesperado). Minijail pegou e matou o programa. Consulte [Sandbox](sandbox.md). |
| `CE` | Erro de compilação | O código não foi compilado. O `stderr` do compilador é retornado para que você possa ver o porquê — o único veredicto decidido antes da execução de qualquer caso. |
| `JE` | Erro do juiz | Algo deu errado *do lado do omegaUp*, não do seu: um corredor morreu no meio da avaliação, um arquivo de caso estava faltando, um erro interno surgiu. O reenvio geralmente o limpa; se não, diga-nos. |
| `VE` | Erro do validador | O próprio validador personalizado do problema travou ou retornou um disparate. Um bug criador de problemas, não um bug concorrente. |

## Por que o veredicto é uma decisão de grupo, não uma decisão de caso

Uma única execução é, na verdade, um lote de muitas execuções — uma por arquivo `.in` — e cada execução
obtém seu próprio veredicto por caso dentro da niveladora (`AC`, `WA`, `TLE`,…). O veredicto que você
finalmente ver é o agregado, e a regra de agregação é onde o comportamento interessante
vidas, porque está diretamente ligado à **pontuação**.

omegaUp agrupa casos de teste: tudo antes do primeiro `.` no nome do arquivo de um caso é seu
**grupo** (então `3.foo.in` e `3.bar.in` pertencem ao grupo `3`; um caso sem ponto, como
`5.in`, forma seu próprio grupo `5`). Um grupo concede seus pontos somente se **todos** casos nele
voltou `AC` ou `PA` - o modelo "tudo ou nada por subtarefa" depende dos problemas competitivos
em diante, onde uma solução parcialmente correta para uma subtarefa não rende nada para essa subtarefa.

Os pesos dos casos vêm do arquivo `testplan` do problema, se houver (normalizado para que eles somem
para 1); caso contrário, cada caso vale `1 / number-of-cases`. A pontuação da corrida é a soma de
os pesos dos grupos que passaram integralmente, multiplicados pelos pontos que vale o problema
no concurso atual (ou dimensionado para 100% no modo de prática). Então `PA` – uma pontuação fracionária –
é o que você obtém quando alguns grupos são aprovados e outros não, ou quando um validador personalizado entrega
devolver uma pontuação parcial para um caso.

Para o caminho completo que um envio segue de `/api/run/create/` através das filas, o
corredor, os validadores e de volta ao placar, consulte [Informações internas do sistema](../architecture/internals.md)
e [Internos da niveladora](../architecture/grader-internals.md).

## Validadores: como um caso se torna AC ou WA

O avaliador decide o veredicto de cada caso com um **validador**. Os validadores integrados
tokenize a saída esperada e a saída do concorrente no espaço em branco e compare:

- **`token`** — compara token por token; a primeira incompatibilidade (ou um fluxo terminando antes do
  outro) é um `WA`. O padrão para a maioria dos problemas.
- **`token-caseless`** — o mesmo, mas sem distinção entre maiúsculas e minúsculas.
- **`token-numeric`** — ignora tokens não numéricos, analisa o restante como ponto flutuante e
  compare com uma tolerância. Isto é o que permite que um problema aceite `3.14159` onde a chave diz
  `3.14160`.
- **`literal`** — uma correspondência exata, sem tokenização.
- **`custom`** — o problema vem com seu próprio programa validador que lê os dados do competidor
  saída (e, para alguns problemas, a entrada) e decide o próprio veredicto, opcionalmente
  atribuição de pontuação parcial. Uma falha aqui é o que produz `VE`.

!!! observe "O veredicto relatado é o mais severo"
    Ao depurar um envio, lembre-se de que o veredicto é o pior caso em todo o
    correr. Uma execução mostrando `TLE` pode estar resolvendo a maioria dos casos corretamente e atingindo o tempo limite em um grande
    um – abra os detalhes da execução para ver o detalhamento por caso antes de concluir todo o seu
    abordagem está errada.
