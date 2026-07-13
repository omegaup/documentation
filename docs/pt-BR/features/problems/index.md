---
title: Problemas
description: Criando e gerenciando problemas de programação no omegaUp
icon: bootstrap/puzzle
---
# Problemas

omegaUp suporta a criação de problemas de programação através de dois métodos: o visual Problem Creator (CDP) ou a geração manual de arquivo ZIP.

## Métodos de criação de problemas

### criador de problemas omegaUp (CDP)

O [Problem Creator](https://omegaup.com/problem/creator) é uma ferramenta visual para criar problemas:

- ✅ Interface amigável
- ✅ Fluxo de trabalho intuitivo
- ⚠️ Algumas limitações (por exemplo, sem problemas de Karel)

!!! dica "Tutorial"
    Assista [este tutorial em vídeo](https://www.youtube.com/watch?v=cUUP9DqQ1Vg) para aprender como usar o Problem Creator.

### Geração manual de arquivo ZIP

Para casos de uso avançados, você pode criar manualmente um arquivo `.zip`:

- ✅ Controle total sobre a estrutura do problema
- ✅ Suporta todos os tipos de problemas, incluindo Karel
- ✅ Validadores personalizados e casos de teste

Consulte [Formato do problema](problem-format.md) para obter instruções detalhadas.

## Componentes do problema

Um problema consiste em:

- **Declaração**: Descrição do problema (Markdown)
- **Casos de teste**: Arquivos de entrada/saída (`.in`/`.out`)
- **Validador**: como os resultados são comparados
- **Limites**: restrições de tempo e memória
- **Idiomas**: linguagens de programação suportadas

## Documentação Relacionada

- **[Criando Problemas](creating-problems.md)** - Guia de criação passo a passo
- **[Formato do problema](problem-format.md)** - Estrutura e formato do arquivo ZIP
- **[API de problemas](../../reference/api.md)** - Endpoints de API para problemas
