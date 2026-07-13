---
title: Adicionando um tipo de notificação
description: Como conectar uma notificação totalmente nova de ponta a ponta, da tabela Notificações até o menu suspenso do sino do Vue
icon: bootstrap/bell
---
# Adicionando um novo tipo de notificação

O pequeno sino na barra de navegação com o emblema da contagem vermelha é alimentado por exatamente uma tabela e um componente Vue. Depois de entender como esses dois se comunicam, adicionar um novo tipo de notificação – “você ganhou um selo”, “sua inscrição no concurso foi aceita”, “um administrador deixou um feedback para você” – é uma mudança pequena e mecânica. Esta página percorre todo o caminho na ordem em que os dados realmente viajam: algo acontece no servidor, uma linha chega à tabela `Notifications`, `apiMyList` a entrega à barra de navegação e `Notification.vue` decide como desenhá-la.

A única ideia a ter em mente antes de qualquer coisa: uma notificação é apenas **um `user_id` mais um blob de JSON**. Tudo o que é interessante reside naquela coluna JSON `contents`, e todo o design é que o servidor decide *o que dizer* enquanto o frontend decide *como dizer* com base em um único discriminador `type`. Obtenha o formato JSON correto e a maior parte do trabalho estará concluída.

## O modelo de dados: uma linha, um blob JSON

As notificações ficam na tabela `Notifications` MySQL, expostas através do par DAO/VO usual - [`frontend/server/src/DAO/Notifications.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Notifications.php) (o DAO público) e [`frontend/server/src/DAO/VO/Notifications.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/VO/Notifications.php) (o objeto de valor). Uma linha possui apenas cinco colunas: `notification_id`, `user_id`, `timestamp`, `read` e `contents`. Quatro delas são a contabilidade que a plataforma gerencia para você – a chave primária, a qual campainha ela pertence, quando foi disparada e se o usuário a dispensou. A coluna `read` é mais importante do que parece: toda a "contagem de não lidas" e o fluxo de marcação como lida dependem desse único booleano, e uma notificação só aparece enquanto `read = 0`.

Tudo o que você realmente projeta vai para **`contents`, que é uma string JSON**. No mínimo deve transportar um `type`:

```json
{
  "type": "yourNotificationType",
  "any_field": "whatever payload this type needs"
}
```
O campo `type` é o discriminador que informa [`Notification.vue`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/components/notification/Notification.vue) qual layout renderizar - com ou sem imagem, qual ícone, se ele está vinculado a algum lugar, qual texto mostrar. As chaves restantes são uma **carga útil** de formato livre: nomeie-as como o tipo precisar, porque sua única função é transportar os dados específicos que o layout irá interpolar. O exemplo mínimo clássico, direto do cron do emblema, é um blob de dois campos onde `badge` é a carga útil:

```json
{
  "type": "badge",
  "badge": "500score"
}
```
Isso diz “esta é uma notificação de crachá, e o crachá em questão é `500score`” – o que é suficiente para o frontend encontrar a arte do crachá, construir a frase e vincular à página do crachá.

## O esquema `contents` é um tipo real gerado

