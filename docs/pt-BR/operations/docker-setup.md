---
title: Configuração do Docker
description: Configuração detalhada do Docker Compose para desenvolvimento local
icon: bootstrap/tools
---
#Configuração do Docker

omegaUp não é um programa - é um aplicativo da web PHP mais um punhado de serviços Go e mais
seus datastores, e a única maneira sensata de executar tudo isso em sua máquina é o Docker
Componha a pilha no [`docker-compose.yml`](https://github.com/omegaup/omegaup/blob/main/docker-compose.yml) do repositório.
Esta página explica o que essa pilha realmente inicia e por que, para que quando algo se comportar mal
você sabe qual contêiner examinar.

Se seu objetivo é *contribuir* — clonar, inicializar, fazer login, editar código — comece com
[Configuração de desenvolvimento](../getting-started/development-setup.md), que trilha o caminho feliz.
Esta página é o mapa abaixo dela.

## Os serviços

Levantar a pilha (`docker-compose up`) inicia esses contêineres, cada um fixado em um
imagem específica para que todos executem as mesmas versões:

| Serviço | Imagem | O que é |
| ------- | ----- | ---------- |
| `frontend` | `omegaup/dev-php` | O aplicativo web PHP 8.1 (php-fpm por trás do nginx) — o aplicativo [MVC](../architecture/mvc-pattern.md) que atende todas as páginas e os endpoints `/api/`. Este é o contêiner no qual você executa testes, webpack e ferramentas PHP. |
| `mysql` | `mysql:8.0.34` | O banco de dados. Exposto ao host na porta **13306** (não o padrão 3306, portanto não colidirá com um MySQL que você já executa). |
| `redis` | `redis` | Cache. |
| `rabbitmq` | `rabbitmq:3-management-alpine` | Fila de mensagens usada para trabalho assíncrono; a imagem `-management` também oferece seu console web. |
| `gitserver` | `omegaup/gitserver:v1.9.13` | O serviço Go que armazena cada problema como um repositório git. Consulte [Gitserver](../architecture/gitserver.md). |
| `grader` | `omegaup/backend` | O avaliador Go - recebe corridas, coloca-as na fila e despacha para os corredores. O frontend chega por HTTP em `OMEGAUP_GRADER_URL` (padrão `https://localhost:21680`). |
| `runner` | `omegaup/runner` | O runner Go – compila e executa envios dentro do minijail. |
| `broadcaster` | `omegaup/backend` | O serviço Go que envia atualizações de placar/veredicto para o navegador por meio de WebSockets. |
| `init-omegaupdata` | `alpine` | Um contêiner init de curta duração que propaga o volume de dados do problema compartilhado antes do início dos serviços de longa execução. |

O grader, o runner, o broadcaster e o gitserver são **binários pré-construídos** enviados como Docker
imagens - elas não são construídas a partir deste repositório, que não contém nenhuma fonte Go. Eles vêm
do separado [omegaup/quark](https://github.com/omegaup/quark) e
projetos [omegaup/gitserver](https://github.com/omegaup/gitserver); veja
[Infraestrutura](../architecture/infrastructure.md) sobre como as peças se encaixam
produção.

## Volumes

Alguns volumes nomeados persistem no estado durante as reinicializações para que você não propague tudo novamente todas as vezes:
`dbdata` (MySQL), `omegaupdata` (os dados do problema compartilhados no frontend, avaliador e gitserver
todos lidos), mais `rabbitmq` e `redis`. Se a pilha entrar em uma posição genuinamente presa
estado, remover esses volumes e semear novamente é o grande martelo - veja
[Solução de problemas](troubleshooting.md).

## Produção vs. desenvolvimento

`docker-compose.yml` é a pilha de desenvolvimento. A produção executa os mesmos serviços em
Kubernetes de [`docker-compose.k8s.yml`](https://github.com/omegaup/omegaup/blob/main/docker-compose.k8s.yml)
com as imagens `omegaup/php` e `omegaup/nginx` em vez do `dev-php` multifuncional
imagem. A topologia do serviço é a mesma; a embalagem e a escala são diferentes. Veja
[Implantação](deployment.md).
