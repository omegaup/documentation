---
title: Começando
description: Comece sua jornada contribuindo para omegaUp
icon: bootstrap/rocket-launch
---
# Introdução ao desenvolvimento omegaUp

Bem-vindo! Este guia irá ajudá-lo a começar a contribuir para o omegaUp, uma plataforma educacional gratuita que ajuda a melhorar as habilidades de programação.

## O que é omegaUp?

omegaUp é uma plataforma de programação educacional usada por dezenas de milhares de estudantes e professores na América Latina. Ele fornece:

- **Solução de problemas**: Milhares de problemas de programação com avaliação automática
- **Concursos**: Organize competições de programação
- **Cursos**: caminhos de aprendizagem estruturados
- **Treinamento**: pratique problemas organizados por tópico e dificuldade

## Antes de começar

Se você é novo no omegaUp, recomendamos:

1. **Experimente a plataforma**: Visite [omegaUp.com](https://omegaup.com/), crie uma conta e resolva alguns problemas
2. **Saiba mais sobre nós**: Explore [omegaup.org](https://omegaup.org/) para saber mais sobre nossa organização
3. **Entenda a base de código**: Revise a [Visão geral da arquitetura](../architecture/index.md) para entender como o omegaUp funciona

## Caminho de início rápido

<div class="grid cards" markdown>

- :material-docker:{ .lg .middle } __[Configuração de desenvolvimento](development-setup.md)__

    ---

    Configure seu ambiente de desenvolvimento local usando Docker. Este é o primeiro passo para começar a contribuir.

    [Guia de configuração :octicons-arrow-right-24:](development-setup.md)

- :material-source-branch:{ .lg .middle } __[Guia de contribuição](contributing.md)__

    ---

    Aprenda como bifurcar o repositório, criar ramificações e enviar solicitações pull.

    [Contribuição :octicons-arrow-right-24:](contributing.md)

- :material-help-circle:{ .lg .middle } __[Obtendo ajuda](getting-help.md)__

    ---

    Preso? Aprenda como fazer perguntas de maneira eficaz e obter ajuda da comunidade.

    [:octicons-arrow-right-24: Obtenha ajuda](getting-help.md)

</div>

## Visão geral do ambiente de desenvolvimento

omegaUp usa Docker para desenvolvimento local:

- **Web + API**: PHP e MySQL (MVC, APIs JSON)
- **Juiz**: Go (grader/runner) e sandbox minijail
- **UI**: Vue.js, TypeScript, Bootstrap 4
- **Problemas**: gitserver e ZIP — ver [Problemas](../features/problems/index.md)

### Caminhos no repositório

| Área | Caminho |
|------|---------|
| API | `frontend/server/src/Controllers/` |
| DAO | `frontend/server/src/DAO/` |
| Migrações | `frontend/database/` |
| Vue/TS | `frontend/www/js/` |
| Testes PHPUnit | `frontend/tests/controllers/` |
| Cypress | `cypress/e2e/` |

### Leituras

- [omegaUp (IOI Journal, 2014)](http://www.ioinformatics.org/oi/pdf/v8_2014_169_178.pdf)
- [libinteractive](https://ioinformatics.org/journal/v9_2015_3_14.pdf)

## Navegadores

Use um navegador **atual** (Chrome, Firefox, Safari, Edge). Apenas **HTTPS**; IE antigo não é suportado.

## Contas de Desenvolvimento

Ao configurar seu ambiente local, você terá acesso a duas contas pré-configuradas:

| Nome de usuário | Senha | Função |
|----------|----------|------|
| `omegaup` | `omegaup` | Administrador |
| `user` | `user` | Usuário regular |

## Próximas etapas

1. **[Configure seu ambiente de desenvolvimento](development-setup.md)** - Coloque o Docker em execução e clone o repositório
2. **[Leia o guia de contribuição](contributing.md)** - Aprenda o fluxo de trabalho para enviar alterações
3. **[Explore a arquitetura](../architecture/index.md)** - Entenda como o omegaUp está estruturado
4. **[Revise as diretrizes de codificação](../development/coding-guidelines.md)** - Aprenda nossos padrões de codificação

## Recursos

- **Site**: [omegaup.com](https://omegaup.com)
- **GitHub**: [github.com/omegaup/omegaup](https://github.com/omegaup/omegaup)
- **Discord**: [Junte-se ao nosso servidor Discord](https://discord.gg/gMEMX7Mrwe) para suporte da comunidade
- **Problemas**: [Relatar bugs ou solicitar recursos](https://github.com/omegaup/omegaup/issues)

---

Pronto para começar? Vá para [Configuração de desenvolvimento](development-setup.md) para começar!