A forma do `contents` não é folclore; é um tipo de Salmo que é compilado em TypeScript, portanto, o front-end e o back-end concordam com ele no momento da construção. A definição canônica é a anotação `@psalm-type NotificationContents` no topo de [`frontend/server/src/Controllers/Notification.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Notification.php#L8):

```php
@psalm-type NotificationContents=array{
    type: string,
    badge?: string,
    message?: string,
    status?: string,
    url?: string,
    body?: array{
        localizationString: string,
        localizationParams: list<string, string>,
        url: string,
        iconUrl: string
    }
}
```
[`APITool.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/cmd/APITool.php) lê essa anotação e regenera a interface de espelho em [`frontend/www/js/omegaup/api_types.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/api_types.ts) (procure por `interface NotificationContents` — ele carrega o banner DO-NOT-EDIT porque é gerado). Portanto, se sua nova notificação precisar de um campo de nível superior totalmente novo em `contents` - algo que ainda não seja `badge`, `message`, `status`, `url` ou o objeto `body` - você edita o `@psalm-type` em `Notification.php` e, em seguida, gera novamente `api_types.ts` para que o lado Vue possa ler seu campo sem TypeScript reclamando. Se você puder expressar seus dados dentro da carga `body` existente (veja abaixo), você pode pular esta etapa completamente, o que é mais um motivo para preferi-lo.

## Dois estilos de renderização: a opção por tipo versus o `body` localizado

Aqui está a decisão mais importante e o motivo para ler `Notification.vue` antes de escrever qualquer código de servidor. Existem **duas maneiras** de gerar uma notificação, e elas ficam lado a lado no mesmo componente:

1. **O switch herdado por `type`.** Para alguns tipos codificados (`badge`, `demotion`, `general_notification`), `Notification.vue` possui braços `switch (this.notification.contents.type)` explícitos que escolhem um ícone, constroem o texto e calculam o link diretamente dos campos de carga útil. Cada um desses getters termina em um braço `default:`, então um tipo não reconhecido ainda é renderizado - ele apenas obtém o ícone `/media/info.png` genérico e nenhum texto.

2. **O caminho `body` localizado.** Se `contents.body` estiver presente, ele vence a troca de ícone, texto e URL — cada getter verifica `if (this.notification.contents.body)` primeiro e retorna do `body` antes mesmo de chegar ao `switch`. O `body` carrega um `localizationString` (uma chave de tradução), `localizationParams` (valores a interpolar), um `url` e um `iconUrl`. Este é o caminho moderno e compatível com i18n, e é por isso que os tipos de notificação mais recentes não precisam de uma única linha nova de Vue: eles entregam ao componente uma chave de tradução e ele é renderizado genericamente.

O resultado prático: **para um novo tipo, use o caminho `body`, a menos que você realmente precise de marcação personalizada.** Isso significa que você adiciona uma string de tradução e chama um auxiliar PHP, e nunca toca em `Notification.vue`. A opção por tipo só vale a pena quando o layout em si é especial (os emblemas, por exemplo, constroem um caminho `<img>` a partir da carga útil e precisam de um estilo personalizado).

### O que o switch realmente faz

Para ver por que o caminho `body` é mais fácil, veja o que você teria que adicionar. `Notification.vue` calcula quatro coisas em `contents`, e cada uma é um getter com a mesma forma - verifique primeiro `body` e depois ative `type`:

- **`iconUrl`** — `body.iconUrl` se existir um corpo; caso contrário, `badge` → `/media/dist/badges/${badge}.svg`, `demotion` → `/media/banned.svg` quando `status == 'banned'`, senão `/media/warning.svg`, `general_notification` → `/media/email.svg` e tudo mais → `/media/info.png`.
- **`text`** — As notificações baseadas em `body` renderizam Markdown (veja a seguir), então `text` atende apenas aos braços simples: `demotion` e `general_notification` retornam `contents.message` (ou `''` se estiver ausente), e todos os outros tipos retornam `''`.
- **`notificationMarkdown`** — se existir um `body`, é `ui.formatString(T[body.localizationString], body.localizationParams)`; caso contrário, o único braço não vazio é o `badge`, que constrói o `ui.formatString(T.notificationNewBadge, { badgeName: T['badge_' + badge + '_name'] })`. Isso resolve a string de tradução `notificationNewBadge = "You have received a new badge: **%(badgeName)**."` em [`frontend/templates/en.lang`](https://github.com/omegaup/omegaup/blob/main/frontend/templates/en.lang), e é por isso que as notificações de crachá aparecem como Markdown em negrito.
- **`url`** — `body.url` se existir um corpo; caso contrário, `general_notification` → `contents.url`, `badge` → `/badge/${badge}/` e `demotion` → `''` (há um `// TODO: Add link to problem page.` ali mesmo na fonte, um bom exemplo do tipo de borda semi-acabada que você encontrará e não deve se surpreender).

Observe que adicionar um tipo ao switch significa tocar em **quatro getters** e obter o ícone, o texto, a marcação e o link todos consistentes — em comparação com o caminho `body`, onde você fornece essas quatro coisas como dados em um objeto JSON.

## Nomeando o tipo: adicione uma constante, não espalhe literais de string

A string de tipo é compartilhada entre o servidor que a escreve e o Vue que a lê, portanto, ele deseja uma única fonte de verdade. O DAO já os coleta como constantes de classe no topo de [`frontend/server/src/DAO/Notifications.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Notifications.php) — atualmente cerca de vinte deles, incluindo `CERTIFICATE_AWARDED = 'certificate-awarded'`, `CONTEST_REGISTRATION_ACCEPTED = 'contest-registration-accepted'`, `CONTEST_REGISTRATION_REJECTED = 'contest-registration-rejected'`, `COURSE_SUBMISSION_FEEDBACK = 'course-submission-feedback'`, `DEMOTION = 'demotion'` e mais uma dúzia de variantes de registro e esclarecimento de cursos/concursos. Adicione seu novo tipo como uma constante para que todo o lado do PHP se refira a `\OmegaUp\DAO\Notifications::YOUR_TYPE` em vez de uma string vazia que pode ficar fora de sincronia devido a um erro de digitação.

Uma coisa que vale a pena conhecer para não atrapalhar você: os tipos de switch mais antigos em `Notification.vue` (`badge`, `general_notification`) *não* estão nessa lista de constantes - eles são anteriores a ela e são escritos como literais brutos em lugares como o emblema cron. As constantes são todas kebab-case (`certificate-awarded`); os tipos de switch legados são cobra/inferior (`general_notification`). Essa não é uma regra que você precisa obedecer, apenas uma junção entre o estilo antigo e o novo que você notará. Novos tipos devem seguir a convenção constante.

## Criando a notificação do servidor

Existem dois lugares realistas em que uma notificação nasce: dentro de uma solicitação PHP ou de um cron Python.

### Do PHP: use os auxiliares do controlador de notificação

`\OmegaUp\Controllers\Notification` (em [`Notification.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/Notification.php)) existe precisamente para que você não role manualmente a inserção do DAO. Para uma notificação localizada no estilo `body` destinada a uma lista de usuários, o one-liner é `setCommonNotification`, que pega os IDs de usuário, um `\OmegaUp\TranslationString`, o tipo, um URL e os parâmetros de localização e monta todo o blob `body` para você (ele até preenche `iconUrl` como `/media/info.png` por padrão):

