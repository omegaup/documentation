---
title: Padrões de banco de dados
description: Compreendendo os padrões DAO/VO no omegaUp
icon: bootstrap/table
---
# Padrões de banco de dados: DAO/VO

Cada byte que omegaUp lê ou grava no MySQL 8.0 passa por uma porta estreita: a camada **DAO/VO** sob `frontend/server/src/DAO/`. Os controladores nunca abrem uma conexão `mysqli`, nunca concatenam um `SELECT` e nunca veem uma linha de resultado bruto. Eles solicitam objetos digitados a um objeto de acesso a dados e retornam objetos digitados manualmente. A razão não é estética – é que omegaUp é uma plataforma de concurso onde uma consulta de placar disparada durante um evento ao vivo com milhares de envios simultâneos deve ser previsível, revisável e à prova de injeção. Centralizar todo o SQL em uma camada significa que cada consulta é preparada (parametrizada), cada consulta pode ser grepada e as caras podem ser armazenadas em cache em exatamente um lugar.

A camada tem três camadas, e a divisão é importante porque duas delas são escritas por máquina e uma é sua:

- **VO (Objeto de Valor)** — `frontend/server/src/DAO/VO/`. Uma classe de suporte de dados digitada e burra por tabela. Gerado automaticamente. Não edite.
- **DAO básico** — `frontend/server/src/DAO/Base/`. Uma classe `abstract` por tabela contendo o padrão CRUD SQL (criar/ler por chave primária/atualizar/excluir). Gerado automaticamente. Não edite.
- **DAO público** — `frontend/server/src/DAO/`. Uma classe por tabela que `extends` é sua Base e é onde **você** adiciona as consultas escritas à mão que o gerador não consegue adivinhar. Esta é a única camada que você toca manualmente.

Ambas as camadas geradas abrem com o mesmo cabeçalho de grito e suporta carga:

```php
/** ************************************************************************ *
 *                    !ATENCION!                                             *
 *                                                                           *
 * Este codigo es generado automáticamente. Si lo modificas, tus cambios     *
 * serán reemplazados la proxima vez que se autogenere el código.            *
 * ************************************************************************* */
```
Se você vir esse banner no topo de um arquivo, tudo o que você escrever nele será revertido silenciosamente na próxima vez que alguém executar o gerador. É por isso que a camada DAO pública existe como um *arquivo separado* estendendo a base - para que seus métodos personalizados fiquem em algum lugar que o gerador nunca irá sobrescrever.

## O VO: uma linha digitada e nada mais

