---
title: Arquivos de dados de documentação GSoC
description: Como omegaUp gera páginas anuais do GSoC a partir de dados JSON
icon: bootstrap/code
---
# Arquivos de dados de documentação do GSoC

Todos os anos, a omegaUp realiza uma campanha Google Summer of Code, e todos os anos os documentos precisam de uma página por ano: uma página "atual" cheia de ideias de projetos e o funil de aplicação enquanto a campanha está ativa, e uma página "passada" enxuta listando o que foi enviado quando terminou. Em vez de escrever essas páginas à mão e deixar seus títulos se separarem, mantemos o conteúdo específico do ano em um único arquivo de dados JSON e eliminamos o Markdown dele com um pequeno gerador Python. Pense no `scripts/generate-gsoc-pages.py` como um pequeno compilador de modelos cuja única linguagem de modelo são strings F do Python e cuja única entrada é `_data/gsoc-data.json` - sem Jinja, sem plugin Zensical, nada além da biblioteca padrão, então ele roda em um `python3` simples com zero `pip install`.

A coisa toda é deliberadamente pequena (cerca de 180 linhas) porque é uma **ferramenta de andaime, não um renderizador ao vivo**. Ele não é executado em tempo de construção - `build_all.py` nunca o chama (faça um grep e você não encontrará nenhuma referência). Você o executa manualmente ao adicionar ou rolar um ano, revisa o Markdown que ele exibe, faz o polimento manual e confirma o resultado. Essa distinção é importante, e voltaremos a ela abaixo, porque as páginas atualmente comprometidas no `docs/en/community/gsoc/` são consideravelmente mais ricas do que qualquer coisa que o gerador emita hoje.

## O modelo mental de uma linha

`gsoc-data.json` é a fonte da verdade para o *esqueleto* da página de cada ano; o gerador percorre `data["years"]` e, para cada ano, despacha em seu campo `type` para uma das duas funções que constroem o Markdown linha por linha. `type: "current"` recebe tratamento completo (ideias de projetos + processo de inscrição em quatro fases + comunicações + FAQ + documentos relacionados); qualquer outra coisa obtém o layout "passado" simplificado (projetos concluídos com resultados + documentos relacionados).

## O que o gerador realmente faz, de ponta a ponta

O ponto de entrada é `main()` na parte inferior do `scripts/generate-gsoc-pages.py`. Em ordem:

