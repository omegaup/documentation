---
title: Gerenciando Concursos
description: Guia para criar e gerenciar concursos de programação
icon: bootstrap/cog
---
# Gerenciando concursos

Guia completo para criação e gerenciamento de concursos de programação no omegaUp.

## Criando um concurso

### Informações Básicas

- **Título**: Nome do concurso
- **Alias**: identificador curto (usado em URLs)
- **Descrição**: descrição do concurso
- **Hora de Início**: Quando o concurso começa
- **Hora de Término**: Quando o concurso termina
- **Público/Privado**: configuração de visibilidade

### Configurações Avançadas

- **Comprimento da janela**: temporizadores individuais estilo USACO
- **Visibilidade do placar**: porcentagem de tempo que o placar fica visível
- **Deterioração de pontos**: fator de redução de pontuação baseado no tempo
- **Política de penalidades**: como as penalidades são calculadas
- **Lacuna entre envios**: segundos entre envios

## Tipos de concurso

### Concurso Padrão
- Horário de início e término fixo
- Temporizador compartilhado para todos os participantes
- Formato de concurso tradicional

### Concurso Virtual (estilo USACO)
- Temporizador individual por participante
- Começa quando o participante entra
- Duração baseada em janela

## Gerenciando problemas

Adicione problemas ao seu concurso:

1. Crie ou selecione problemas
2. Definir valores de pontos
3. Problemas de pedido
4. Defina configurações específicas do problema

## Gerenciando Participantes

### Concursos Públicos
- Aberto a todos os usuários
- Não é necessário convite

### Concursos Privados
- Convide usuários específicos
- Gerenciar lista de participantes
- Controle de acesso

## Configuração do placar

- **Visibilidade**: controle quando o placar está visível
- **Congelar**: Congele o placar antes do final da competição
- **Atualizar**: atualizações em tempo real via WebSocket

## Concurso em escola (rede)

Permita **HTTPS (443)** para `https://omegaup.com` (modo normal) ou `https://arena.omegaup.com` (modo **lockdown**; bloqueie o domínio normal se usar lockdown). Inclua `https://ssl.google-analytics.com`. Opcional: Gravatar, Google.

Evite **DROP** silencioso que deixe o navegador esperando dezenas de segundos. Lockdown restringe prática, fonte de submissões antigas, etc.

Julgamento é em **Linux**. Eventos grandes: **hello@omegaup.com**.

## Documentação Relacionada

- **[API de concursos](../../api/contests.md)** — Endpoints
- **[Arena](../arena.md)** — Interface do concurso