Um objeto de valor mapeia um para um para uma tabela. Pegue [`frontend/server/src/DAO/VO/Runs.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/VO/Runs.php), o objeto da tabela `Runs` (o resultado avaliado de uma submissão). Ele `extends \OmegaUp\DAO\VO\VO` declara uma constante `FIELD_NAMES` listando exatamente as colunas que existem e expõe uma propriedade de tipo público por coluna com seu esquema padrão incorporado:

```php
class Runs extends \OmegaUp\DAO\VO\VO {
    const FIELD_NAMES = [
        'run_id' => true,
        'submission_id' => true,
        'version' => true,
        'commit' => true,
        'status' => true,
        'verdict' => true,
        // ...
    ];

    /** @var string */
    public $status = 'new';   // a fresh Run starts life as 'new'

    /** @var float */
    public $score = 0.00;

    /** @var \OmegaUp\Timestamp */
    public $time;             // CURRENT_TIMESTAMP
}
```
O construtor pega um `?array $data` opcional — a linha associativa que você obteria diretamente do `mysqli` — e executa três trabalhos antes de confiar em um único valor. Primeiro, ele rejeita o lixo: `array_diff_key($data, self::FIELD_NAMES)` captura qualquer coluna que não esteja na tabela, e uma coluna desconhecida lança `Unknown columns: ...` imediatamente, então um alias SELECT digitado explode na hidratação, em vez de surgir silenciosamente um `null` três camadas acima. Em segundo lugar, ele *coage* todos os campos ao seu tipo declarado - `run_id` a `intval`, `score` a `floatval`, `commit` a `strval` - porque uma linha `mysqli` bruta fornece strings para tudo e omegaUp é executado em Psalm com tipos estritos, portanto, um `"42"` fibroso onde um `int` esperado é uma falha na análise estática. Terceiro, os carimbos de data e hora recebem tratamento especial: `time` é percorrido por `\OmegaUp\DAO\DAO::fromMySQLTimestamp()` em um `\OmegaUp\Timestamp` (wrapper interno de segundos POSIX do omegaUp) e se a linha omitir `time` inteiramente, o VO o padroniza como `new \OmegaUp\Timestamp(\OmegaUp\Time::get())` - "agora" - em vez de deixá-lo nulo.

Vale a pena ler o PHPDoc em nível de campo, em vez de ignorá-lo, porque ele carrega a semântica que o nome da coluna oculta. No `Runs`, `commit` é documentado como *"El hash SHA1 del commit en la rama master del problema con el que se realizou el envío"* e `version` como *"El hash SHA1 del árbol de la rama private"* - ou seja, esses dois parecem strings genéricas, mas são hashes de objeto git que vinculam uma execução julgada à revisão exata do problema que ele executou contra. Retire esse comentário e a próxima pessoa o tratará como um texto opaco e interromperá o julgamento.

A base compartilhada [`\OmegaUp\DAO\VO\VO`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/VO/VO.php) fornece a cada VO três maneiras de chegar à rede: `asArray()` (via `get_object_vars`) para empacotamento JSON, `asFilteredArray($filters)` para emitir apenas um subconjunto de campos na lista de permissões (usado constantemente em respostas de API para que um controlador possa retornar, digamos, colunas públicas de um usuário sem vazar o hash de senha) e `__toString()` que é apenas `json_encode` de `asArray()`. Um VO é deliberadamente livre de comportamento: sem consultas, sem validação além da coerção de tipo, sem regras de negócios. É uma mala para uma fila.

## The Base DAO: o CRUD que você nunca escreve

A base abstrata gerada contém as quatro operações que são idênticas para todas as tabelas, diferindo apenas na lista de colunas. Veja [`frontend/server/src/DAO/Base/Runs.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Base/Runs.php): é um `abstract class Runs` cujo método é `final public static`, então as consultas são chamadas como `RunsDAO::getByPK(...)` e uma subclasse não pode sombreá-las acidentalmente. Cada método passa pelo singleton `\OmegaUp\MySQLConnection::getInstance()` e - este é todo o argumento de segurança - usa espaços reservados `?` com um array `$params` separado, nunca interpolação de string:

```php
final public static function getByPK(int $run_id): ?\OmegaUp\DAO\VO\Runs {
    $sql = '
        SELECT `Runs`.`run_id`, `Runs`.`submission_id`, /* ...all columns... */
        FROM `Runs`
        WHERE (`run_id` = ?)
        LIMIT 1;';
    $params = [$run_id];
    $row = \OmegaUp\MySQLConnection::getInstance()->GetRow($sql, $params);
    if (empty($row)) {
        return null;
    }
    return new \OmegaUp\DAO\VO\Runs($row);
}
```
`getByPK` retorna `?\OmegaUp\DAO\VO\Runs` - o `?` não é decoração, é o contrato: **uma falha retorna `null`, e o chamador deve lidar com isso. ** `create()` executa o `INSERT` e, em seguida, grava o ID de incremento automático recém-criado de volta no VO (`$Runs->run_id = ...->Insert_ID()`) e retorna a contagem de linhas afetadas, para que, após a criação, você possa ler o novo chave primária diretamente do objeto que você passou. `update()` retorna `Affected_Rows()`. `delete()` é o mais preciso: se o `DELETE` tocar em zero linhas, ele não retorna silenciosamente, ele lança `\OmegaUp\Exceptions\NotFoundException('recordNotFound')`, na lógica de que pedir para excluir uma linha que não existe é um bug no chamador, não um no-op - e o docblock avisa que um objeto excluído *não* pode ser ressuscitado reinserindo, porque `create()` criará um novo chave primária em vez de reutilizar a antiga.

Dois ajudantes gerados existem puramente para que testes e caminhos quentes não paguem pela hidratação que não usarão. `existsByPK($run_id)` executa `SELECT COUNT(*)` e retorna um `bool` "**sin necesidad de carregar sus campos**" - mais barato que `getByPK` quando você só precisa saber *se* existe uma linha, porque você pula a construção do VO. `countAll()` retorna a contagem total de linhas da mesma maneira, principalmente para testes que afirmam cardinalidade.

