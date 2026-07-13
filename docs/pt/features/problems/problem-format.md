---
title: Formato do problema
description: Estrutura de arquivo ZIP para criação manual de problemas
icon: bootstrap/file-document
---
# Formato do problema (ZIP manual)

Esta página é para o solucionador de problemas experiente que precisa construir um problema manualmente
`.zip` — ou edite um omegaUp já implantado — porque eles precisam de algo que
ferramentas apontar e clicar não expõem: problemas do **Karel**, tarefas **interativas**,
um **validador personalizado** ou controle preciso sobre agrupamento e pesos. Se você estiver
apenas começando, ou seu problema é uma tarefa simples de "ler entrada, imprimir saída",
use o [Problem Creator (CDP)](https://omegaup.com/problem/creator) e
guarde a embalagem – há um [passo a passo do CDP no YouTube](https://www.youtube.com/watch?v=cUUP9DqQ1Vg).

!!! dica "Passeios em vídeo"
    Se você seguir o caminho manual, será útil observar alguém fazendo isso primeiro:
    [parte 1](https://www.youtube.com/watch?v=LfyRSsgrvNc) e
    [parte 2](https://www.youtube.com/watch?v=i2aqXXOW5ic) do manual
    tutorial de criação de problemas.

A coisa mais importante a internalizar antes de construir qualquer coisa: o
`.zip` que você carrega **não** é o que o omegaUp armazena. Quando você faz upload, o omegaUp's
gitserver (o serviço Go em [`omegaup/gitserver`](https://github.com/omegaup/gitserver)
que mantém cada problema como seu próprio repositório git) descompacta o arquivo, lê
seu `cases/`, seu `testplan` opcional e qualquer `settings.json` incluído,
e **compila tudo em um `settings.json` canônico** que o
a motoniveladora realmente consome. `testplan` e qualquer `settings.json` parcial que você enviou
são excluídos depois de serem dobrados, precisamente porque agora são redundantes
com o arquivo gerado (veja
[`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L463-L492)).
Então pense no `.zip` como *fonte* e `settings.json` como o *artefato compilado* —
é exatamente por isso que os nomes de diretório e extensões de arquivo abaixo devem ser
letra perfeita.

## As configurações configuráveis (modelo mental)

Quer você os configure por meio da UI da web ou os envie em metadados empacotados, cada
problema carrega o mesmo punhado de botões. Entendendo o que cada um *significa* —
e o veredicto que você obtém quando ele é excedido é o que permite empacotar corretamente.

### Validador: como o resultado do competidor é julgado

O validador decide se uma saída está correta e dá uma pontuação por caso em
`[0.0, 1.0]`. omegaUp envia cinco, cujos nomes canônicos vivem em
[`ProblemParams.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/ProblemParams.php#L28-L40)
(lado PHP) e
[`common/problemsettings.go`](https://github.com/omegaup/quark/blob/main/common/problemsettings.go#L30-L48)
(lado do aluno):

- **`token`** — token por token. Ele lê cada token (uma série de até
  **4.194.304** caracteres imprimíveis contíguos — 4 MiB, o `MaxTokenLength` em
  o [`tokenizer.go`](https://github.com/omegaup/quark/blob/main/runner/tokenizer.go#L13) do executor —
  separados por espaço em branco) do `.out` esperado e do concorrente
  saída e requer que as duas sequências de token sejam **idênticas**. Este é o
  padrão e o que você deseja para quase tudo.
- **`token-caseless`** — o mesmo que `token`, mas primeiro coloca todos os tokens em minúsculas, então
  `Yes` e `yes` correspondem. Alcance isso quando a capitalização não fizer parte do
  resposta.
- **`token-numeric`** — lê apenas tokens numéricos, interpreta-os como números,
  e os aceita quando o valor do competidor estiver dentro de um **absoluto *ou*
  erro relativo de 1e-9** do valor esperado (o padrão `Tolerance`, também
  `1e-9`, definido em
  [Configurações padrão do `Problem.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L4560)).
  As duas sequências ainda devem ter o mesmo comprimento. Use-o para ponto flutuante
  respostas onde os últimos dígitos podem oscilar.
- **`literal`** (mostrado na UI como "interpretar saída padrão como pontuação") — lê
  o stdout do competidor, analisa-o como um único float e ** fixa-o em
  `[0.0, 1.0]` para usar diretamente como pontuação do caso**. É quase exclusivamente para
  Problemas **interativos**: o processo do interator, e não o competidor, imprime o
  pontuação, o que impede o competidor de simplesmente imprimir `1.0` para trapacear.
- **`custom`** (`validator.<lang>`) — você envia um programa que lê o
  stdout do competidor (e, se quiser, a entrada e a saída esperada do caso) e
  imprime a própria pontuação. Detalhes completos e exemplos trabalhados estão em
  [Validador personalizado](#custom-validator-validatorlang) abaixo.

### Idiomas: o que o concorrente pode enviar

- **C, C++, Java, Python,…** — o concorrente envia o código-fonte em um dos omegaUp's
  idiomas suportados.
- **Karel** — o competidor envia um programa Karel. Veja o
  Seção [problemas de Karel](#karel-problems) sobre como construir os casos.
- **Somente saída** — o competidor envia um `.zip` de respostas para cada caso
  em vez de um programa. Se você quiser *também* deixá-los colar um único caso
  responda como texto simples em vez de zip, o problema deve ter exatamente **um**
  caso denominado `Main.in`/`Main.out`.
- **Sem inscrições** — o competidor não pode enviar nenhuma inscrição. Isto existe puramente para
  exibir conteúdo (uma leitura, uma lição) dentro de um curso.

### Limites de tempo, memória e saída

Cada um deles mapeia para um veredicto específico quando o programa do competidor o ultrapassa,
e cada um tem um padrão real. O formulário de criação de problemas atualmente preenche previamente estes
valores (ver
[`Problem.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L5952-L5961)),
e o próprio `DefaultLimits` da niveladora
([`common/problemsettings.go`](https://github.com/omegaup/quark/blob/main/common/problemsettings.go#L193))
concordo com eles, então um pacote que omite limites ainda funciona de maneira sensata:

- **Limite de tempo — `TimeLimit` (ms), padrão `1000`** — o tempo máximo de **CPU** que o
  O sistema operacional permite que o processo do competidor seja executado *para cada caso* antes de ser eliminado com
  **`TLE`**. Este é o tempo da CPU, não do relógio de parede, portanto, o tempo gasto dormindo ou bloqueado
  não conta contra isso.
- ** Limite de tempo total (parede geral) — `OverallWallTimeLimit` (ms), padrão
  `60000`** — o tempo máximo **real** que o aluno espera pelo problema *completo*
  para terminar antes de interrompê-lo com **`TLE`**. Qualquer caso que não foi executado
  antes deste prazo simplesmente **não é avaliado**. Para manter os resultados pelo menos
  um tanto consistente quando dispara, os casos são avaliados em **lexicográfico
  ordem **, portanto, os casos ignorados são determinísticos e não aleatórios.
- **Limite de memória — `MemoryLimit` (KiB), padrão `32768`** (ou seja, 32 MiB) — o
  RAM máxima (heap + pilha) que o sistema operacional permite que o programa use antes de eliminá-lo com
  **`MLE`**. É expresso em
  [kibibytes](https://en.wikipedia.org/wiki/Kibibyte), então `32768` KiB = 32 MiB.
- **Limite de saída — `OutputLimit` (bytes), padrão `10240`** — o máximo do programa
  pode gravar em stdout *ou* stderr antes de ser eliminado com **`OLE`**. Para comum
  problemas de token omegaUp normalmente **detecta automaticamente** isso em seus arquivos `.out` -
  ele pega o maior e adiciona 10 KiB de headroom - então você raramente o define por
  mão. **Mas se você usar um validador personalizado você deve configurá-lo explicitamente**, porque
  não há um `.out` simples para dimensionar.
- **Limite de entrada — `inputLimit` (bytes), padrão `10240`** — o comprimento máximo de
  o **código-fonte** do concorrente. Abaixe o volume quando quiser impedir as pessoas
  colar em uma tabela de respostas pré-computada em vez de realmente resolver o problema
  problema.
- **Limite de tempo do validador — `validatorTimeLimit` (ms), padrão `1000`** — quanto tempo
  o avaliador espera que um *validador personalizado* emita um veredicto para cada caso antes
  desistindo de **`JE`**.
- **Tempo de espera extra para libinteractive — `ExtraWallTime` (ms), padrão `0`** — como
  quanto tempo o avaliador espera que o programa *interator* termine cada caso (além
  limites normais) antes de interrompê-lo com **`TLE`**. Relevante apenas para
  problemas interativos.

!!! note "Validadores personalizados obtêm seus próprios limites mais generosos"
    No momento em que você muda o validador para `custom`, o omegaUp semeia um conjunto separado
    de limites para o processo *validador* — atualmente **256 MiB** de memória, um **30 s**
    Limite de tempo da CPU, tempo total de parede de **5 s** e saída de **10 KiB**
    ([`Problem.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Problem.php#L4606-L4611)).
    A ideia é que o julgamento pode se dar ao luxo de ser mais lento e mais faminto do que o
    solução do concorrente.

### Todo o resto

- **Fonte** — atribuição/origem do depoimento, mostrada aos concorrentes.
- **Aparece na listagem pública** — se o problema pode ser mostrado publicamente e
  usado em concursos e cursos de *outras pessoas*.
- **Enviar esclarecimentos por e-mail** — se a omegaUp envia um e-mail para você (o autor) quando um
  usuário pede esclarecimentos sobre esse problema.
- **Tags** — rótulos de classificação.

## O layout ZIP

Salve tudo em um arquivo **`.zip`** — não `.rar`, `.tar.bz2`, `.7z` ou
`.zx`. O nome do zip em si não importa. Um problema mínimo de linguagem
parece com isso:

```
problem.zip
├── cases/                 # Required: the .in/.out test data
│   ├── 1.in
│   ├── 1.out
│   └── …
├── statements/            # Required: at least one <locale>.markdown
│   └── es.markdown
├── solutions/             # Optional: editorial / official write-up
├── interactive/           # Optional: libinteractive bundle
├── validator.cpp          # Optional: custom validator (one of validator.<lang>)
├── settings.json          # Optional: pre-baked settings (usually generated for you)
└── testplan               # Optional: per-case weights
```
Um pacote de referência real e funcional reside no repositório em
[`frontend/tests/resources/testproblem.zip`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/resources/testproblem.zip),
e há muitos mais abaixo
[`frontend/tests/resources`](https://github.com/omegaup/omegaup/tree/main/frontend/tests/resources).

!!! aviso "`cases/` e `statements/` devem ficar na raiz"
    É *criticamente* importante que `cases/` e `statements/` estejam diretamente
    a raiz do `.zip`, sem **nenhuma** pasta intermediária envolvendo-os - isso
    já mordeu gente suficiente para ganhar seu próprio vírus,
    [omegaup#310](https://github.com/omegaup/omegaup/issues/310). No Linux/Mac o
    Uma maneira confiável de acertar é colocar `cd` no diretório do problema e executar
    `zip -r myproblem.zip *`, que compacta o *conteúdo* em vez do conteúdo
    pasta. E como o omegaUp é executado em **Linux, os nomes diferenciam maiúsculas de minúsculas**: a
    pasta chamada `Cases` não será encontrada e nem um arquivo de entrada terminando
    em `.In` em vez de `.in`.

###`cases/`

Esta pasta contém todos os casos de teste como arquivos `.in`/`.out` emparelhados. Os **nomes básicos
deve corresponder** — `1.in` com `1.out`, `hola.in` com `hola.out` — mas o nome base
em si é arbitrário. Internamente, o implantador aceita apenas arquivos que correspondam ao
expressão regular `^cases/([^/]+)\.in$`
([`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L130)),
e se a pasta estiver faltando ou vazia, o upload falhará completamente com
`cases/ directory missing or empty`
([`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L1095)).
Cada `.in` que espera envios deve ter um `.out` correspondente, ou o código de implantação
erros com `failed to find the output file for cases/<name>`.

**O `.` (ponto) em um nome de caso é reservado para agrupamento.** Não coloque um ponto em um
nome do caso, a menos que você pretenda agrupar - o texto *antes do primeiro ponto* torna-se o
**nome do grupo** (`strings.SplitN(caseName, ".", 2)[0]` em
[`common/problemsettings.go`](https://github.com/omegaup/quark/blob/main/common/problemsettings.go#L336-L342)).
Então `grupo1.caso1.in`, `grupo1.caso1.out`, `grupo1.caso2.in`, `grupo1.caso2.out`
formam **um grupo** (`grupo1`) com **dois casos**.

**Casos agrupados** existem porque às vezes o conjunto de respostas plausíveis é pequeno e
você não quer que um competidor obtenha crédito parcial em um palpite de sorte: ganhar um
pontos do grupo você deve resolver **todos os casos desse grupo**. Não há limite
o número de grupos, e os grupos podem ter diferentes números de casos.

Também não há limite rígido para o número de casos, mas **mantenha o total de casos
carga útil inferior a ~100 MB**. Mais casos significa que cada envio leva mais tempo para ser avaliado,
e em um concurso ao vivo que se traduz diretamente em tempos de espera na fila – especialmente
doloroso quando uma solução lenta vinculada ao `TLE` está à frente de todos os outros no
fila.

###`statements/`

Isso contém a declaração do problema no Markdown (o mesmo tipo que a Wikipedia usa), um
arquivo por localidade: `es.markdown`, `en.markdown`, `pt.markdown`. Pelo menos um é
necessário. Você pode visualizar exatamente como seu Markdown e LaTeX serão renderizados em
[omegaup.com/redaccion.php](https://omegaup.com/redaccion.php) — por favor, faça
isso e confirme se as tabelas de entrada/saída estão corretas, porque uma instrução distorcida
é uma experiência miserável no meio da competição.

LaTeX é totalmente suportado. Coloque nomes de variáveis em `$…$` — escreva `$n$`, `$x$`,
`$x_i$` para um subscrito – para que se destaquem da prosa e os concorrentes possam encontrar
eles de relance. Lê melhor e evita ambiguidades.

###`solutions/`

Estruturalmente idêntico ao `statements/`: o artigo oficial da solução em
Markdown, nomeado por localidade (`es.markdown` e traduções `en.markdown`,
`pt.markdown`). O pacote em
[`testproblem.zip`](https://github.com/omegaup/omegaup/blob/main/frontend/tests/resources/testproblem.zip)
inclui um exemplo de soluções.

### `interactive/` (opcional)

Problemas interativos - onde o programa do competidor fala de um lado para o outro com um
julgar o processo em vez de ler uma entrada fixa - deve ser construído com
[libinterativo](https://omegaup.com/libinteractive/); essa página documenta o
Formato da interface `.idl` e como os calços são gerados. Para um completo e real
referência de como o zip de um problema interativo está estruturado, use
[Caverna do IOI 2013](https://omegaup.com/resources/cave.zip) como modelo.

Uma conveniência que o implementador cuida para você: casos de amostra libinteractive em
`interactive/examples/` **não precisa de um `.out`** — o gitserver gera um vazio
um automaticamente
([`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L495-L514)).

### Validador personalizado (`validator.<lang>`)

Quando a comparação de tokens não é suficiente – múltiplas respostas corretas, juiz especial
pontuação, crédito parcial — envie exatamente **um** arquivo chamado `validator.<lang>` em
a **raiz** do zip, onde `<lang>` é um dos `c`, `cpp`, `java`, `p` (Pascal),
ou `py`. Você só precisa de um validador, e ele é **independente da identidade do competidor
idioma**.

Aqui está o contrato exato e vale a pena acertar:

- Seu validador lê a saída do **concorrente em seu próprio stdin** — `scanf` simples
  /`cin`/`input()`. Mentalmente, o avaliador executa o equivalente a
  `./contestant < data.in | ./validator <casename>`, onde `<casename>` é o
  nome `.in` do caso atual **sem a extensão**.
- Pode abrir um arquivo literalmente chamado **`data.in`** — a mesma entrada que foi alimentada
  o concorrente - e um arquivo chamado **`data.out`** - a saída esperada emparelhada
  com aquele `data.in`. Leia um, ambos ou nenhum.
- **deve imprimir um único float em `[0.0, 1.0]` para stdout** — a fração do
  caso o competidor tenha acertado. **Imprimir nada → `JE`.** Imprimir menos que 0 → o
  a pontuação é fixada em 0; imprima mais de 1 → fixado em 1.
- O validador é executado **dentro da mesma sandbox** dos programas concorrentes. Se *o
  o próprio validador* se comporta mal (`WA`, `RFE`, `RTE`, …), o envio é julgado
  **`JE`** — portanto, um validador com erros falha ruidosamente, em vez de pontuar incorretamente silenciosamente.
- **Você ainda deve enviar arquivos `.out` mesmo que eles não sejam usados** para
  comparação. Arquivos vazios estão bem; eles apenas precisam existir, então o emparelhamento de casos
  consegue.

Um validador para [sumas](https://omegaup.com/arena/problem/sumas) (leia dois
inteiros, imprima sua soma) em C++ 17 - observe como ele lê o `a` e `b` originais
de `data.in`, a soma esperada de `data.out`, a resposta do competidor de
stdin e imprime `1.0` ou `0.0`:

```c++
#include <iostream>
#include <fstream>

int main() {
  // read "data.in" to get the original input.
  int64_t a, b;
  {
    std::ifstream original_input("data.in", std::ifstream::in);
    original_input >> a >> b;
  }
  // you can store anything that helps you evaluate in "data.out".
  int64_t sum;
  {
    std::ifstream original_output("data.out", std::ifstream::in);
    original_output >> sum;
  }

  // read standard input to get the contestant's output.
  int64_t contestant_sum;
  if (!(std::cin >> contestant_sum)) {
    // anything you print to cerr is ignored, but it's useful for debugging.
    std::cerr << "Error reading the contestant's output\n";
    std::cout << 0.0 << '\n';
    return 0;
  }

  // determine whether the answer is incorrect.
  if (sum != contestant_sum && sum != a + b) {
    std::cerr << "Incorrect output\n";
    std::cout << 0.0 << '\n';
    return 0;
  }

  // If execution reaches here, the contestant's output is correct.
  std::cout << 1.0 << '\n';
  return 0;
}
```
O mesmo validador em Python 3:

```python
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import sys

def _main():
  # read "data.in" to get the original input.
  with open('data.in', 'r') as f:
    a, b = [int(x) for x in f.read().strip().split()]
  # you can store anything that helps you evaluate in "data.out".
  with open('data.out', 'r') as f:
    expected_sum = int(f.read().strip())

  score = 0
  try:
    # Read the contestant's output.
    contestant_sum = int(input().strip())

    # Determine whether the output is incorrect.
    if contestant_sum not in (expected_sum, a + b):
      # Anything printed to sys.stderr is ignored, but useful for debugging.
      print('Incorrect output', file=sys.stderr)
      return

    # If execution reaches here, the contestant's output is correct.
    score = 1
  except:
    logging.exception("Error reading the contestant's output")
  finally:
    print(score)

if __name__ == '__main__':
  _main()
```
### `testplan` (opcional)

Por padrão **cada caso vale `1/number-of-cases`** — o implementador atribui cada
caso, um peso de `1/1` e a niveladora normaliza todos os pesos para que somam 1
(`AddCaseName(caseName, big.NewRat(1, 1), false)` em
[`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L453-L461),
pesos divididos pelo total em
[`common/literalinput.go`](https://github.com/omegaup/quark/blob/main/common/literalinput.go#L317-L333)).
Quando você quiser que os casos sejam ponderados de forma desigual, descarte um arquivo chamado **`testplan`** (sem
extensão) na raiz do zip, uma linha por caso: o nome do arquivo do caso
**sem a extensão**, espaço em branco e depois o número de pontos. Para um problema
com casos `cases/caso1.in`, `cases/grupo2.caso1.in`, `cases/grupo2.caso2.in`:

```
caso1 5
grupo2.caso1 10
grupo2.caso2 0
```
Algumas coisas que o analisador
([`NewCaseWeightMappingFromTestplan`](https://github.com/omegaup/quark/blob/main/common/problemsettings.go#L305-L334))
realmente impõe, comparando cada linha com
`^\s*([^#[:space:]]+)\s+([0-9.]+)\s*$`:

- **Sem espaços nos nomes dos arquivos do caso** — o token do nome do caso não pode conter
  espaço em branco.
- **`#` inicia um comentário** — uma linha cujo primeiro caractere sem espaço é `#` (e qualquer
  linha que não corresponde ao padrão) é ignorada, para que você possa anotar seu
  plano de teste.
- O `testplan` e o `.zip` devem **concordar no conjunto de casos**. gitserver é executado
  uma *diferença simétrica* nos dois sentidos
  ([`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L463-L488)):
  um caso no plano de teste, mas ausente no `cases/` falha com
  `testplan missing case "<name>"`, e um case em `cases/`, mas ausente do
  testplan falha com `.zip missing case "<name>"`. Você não pode especificar pela metade.

**Para pontuar um grupo inteiro** sem dividir os pontos entre os casos, o
convenção é colocar a pontuação total do grupo no **primeiro** caso e **0** em todos
os outros - como `grupo2.caso1 10` / `grupo2.caso2 0` faz acima.

Isso interage com a **política de pontuação** do grupo, um dos dois valores em
[`ProblemParams.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/ProblemParams.php#L48-L49):
`sum-if-not-zero` (o padrão — um grupo pontua a **soma** das pontuações de seus casos,
mas somente se forem *todos* diferentes de zero) ou `min` (o grupo pontua o **mínimo** de
a pontuação de seus casos vezes o peso do grupo). O padrão é por que o
A convenção "pontos no primeiro caso, zero no resto" funciona: resolva o todo
grupo e você coleta o peso total; perder qualquer caso e o grupo entra em colapso para
zero.

### `settings.json` (geralmente gerado, ocasionalmente escrito à mão)

Na maioria das vezes você *nunca* escreverá este arquivo — é o artefato compilado gitserver
produz a partir de seu `cases/`, `testplan` e limites, organizados em
[`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go#L580-L597).
Sua forma é a estrutura `ProblemSettings`
([`common/problemsettings.go`](https://github.com/omegaup/quark/blob/main/common/problemsettings.go#L174-L182)):
um bloco `Limits`, um bloco `Validator` (`Name`, `Tolerance`, opcional
`GroupScorePolicy`, validador personalizado opcional `Limits`), uma matriz de grupos `Cases`
cada um com seus casos ponderados e - para problemas interativos - um `Interactive`
bloco. Se você *enviar* seu próprio `settings.json`, o gitserver o lê, então ainda assim
permite que um `testplan` substitua os pesos do gabinete em cima dele. De qualquer forma, apenas o
`settings.json` gerado sobrevive no repositório de problemas implantado.

## Imagens

omegaUp tem suporte nativo a imagens :). Para incorporar uma imagem em uma declaração, adicione o
arquivo de imagem para seu zip **dentro de `statements/`** e referenciá-lo em seu
`es.markdown` com Markdown normal:

```markdown
![Alt text](image.jpg)
```
Os formatos suportados são **jpg, gif, png**. Cuidado com o tamanho – Markdown **não**
redimensione-o - portanto, mantenha as imagens com largura igual ou inferior a **650 pixels**.

## Exemplo de zips

Os zips que o omegaUp usa em seus próprios testes são os melhores modelos para copiar:
[`frontend/tests/resources`](https://github.com/omegaup/omegaup/tree/main/frontend/tests/resources).

## Problemas de Karel

Primeiro, tente [karel.js](https://omegaup.com/karel.js/) — ele converte casos para
você e é muito menos problemático do que o que se segue.

Se você já tem seus casos e prefere não recriá-los em karel.js, o
as etapas abaixo são para **Windows** e supõem que você tenha o **Python 2.7** instalado e ativado
seu `PATH` (o caminho de instalação padrão normalmente é `C:\Python27`); verifique se você pode
execute `python` no console DOS antes de iniciar.

1. Tenha estes arquivos em mãos:
   [o kit de ferramentas Karel](https://docs.google.com/file/d/0B6Rb3__ksbxDRC1VSDV0amRYNmc/edit?usp=sharing) —
   `karel.exe` (executa uma solução em um mundo), `kcl.exe` (a solução
   compilador), o script Python `karel_mdo_convert.py` e o wrapper
   `karel-to-omegaup.bat` que os une.
2. Coloque seus casos MDO e KEC em uma pasta. Para gerá-los você pode usar o
   Karel de criação de casos de [KarelOMI.zip](http://www.cimat.mx/~amor/Omi/Utilerias/KarelOMI.zip).
3. Você também precisa da sua **solução**. Se você programa em Java, dê uma olhada na solução
   Extensão `.JS` (então `kcl.exe` a interpreta como karel-java); para Pascal, use
   `.PAS` (karel-pascal).
4. Coloque os exes, o script Python e o `.bat`, todos na mesma pasta.
5. Execute `karel-to-omegaup.bat` sem argumentos e ele solicitará o
   caminho da solução e o caminho dos casos, ou passe-os na linha de comando -
   citar caminhos que contêm espaços:

   ```
   karel-to-omegaup.bat "karel vs chuzpa\solucion.js" "karel vs chuzpa\casos"
   ```
6. Com tudo pronto, o script primeiro compila a solução com `kcl.exe`
   (produzindo um `.KX`), então constrói os mundos `.IN` a partir de cada `.MDO` nos casos
   pasta. Observe que o conversor Python precisa que o `.KEC` correspondente exista: para
   `caso1.MDO` você também deve ter `caso1.KEC`. Deles extrai bipes,
   orientação e posição em cada `.IN`.
7. Em seguida, ele executa `karel.exe` com cada `.IN` gerado e o `.KX` compilado
   solução para produzir o `.OUT` correspondente - portanto, uma solução *correta* é essencial,
   já que as saídas são tão corretas quanto são.
8. O `.bat` coloca uma pasta `cases` (com os pares `.IN`/`.OUT`) dentro do seu
   diretório de casos.
9. Finalmente, adicione uma pasta `statements` com `es.markdown` e compacte-a exatamente como
   você teria um problema de idioma.

## Como tudo acontece

Para fechar o ciclo: quando você faz upload, o gitserver
[`ziphandler.go`](https://github.com/omegaup/gitserver/blob/main/ziphandler.go)
descompacta o arquivo, valida que `cases/` existe e cada caso enviado tem
seu `.out`, dobra `testplan`/`settings.json` em um `settings.json` canônico,
compromete tudo como uma nova revisão do repositório git do problema, e
exclui o `testplan` agora redundante. Na hora da aula, o frontend do PHP
(`\OmegaUp\Controllers\Run::apiCreate` →
[`\OmegaUp\Grader::grade`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Grader.php))
entrega o envio ao avaliador Go por HTTP, que lê `settings.json`,
normaliza os pesos dos casos para somar 1, executa cada caso na sandbox em relação
seus limites, aplica o validador e acumula as pontuações por caso através do
política de pontuação do grupo. Cada caminho e extensão neste documento existem para fazer isso
o pipeline é resolvido corretamente - e é por isso que acertá-los é importante.

## Documentação relacionada

- **[Criando problemas](creating-problems.md)** — o fluxo de trabalho de autoria e caminhos de UI
- **[Veredictos](../verdicts.md)** — o que `AC`, `TLE`, `MLE`, `OLE`, `JE` e o resto significam
