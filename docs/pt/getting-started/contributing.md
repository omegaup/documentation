---
title: Contribuindo para omegaUp
description: Aprenda como contribuir com código para omegaUp por meio de pull requests
icon: bootstrap/code-tags
---
# Contribuindo para omegaUp

Obrigado pelo seu interesse em contribuir com o omegaUp! Esta página orienta você em todo o ciclo de uma contribuição: bifurcação e clonagem, manter sua cópia local honesta antes de tocar em qualquer coisa, ramificar, abrir uma boa solicitação de pull e consertar uma depois de já ter enviado algo de que não se orgulha. Nada aqui é exótico — é o fluxo de trabalho diário que a equipe de manutenção realmente usa, com o raciocínio anexado para que você possa improvisar com segurança quando sua situação não corresponder ao caminho feliz.

Antes de escrever uma linha de código, convidamos você a ler as [Diretrizes de codificação](../development/coding-guidelines.md). Vale a pena internalizar sua estrela norte desde o início: é preferível explicar *por que* as coisas são feitas da maneira como são feitas, em vez de *o que* o código faz. Segui-los torna sua alteração muito mais fácil para um revisor ler e mesclar, de modo que o esforço será recompensado na mesma semana.

## Por que você nunca se compromete com `main`

Depois de bifurcar omegaUp, a ramificação `main` em sua bifurcação deve sempre permanecer um espelho byte por byte da ramificação `main` de `omegaup/omegaup`, que contém as alterações mais recentes que a equipe de revisão já aprovou. Essa é a razão da regra que você verá repetida em todos os lugares: **nunca confirme diretamente com `main`**. Depois que seus commits chegam ao `main` e o `main` upstream segue em frente, é genuinamente doloroso arrastar seu `main` de volta para um estado limpo - você acaba rebaseando, redefinindo ou empurrando à força para sair de um buraco que cavou sem motivo. Em vez disso, crie uma ramificação separada para cada alteração que você pretende enviar como uma solicitação pull e deixe o `main` fazer nada além de rastrear o upstream.

## Pré-requisitos

Antes de começar:

1. [Configure seu ambiente de desenvolvimento](development-setup.md)
2. Leia as [Diretrizes de codificação](../development/coding-guidelines.md)
3. Saiba [como obter ajuda](getting-help.md) se tiver dúvidas

## Todo PR precisa de um problema atribuído

!!! importante "Obrigatório antes de abrir um PR"
    Cada solicitação pull **deve** estar vinculada a um problema existente do GitHub que é **atribuído a você**. Isso não é burocracia por si só – é como a equipe evita que duas pessoas construam silenciosamente a mesma solução, e isso é aplicado pela automação, de modo que um PR sem nenhum problema atribuído por trás dele não pode ser mesclado, não importa quão bom seja o código.

### Como atribuir um problema