`getAll()` é o único método base com uma mina terrestre, e o gerador o documenta inline: ele lê a tabela *inteira* em um array de VOs, "*consumir una cantidad de memoria proporcional ao número de registros registrados*". O padrão é 100 linhas por página (`$filasPorPagina = 100`), ordenadas pela chave primária `run_id` crescente, e fortalece os dois parâmetros que de outra forma seriam vetores de injeção - a coluna de classificação é passada por `MySQLConnection::escape()` e a direção por `Validators::validateInEnum($tipoDeOrden, 'order_type', ['ASC', 'DESC'])` - porque, diferentemente de um valor `?`, um nome de coluna e uma direção de classificação não podem ser um parâmetro vinculado e devem ser higienizados manualmente. Use `getAll()` em `Countries` ou `Languages`; nunca procure-o em `Runs` ou `Submissions`, que possuem milhões de linhas.

## A classe de utilitário base `DAO`

Por baixo de tudo isso está [`\OmegaUp\DAO\DAO`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/DAO.php), uma classe `final` de auxiliares estáticos na qual o código gerado se apoia. Ele possui transações - `transBegin()`, `transEnd()` e `transRollback()` envolvem `MySQLConnection` `StartTrans()` / `CompleteTrans()` / `FailTrans()` - então, quando um controlador precisa de várias gravações para ter sucesso ou falhar juntas (criar um problema, sua ACL e seu conjunto de problemas de uma só vez), ele os coloca entre `DAO::transBegin()` / `DAO::transEnd()`. Ele possui a ponte de carimbo de data / hora (`toMySQLTimestamp` / `fromMySQLTimestamp`) que traduz entre o `\OmegaUp\Timestamp` do omegaUp e o `'Y-m-d H:i:s'` do MySQL em UTC via `gmdate`. E expõe `isDuplicateEntryException($e)`, que permite que um chamador capte uma colisão de chave única (um nome de usuário duplicado, digamos) e transforme-o em um erro de validação amigável em vez de 500 – ele inspeciona um `\OmegaUp\Exceptions\DatabaseOperationException` e pergunta `->isDuplicate()`.

## Quando escrever um método DAO personalizado

A base gerada cobre exatamente uma forma de acesso: tabela única, linha única, codificada por chave primária. No momento em que você precisa de um `JOIN`, um agregado, uma lista filtrada ou uma gravação em lote, o gerador não tem nada para você e você escreve o método manualmente no DAO público. Isso não é uma solução alternativa – é a costura projetada. A classe pública `extends` a base, herda todo o CRUD gratuito e adiciona tudo o que o recurso precisar.

