---
title: Padrões de banco de dados
description: Compreendendo os padrões DAO/VO no omegaUp
icon: bootstrap/table
---
# Padrões de banco de dados: DAO/VO

omegaUp usa o padrão **DAO/VO (Data Access Object/Value Object)** para todas as interações de banco de dados.

## Visão geral do padrão

### Objetos de valor (VO)
- Mapeie diretamente para tabelas de banco de dados
- Uma aula VO por mesa
- Gerado automaticamente a partir do esquema
- Localizado em `frontend/server/src/DAO/VO/`

### Objetos de acesso a dados (DAO)
- Classes estáticas para operações de banco de dados
- Uma classe DAO por tabela
- Métodos: `search()`, `getByPK()`, `save()`, `delete()`
- Localizado em `frontend/server/src/DAO/`

## Exemplo de uso

### Pesquisando usuários

```php
// Create a VO with search criteria
$user = new Users();
$user->setEmail('user@example.com');

// Search using DAO
$results = UsersDAO::search($user);

// Process results
if (count($results) > 0) {
    $foundUser = $results[0];
    echo "User ID: " . $foundUser->getUserId();
    echo "Username: " . $foundUser->getUsername();
}
```
### Criando um registro

```php
// Create new VO
$problem = new Problems();
$problem->setTitle('My Problem');
$problem->setAlias('my-problem');
$problem->setAuthorId($userId);

// Save using DAO
ProblemsDAO::save($problem);
```
### Obtendo por chave primária

```php
// Get user by ID
$user = UsersDAO::getByPK($userId);
if ($user !== null) {
    echo $user->getUsername();
}
```
## Princípios Chave

### Sem SQL direto nos controladores
Os controladores nunca escrevem SQL diretamente. Eles usam DAOs:

```php
// ✅ Good: Using DAO
$runs = RunsDAO::searchByUserId($userId);

// ❌ Bad: Direct SQL
$runs = $conn->query("SELECT * FROM Runs WHERE user_id = ...");
```
### Evite consultas O(n)
Crie consultas manuais para viagens únicas de ida e volta:

```php
// ❌ Bad: Multiple queries
foreach ($users as $user) {
    $runs = RunsDAO::searchByUserId($user->userId);
}

// ✅ Good: Single query
$userIds = array_map(fn($u) => $u->userId, $users);
$runs = RunsDAO::searchByUserIds($userIds);
```
## Geração automática

As classes VO e DAO são geradas automaticamente a partir do esquema do banco de dados:

1. Modifique o esquema do banco de dados (adicione migração)
2. Execute `./stuff/update-dao.sh`
3. As classes VO e DAO são regeneradas

## Notificações de usuário (tabela `Notifications`)

A UI carrega notificações pendentes da tabela **`Notifications`**. A coluna **`contents`** é JSON que define o render em [`Notification.vue`](https://github.com/omegaup/omegaup/blob/main/frontend/www/js/omegaup/components/notification/Notification.vue).

Inclua pelo menos `type`; os demais campos são **payload** conforme o tipo. Tipos comuns: `badge` (campo `badge`), `demotion` (`status`, `message`), `general_notification` (`message`, `url` opcional). Para i18n use um objeto `body` com `localizationString`, `localizationParams`, `url`, `iconUrl`.

Exemplo: `{ "type": "badge", "badge": "500score" }`. Referência no servidor: [`stuff/cron/assign_badges.py`](https://github.com/omegaup/omegaup/blob/main/stuff/cron/assign_badges.py).

!!! dica "Dúvidas"
    Pergunte no [Discord](https://discord.gg/gMEMX7Mrwe).

## Documentação Relacionada

- **[Arquitetura de back-end](../architecture/backend.md)** - Estrutura de back-end
- **[Esquema de banco de dados](../architecture/database-schema.md)** - Visão geral do esquema
- **[Diretrizes de codificação](coding-guidelines.md)** - Diretrizes de PHP