Primeiro, **encontre ou crie um problema**. Navegue pelos [problemas existentes](https://github.com/omegaup/omegaup/issues) ou, se estiver corrigindo algo que ninguém registrou ainda, [abra um novo problema](https://github.com/omegaup/omegaup/issues/new) descrevendo o bug ou recurso para que haja algo para apontar seu PR.

Então ** reivindique **. omegaUp executa o bot [`takanome-dev/assign-issue-action`](https://github.com/takanome-dev/assign-issue-action) precisamente para que você não precise esperar que um mantenedor clique em "atribuir" em cada ticket. Comente o assunto com:

- `/assign` — atribua o problema a você mesmo.
- `/unassign` — retire-se do problema quando não puder continuar, para que outra pessoa possa resolver o problema.

O bot também pode se oferecer para atribuir o problema quando seu comentário deixar óbvio que você deseja trabalhar nele.

Por fim, faça referência ao problema na descrição do seu PR com `Fixes #1234` ou `Closes #1234` (usando seu número real do problema). O GitHub lê essa linha e fecha o problema automaticamente no momento em que seu PR é mesclado, para que o rastreador permaneça honesto, sem que ninguém o resolva manualmente.

!!! falha "Um PR sem problema atribuído falhará em suas verificações"
    Se o seu PR não estiver vinculado a um problema atribuído a você, as verificações automatizadas falharão e o PR não poderá ser mesclado. Reivindique o problema primeiro.

### Os limites de atribuição e por que eles existem

O bot impõe alguns prazos para que problemas reivindicados, mas abandonados, não apodreçam indefinidamente e bloqueiem outros contribuidores:

- Você pode manter no máximo **5** problemas atribuídos a você de uma só vez em todo o repositório. O limite evita que qualquer pessoa acumule pendências.
- Depois de ser atribuído, você deve **abrir uma solicitação pull** — um **rascunho** PR conta — dentro de **7 dias**. A janela é o que transforma o “eu vou lá” em um progresso real ou em uma questão liberada.
- Um lembrete é postado na metade, aproximadamente **3,5 dias**, para que uma semana agitada não lhe custe o problema de surpresa.
- Se não existir nenhum PR até o dia 7, você será **desatribuído automaticamente** e **bloqueado de autoatribuir o mesmo problema novamente**; se você ainda quiser depois disso, pergunte a um mantenedor.

Há uma exceção deliberada: se **você foi o autor do problema** e já tem pelo menos **10 PRs mesclados** neste repositório, você pode autoatribuir seus próprios problemas **sem** que eles sejam contabilizados no limite de 5 atribuições ativas — você conquistou a confiança e o problema é seu. A regra de 7 dias para um PR ainda se aplica mesmo assim, e edições de autoria de *outras* pessoas ainda contam para o seu limite de 5.

!!! dica "Não perca uma tarefa que você pretendia manter"
    Comente `/assign` e abra um **rascunho** PR no mesmo dia - isso satisfaz a regra dos 7 dias imediatamente e dá a você todo o tempo necessário para terminar. Se você realmente precisar de mais tempo, peça a um mantenedor para adicionar o rótulo **`📌 Pinned`**, que isenta o problema da varredura de cancelamento automático de atribuição.

## Configure seu fork e controles remotos (uma vez)

Você só faz isso uma vez por clone. omegaUp usa os mesmos dois nomes remotos que o fluxo de trabalho padrão do fork do GitHub, então cada tutorial e ferramenta git que você já conhece continua funcionando:

- **`origin`** — seu fork, `https://github.com/YOURUSERNAME/omegaup.git`: de onde você **envia** ramificações e abre pull requests.
- **`upstream`** — o repositório canônico, `https://github.com/omegaup/omegaup.git`: de onde você **extrai** as alterações aprovadas pela equipe de revisão.

!!! note "Páginas wiki mais antigas trocaram esses nomes"
    Algumas das páginas wiki mais antigas do omegaUp usavam `origin` para o repositório canônico e um segundo controle remoto para o fork - o oposto da convenção aqui. Este site segue a convenção padrão acima (`origin` = seu fork, `upstream` = canônico). Se você estiver fazendo referência cruzada de uma página antiga e um comando for lido de trás para frente, é por isso.

### 1. Bifurque o repositório

Visite [github.com/omegaup/omegaup](https://github.com/omegaup/omegaup) e clique no botão **Fork** para criar sua própria cópia do `omegaup/omegaup`.

### 2. Clone seu garfo

```bash
git clone https://github.com/YOURUSERNAME/omegaup.git
cd omegaup
```
### 3. Adicione `upstream` e verifique

Seu novo clone já tem `origin` apontando para seu fork. Adicione `upstream` para poder buscar as alterações do repositório canônico:

```bash
git remote add upstream https://github.com/omegaup/omegaup.git
git remote -v
```
Você deverá ver exatamente isto – duas linhas para cada controle remoto, `origin` em seu fork e `upstream` no repositório canônico:

```
origin     https://github.com/YOURUSERNAME/omegaup.git (fetch)
origin     https://github.com/YOURUSERNAME/omegaup.git (push)
upstream   https://github.com/omegaup/omegaup.git (fetch)
upstream   https://github.com/omegaup/omegaup.git (push)
```
Se `origin` apontar para algum lugar errado - mais comumente porque você clonou o URL canônico em vez de seu fork - aponte-o novamente sem clonar novamente:

```bash
git remote set-url origin https://github.com/YOURUSERNAME/omegaup.git
```
## Mantenha seu `main` atualizado antes de começar

Vale a pena repetir: você não deve fazer alterações no `main`, porque é muito difícil retorná-lo a um estado decente depois que as alterações forem mescladas. Mas é uma boa ideia sincronizá-lo de tempos em tempos — sempre antes de iniciar uma nova mudança — para que seu trabalho comece a partir do mesmo commit que a equipe de revisão está analisando:

```bash
git checkout main               # Switch back to main if you were on a feature branch
git fetch upstream              # Download the latest omegaup/main
git pull --rebase upstream main # Replay upstream's commits under yours, keeping main linear
git push origin main            # Update your fork's main to match
```
!!! aviso "Se `git push origin main` for rejeitado"
    Um push rejeitado para `main` significa que você quebrou a regra e cometeu algo diretamente no `main` - seu `main` e o `main` do upstream agora divergiram. A solução limpa é mover esses commits para uma ramificação de recursos e redefinir `main` de volta para `upstream/main`; pergunte a um mantenedor se não tiver certeza de como. Somente se você entender exatamente o que está descartando, deverá substituir o `main` do seu fork por `git push origin main --force-with-lease`. A verdadeira lição é aquela que está no topo desta página: em primeiro lugar, não faça commit no `main` - em vez disso, ramifique.

## Iniciar uma nova mudança

### 1. Ramifique o `main` upstream mais recente

Crie sua ramificação diretamente do `upstream/main` para que ela comece a partir do código aprovado pela revisão e, em seguida, envie-a para o seu fork imediatamente para que haja um local para ela no GitHub:

```bash
git fetch upstream
git checkout -b feature-name upstream/main   # New branch, synced with omegaUp's main
git push -u origin feature-name              # Publish it to your fork; -u sets up tracking
```
!!! dica "Nomeie o branch após a mudança"
    Nomes descritivos como `fix-login-bug` ou `add-dark-mode-toggle` informam rapidamente aos revisores para que serve a filial e mantêm sua própria lista de filiais navegável meses depois.

### 2. Faça suas alterações

Escreva seu código seguindo as [diretrizes de codificação](../development/coding-guidelines.md), adicione testes para o que você alterou e certifique-se de que o pacote existente ainda seja aprovado. Uma mudança nos testes é uma mudança em que o revisor pode confiar.

### 3. Defina sua identidade git (apenas na primeira vez)

Se você nunca configurou o git nesta máquina, faça isso uma vez para que seus commits sejam atribuídos corretamente:

```bash
git config --global user.email "your-email@domain.com"
git config --global user.name "your-username"
```
### 4. Comprometa-se

```bash
git add .
git commit -m "Write a clear description of what changed and why"
```
Uma mensagem de commit que explica *por que* a mudança foi feita — e não apenas *que* arquivo foi movido — é a mesma cortesia que as diretrizes de codificação pedem aos comentários do seu código, e é o que um revisor lê primeiro.

### 5. Execute os validadores antes de enviar

Execute o linter **fora** do contêiner, na raiz do repositório:

```bash
./stuff/lint.sh
```
Sem argumentos, `stuff/lint.sh` descobre quais arquivos você alterou (é diferente de `upstream/main` ou `origin/main` se você não tiver nenhum controle remoto `upstream`) e executa a passagem `fix` apenas sobre esses arquivos, girando o contêiner `omegaup/hook_tools` fixado para fazer a formatação real e verificações estáticas para cada idioma que o omegaUp usa. Ele alinha o código, elimina prazos e valida. Se você deseja apenas *verificar* sem reescrever os arquivos, passe `validate` explicitamente: `./stuff/lint.sh validate`.

!!! note "Ele deve ser executado fora do contêiner"
    `stuff/lint.sh` se recusa a ser executado quando seu diretório de trabalho é `/opt/omegaup` (o caminho em que o código reside *dentro* do contêiner de desenvolvimento) e imprime `Running ./stuff/lint.sh inside a container is not supported.`. Ele precisa do Docker do seu host para iniciar a imagem de ferramentas de gancho, então execute-o a partir do shell do host, não de dentro do `docker exec`.

!!! note "O gancho pré-empurrado executa isso para você"
    omegaUp instala um git hook `pre-push` que executa `stuff/lint.sh ... validate` automaticamente, portanto, um push com erros de lint é interrompido antes de sair de sua máquina. Executar o linter primeiro significa apenas encontrar e corrigir problemas de acordo com sua própria programação, em vez de ter o push bounce.

## Abra a solicitação pull

### 1. Empurre seu branch

```bash
git push -u origin feature-name
```
O sinalizador `-u` vincula sua ramificação local à ramificação em seu fork (`origin`), portanto, cada push posterior será apenas `git push` sem argumentos - o rastreamento já está definido.

### 2. Abra o PR no GitHub

Vá para seu fork em `https://github.com/YOURUSERNAME/omegaup`, use o seletor de branch para mudar para `feature-name` e clique em **Pull request**. O GitHub se oferecerá para abrir o PR contra o `main` do `omegaup/omegaup` - é exatamente onde você deseja.

### 3. Escreva a descrição

Uma boa descrição é o que faz com que seu PR seja revisado rapidamente. Inclua o que a mudança faz, o problema que ela resolve, o que realmente mudou e como você sabe que funciona:

```markdown
## Description
Brief description of what this PR does.

## Related Issue
Fixes #1234  <!-- Replace with your real issue number -->

## Changes Made
- Change 1
- Change 2

## Testing
How you tested the change.

## Screenshots (if applicable)
Before/after images for any UI change.
```
!!! importante "Sempre faça referência ao assunto"
    A linha `Fixes #1234` / `Closes #1234` não é uma decoração opcional - é o que vincula o PR ao problema atribuído (satisfazendo a verificação automatizada) e o que fecha o problema automaticamente quando o PR é mesclado.

## Atualizar um PR após revisão

Os revisores deixarão comentários. Aborde-os da mesma forma que você fez a alteração original – confirme no mesmo branch e faça push. Não há `-u` desta vez porque a filial já está rastreando `origin`:

```bash
git add .
git commit -m "Address review: <what you changed>"
git push
```
O PR aberto se atualiza automaticamente com os novos commits e o revisor os vê na próxima vez que olhar.

## Corrija um PR que você já enviou

Às vezes você empurra e só então percebe que o branch carrega três commits "wip", "oops" e "typo", ou o commit superior tem uma mensagem que você prefere não imortalizar. Como este é o *seu* branch de recurso e não o histórico compartilhado, você está livre para reescrevê-lo e forçar o push. A única regra rígida é a mesma de qualquer outro lugar nesta página: **reescreva apenas o histórico em sua própria ramificação de recursos - nunca force o push para `main` no repositório canônico.**

### Altere apenas a mensagem do último commit

Se a mensagem no seu commit mais recente estiver errada, altere-a — isso abre o seu editor na mensagem existente:

```bash
git commit --amend
```
Você verá a mensagem atual seguida pelo texto auxiliar do git:

```
Old commit message

# Please enter the commit message for your changes. Lines starting
# with '#' will be ignored, and an empty message aborts the commit.
```
Edite a linha superior, salve e feche. Confirme com `git log`, que agora deve mostrar sua nova mensagem nesse commit. Se você já executou o commit, o controle remoto ainda possui a versão antiga, então atualize-o:

```bash
git push --force-with-lease
```
`--force-with-lease` é a forma segura de `--force`: ele se recusa a sobrescrever a ramificação remota se alguém a tiver pressionado desde a última vez que você a buscou, portanto, um push forçado nunca pode atrapalhar silenciosamente o trabalho de um colaborador.

### Esmague os commits descartáveis

Para dobrar uma série de commits confusos em um commit limpo, rebase interativamente o último `n` deles:

```bash
git rebase -i HEAD~n
```
Substitua `n` por quantos commits você deseja recolher. Git abre um editor listando os mais antigos primeiro:

```
pick commit-1
pick commit-2
pick commit-3
...
pick commit-n
```
Mantenha o de cima como `pick` — que é o commit cuja mensagem sobrevive — e mude cada linha abaixo dele de `pick` para `fixup` (ou apenas `f`), que dobra as alterações do commit na linha acima dele e descarta sua mensagem:

```
pick  commit-1
f     commit-2
f     commit-3
...
f     commit-n
```
Salve e feche. Em seguida, publique o branch reescrito:

```bash
git push --force-with-lease
```
O PR agora mostra um único commit organizado em vez da trilha de correção, e nenhuma das mensagens descartadas aparece no histórico.

## Depois de enviar

Assim que o PR é aberto, uma sequência previsível se desenrola. GitHub Actions executa uma bateria completa de testes e validações - certifique-se de que todos fiquem verdes, já que um cheque vermelho é a primeira coisa que um revisor irá rejeitar no PR. Em seguida, um membro da equipe omegaUp analisa seu código; resolva tudo o que eles levantarem, enviando mais commits para o mesmo branch. Depois de aprovado e mesclado, há mais uma espera: os PRs mesclados vão para produção na **implantação de fim de semana**, portanto, sua alteração entra em vigor após o próximo fim de semana, e não no instante em que é mesclada.

## Limpar após uma mesclagem

Depois que seu PR for mesclado, a filial terá feito seu trabalho. Exclua-o localmente:

```bash
git branch -D feature-name
```
Exclua-o também no GitHub - na página **Branches**, no próprio PR mesclado (o GitHub oferece um botão de exclusão) ou na linha de comando:

```bash
git push origin --delete feature-name
```
Mesmo depois de excluir a ramificação remota, seu repositório local mantém uma referência obsoleta de rastreamento remoto, que você pode ver com `git branch -a`. Remova essas referências mortas para que `git branch -a` pare de listar ramificações que não existem mais:

```bash
git remote prune origin --dry-run  # Preview what would be pruned
git remote prune origin            # Actually remove the stale references
```
## Dicas ambientais que você pode encontrar no primeiro empurrão

Esses são os obstáculos de configuração que os colaboradores iniciantes costumam encontrar. Cada um mostra o sintoma para que você possa combinar o seu e depois a correção.

### A localidade da VM não é `en_US.UTF-8`

A VM de desenvolvimento não é fornecida com `en_US.UTF-8` como localidade padrão, o que algumas ferramentas reclamam. Corrija-o seguindo [este guia do askubuntu](https://askubuntu.com/questions/881742/locale-cannot-set-lc-ctype-to-default-locale-no-such-file-or-directory-locale/893586#893586).

### Dependências PHP ausentes

Um novo checkout não tem diretório `vendor/`, então as dependências do PHP estão faltando até você instalá-las:

```bash
composer install
```
### `FileNotFoundError: ... 'mysql'` ao pressionar

Se o seu push for abortado com algo assim:

```
FileNotFoundError: [Errno 2] No such file or directory: 'mysql'
error: failed to push some refs to 'https://github.com/YOURUSERNAME/omegaup.git'
```
o que ele está dizendo é que o gancho pré-push tentou executar o cliente `mysql` e não conseguiu encontrá-lo - o MySQL não está instalado em seu host. O **servidor** MySQL é executado dentro do contêiner de desenvolvimento, mas o cliente que o gancho invoca deve residir no host, **fora** do contêiner. Instale os dois pacotes lá:

```bash
sudo apt install mysql-client mysql-server
```
Em seguida, aponte o cliente para o MySQL do contêiner, que está publicado na porta **13306** (não o padrão 3306, para que não colida com nenhum MySQL que você já execute):

```bash
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
Com o `.my.cnf` vinculado, o cliente lê essa configuração automaticamente e o gancho pré-push pode alcançar o banco de dados.

## Para onde ir em seguida

- **[Diretrizes de codificação](../development/coding-guidelines.md)** — os padrões que facilitam a revisão do seu PR.
- **[Comandos úteis](../development/useful-commands.md)** — a referência diária de comandos de desenvolvimento.
- **[Guia de teste](../development/testing.md)** — como escrever e executar os testes que seu PR precisa.
- **[Como obter ajuda](getting-help.md)** — onde perguntar quando você tiver dúvidas.
- **[Visão geral da arquitetura](../architecture/index.md)** — como as peças que você está alterando se encaixam.
- Junte-se ao [servidor Discord](https://discord.gg/gMEMX7Mrwe) para conversar com a comunidade.

---

**Pronto para fazer sua primeira contribuição?** Reivindique um problema, ramifique `upstream/main` e abra seu PR.