[`frontend/server/src/DAO/Runs.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Runs.php) é o exemplo vívido: cerca de quarenta métodos escritos à mão sobrepostos aos sete herdados. A maioria são junções que a base nunca poderia expressar, como `getBestProblemScore`, que caminha de uma linha `Submissions` para sua linha `Runs` atual para encontrar a pontuação máxima de um usuário em um problema:

```php
final public static function getBestProblemScore(
    int $problemId,
    int $identityId
): ?float {
    $sql = '
        SELECT r.score * 100
        FROM Submissions s
        INNER JOIN Runs r ON s.current_run_id = r.run_id
        WHERE s.identity_id = ? AND s.problem_id = ? AND
              r.status = "ready" AND s.`type` = "normal"
        ORDER BY r.score DESC, r.penalty ASC
        LIMIT 1;';
    $val = [$identityId, $problemId];
    /** @var float|null */
    return \OmegaUp\MySQLConnection::getInstance()->GetOne($sql, $val);
}
```
Observe a anotação `/** @var float|null */` logo antes do retorno. `mysqli` devolve escalares não digitados e `GetOne` / `GetAll` retorna `mixed`, então o Salmo não pode conhecer a forma por si só; o `@var` (e, para linhas com várias colunas, um docblock completo em forma de array como `@return list<array{alias: string, contest_score: float|null, guid: string, ...}>`) é como o DAO personalizado permanece seguro para tipos e, principalmente, como a forma flui até o TypeScript. Essas anotações de formato de retorno são lidas por `frontend/server/cmd/APITool.php`, o gerador que produz `frontend/www/js/omegaup/api_types.ts` – portanto, um docblock desleixado em um método DAO aparece como um tipo errado no frontend Vue.

A outra razão para escrever um método à mão é **recolher viagens de ida e volta**, e é aqui que a regra "evitar O(n) consultas" do andaime ganha força. O antipadrão está chamando um método DAO por linha dentro de um loop:

```php
// ❌ Bad: one query per user — O(n) round-trips to MySQL
foreach ($users as $user) {
    $notification = new \OmegaUp\DAO\VO\Notifications([/* ... */]);
    \OmegaUp\DAO\Notifications::create($notification);
}
```
Cada iteração é uma viagem completa de ida e volta da rede para o MySQL; cem usuários equivalem a cem viagens sequenciais e, sob carga de concurso, é assim que você derrete o banco de dados. A correção é um único método personalizado que faz o lote em uma consulta. [`\OmegaUp\DAO\Notifications::createBulk`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Notifications.php) é a versão canônica do lado de gravação, e seu docblock afirma claramente a vitória - *"reduzindo viagens de ida e volta do banco de dados de O(N) para O(1)"* - construindo um `INSERT` de várias linhas com uma tupla de espaço reservado por linha:

```php
public static function createBulk(array $notifications): int {
    if (empty($notifications)) {
        return 0;
    }
    $rowPlaceholders = [];
    $params = [];
    foreach ($notifications as $notification) {
        $rowPlaceholders[] = '(?, ?, ?, ?)';
        $params[] = is_null($notification->user_id) ? null : intval($notification->user_id);
        $params[] = \OmegaUp\DAO\DAO::toMySQLTimestamp($notification->timestamp);
        $params[] = intval($notification->read);
        $params[] = $notification->contents;
    }
    $sql = 'INSERT INTO `Notifications` (`user_id`, `timestamp`, `read`, `contents`)
            VALUES ' . join(', ', $rowPlaceholders) . ';';
    \OmegaUp\MySQLConnection::getInstance()->Execute($sql, $params);
    return \OmegaUp\MySQLConnection::getInstance()->Affected_Rows();
}
```
O envio de 500 notificações de crachá após uma execução do cron é um `INSERT` em vez de 500. Mesmo aqui a disciplina `?` é válida – os espaços reservados são gerados, os valores permanecem vinculados. `Notifications` também mostra o terceiro trabalho da camada DAO pública: ele eleva o vocabulário de domínio da tabela em constantes de classe (`Notifications::DEMOTION`, `Notifications::CERTIFICATE_AWARDED`, `Notifications::CONTEST_CLARIFICATION_REQUEST`,…) para que o resto da base de código se refira aos tipos de notificação por nome, não por string mágica.

## A filosofia da consulta: *sencillito, carismático y cacheable*

Os mantenedores têm uma frase para as perguntas que fundamentam as páginas que os competidores mais atingiram – o acesso público de um concurso, um placar, uma lista de problemas. A wiki descreve a consulta ideal de detalhes do concurso como *"un query sencilito, carismático y cacheable"*: pequena, carismática e armazenável em cache. É uma piada, mas também é a verdadeira regra de design. "Pouco" significa que ele toca poucas tabelas e retorna o mínimo que a página precisa — mini-classificação, tempo restante, stubs de problemas — e não todo o gráfico do objeto. "Cacheable" significa que é determinístico e principalmente de leitura, então o resultado pode ser memorizado e servido sem tocar no MySQL. Quando você está decidindo se deseja adicionar um método DAO personalizado ou engordar um já existente, esta é a barreira: se a consulta estiver em um caminho de leitura dinâmica, torne-a pequena o suficiente para que seu resultado possa residir no Redis.

## Cache com Redis (e APCu)

O cache reside em [`frontend/server/src/Cache.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Cache.php). `\OmegaUp\CacheAdapter` é uma abstração sobre dois back-ends selecionados por `OMEGAUP_CACHE_IMPLEMENTATION` em `config.default.php` - o padrão é `'apcu'` (por processo na memória, bom para uma única caixa), e a produção o transforma em `'redis'`, que `pconnect`s para `REDIS_HOST` (`'redis'`) em `REDIS_PORT` (`6379`) e autentica com `REDIS_PASS`. Tudo acima do adaptador é independente de backend, então o DAO e o código do controlador nunca sabem ou se importam com qual armazenamento está por trás dele.

