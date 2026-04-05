---
title: Criando Problemas
description: Guia passo a passo para criar problemas de programação
icon: bootstrap/plus-circle
---
# Criando Problemas

Este guia orienta você na criação de problemas de programação no omegaUp.

## Início rápido

A maneira mais fácil de criar um problema é usando o [Problem Creator (CDP)](https://omegaup.com/problem/creator):

1. Visite [omegaup.com/problem/creator](https://omegaup.com/problem/creator)
2. Preencha os detalhes do problema
3. Adicione casos de teste
4. Configure limites e idiomas
5. Faça upload e publique

!!! dica "Vídeo Tutorial"
    Assista [este tutorial](https://www.youtube.com/watch?v=cUUP9DqQ1Vg) para uma explicação visual.

## Componentes do problema

### Elementos obrigatórios

- **Título**: Nome do problema
- **Alias**: identificador curto (usado em URLs)
- **Declaração**: Descrição do problema (Markdown suportado)
- **Casos de teste**: arquivos de entrada/saída
- **Validador**: como os resultados são comparados
- **Limites**: restrições de tempo e memória

### Elementos Opcionais

- **Fonte**: Origem do problema (por exemplo, "OMI 2020")
- **Tags**: tags de categorização
- **Código validador**: programa validador personalizado
- **Verificador**: verificador de saída personalizado

## Tipos de validadores

| Tipo | Descrição |
|------|-------------|
| `literal` | Correspondência exata |
| `token` | Comparação token por token |
| `token-caseless` | Comparação de tokens sem distinção entre maiúsculas e minúsculas |
| `token-numeric` | Comparação numérica com tolerância |
| `custom` | Validador definido pelo usuário |

## Limites de problemas

Configure limites apropriados:

- **Tempo Limite**: Tempo de execução por caso de teste (milissegundos)
- **Limite de memória**: limite de uso de memória (KB)
- **Limite de saída**: Tamanho máximo de saída (bytes)

## Idiomas Suportados

omegaUp suporta muitas linguagens de programação:

- C, C++ (vários padrões)
-Java, Kotlin
-Píton 2/3
-Rubi, Perl
- C#, Pascal
-Karel (Karel.js)
- E mais...

## Avançado: Criação Manual de ZIP

Para casos de uso avançados, consulte [Formato do problema](problem-format.md) para criação manual de arquivo ZIP.

## Documentação Relacionada

- **[Formato do problema](problem-format.md)** - Estrutura do arquivo ZIP
- **[API de problemas](../../api/problems.md)** - Pontos de extremidade da API
- **[Formato do problema (ZIP)](problem-format.md)** — layout manual do ZIP
- **[Manual longo no GitHub](https://github.com/omegaup/omegaup/blob/main/frontend/www/docs/Manual-for-Zip-File-Creation-for-Problems.md)**
