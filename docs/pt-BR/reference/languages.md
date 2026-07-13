---
title: Idiomas Suportados
description: Linguagens de programação suportadas pelo omegaUp
icon: bootstrap/code-tags
---
# Idiomas Suportados

omegaUp aceita envios em um conjunto fixo de idiomas — a coluna `language` em uma execução é
um enum, portanto, um envio é sempre um dos identificadores abaixo e nada mais. A lista
abaixo está esse enum, exatamente como o banco de dados o define. Quando você envia através do
[API](api.md), você passa um desses identificadores curtos (por exemplo, `cpp17-gcc`), não um
nome legível por humanos.

Duas convenções se aplicam a todas as linguagens compiladas e enganam as pessoas se não o fizerem
conheça-os:

- **Seu ponto de entrada deve se chamar `Main`.** Não há configuração de compilação por problema;
  o executor compila por convenção. O arquivo fonte principal (e, para idiomas que precisam dele,
  a classe principal) deve ser nomeada `Main` — `Main.java` com `public class Main`, um `Main`
  executável para C/C++ e assim por diante. Consulte [Interiores do Runner](../architecture/runner-internals.md)
  para saber como a compilação realmente acontece dentro da sandbox.
- **Quando uma linguagem oferece GCC e Clang**, o identificador nomeia o conjunto de ferramentas
  explicitamente (`-gcc` vs `-clang`), porque os dois ocasionalmente discordam no limite
  conformidade com o padrão e um criador de problemas pode ter testado um deles.

## Os idiomas

### C e C++

Os burros de carga da programação competitiva e a razão pela qual a lista C++ é tão longa - cada um
a revisão padrão é um identificador separado, portanto, um problema mais antigo continua sendo compilado da maneira que foi
sempre fiz:

| Identificador | Idioma |
| ---------- | -------- |
| `c` | C (GCC legado) |
| `c11-gcc`, `c11-clang` | C11 |
| `cpp` | C++ (GCC legado) |
| `cpp11`, `cpp11-gcc`, `cpp11-clang` | C++11 |
| `cpp17-gcc`, `cpp17-clang` | C++17 |
| `cpp20-gcc`, `cpp20-clang` | C++20 |

Para novos envios em C++, você quase sempre deseja `cpp17-gcc` ou `cpp20-gcc`.

### Outras linguagens de uso geral

| Identificador | Idioma |
| ---------- | -------- |
| `java` | Java |
| `kt` | Kotlin |
| `py3` | Pitão 3 |
| `py2` | Pitão 2 |
| `py` | Python (alias legado) |
| `cs` | C# |
| `rb` | Rubi |
| `pl` | Perl |
| `pas` | Pascal |
| `hs` | Haskel |
| `lua` | Lua |
| `go` | Vá |
| `rs` | Ferrugem |
| `js` | JavaScript |

### Os especiais

Três identificadores não são linguagens de uso geral, e saber o que são explica uma
muito sobre para quem o omegaUp foi criado:

- **`kp` e `kj` — Karel.** omegaUp surgiu da Olimpíada Mexicana de Informática, cujo
  o curso básico usa **Karel the Robot**, uma linguagem de ensino onde você programa um robô
  em uma grade. `kp` é Karel com sintaxe com sabor Pascal e `kj` é Karel com sabor Java
  sintaxe - a mesma linguagem, duas gramáticas de superfície, para que um iniciante possa usar qualquer que seja sua
  aula ministrada. Os problemas de Karel são um cidadão de primeira classe, não uma novidade.
- **`cat` — somente saída.** Para problemas em que você não envia nenhum programa, você envia
  a *resposta*. A "linguagem" `cat` significa que o executor simplesmente trata seu envio como o
  saída a ser validada em relação à saída esperada. É assim que somente saída e
  problemas de arquivo de dados funcionam.

!!! observe "O conjunto muda com o tempo"
    Novos padrões e conjuntos de ferramentas são adicionados à medida que amadurecem (a lista C++ é a mais clara
    registro disso). Trate a tabela acima como atual; a fonte oficial é o
    Enumeração `language` em [`frontend/database/schema.sql`](https://github.com/omegaup/omegaup/blob/main/frontend/database/schema.sql)
    e as versões do compilador configuradas no executor ([omegaup/quark](https://github.com/omegaup/quark)).
