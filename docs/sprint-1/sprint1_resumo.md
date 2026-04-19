# Resumo da Sprint 1

Período considerado: 20/03 a 09/04 (fundação do projeto).

## Objetivo da sprint

Entregar uma base funcional para os casos de uso iniciais:

- UC01: cadastro e gestão básica de conta.
- UC02: configuração de perfil nutricional com cálculo automático.
- UC03: registro manual de refeição com catálogo de alimentos.

## Entregas concluídas

### UC01 - Contas de usuário (accounts)

- API de contas implementada com endpoints de:
  - registro;
  - login e logout;
  - consulta e atualização de dados da conta;
  - desativação de conta (soft delete);
  - ativação por token assinado;
  - solicitação e confirmação de redefinição de senha.
- Regras de validação aplicadas:
  - username e e-mail únicos;
  - política de senha forte (maiúscula, minúscula, número, especial e tamanho mínimo);
  - normalização de e-mail.
- Fluxo de ativação e reset por e-mail implementado com serviços dedicados.
- Telas de autenticação e conta implementadas com Django Templates + HTMX:
  - cadastro;
  - login;
  - verificação de e-mail;
  - perfil do usuário;
  - reset de senha (solicitação, confirmação e sucesso).

### UC02 - Perfil nutricional (profiles)

- Modelo `NutritionalProfile` implementado (1:1 com usuário).
- Modelo `FoodRestriction` implementado (restrições alimentares vinculadas ao perfil).
- Serviço de perfil implementado para:
  - cálculo de TMB/BMR;
  - cálculo de meta calórica diária por nível de atividade e objetivo;
  - recálculo automático em atualizações.
- API de perfil implementada com:
  - criação de perfil;
  - atualização parcial de perfil;
  - criação e remoção de restrições alimentares.
- Tela de perfil nutricional implementada para preenchimento e atualização dos dados.

### UC03 - Registro manual de refeição (foods + tracker)

- Catálogo de alimentos implementado com:
  - modelo `Food`;
  - criação manual de alimento;
  - listagem global paginada;
  - busca por nome;
  - endpoint de detalhe por ID.
- Validações nutricionais implementadas:
  - não permitir valores negativos;
  - cálculo automático de kcal/100g quando esse campo não é enviado.
- Registro de consumo implementado em duas frentes:
  - endpoint de log em `foods` (`MealLog`);
  - endpoint de refeições no `tracker` (`Meal` e `MealItem`).
- Tela de diário alimentar implementada com:
  - formulário para registrar refeição com múltiplos itens;
  - histórico de refeições do usuário autenticado.
- Tela de cadastro de alimentos implementada para alimentar o catálogo manual.

## Fundação técnica e infraestrutura

- Estrutura Django organizada por apps (`accounts`, `profiles`, `foods`, `tracker`).
- Padrão de camadas adotado em boa parte dos módulos:
  - view/controller;
  - service;
  - repository;
  - serializer.
- Rotas UI e API centralizadas no roteador principal do projeto.
- Ambiente containerizado configurado com:
  - Dockerfile com estágios dev/prod;
  - docker-compose para web, banco PostgreSQL, Redis e worker Celery.
- Configurações separadas por ambiente (`base`, `dev`, `prod`).
- Dependências principais já integradas:
  - Django e DRF;
  - PostgreSQL;
  - Redis;
  - Celery;
  - ferramentas de qualidade (Ruff, Pyright, Pytest).

## Status geral da sprint 1

- A base funcional prevista para UC01, UC02 e UC03 está implementada no repositório, com APIs e telas principais.

## (i) Casos de uso planejados: finalizados e pendentes

| Caso de uso                                  | Status atual | Observação                                                                                      |
| -------------------------------------------- | ------------ | ----------------------------------------------------------------------------------------------- |
| UC01 - Cadastro de usuário                   | Finalizado   | Cadastro, login, ativação, edição de conta e reset de senha implementados.                      |
| UC02 - Perfil nutricional e cálculo          | Finalizado   | Perfil com cálculo de BMR/meta diária e gestão de restrições implementados.                     |
| UC03 - Registro manual de refeição           | Finalizado   | Catálogo de alimentos + registro de refeição já em funcionamento.                               |
| UC04 - Dashboard diário                      | Parcial      | Existe diário alimentar/histórico básico, mas falta dashboard consolidado de meta e macros.     |
| UC05 - Histórico com filtros semanal/mensal  | Parcial      | Histórico básico existe, porém sem filtros completos por período e visão analítica.             |
| UC06 - Notificações e artigos por e-mail     | Pendente     | Celery está configurado, mas fluxo de notificações da regra de negócio ainda não foi concluído. |
| UC07 - Sugestão inteligente de refeições     | Pendente     | Funcionalidade de IA ainda não implementada no fluxo de produto.                                |
| UC08 - Lista de compras automática           | Pendente     | Geração automática de lista de compras ainda não implementada.                                  |
| UC09 - Plano alimentar semanal personalizado | Pendente     | Geração de plano semanal com contexto/histórico ainda não implementada.                         |

## Próximas sprints (o que é esperado)

### Sprint 2 (10/04 a 23/04) - Maior interação com o usuário

Entregas esperadas:

- Fechar UC04 com dashboard diário (consumo vs meta, totais de macros e acompanhamento diário).
- Fechar UC05 com histórico filtrável (semanal/mensal) e melhor visualização dos dados.
- Implementar UC06 com notificações por e-mail (reativação de uso, alertas de consumo e conteúdos nutricionais), usando Celery + Redis.
- Consolidar o domínio de tracking para evitar duplicidade entre fluxos de refeição e fortalecer testes automatizados.

### Sprint 3 (24/04 a 12/05) - Implementação de IA

Entregas esperadas:

- Implementar UC07 com sugestão inteligente de refeições com base no histórico do usuário.
- Implementar UC08 com geração automática de lista de compras da dieta recomendada.
- Implementar UC09 com plano alimentar semanal personalizado por objetivo, contexto e histórico.
- Evoluir exportações e relatórios (por exemplo, `.md`, `.xlsx`, `.pdf`) de forma incremental.

## (ii) Diagrama de classes simplificado (até o momento)

[Caloria-1.png]

## (iii) Vídeo online da execução atual (obrigatório)

- Link do vídeo: https://drive.google.com/file/d/1KEyKkw4yD0IBH4whFQCdSCWJO32JQHkw/view?usp=sharing

## (iv) Slides e repositório para apresentação (obrigatório)

- Repositório oficial atualizado: https://github.com/thallystorres/calorie-tracker-engsoft
- Os slides devem conter explicitamente esse link do repositório.