1. **Ele resolve caminhos relativos ao próprio script**, não ao diretório de trabalho do seu shell. `PROJECT_ROOT = Path(__file__).parent.parent` (a raiz do repositório, um nível acima de `scripts/`) e, em seguida, codifica `DATA_FILE = PROJECT_ROOT / "docs" / "community" / "gsoc" / "_data" / "gsoc-data.json"` e `OUTPUT_DIR = PROJECT_ROOT / "docs" / "community" / "gsoc"`. **Leia esses dois caminhos com atenção** — eles não correspondem mais ao repositório e essa é a primeira coisa que irá incomodar você. Mais sobre isso em [A pegadinha do caminho obsoleto](#the-stale-path-gotcha-read-this-before-you-run-it).

2. **Ele falha ruidosamente se o arquivo de dados estiver faltando.** Antes de fazer qualquer coisa, `main()` verifica `DATA_FILE.exists()`; caso contrário, imprime `Error: Data file not found: <path>` mais `Please create the data file first.` e chama `sys.exit(1)`. Portanto, um arquivo de dados ausente ou extraviado é uma parada brusca, e não uma operação silenciosa.

3. **Ele analisa JSON e apenas JSON.** `load_data()` faz um `json.load()` simples em `DATA_FILE`. Se o JSON estiver malformado, `main()` captura o `json.JSONDecodeError` e imprime `Error: Invalid JSON in data file: <message>` antes de sair do `1`, portanto, uma vírgula à direita fornece um diagnóstico real em vez de um rastreamento. Observe o que *não* lê: o irmão `gsoc-data.yaml`. Esse arquivo YAML é um espelho amigável que mantemos para conveniência de edição (é comentado, é diferenciável), mas o gerador nunca o toca - não há `import yaml` em nenhum lugar do script, precisamente para que a ferramenta permaneça apenas na biblioteca padrão. Se você editar o YAML e esquecer o JSON, nada muda. **O JSON é a entrada; o YAML é uma cópia de cortesia.**

4. **Ele gera o ano mais novo primeiro.** `main()` itera `sorted(data["years"].keys(), reverse=True)`, então `"2025"`, depois `"2024"` e depois `"2023"`. Esta é uma classificação de string pelas chaves do ano, que é correta para anos de quatro dígitos; afeta apenas a ordem do console, não os próprios arquivos de saída.

5. **Para cada ano, `generate_page()` despacha em `type`.** Ele puxa `year_data = data["years"][year]` e ramifica: `if year_data["type"] == "current"` chama `generate_current_year_page()`, `else` chama `generate_past_year_page()`. Observe o `else` — o despacho é "atual versus *tudo que não é atual*". Portanto, `"type": "past"` e um erro de digitação como `"type": "pastt"` caem no layout anterior. Não há validação que detecte um tipo digitado incorretamente; você apenas obtém silenciosamente uma página anterior. Ele grava o resultado em `OUTPUT_DIR / f"{year}.md"` e imprime `✓ Generated <path>`.

Ao terminar, imprime `✓ All GSoC pages generated successfully!` e um lembrete para revisar e enviar os arquivos. Nada é preparado no git para você - isso é por sua conta.

## Os dois layouts, campo por campo

O verdadeiro valor do ensino é saber exatamente qual chave JSON se torna qual parte do Markdown, porque é isso que você está editando às cegas quando toca no arquivo de dados.

### Página do ano atual — `generate_current_year_page()`

Dado um ano `type: "current"`, a função emite, nesta ordem fixa:

- **Frontmatter** criado a partir de três chaves: `title`, `description` e um `icon: material/school` codificado. (Observe esse ícone - consulte [Deslocamento do ícone](#icon-drift) abaixo; as páginas comprometidas não usam `material/school`.)
- **`# {title}`** como H1, depois uma linha em branco e, em seguida, a string `intro` bruta literalmente. O `intro` é de passagem Markdown, portanto, os links e a ênfase dentro dele sobrevivem.
- **`## Project Ideas`** — sempre emitido, mesmo que não haja ideias. As próprias ideias vêm do `year_data.get("project_ideas", [])`, portanto, uma chave ausente fornece uma seção vazia em vez de uma falha. Cada objeto de ideia se torna:
    ```
    ### {name}
    {description}

    **Skills**: {skills}
    **Size**: {size}
    **Level**: {level}
    ```
Uma pegadinha sutil de renderização reside aqui: `**Skills**`, `**Size**` e `**Level**` são emitidos em três linhas consecutivas sem **nenhuma linha em branco entre eles**, então Markdown os recolhe em um parágrafo moldado suavemente. É por isso que os dados de origem mantêm cada um desses valores curtos — `"350 hours"`, `"Advanced"`, `"Vue.js, TypeScript, PHP"` — em vez de tentar separá-los em linhas visuais.
- **`## Application Process`** — construído a partir do `year_data.get("application_process", {})`. A função percorre a lista literal fixa `["phase1", "phase2", "phase3", "phase4"]` e emite apenas as fases presentes, nessa ordem. Duas consequências que valem a pena internalizar: uma chave `phase5` seria **ignorada silenciosamente** (o loop nunca a procura) e as fases são renderizadas na ordem `phase1..phase4`, independentemente da ordem em que aparecem no JSON. Dentro de cada fase ele emite `### {title}`, então — se a fase tiver um array `steps` — uma lista numerada (`enumerate(..., 1)`), e/ou — se tiver uma string `description` — essa descrição como um parágrafo. Ambos podem coexistir; uma fase sem nenhum dos dois apenas contribui com seu título. É por isso que as fases 1–3 nos dados ao vivo usam `steps` (listas de verificação concretas), enquanto `phase4` usa um único `description` (a sinopse da entrevista).
- **`## Communications`** — emitido apenas `if "communications" in year_data`, como uma lista com marcadores onde cada entrada da matriz é impressa literalmente após `- `. As entradas já são Markdown (`"**Discord**: [Join our Discord server](...)"`), então o negrito e os links são seus para escrever nos dados.
- **`## FAQ`** — emitido apenas `if "faq" in year_data`. Cada item se torna `**{question}**` em uma linha e `{answer}` na próxima - novamente sem nenhuma linha em branco entre eles, então a pergunta e a resposta são renderizadas como um parágrafo, com a pergunta em negrito.
- **`## Related Documentation`** — emitido apenas `if "related_docs" in year_data`, cada entrada como `- **{doc}**`. Como toda a string `doc` é agrupada em `**...**`, a entrada *inteira* (texto do link *e* o "- descrição" final) aparece em negrito. Essa é uma peculiaridade do modelo atual, e não uma escolha de design que valha a pena defender.

### Página do ano passado — `generate_past_year_page()`

Qualquer coisa que não seja `current` obtém o layout enxuto: o mesmo frontmatter de três teclas e cabeçalho `# {title}` / `intro` e, em seguida, **`## Projects`** construído a partir de `year_data.get("projects", [])`. Cada objeto do projeto é apenas:

```
### {name}
{description}

**Result**: {result}
```
Em seguida, o mesmo bloco opcional **`## Related Documentation`**. Esse é todo o modelo anterior – sem habilidades, sem fases, sem perguntas frequentes. A divisão mental é: uma página *atual* é um funil de recrutamento, uma página *passada* é um currículo.

## O esquema de dados

Tudo depende de um objeto `years` de nível superior codificado por sequências de anos de quatro dígitos. Cada ano tem uma de duas formas.

Um ano **atual** (veja `2025` nos dados ao vivo):

```json
"2025": {
  "type": "current",
  "title": "GSoC 2025",
  "description": "Google Summer of Code 2025 program at omegaUp",
  "intro": "omegaUp is participating in Google Summer of Code 2025! ...",
  "project_ideas": [
    {
      "name": "AI Teaching Assistant",
      "description": "Create a bot that can answer clarifications ...",
      "skills": "Python, PHP, MySQL, LLM Prompt Engineering, REST APIs",
      "size": "350 hours",          // free text; GSoC sizes are 90 / 175 / 350 hours
      "level": "Advanced"           // free text; e.g. "Medium", "High", "Medium to Advanced"
    }
  ],
  "application_process": {
    "phase1": { "title": "...", "steps": ["...", "..."] },   // steps -> numbered list
    "phase4": { "title": "...", "description": "..." }         // description -> paragraph
  },
  "communications": ["**Discord**: [...](...)"],   // verbatim Markdown bullets, optional
  "faq": [ { "question": "...", "answer": "..." } ], // optional
  "related_docs": ["[Getting Started](../getting-started/index.md) - Development setup"]
}
```
Um ano **último** (consulte `2023` / `2024`):

```json
"2024": {
  "type": "past",
  "title": "GSoC 2024",
  "description": "Google Summer of Code 2024 projects",
  "intro": "Projects completed during GSoC 2024.",
  "projects": [
    {
      "name": "Migrate Problem Creator to Vue.js + TypeScript",
      "description": "Migrated the Problem Creator ...",
      "result": "Problem Creator can now be used directly on omegaUp.com ..."
    }
  ],
  "related_docs": ["[GSoC 2025](../community/gsoc/2025.md) - Current year program"]
}
```
`type`, `title`, `description` e `intro` são as únicas chaves que o gerador desreferencia diretamente (`year_data['title']`, etc.), portanto, essas quatro são efetivamente **obrigatórias** — omita uma e você obterá um `KeyError`. Todo o resto (`project_ideas`, `application_process`, `communications`, `faq`, `related_docs`, `projects`) é lido através de `.get(...)` ou protegido por um `if ... in year_data`, então é tudo opcional e degrada para uma seção vazia (ou ausente).

Uma coisa que o esquema *não* codifica: os links relativos dentro das etapas `related_docs`, `application_process` e `communications` são gravados da perspectiva do próprio diretório da página do ano (`../getting-started/...`, `../index.md` e irmão `2025.md`). Se você mover para onde as páginas são geradas, esses links se moverão com elas e poderão quebrar – verifique-os com `scripts/verify_docs_nav.py` após a regeneração.

## Adicionando um novo ano

Quando uma nova campanha é aberta, você faz duas edições e acumula um ano:

1. **Adicione o novo ano atual** a `gsoc-data.json`. Dê `"type": "current"`, preencha `title`/`description`/`intro` e preencha `project_ideas`, `application_process` (fases `phase1` – `phase4`), `communications`, `faq` e `related_docs`. Mantenha os valores `skills`/`size`/`level` curtos (eles são colados na renderização).
2. **Rebaixar a página do ano passado para o passado.** Mude o `"type"` do ano anterior de `"current"` para `"past"` e troque seu `project_ideas` por uma matriz `projects` onde cada objeto carrega `name` / `description` / `result` descrevendo o que realmente foi enviado. O modelo anterior ignora `project_ideas` totalmente, portanto, deixar o array antigo no lugar apenas torna os dados mortos – exclua-os.
3. **Espelhe a alteração em `gsoc-data.yaml`** para que a cópia editável por humanos não apodreça. Esta é uma cortesia manual — o gerador não fará isso e não lerá — mas a próxima pessoa a editar irá buscar o YAML primeiro.
4. **Regenerar** e depois revisar a comparação. Veja a advertência do caminho imediatamente abaixo antes de executar qualquer coisa.
5. **Polir manualmente e confirmar os arquivos `YYYY.md`.** A saída do gerador é um esqueleto inicial; as páginas comprometidas contêm seções extras (tabelas de estatísticas, listas de conquistas, comparações de benefícios) que não existem no arquivo de dados. Não espere que a regeneração os reproduza.

Como omegaUp mantém quatro localidades (`docs/en`, `docs/es`, `docs/pt`, `docs/pt-BR`), cada uma com seu próprio `_data/gsoc-data.json`, "adicionar um ano" significa repetir as etapas 1 a 5 por localidade que você mantém - o gerador não tem noção de localidade, ele apenas é executado em qualquer JSON único para o qual seu `DATA_FILE` aponta. `scripts/translate_docs.py` lida com a tradução em massa de prosa, mas os dados estruturados do ano são editados manualmente por localidade.

## O caminho obsoleto, peguei - leia isto antes de executá-lo

Aqui está a vantagem. O `DATA_FILE` do script é codificado para:

```
docs/community/gsoc/_data/gsoc-data.json
```
Mas a árvore de documentos foi reorganizada em raízes por localidade (`docs/en/…`, `docs/es/…`, `docs/pt/…`, `docs/pt-BR/…`) e `docs/community/` **não existe mais**. Portanto, executar o script conforme confirmado, de qualquer lugar, fornece:

```
$ python3 scripts/generate-gsoc-pages.py
Error: Data file not found: /…/ou-documentation/docs/community/gsoc/_data/gsoc-data.json
Please create the data file first.
```
Esse erro não é "você esqueceu de criar o arquivo" - é "o gerador foi escrito antes dos documentos serem divididos por idioma e suas duas constantes de caminho nunca foram atualizadas". Os arquivos reais ficam em `docs/<lang>/community/gsoc/_data/gsoc-data.json`. Para realmente usar o gerador hoje, você precisa apontar novamente `DATA_FILE` e `OUTPUT_DIR` em um local específico, por exemplo:

```python
DATA_FILE  = PROJECT_ROOT / "docs" / "en" / "community" / "gsoc" / "_data" / "gsoc-data.json"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "en" / "community" / "gsoc"
```
e execute-o uma vez por localidade. Uma correção adequada usaria o código do idioma como um argumento e um loop, mas no momento em que este livro foi escrito, o script ainda era de caminho único e cego ao local. Trate as constantes confirmadas como um bug para contornar, não como um layout confiável.

## Mais dois desvios para conhecer

### Desvio de ícone

O gerador codifica `icon: material/school` no frontmatter de cada página que ele emite. As páginas realmente comprometidas em `docs/en/community/gsoc/` usam `icon: bootstrap/school` - todo o site de documentos padronizado no conjunto de ícones `bootstrap/…` (veja qualquer irmão em `docs/en/development/`, por exemplo, `icon: bootstrap/terminal`). Portanto, páginas recém-geradas aparecem com o namespace de ícone errado e precisam de uma correção de uma linha, ou a string frontmatter do gerador precisa ser atualizada para `bootstrap/school`. Até que alguém faça o último, espere corrigi-lo manualmente a cada regeneração.

### As páginas comprometidas são mais ricas que o gerador

Se você comparar uma página comprometida com o que o gerador produziria, elas não corresponderão – e isso é esperado. Veja `docs/en/community/gsoc/2023.md`: o layout anterior do gerador forneceria dois blocos `### {name}` com uma descrição de uma linha e um `**Result**:` cada. A página comprometida, em vez disso, tem um aprofundamento em **Conformidade COPPA**, listas de marcadores de "Principais Conquistas" e "Implementação Técnica", uma tabela de benefícios Selenium-vs-Cypress, uma seção "Ideias de Projeto (2023)" e uma tabela de estatísticas - nenhuma das quais existe em qualquer lugar no `gsoc-data.json`. Da mesma forma, `2026.md` está confirmado e ativo, embora o ano mais recente do arquivo de dados ainda seja `2025`.

Conclusão: o gerador é uma **ferramenta de bootstrap para o esqueleto inicial de uma página anual**, não o renderizador oficial das páginas que você vê no site. A regeneração *sobrescreverá* essas seções feitas à mão pelo modelo simples. Portanto, antes de executá-lo novamente em um ano que já foi enriquecido manualmente, certifique-se de estar preparado para reaplicar (ou restaurar git) o ​​conteúdo mais rico - ou, melhor, apenas regenerar anos genuinamente novos.

## Layout do arquivo

```
docs/<lang>/community/gsoc/
├── _data/
│   ├── gsoc-data.json   # the generator's input (JSON only)
│   └── gsoc-data.yaml   # human-editable mirror; NOT read by the generator
├── index.md             # public hub (cards + links) — hand-written, not generated
├── 2023.md              # generated skeleton, then hand-enriched
├── 2024.md
├── 2025.md
├── 2026.md
└── …
```
Uma regra permanente para esta pasta: **nunca coloque um `README.md` próximo a `index.md`.** Zensical trata `README.md` como o índice da seção, portanto, ele reivindicaria o URL `/community/gsoc/` e ocultaria o hub `index.md` real. Se a página de destino “desaparecer”, um `README.md` perdido é a primeira coisa a verificar.

## Notas

- O gerador é uma biblioteca padrão pura (`json`, `sys`, `pathlib`) - sem dependências, sem necessidade de virtualenv. Essa restrição é a razão pela qual ele lê JSON e não o espelho YAML mais amigável.
- Não roda durante `build_all.py`; a regeneração é sempre uma etapa manual deliberada que você revisa antes de se comprometer.
- Confirme os arquivos `YYYY.md` gerados (e polidos manualmente) junto com a alteração dos dados para que o site e sua fonte permaneçam sincronizados.
</content>
</invoke>
