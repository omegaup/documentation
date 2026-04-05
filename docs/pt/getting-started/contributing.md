---
title: Contribuindo para omegaUp
description: Aprenda como contribuir com código para omegaUp por meio de pull requests
icon: bootstrap/code-tags
---
# Contribuindo para omegaUp

Obrigado pelo seu interesse em contribuir com o omegaUp! Este guia orientará você no processo de envio de sua primeira contribuição.

## Visão geral do processo de desenvolvimento

A ramificação `main` em seu fork deve sempre ser mantida atualizada com a ramificação `main` do repositório omegaUp. **Nunca se comprometa diretamente com `main`**. Em vez disso, crie um branch separado para cada alteração que você planeja enviar por meio de uma solicitação pull.

## Pré-requisitos

Antes de começar:

1. ✅ [Configure seu ambiente de desenvolvimento](development-setup.md)
2. ✅ Leia as [Diretrizes de codificação](../development/coding-guidelines.md)
3. ✅ Entenda [como obter ajuda](getting-help.md) se tiver dúvidas

## Requisito de atribuição de problemas

!!! importante "Obrigatório antes de abrir PR"
    Cada solicitação pull **deve** estar vinculada a um problema existente do GitHub que é **atribuído a você**.

### Etapas para atribuir o problema

1. **Encontre ou crie um problema**:
   - Procure [problemas existentes](https://github.com/omegaup/omegaup/issues)
   - Ou [crie um novo problema](https://github.com/omegaup/omegaup/issues/new) descrevendo sua correção de bug ou recurso

2. **Expressar interesse**:
   - Comente o assunto manifestando seu interesse em trabalhar nele
   - Espere que um mantenedor o atribua a você

3. **Comece a trabalhar**:
   - Uma vez atribuído, você pode criar sua filial e começar a codificar
   - Faça referência ao problema na descrição do seu PR usando: `Fixes #1234` ou `Closes #1234`

!!! falha "PR falhará sem atribuição de problemas"
    Se o seu PR não estiver vinculado a um problema atribuído, as verificações automatizadas falharão e o seu PR não poderá ser mesclado.

### Atribuição automática (bot)

Este repositório usa [`takanome-dev/assign-issue-action`](https://github.com/takanome-dev/assign-issue-action) para que você possa reivindicar trabalho sem depender sempre de uma atribuição manual.

**Comandos** (comente na issue do GitHub):

- `/assign` — atribui a issue a você.
- `/unassign` — remove a sua atribuição.

O bot também pode sugerir atribuição quando o seu comentário mostra interesse.

**Limites e prazos**

- No máximo **5** issues atribuídas a você ao mesmo tempo (em todo o repositório).
- Depois da atribuição, você deve **abrir um pull request** (um PR **rascunho** conta) em até **7 dias**.
- Por volta da metade desse prazo (~3,5 dias) é publicado um lembrete.
- Se não houver PR no dia 7, você é **desatribuído automaticamente** e **não poderá voltar a autoatribuir** nessa issue; peça a um mantenedor se ainda precisar dela.

**Autores de issue experientes**

- Se **você criou a issue** e tem pelo menos **10 PRs mesclados** neste repositório, pode autoatribuir **sem** contar no limite de 5 para issues **que você abriu**.
- A regra dos **7 dias** (abrir PR após atribuição) continua valendo.
- Em issues **criadas por outras pessoas**, o limite usual de **5** atribuições ativas aplica-se.

**Dicas**

- Escreva `/assign` e abra cedo um rascunho de PR para não perder a atribuição.
- Use `/unassign` se não puder continuar.
- Se precisar de mais tempo, peça a um mantenedor o rótulo **`📌 Pinned`** na issue.

## Configurando seu fork e controles remotos

Você só precisa fazer isso uma vez. Os nomes seguem o **fluxo habitual de fork no GitHub**:

- **`origin`** — o seu fork (`https://github.com/YOURUSERNAME/omegaup.git`): onde você faz **push** de branches e de onde abre pull requests.
- **`upstream`** — o repositório canónico (`https://github.com/omegaup/omegaup.git`): de onde você **puxa** as alterações oficiais.

Algumas páginas antigas da wiki do omegaUp invertiam esses nomes; neste site de documentação usamos a convenção acima.

### 1. Bifurque o repositório

Visite [github.com/omegaup/omegaup](https://github.com/omegaup/omegaup) e clique no botão "Fork".

### 2. Clone seu fork

```bash
git clone https://github.com/YOURUSERNAME/omegaup.git
cd omegaup
```

### 3. Adicione `upstream` e verifique os remotos

O clone já tem **`origin`** apontando para o seu fork. Adicione **`upstream`** uma vez:

```bash
git remote add upstream https://github.com/omegaup/omegaup.git
git remote -v
```

Você deverá ver:

```
origin     https://github.com/YOURUSERNAME/omegaup.git (fetch)
origin     https://github.com/YOURUSERNAME/omegaup.git (push)
upstream   https://github.com/omegaup/omegaup.git (fetch)
upstream   https://github.com/omegaup/omegaup.git (push)
```

Se `origin` estiver errado, corrija com:

```bash
git remote set-url origin https://github.com/YOURUSERNAME/omegaup.git
```

## Atualizando sua filial principal

Mantenha o seu `main` local e o `main` do **seu fork** alinhados com o `main` do **omegaUp**:

```bash
git checkout main
git fetch upstream
git pull --rebase upstream main
git push origin main
```

!!! aviso "Se o push para main falhar"
    Se `git push origin main` falhar porque você fez commits diretamente em `main`, peça ajuda para limpar a branch ou use `git push origin main --force-with-lease` só se entender o risco. Em geral, **não faça commits em `main`**; use uma branch de trabalho.

## Iniciando uma nova mudança

### 1. Crie uma ramificação de recursos

Crie uma branch a partir do último `main` oficial:

```bash
git fetch upstream
git checkout -b feature-name upstream/main
git push -u origin feature-name
```
!!! dica "Nomeação de filiais"
    Use nomes de ramificação descritivos como `fix-login-bug` ou `add-dark-mode-toggle`.

### 2. Faça suas alterações

- Escreva seu código seguindo as [diretrizes de codificação](../development/coding-guidelines.md)
- Escreva testes para suas alterações
- Garantir que todos os testes sejam aprovados

### 3. Confirme suas alterações

```bash
git add .
git commit -m "Write a clear description of your changes"
```
!!! dica "Confirmar mensagens"
    Escreva mensagens de commit claras e descritivas. Consulte [Commits convencionais](https://www.conventionalcommits.org/) para conhecer as práticas recomendadas.

### 4. Execute validadores

Antes de enviar, execute o script linting:

```bash
./stuff/lint.sh
```
Este comando:
- Alinha elementos de código
- Remove linhas desnecessárias
- Realiza validações para todas as linguagens utilizadas no omegaUp

!!! observe "Ganchos pré-empurrados"
    Esse script também é executado automaticamente por meio de ganchos pré-push, mas executá-lo manualmente garante que suas alterações atendam aos padrões.

### 5. Configurar usuário Git (somente na primeira vez)

Se você não configurou as informações do usuário do Git:

```bash
git config --global user.email "your-email@domain.com"
git config --global user.name "Your Name"
```
## Criando uma solicitação pull

### 1. Envie suas alterações

```bash
git push -u origin feature-name
```
O sinalizador `-u` configura o rastreamento entre sua filial local e **`origin`** (o seu fork).

### 2. Solicitação pull aberta no GitHub

1. Acesse [github.com/SEU NOME DE USUÁRIO/omegaup](https://github.com/YOURUSERNAME/omegaup)
2. Clique em "Filial" e selecione sua filial
3. Clique em "Solicitação pull"
4. Preencha a descrição do PR

### 3. Modelo de descrição de relações públicas

Sua descrição de RP deve incluir:

```markdown
## Description
Brief description of what this PR does.

## Related Issue
Fixes #1234  <!-- Replace with your issue number -->

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
Describe how you tested your changes.

## Screenshots (if applicable)
Add screenshots if your changes affect the UI.
```
!!! importante "Referência do problema necessária"
    Sempre inclua `Fixes #1234` ou `Closes #1234` na descrição do seu PR. Isso fecha automaticamente o problema quando o PR é mesclado.

## Atualizando sua solicitação pull

Se você precisar fazer alterações após criar o PR:

```bash
git add .
git commit -m "Description of additional changes"
git push  # No -u flag needed after first push
```
O PR será atualizado automaticamente com seus novos commits.

## O que acontece após o envio

1. **Verificações automatizadas**: GitHub Actions executará testes e validações
2. **Revisão de código**: um mantenedor revisará seu código
3. **Feedback sobre endereço**: faça as alterações solicitadas e envie atualizações
4. **Mesclar**: Depois de aprovado, seu PR será mesclado
5. **Implantação**: as alterações são implantadas nos finais de semana

!!! info "Implantações de fim de semana"
    Os PRs mesclados são implantados na produção durante as implantações de fim de semana. Você verá suas alterações ao vivo após a próxima implantação.

## Excluindo filiais

Depois que seu PR for mesclado:

### Excluir filial local

```bash
git branch -D feature-name
```
### Excluir filial remota

1. Acesse GitHub e clique em "Ramos"
2. Encontre sua filial e clique no ícone excluir

Ou use Git:

```bash
git push origin --delete feature-name
```
### Limpar referências remotas

Remova referências de rastreamento obsoletas (por exemplo, após apagar uma branch no GitHub):

```bash
git remote prune origin --dry-run  # Pré-visualização
git remote prune origin             # Aplicar
```

## Corrigir um pull request (commits ou histórico)

Se você já fez push e precisa **esmagar**, **remover** ou **editar** commits recentes, use rebase interativo e depois push com segurança:

### Squash ou fixup dos últimos `n` commits

```bash
git rebase -i HEAD~n
```

Substitua `n` pelo número de commits. No editor, mantenha o primeiro como `pick` e altere os demais para `fixup` (ou `f`). Salve e feche.

Prefira **`--force-with-lease`**:

```bash
git push --force-with-lease
```

### Alterar só a mensagem do último commit

Se o commit problemático é o **último** e ainda **não** foi enviado:

```bash
git commit --amend
```

Se já foi enviado:

```bash
git commit --amend
git push --force-with-lease
```

!!! aviso "Reescrever histórico público"
    Reescreva histórico apenas na **sua** branch de trabalho. Nunca faça force-push para o `main` do repositório canónico.
## Configurações adicionais

### Configuração de localidade

A máquina virtual pode não ter `en_US.UTF-8` como localidade padrão. Para corrigir isso, siga [este guia](https://askubuntu.com/questions/881742/locale-cannot-set-lc-ctype-to-default-locale-no-such-file-or-directory-locale/893586#893586).

### Dependências do compositor

Na primeira configuração, instale as dependências do PHP:

```bash
composer install
```
### Configuração MySQL

Se você encontrar erros do MySQL ao enviar, instale e configure o MySQL:

```bash
sudo apt install mysql-client mysql-server

cat > ~/.mysql.docker.cnf <<EOF
[client]
port=13306
host=127.0.0.1
protocol=tcp
user=root
password=omegaup
EOF
ln -sf ~/.mysql.docker.cnf .my.cnf
```
## Recursos

- **[Diretrizes de codificação](../development/coding-guidelines.md)** - Nossos padrões de codificação
- **[Comandos úteis](../development/useful-commands.md)** - Referência de comandos de desenvolvimento
- **[Guia de testes](../development/testing.md)** - Como escrever e executar testes
- **[Como obter ajuda](getting-help.md)** - Onde fazer perguntas

## Próximas etapas

- Revise a [Visão geral da arquitetura](../architecture/index.md) para entender a base de código
- Confira [Guias de desenvolvimento](../development/index.md) para guias detalhados
- Junte-se ao nosso [servidor Discord](https://discord.gg/gMEMX7Mrwe) para se conectar com a comunidade

---

**Pronto para fazer sua primeira contribuição?** Escolha um problema, crie um ramo e envie seu PR!