```php
\OmegaUp\Controllers\Notification::setCommonNotification(
    userIds: $userIds,
    localizationString: new \OmegaUp\TranslationString('notificationYourNewString'),
    notificationType: \OmegaUp\DAO\Notifications::YOUR_TYPE,
    url: "/somewhere/{$alias}/",
    localizationParams: ['contestTitle' => $contest->title],
);
```
Nos bastidores, isso chama `setNotification(userIds, contents)`, que faz um loop dos IDs de usuário em objetos de valor `\OmegaUp\DAO\VO\Notifications` e os persiste com `\OmegaUp\DAO\Notifications::createBulk(...)`. O nome `createBulk` é deliberado: ele faz um único `INSERT` em massa em vez de uma consulta por usuário, transformando o que seriam O(N) viagens de ida e volta em O(1) — o que é importante quando você notifica todos os participantes de um concurso de uma só vez. Se você precisar de algo que o auxiliar não modela, o exemplo mais completo é `createForCourseAccessRequest`, que codifica json um `body` completo (com seu próprio `localizationString`, `localizationParams`, `url` e `iconUrl`) manualmente e chama `\OmegaUp\DAO\Notifications::create(...)` para um único usuário.

### No cron do Python: insira a linha diretamente

Os crons não passam pelo controlador PHP - eles próprios escrevem a linha `Notifications`. O atribuidor do crachá, [`stuff/cron/assign_badges.py`](https://github.com/omegaup/omegaup/blob/main/stuff/cron/assign_badges.py), é a referência: em `save_new_owners` ele constrói uma tupla por novo proprietário do crachá e executa um `INSERT INTO Notifications (user_id, contents) VALUES (%s, %s)` simples, onde `contents` é `json.dumps({'type': 'badge', 'badge': badge})`. Esse é o truque - o cron só precisa produzir o mesmo formato JSON que o frontend espera; as colunas `notification_id`, `timestamp` e `read` assumem seus padrões. Se você estiver adicionando uma notificação baseada em cron, espelhe isto: crie seu ditado `contents` com um `type` e carga útil, `json.dumps` e insira.

## Adicionando a string de tradução

Se você seguiu o caminho `body` (e deveria), o `localizationString` que você passou deve realmente existir ou `ui.formatString(T[...], ...)` no frontend será resolvido como `undefined`. Adicione sua chave a [`frontend/templates/en.lang`](https://github.com/omegaup/omegaup/blob/main/frontend/templates/en.lang) — e a `es.lang` e `pt.lang` junto com ela — usando a mesma interpolação `%(paramName)` que o objeto params fornece. A sequência do crachá é o padrão a ser copiado: `notificationNewBadge = "You have received a new badge: **%(badgeName)**."`, onde `%(badgeName)` se alinha com a chave `badgeName` entregue a `formatString`. O valor é renderizado como Markdown, então `**bold**` e links funcionam.

## Ensinando Notification.vue a renderizá-lo (somente se você ignorou `body`)

Se a sua notificação usa `body`, pare - o frontend está concluído, porque o braço `body` genérico em cada getter já o renderiza. Somente se você precisar de um layout personalizado, você edita [`Notification.vue`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/components/notification/Notification.vue): adicione um braço `case 'yourType':` aos getters `iconUrl`, `text`/`notificationMarkdown` e `url` para que o ícone, o texto e o link sejam todos cobertos e adicione qualquer SCSS com escopo que o layout precisa na parte inferior do arquivo. Mantenha-os consistentes - um tipo que retorna uma URL de `url`, mas nada dos getters de texto será renderizado como uma linha clicável vazia, o que é confuso. Este é o caminho que o wiki alerta: “este formato só funcionará se os estilos apropriados forem criados ou ajustados no componente Vue”.

## O caminho de leitura: como a linha volta ao sino

Vale a pena ver a viagem de volta uma vez, porque explica por que `read` e `user_id` são importantes e onde procurar quando uma notificação “não aparece”.

Quando a barra de navegação é carregada, [`frontend/www/js/omegaup/common/navbar.ts`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/common/navbar.ts) chama a API `Notification.myList`, que atinge `apiMyList` no controlador. Esse endpoint executa `ensureIdentity()` (você deve estar logado), busca linhas via `\OmegaUp\DAO\Notifications::getUnreadNotifications($r->user)` - uma consulta que seleciona `notification_id`, `contents` e `timestamp` `WHERE user_id = ? AND read = 0 ORDER BY timestamp ASC` - `json_decode` coloca cada string `contents` na matriz `NotificationContents` e `array_reverse`s o lista para que o mais novo fique no topo. Então: se a sua linha inserida já tiver `read` verdadeiro, ou o `user_id` errado, ela nunca aparecerá silenciosamente. Essa é a primeira coisa a verificar quando uma notificação desaparece.

A lista decodificada flui para `List.vue` (o menu suspenso), que mostra o sino FontAwesome, um emblema de contagem vermelha igual a `notifications.length` e um `Notification.vue` por entrada digitada por `notification_id`. Clicar em uma única notificação ou "marcar tudo como lido" emite um evento `read`/`read-notifications` de volta para `navbar.ts`, que chama `Notification.readNotifications({ notifications: [...ids] })` e, em seguida, busca novamente `myList` para atualizar o selo. No servidor, `apiReadNotifications` chama `ensureMainUserIdentity()`, então para cada ID carrega a linha e ** verifica se `notification->user_id === r->user->user_id`, jogando `ForbiddenAccessException` caso contrário ** (para que você não possa marcar as notificações de outra pessoa como lidas adivinhando IDs), lança `NotFoundException` para um ID desconhecido e, finalmente, define `read = true` e atualizações. Se uma notificação continha um `url`, clicar nele marca a leitura e navega até lá - é por isso que o getter `url` e `handleClick` em `Notification.vue` emitem o evento `remove` com o URL anexado.

## A lista de verificação, de ponta a ponta

Juntando tudo, adicionar um novo tipo de notificação é, na ordem:

1. **Adicione uma constante `type`** a `\OmegaUp\DAO\Notifications` para que ambos os lados compartilhem a mesma grafia.
2. **Decida o formato da carga útil.** Prefira o caminho `body` (`localizationString` + `localizationParams` + `url` + `iconUrl`) para que o frontend o renderize genericamente. Invente novos campos `contents` de nível superior apenas se `body` não puder expressá-los - e se você fizer isso, atualize o `@psalm-type NotificationContents` em `Notification.php` e gere novamente `api_types.ts` com `APITool.php`.
3. **Adicione a string de tradução** a `en.lang`/`es.lang`/`pt.lang` com espaços reservados `%(param)` correspondentes.
4. **Emitir a notificação** — do PHP via `\OmegaUp\Controllers\Notification::setCommonNotification(...)` (ou `createBulk` para muitos usuários), ou de um cron com um `INSERT INTO Notifications (user_id, contents)` direto cujo `contents` é `json.dumps({...})`.
5. **Somente se você ignorou `body`:** adicione os braços `case` correspondentes aos getters `iconUrl` / text / `url` de `Notification.vue`, além de quaisquer estilos de escopo.
6. **Verifique** fazendo login como usuário alvo e observando o sino — lembrando que a linha deve ter `read = 0` e o `user_id` correto para aparecer.

!!! dica "Na dúvida, pergunte"
    Se você não tiver certeza de qual `type` e formato de carga útil se adaptam ao seu caso, os mantenedores preferem que você pergunte do que adivinhar - aumente-o no canal `#depto_tecnico` no Slack (ou nos canais do desenvolvedor no omegaUp [Discord](https://discord.gg/gMEMX7Mrwe)). :)

## Documentação relacionada

- **[Padrões de banco de dados](database-patterns.md)** — a camada DAO/VO na qual a tabela `Notifications` funciona, incluindo a forma JSON `contents`.
- **[Componentes Vue](components.md)** — convenções de componentes, i18n com `ui.formatString` e Storybook.
- **[Diretrizes de codificação](coding-guidelines.md)** — as regras de PHP e TypeScript que essas alterações devem passar.