As entradas de cache são delimitadas por uma **constante de prefixo**, e ler a lista delas em `Cache.php` é a maneira mais rápida de aprender o que omegaUp considera que vale a pena armazenar em cache: `Cache::PROBLEM_STATEMENT` (`'statement-'`), `Cache::USER_PROFILE` (`'profile-'`), `Cache::CONTESTANT_SCOREBOARD_PREFIX` (`'scoreboard-'`), `Cache::CONTEST_INFO` (`'contest-info-'`), `Cache::PROBLEMS_LIST` (`'problems-list-'`), `Cache::RUN_COUNTS` (`'run-counts-'`) e mais algumas dúzias. Uma chave completa é `prefix + id` – por ex. o cache de perfil do usuário `omegaup` é `profile-omegaup`.

O único método que você usará é `getFromCacheOrSet` – cache de leitura em uma única chamada:

```php
$accessibleAclIds = \OmegaUp\Cache::getFromCacheOrSet(
    \OmegaUp\Cache::PROBLEM_IDENTITY_TYPE,   // prefix
    $cacheKeyId,                             // id
    fn () => /* the sencillito query goes here */,  // computed only on a miss
    $timeout                                 // TTL in seconds
);
```
Em caso de acerto, ele retorna o valor armazenado em cache e o encerramento nunca é executado; em caso de falha, ele executa o fechamento, armazena o resultado na chave com o TTL fornecido e o retorna. Sob o capô `set` / `get` / `delete` cada curto-circuito quando o cache é desabilitado (`isEnabled()` falso) - `get` retorna `null`, `set` e `delete` retorna `false` - então uma caixa sem back-end de cache degrada para atingir o MySQL todas as vezes em vez de travar, e cada acerto/erro/armazenamento é registrado Monolog sob o nome de canal `cache` para quando você precisar ver por que algo está ou não sendo servido no cache.

Os TTLs são por domínio e ajustados à rapidez com que os dados subjacentes ficam obsoletos, tudo em `config.default.php` em segundos. O padrão global `APC_USER_CACHE_TIMEOUT` é `7 * 24 * 3600` – sete dias – para dados que essencialmente nunca mudam. Mas as informações de um concurso ao vivo são armazenadas em cache por apenas `10` segundos (`APC_USER_CACHE_CONTEST_INFO_TIMEOUT`), uma declaração de problema para `60`, uma lista de problemas para `60 * 30` (trinta minutos) e sessões para `8 * 3600` para corresponder ao tempo de vida do token de autenticação. `APC_USER_CACHE_PROBLEM_STATS_TIMEOUT` é `0`, que significa "cache sem expiração, até que seja explicitamente invalidado". Esses números são o ajuste atual e devem ser revisados ​​– escolha um TTL perguntando até que ponto a página pode estar errada e por quanto tempo.

### Invalidação: TTL, exclusão direcionada ou aumento de versão

Como a maioria das gravações passa por DAOs, mas o cache é codificado por conceitos de domínio, **a invalidação reside nos controladores próximos à gravação, não dentro do DAO.** Quando um controlador altera algo do qual uma entrada de cache depende, ele exclui essa entrada pela chave exata. O caminho de verificação de perfil em [`Controllers/User.php`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/User.php) faz exatamente isso logo após inverter o sinalizador verificado de um usuário:

```php
// Expire profile cache
\OmegaUp\Cache::deleteFromCache(
    \OmegaUp\Cache::USER_PROFILE,
    strval($identity->username)
);
```
A regra prática: se uma gravação tornar um valor em cache errado *agora* e uma leitura obsoleta confundir um usuário (uma conta recém-verificada ainda aparecendo como não verificada), exclua a chave específica para que a próxima leitura a recalcule; se um pouco de obsolescência for inofensivo, deixe o TTL expirar sozinho.

