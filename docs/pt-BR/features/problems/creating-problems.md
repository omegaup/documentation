---
title: Criando Problemas
description: Guia passo a passo para criar problemas de programação
icon: bootstrap/plus-circle
---
# Criando Problemas

Obrigado por querer adicionar conteúdo ao omegaUp. Um problema são quatro coisas coladas: uma **declaração** que o competidor lê, um conjunto de **casos** (pares `.in`/`.out`) que definem o que significa "correto", um conjunto de **limites** que decidem quando um envio é eliminado e um **validador** que decide com que rigor a saída é comparada. Esta página percorre todos os quatro e explica *por que* cada botão existe, para que você possa escolher valores sensatos em vez de copiar os padrões às cegas.

Existem duas maneiras de criar um problema e você deve procurá-las nesta ordem:

- **The Problem Creator (CDP)** em [omegaup.com/problem/creator](https://omegaup.com/problem/creator) é um editor visual que cobre casos comuns de forma intuitiva. Ele tem algumas limitações - mais notavelmente ele **não** suporta problemas do Karel - então se não conseguir expressar o que você precisa, vá até a opção manual abaixo. Há um [vídeo passo a passo](https://www.youtube.com/watch?v=cUUP9DqQ1Vg) se você preferir assistir primeiro.
- **Construir manualmente o `.zip`** oferece controle total e é a escolha certa para Karel, tarefas interativas ou validadores personalizados. O layout do arquivo bruto está em [Formato do problema (ZIP manual)](problem-format.md); esta página explica as *decisões de conteúdo* que vão para esse arquivo. Vídeo em modo manual: [parte 1](https://www.youtube.com/watch?v=LfyRSsgrvNc), [parte 2](https://www.youtube.com/watch?v=i2aqXXOW5ic).

De qualquer forma, quando você clica em **Criar**, a solicitação chega a `\OmegaUp\Controllers\Problem::apiCreate` ([`frontend/server/src/Controllers/Problem.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L460)), que valida seus metadados, cria um objeto `ProblemSettings` e entrega todo o pacote para `\OmegaUp\ProblemDeployer`. O implementador não armazena seus arquivos no MySQL — ele os envia como um **repositório git** no serviço separado [omegaup-gitserver](https://github.com/omegaup/gitserver) ([`ProblemDeployer.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/ProblemDeployer.php#L91)), e é por isso que cada edição que você faz se torna uma nova revisão que você pode publicar ou reverter.

## A declaração

A instrução é Markdown e fica em `statements/` no arquivo, um arquivo por idioma: `es.markdown`, `en.markdown`, `pt.markdown` - esses três (`en`, `es`, `pt`) são os únicos locais que omegaUp reconhece (`\OmegaUp\Controllers\Problem::VALID_LANGUAGES`). O espanhol é o padrão histórico, portanto, a maioria dos problemas legados vem com `es.markdown` e nada mais.

Algumas coisas que fazem com que as declarações sejam bem lidas e o raciocínio por trás de cada uma:

- **Envolva cada variável em delimitadores matemáticos** — escreva `$n$`, `$x$`, `$x_i$` (os subscritos usam `_`) em vez de um `n` simples. Isto não é decoração: durante um concurso ao vivo, uma variável separada da prosa é muito mais fácil de detectar e impossível de confundir com uma palavra em inglês, o que reduz os esclarecimentos.
- **LaTeX é totalmente suportado**, portanto fórmulas, somatórios e matrizes são renderizados corretamente. Visualize o LaTeX *e* a tabela de entrada/saída de amostra antes de publicar em [omegaup.com/redaccion.php](https://omegaup.com/redaccion.php) — o que você vê lá é o que o concorrente vê.
- **As imagens vão dentro de `statements/`** ao lado do Markdown, e você as referencia com a sintaxe de imagem simples do Markdown, `![alt text](imagen.jpg)`. Os formatos suportados são **jpg, gif e png**. Não há redimensionamento no Markdown, então dimensione a imagem antes de adicioná-la. Mantenha-a abaixo de **650 pixels de largura** ou ela transbordará a coluna de instruções.

Se você tiver um artigo ou editorial oficial, coloque-o em `solutions/` usando a mesma nomenclatura por localidade (`es.markdown`, `en.markdown`, `pt.markdown`). O repositório fornece exemplos trabalhados em [`frontend/tests/resources`](https://github.com/omegaup/omegaup/tree/main/frontend/tests/resources) - [`testproblem.zip`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/resources/testproblem.zip) em particular inclui uma solução.

## Casos

Cada caso é um par de arquivos em `cases/`: uma entrada `.in` e sua saída esperada `.out`. Os **nomes básicos devem corresponder** e ser emparelhados corretamente — `1.in`/`1.out`, `hola.in`/`hola.out` — mas o nome específico é irrelevante. omegaUp é executado no Linux, portanto, o case é resistente: uma pasta chamada `Cases` ou um arquivo que termina em `.In` **não será encontrado**. Não há limite rígido para o número de casos, mas mantenha a carga útil total do caso abaixo de **~100 MB**: cada caso extra é mais trabalho por envio e, em um concurso ao vivo, uma solução lenta que `TLE`s em cem casos pode fazer backup da fila de classificação e prejudicar a experiência de todos.

### Casos agrupados

Por padrão, cada caso pontua de forma independente. Se, em vez disso, você quiser uma pontuação de **tudo ou nada** - o competidor só ganha os pontos do grupo quando *todos* os casos nele passam - use **casos agrupados**. Você agrupa colocando um `.` (ponto) no nome do arquivo para separar o nome do grupo do nome do caso; o nome do grupo é tudo antes do primeiro ponto. Portanto, `grupo1.caso1.in`, `grupo1.caso1.out`, `grupo1.caso2.in`, `grupo1.caso2.out` é um **grupo único com dois casos**. Não há limite para o número de grupos, e os grupos podem conter diferentes números de casos.

Esta é a ferramenta certa quando o espaço de respostas plausíveis é pequeno – digamos, um problema de sim/não – onde um concorrente poderia, de outra forma, obter crédito parcial ao adivinhar casos individuais. Observe o outro lado: **o ponto é reservado para agrupamento**, portanto, não coloque pontos perdidos no nome de um caso, a menos que você realmente pretenda agrupá-lo.

### Pesos (`testplan`)

Por padrão, cada caso vale `1 / number-of-cases`, então as pontuações somam 100%. Para ponderar os casos de maneira diferente, adicione um arquivo chamado literalmente **`testplan`** (sem extensão) na raiz do zip, uma linha por caso, cada linha sendo o nome base do caso (sem extensão) seguido por seus pontos:

```
caso1 5
grupo2.caso1 10
grupo2.caso2 0
```
Certifique-se de que nenhum arquivo tenha espaços em seu nome. Para atribuir pontos a um *grupo* como um todo, em vez de dividi-los entre seus casos, a convenção é colocar o valor total de pontos do grupo em seu **primeiro** caso e `0` em todos os outros casos do grupo.

## Limites

Limites são o que o avaliador impõe por caso. Todo problema começa a partir de um bloco de padrões em `\OmegaUp\Controllers\Problem::getDefaultProblemSettings` ([`Problem.php#L4549`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L4549)):

| Configuração | Padrão | O que faz |
|---|---|---|
| **Limite de tempo** (`TimeLimit`) | `1s` (1000ms) | Tempo máximo de **CPU** que o processo do concorrente pode executar *por caso* antes que o sistema operacional o elimine com `TLE`. |
| **Limite de memória** (`MemoryLimit`) | `64MiB` | Máximo de RAM (heap + pilha) em [kibibytes](https://en.wikipedia.org/wiki/Kibibyte); excedê-lo é `MLE`. |
| **Limite geral de tempo de parede** (`OverallWallTimeLimit`) | `30s` | Tempo máximo **real** que o avaliador espera que o problema *todo* (todos* os casos) termine, caso contrário, `TLE`. |
| **Tempo de parede extra** (`ExtraWallTime`) | `0s` | Graça extra em tempo real, usada principalmente para problemas `libinteractive` onde o processo do avaliador também precisa ser finalizado. |
| **Limite de saída** (`OutputLimit`) | `10240KiB` | Máximo de bytes que o processo pode gravar em stdout/stderr antes de ser eliminado com `OLE`. |
| **Limite de entrada** (`inputLimit`) | Bytes `10240` | Tamanho máximo do *código-fonte* do concorrente - uma alavanca para impedir soluções pré-computadas/codificadas. |

Duas sutilezas que vale a pena internalizar. Primeiro, **o limite de tempo é o tempo da CPU, mas o limite geral de tempo é o tempo real** — eles medem relógios diferentes propositalmente. Um envio pode ultrapassar o limite geral da parede, mesmo que nenhum caso exceda o limite da CPU. Quando isso acontece, qualquer caso que não foi executado não é pontuado e, para manter os resultados reproduzíveis, o avaliador avalia os casos em **ordem lexicográfica** - portanto, quais casos "fazem sucesso" sob um limite geral restrito são determinísticos, não um cara ou coroa.

Em segundo lugar, o **limite de saída normalmente é detectado automaticamente**: omegaUp pega o tamanho do maior arquivo `.out` e adiciona **10 KiB** de espaço livre. Você só precisa configurá-lo manualmente ao usar um validador personalizado, porque o omegaUp não pode inferir o tamanho de saída esperado - portanto, para problemas de validador personalizado, forneça `OutputLimit` explicitamente.

## Validadores

O validador decide *como* o resultado do competidor é comparado com o seu `.out`. omegaUp envia cinco tipos; as constantes de string residem em [`\OmegaUp\ProblemParams`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/ProblemParams.php#L28):

- **`token`** — lê todos os *tokens* (execuções de até **4.194.304** caracteres imprimíveis contíguos separados por espaços em branco) de ambos os arquivos e exige que as duas sequências de token sejam **idênticas**. Este é o padrão diário e o que `getDefaultProblemSettings` inicia você. Ele ignora quantos espaços em branco separam os tokens, que é o que você quase sempre deseja.
- **`token-caseless`** — igual a `token`, mas primeiro coloca todos os tokens em letras minúsculas, para que `Yes` e `yes` correspondam. Use-o quando a resposta for uma palavra e você não quiser que as letras maiúsculas e minúsculas sejam importantes.
- **`token-numeric`** — lê tokens numéricos, interpreta-os como números e exige que as duas sequências tenham o mesmo comprimento *e* que cada número correspondente corresponda a um **erro absoluto OU relativo de 1e-9** (esse é o `Tolerance`, [`Problem.php#L4562`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L4562)). Este é o único para respostas de ponto flutuante, onde uma correspondência exata de string rejeitaria erroneamente `0.5000000001`.
- **`literal`** — correspondência exata byte por byte, sem tokenização. Alcance-o apenas quando o próprio espaço em branco fizer parte da resposta.
- **`custom`** — você envia um programa validador. Veja abaixo.

### Validadores personalizados (`validator.<lang>`)

Quando "comparar esses tokens" não é expressivo o suficiente — por exemplo, quando um problema tem **muitas respostas corretas** — você escreve um validador. Coloque um único arquivo chamado `validator.<lang>` na **raiz** do zip, onde `<lang>` é `c`, `cpp`, `java`, `p` (Pascal) ou `py`. Você só precisa de um validador, independentemente do idioma em que o concorrente se inscreve.

Aqui está o modelo mental para o que o avaliador entrega ao seu validador:

- A saída do competidor chega na **entrada padrão** do validador — leia-a normalmente com `scanf`/`cin`/`input()`. Ele se comporta como se a motoniveladora tivesse executado `./contestant < data.in | ./validator casename`, onde `casename` é o nome `.in` do caso atual sem a extensão.
- Você pode `open("data.in")` ler a *entrada original do caso* e `open("data.out")` ler a *saída esperada* para esse caso, se precisar julgar.
- Seu validador **deve imprimir um número de ponto flutuante em `[0, 1]`** para stdout — a fração do caso que o competidor ganhou. **Não imprima nada e você obterá `JE`.** Um valor abaixo de `0` é fixado em `0`; acima, `1` é fixado em `1`. Tudo o que você escreve em *stderr* é ignorado pela pontuação, mas é útil para depuração.

Duas pegadinhas que incomodam as pessoas: o validador **executa dentro da mesma sandbox** que o código do concorrente, então se *ele* travar ou se comportar mal (`WA`, `RFE`, `RTE`, …) todo o envio será julgado como `JE`, não por culpa do competidor — teste seu validador com afinco. E mesmo que seus arquivos `.out` nunca sejam comparados quando você usa um validador personalizado, **você ainda deve enviar um `.out` para cada caso** (eles podem ser arquivos vazios) para que o emparelhamento seja completo.

Um validador para um problema de "imprimir a soma de `a` e `b`", aceitando a soma literal ou o valor recalculado, em C++17:

```cpp
#include <iostream>
#include <fstream>

int main() {
  // Read "data.in" to recover the original case input.
  int64_t a, b;
  {
    std::ifstream original_input("data.in", std::ifstream::in);
    original_input >> a >> b;
  }
  // "data.out" holds the expected output for this case.
  int64_t expected;
  {
    std::ifstream original_output("data.out", std::ifstream::in);
    original_output >> expected;
  }

  // Standard input carries the contestant's output.
  int64_t contestant;
  if (!(std::cin >> contestant)) {
    // stderr is ignored by scoring but useful while debugging.
    std::cerr << "Could not read contestant output\n";
    std::cout << 0.0 << '\n';
    return 0;
  }

  if (expected != contestant && contestant != a + b) {
    std::cerr << "Wrong answer\n";
    std::cout << 0.0 << '\n';
    return 0;
  }

  std::cout << 1.0 << '\n';  // full credit for this case
  return 0;
}
```
Os problemas do validador personalizado também recebem seu próprio bloco de limites, separado do do competidor, porque seu programa de julgamento tem necessidades de recursos diferentes. Quando o tipo de validador é `custom` e você não os substitui, omegaUp preenche `TimeLimit` `30s`, `MemoryLimit` `256MiB`, `OverallWallTimeLimit` `5s`, `OutputLimit` `10KiB`, `ExtraWallTime` `0s` ([`Problem.php#L4605`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L4605)). O **limite de tempo do validador** separado (`validatorTimeLimit`) é o orçamento em tempo real que o avaliador fornece ao seu validador para emitir um veredicto por caso antes de desistir do `JE`.

### "Saída padrão como pontuação"

Há um sexto modo que vale a pena conhecer: interpretar o stdout do competidor diretamente como a pontuação. O avaliador lê stdout, analisa-o como um ponto flutuante, fixa-o em `[0.0, 1.0]` e usa-o como pontuação final. Isso é usado quase exclusivamente com problemas **interativos**, onde deixar o *interator* (em vez do competidor) declarar a pontuação impede que o competidor simplesmente imprima `1.0` para trapacear.

## Idiomas e modos de envio

"Idiomas" controla não apenas quais linguagens de programação são permitidas, mas todo o *modo* de envio:

- **Linguagens normais** — C, C++ (vários padrões), Java, Kotlin, Python 2/3, Ruby, C#, Pascal e muito mais. O competidor envia o código-fonte, o omegaUp o compila e executa.
- **Karel** — a linguagem do bloco/robô, enviada como Karel-Java (`kj`) ou Karel-Pascal (`kp`). Os problemas do Karel só podem ser criados através do caminho ZIP manual; o CDP não os apóia.
- **Somente saída** (`cat`) — o competidor carrega um `.zip` de respostas para todos os casos em vez de código. Se você também quiser permitir o envio da resposta de um único caso como texto simples (sem zip), deve haver exatamente um caso denominado `Main.in`/`Main.out`.
- **Sem envios** — desativa totalmente o envio. Isso existe apenas para que um "problema" possa exibir conteúdo dentro de um curso sem ser solucionável.

## Botões de publicação

Alguns campos de metadados determinam como o problema é descoberto e administrado:

- **Aparece na listagem pública** (visibilidade) — se o problema pode aparecer publicamente e ser reaproveitado em concursos e cursos de terceiros. Novos problemas são padronizados como **privados** (`VISIBILITY_PRIVATE`), então nada do que você ainda está esboçando vaza.
- **Esclarecimentos por e-mail** — se a omegaUp envia por e-mail os esclarecimentos que os concorrentes perguntam sobre esse problema, para que você possa responder sem acampar no site.
- **Fonte** — atribuição da origem do problema (por exemplo, `OMI 2020`).
- **Tags** — rótulos de classificação; você também pode escolher se os usuários têm permissão para adicionar suas próprias tags.

## Erros comuns

As duas falhas que tropeçam em quase todos os autores de manuais iniciantes:

- **`cases/` e `statements/` devem ficar na *raiz* do zip**, sem nenhuma pasta de empacotamento — esta é uma pegadinha de embalagem de longa data ([problema #310](https://github.com/omegaup/omegaup/issues/310)). No diretório do problema no Linux/macOS, `zip -r myproblem.zip *` produz um arquivo com raiz correta; compactar a *pasta que contém* não.
- **Deve ser um `.zip`** — não `.rar`, `.tar.bz2`, `.7z` ou `.zx`. O próprio nome do arquivo não importa.

## Documentação relacionada

- **[Formato do problema (ZIP manual)](problem-format.md)** — o layout exato do arquivo, arquivo por arquivo
- **[Veredictos](../verdicts.md)** — o que `AC`, `PA`, `WA`, `TLE`, `MLE`, `OLE`, `RTE`, `JE` e o resto realmente significam
- **[API de problemas](../../reference/api.md)** — os endpoints por trás do `apiCreate` e amigos
- **[Manual longo (GitHub)](https://github.com/omegaup/omegaup/blob/main/frontend/www/docs/Manual-for-Zip-File-Creation-for-Problems.md)** — detalhes suplementares no repositório principal
