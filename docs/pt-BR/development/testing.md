---
title: Guia de teste
description: Guia de teste abrangente para omegaUp
icon: bootstrap/flask
---
# Guia de teste

omegaUp usa várias estruturas de teste para garantir a qualidade do código em diferentes camadas.

## Pilha de testes

| Camada | Estrutura | Localização |
|-------|-----------|----------|
| Testes de Unidade PHP | Unidade PHP | `frontend/tests/controllers/` |
| Testes TypeScript/Vue | Brincadeira | `frontend/www/js/` |
| Testes E2E | Cipreste | `cypress/e2e/` |
| Testes Python | pytest | `stuff/` |

## Testes de Unidade PHP

### Executando todos os testes PHP

```bash
./stuff/runtests.sh
```
Executa testes PHPUnit, validação de tipo MySQL e Psalm.

**Localização**: Dentro do contêiner Docker

### Executando arquivo de teste específico

```bash
./stuff/run-php-tests.sh frontend/tests/controllers/MyControllerTest.php
```
Omita o nome do arquivo para executar todos os testes.

### Requisitos de teste

- Todos os testes devem passar 100% antes de serem confirmados
- Nova funcionalidade requer testes novos/modificados
- Testes localizados em `frontend/tests/controllers/`

## Testes TypeScript/Vue

### Executando testes Vue (modo Watch)

```bash
yarn run test:watch
```
Executa novamente testes automaticamente quando o código é alterado.

**Localização**: Dentro do contêiner Docker

### Executando arquivo de teste específico

```bash
./node_modules/.bin/jest frontend/www/js/omegaup/components/MyComponent.test.ts
```
### Estrutura de teste

Verificação de testes de componentes Vue:
- Visibilidade dos componentes
- Emissão de eventos
- Comportamento esperado
- Adereços e estado

## Testes E2E com Cypress

Os testes de ponta a ponta ficam na pasta `cypress/` na raiz do repositório. **O Cypress costuma rodar no host** (não dentro do contêiner Docker do frontend omegaUp), então você precisa de Node, dependências Yarn e, no Linux, bibliotecas de sistema para o runner baseado em Electron.

A versão fixada está no `package.json` raiz (campo `cypress`). Depois de atualizar dependências, rode `yarn install` e, se faltar o binário:

```bash
./node_modules/.bin/cypress install
```

### Abrir e executar o Cypress

```bash
npx cypress open
# ou
./node_modules/.bin/cypress open
```

Modo headless:

```bash
npx cypress run
# ou
yarn test:e2e
```

`yarn test:e2e` executa `cypress run --browser chrome` (veja os scripts em `package.json`).

### Dependências no Linux (Ubuntu / Debian)

Lista oficial: [required dependencies](https://on.cypress.io/required-dependencies).

Pacotes comuns:

```bash
sudo apt update
sudo apt install -y libatk1.0-0 libatk-bridge2.0-0 libgdk-pixbuf2.0-0 libgtk-3-0 libgbm-dev libnss3 libxss-dev
```

**Erros `libnss3.so` / NSS** — instale `libnss3` ou `libnss3-dev` conforme a distro.

**Erros `libasound.so.2`**:

```bash
sudo apt-get install libasound2
```

No **Ubuntu 24.04+** o pacote pode chamar-se:

```bash
sudo apt install libasound2t64
```

Se persistir, `sudo apt update` e tente de novo; confira a versão na mensagem com o caminho em `~/.cache/Cypress/<versão>/`.

### Estrutura e escrita de testes

- Specs: `cypress/e2e/`, padrão `*.cy.ts` (subpastas permitidas).
- Comandos customizados: `cypress/support/commands.js` (tipos em `cypress/support/cypress.d.ts`).
- Handlers globais / `uncaught:exception`: `cypress/support/e2e.ts`.
- [Custom commands](https://docs.cypress.io/api/cypress-api/custom-commands) e [eventos](https://docs.cypress.io/api/events/catalog-of-events).
- **Cypress Studio**: [documentação](https://docs.cypress.io/guides/core-concepts/cypress-studio).

Plugins neste repo incluem **cypress-wait-until** e **cypress-file-upload** (`package.json`).

### Depurar falhas na CI

Na aba **Checks** do PR → **CI**, baixe artefatos `cypress-screenshots-<tentativa>` e `cypress-videos-<tentativa>` (número na URL do workflow, ex. `/attempts/3`).

## Testes Python

Os testes Python usam pytest e estão localizados no diretório `stuff/`.

## Cobertura de teste

Usamos **Codecov** para medir a cobertura:

- **PHP**: Cobertura medida ✅
- **TypeScript**: Cobertura medida ✅
- **Cypress**: Cobertura ainda não medida ⚠️

## Melhores práticas

### Escreva os testes primeiro
Quando possível, escreva testes antes da implementação (TDD).

### Testar caminhos críticos
Concentre-se em:
- Fluxos de autenticação de usuários
- Envio e avaliação de problemas
- Gestão de concursos
- Terminais de API

### Mantenha os testes rápidos
- Os testes unitários devem ser rápidos (<1 segundo)
- Os testes E2E podem ser mais lentos, mas devem ser concluídos em um tempo razoável

### Teste de isolamento
- Cada teste deve ser independente
- Limpe os dados de teste após os testes
- Use acessórios de teste para dados consistentes

## Documentação Relacionada

- **[Diretrizes de codificação](coding-guidelines.md)** - Padrões de código
- **[Comandos úteis](useful-commands.md)** - Comandos de teste
- **[Configuração do ambiente de desenvolvimento](../getting-started/development-setup.md)** — Node, Yarn e Docker antes do Cypress