Para o caso em que você teria que excluir centenas de chaves compartilhando um prefixo - cada placar de um concurso, digamos - existe o `invalidateAllKeys($prefix)`, e sua implementação é a parte inteligente. Ele **não** verifica e exclui chaves correspondentes. Em vez disso, ele mantém um número inteiro de versão por prefixo (`v{prefix}`) que está inserido em cada chave real, e a invalidação apenas o incrementa (`inc("v{prefix}")`). As chaves antigas ainda estão fisicamente no Redis, mas agora estão inacessíveis porque cada nova leitura e gravação usa a versão alterada, portanto, elas nunca são buscadas ou atualizadas novamente e simplesmente envelhecem. Um `INCR` invalida um namespace inteiro em O(1) em vez de uma varredura O(n) — o mesmo instinto *sencillito* aplicado ao próprio gerenciamento de cache.

## Regenerando a camada DAO e VO

Você nunca escreve à mão um Base DAO ou um VO. Você altera o esquema e deixa o gerador reescrevê-los. A fonte da verdade é `frontend/database/schema.sql`; depois de editá-lo (normalmente junto com uma migração criada com `stuff/db-migrate.py`), execute:

```sh
./stuff/update-dao.sh
```
Esse script copia `schema.sql` para `frontend/database/dao_schema.sql` para acionar a regeneração e, em seguida, executa `stuff/update-dao.py`, que reescreve tudo em `frontend/server/src/DAO/Base/` e `frontend/server/src/DAO/VO/` a partir dos modelos em `stuff/dao_templates/` (com `stuff/dao_utils.py` e `stuff/dao_linter.py` mantendo a saída consistente). Seus métodos escritos à mão nas classes públicas `frontend/server/src/DAO/` permanecem intocados, porque residem em arquivos diferentes - que é o motivo da divisão base versus público. Se você deseja editar um arquivo que carrega o banner `!ATENCION!`, pare: você deseja um método personalizado no DAO público ou deseja uma alteração de esquema e uma regeneração.

## Notificações do usuário (tabela `Notifications`)

A IU da web carrega linhas pendentes para um usuário da tabela **`Notifications`** por meio de [`\OmegaUp\DAO\Notifications::getUnreadNotifications`](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/DAO/Notifications.php) — ele próprio um método DAO escrito à mão que seleciona as linhas `read = 0` ordenadas mais antigas primeiro. A coluna **`contents`** de cada linha é JSON que orienta a renderização em [`Notification.vue`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/components/notification/Notification.vue).

### Formato JSON

No mínimo, inclua uma string `type` para que o componente escolha o layout correto. Outras chaves são uma **carga útil** específica para esse tipo.

```json
{
  "type": "notificationType",
  "any_field": "value"
}
```
### Valores `type` suportados (alto nível)

| `type` | Finalidade | Carga útil típica |
|--------|---------|-----------------|
| `badge` | Distintivo ganho | `badge` — identificador do crachá (por exemplo, nome do marco de pontuação) |
| `demotion` | Alteração de conta/estado | `status`, `message` |
| `general_notification` | Texto de formato livre | `message`, opcional `url` |

### Estilo de "sistema" localizado (`body`)

Para traduções através do sistema i18n, você pode usar:

```json
{
  "type": "notification-type",
  "body": {
    "localizationString": "translationKey",
    "localizationParams": {
      "param1": "value1"
    },
    "url": "/path/to/resource",
    "iconUrl": "/media/icon.png"
  }
}
```
### Exemplo (emblema)

Inserindo uma linha cujo `contents` se assemelha a:

```json
{
  "type": "badge",
  "badge": "500score"
}
```
diz à UI para renderizar uma notificação em estilo de crachá; os campos extras são interpretados em `Notification.vue`. Para obter um exemplo concreto do lado do servidor, consulte [`stuff/cron/assign_badges.py`](https://github.com/omegaup/omegaup/blob/main/stuff/cron/assign_badges.py) — um cron que atribui emblemas e é exatamente o tipo de trabalho que distribui muitas notificações, portanto, ele as insere por meio do `Notifications::createBulk` em vez de uma linha por vez.

!!! dica "Perguntas"
    Pergunte nos canais do desenvolvedor omegaUp [Discord](https://discord.gg/gMEMX7Mrwe) se não tiver certeza de qual `type` e carga útil usar.

## Documentação Relacionada

- **[Arquitetura de back-end](../architecture/backend.md)** - Estrutura de back-end
- **[Esquema de banco de dados](../architecture/database-schema.md)** - Visão geral do esquema
- **[Diretrizes de codificação](coding-guidelines.md)** - Diretrizes de PHP
