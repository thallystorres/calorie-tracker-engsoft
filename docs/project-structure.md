# Documentação da Estrutura do Projeto

## Estrutura do Diretório Raiz

```
.
├── docker-compose.yml          # Configuração do Docker Compose para desenvolvimento
├── docker-compose-prod.yml     # Configuração do Docker Compose para produção
├── Dockerfile                  # Definição da imagem Docker
├── pyproject.toml             # Dependências e configuração do projeto Python
├── uv.lock                    # Arquivo de lock para resolução determinística de dependências
├── README.md                  # Descrição breve do projeto
├── src/                       # Código fonte do projeto Django
└── docs/                      # Arquivos de documentação
```

## Código Fonte (`src/`)

O diretório `src/` contém o projeto Django e as aplicações.

```
src/
├── core/                      # Configurações e configurações principais do projeto Django
│   ├── __init__.py
│   ├── settings/             # Configurações específicas por ambiente
│   │   ├── __init__.py
│   │   ├── base.py           # Configurações base (comuns entre ambientes)
│   │   ├── dev.py            # Configurações específicas de desenvolvimento
│   │   └── prod.py           # Configurações específicas de produção
│   ├── urls.py               # Roteamento principal de URLs (inclui rotas UI e API)
│   ├── wsgi.py               # Ponto de entrada da aplicação WSGI
│   ├── asgi.py               # Ponto de entrada da aplicação ASGI
│   └── celery.py             # Configuração do Celery (se usado)
├── apps/                      # Aplicações Django (componentes modulares)
│   ├── accounts/             # Autenticação de usuário e gerenciamento de contas
│   ├── ai_engine/            # Sugestões de refeições e listas de compras via LLM
│   ├── foods/                # Banco de dados de alimentos e registro de refeições
│   ├── profiles/             # Perfis nutricionais e restrições alimentares
│   └── tracker/              # Rastreamento de refeições com múltiplos itens
├── manage.py                  # Script de gerenciamento Django
└── __init__.py
```

## Aplicações

### 1. Accounts (`apps/accounts/`)
Gerencia autenticação de usuários, registro, login, logout, redefinição de senha e ativação de conta.
...
### 2. AI Engine (`apps/ai_engine/`)
Fornece inteligência artificial para sugestão de refeições e geração de listas de compras personalizadas.

```
ai_engine/
├── __init__.py
├── apps.py
├── dependencies.py            # Injeção de dependência para serviços e clientes de IA
├── exceptions.py              # Exceções personalizadas de IA
├── urls.py
├── views.py                   # Views para interagir com as sugestões de IA
├── clients/                   # Clientes para provedores de LLM (Gemini)
│   ├── __init__.py
│   ├── base.py
│   └── gemini.py
├── prompts/                   # Templates de prompt para a LLM
│   ├── shopping_list.txt
│   └── system.txt
└── services/                  # Lógica para processar sugestões e contexto
    ├── __init__.py
    ├── context_builder.py     # Constrói o contexto do usuário para a IA
    ├── meal_suggester.py      # Orquestra sugestões de refeições
    └── shopping_list.py       # Gera listas de compras baseadas na dieta
```

### 3. Profiles (`apps/profiles/`)

accounts/
├── __init__.py
├── apps.py                    # Configuração da aplicação Django
├── admin.py                   # Registro no admin Django
├── dependencies.py            # Fábricas de injeção de dependência
├── repositories.py            # Camada de acesso a dados (repositório User)
├── services.py                # Camada de lógica de negócio (UserService)
├── serializers.py             # Serializadores DRF para validação de request/response
├── validators.py              # Validadores personalizados de senha
├── views.py                   # Classes de view da API (camada Controller)
├── ui_views.py                # Funções de view UI (para páginas renderizadas no servidor)
├── urls.py                    # Roteamento de URLs da API
├── ui_urls.py                 # Roteamento de URLs da UI
├── tests.py                   # Testes unitários
└── migrations/                # Migrações do banco de dados (se houver)
```

### 3. Profiles (`apps/profiles/`)
Gerencia perfis nutricionais (peso, altura, idade, nível de atividade, objetivo) e restrições alimentares.

```
profiles/
├── __init__.py
├── apps.py
├── admin.py
├── dependencies.py
├── repositories.py
├── services.py                # ProfileService com cálculos de TMB e meta calórica
├── serializers.py
├── views.py                   # Views da API para perfil e restrições alimentares
├── ui_views.py                # Views UI para página de perfil nutricional
├── urls.py
├── ui_urls.py
├── tests.py
├── models.py                  # Modelos NutritionalProfile e FoodRestriction
└── migrations/
```

### 4. Foods (`apps/foods/`)
Gerencia o banco de dados de alimentos (informação nutricional por 100g).

```
foods/
├── __init__.py
├── apps.py
├── admin.py
├── dependencies.py
├── repositories.py
├── services.py                # FoodService para operações CRUD
├── serializers.py
├── views.py                   # Listagem/criação/detalhe de alimentos e registro de refeições
├── models.py                  # Model Food
├── urls.py
├── tests.py
└── migrations/
```

### 5. Tracker (`apps/tracker/`)
Fornece rastreamento avançado de refeições com múltiplos itens (modelos Meal e MealItem).

```
tracker/
├── __init__.py
├── apps.py
├── admin.py
├── dependencies.py
├── services.py                # TrackerService para criação de refeições
├── serializers.py
├── views.py                   # View da API para criação de refeições
├── ui_views.py                # View UI para página de rastreamento
├── models.py                  # Modelos Meal e MealItem
├── urls.py
├── ui_urls.py
└── migrations/
```

## Core (`core/`)

### Configurações
- `base.py`: Configurações comuns (banco de dados, aplicações instaladas, middleware, REST framework, email, segurança).
- `dev.py`: Sobrescritas específicas de desenvolvimento (DEBUG=True, banco de dados local, etc.).
- `prod.py`: Sobrescritas específicas de produção (DEBUG=False, headers de segurança, etc.).

### Roteamento de URLs
O `urls.py` principal mapeia dois conjuntos de rotas:
- **Rotas UI** (páginas renderizadas no servidor): `/accounts/`, `/tracker/`, `/profiles/`
- **Rotas API** (REST API): `/api/accounts/`, `/api/profiles/`, `/api/foods/`, `/api/tracker/`, `/api/ai/`

### WSGI/ASGI
Pontos de entrada padrão do Django para produção (WSGI) e servidores assíncronos (ASGI).

## Camadas da Arquitetura

### Camada Controller (Views)
- Localizada nos arquivos `views.py` em todas as aplicações.
- Processa requisições HTTP, valida entrada via serializadores, delega para serviços, retorna respostas HTTP.
- Usa classes `APIView` do Django REST Framework.

### Camada Service
- Localizada nos arquivos `services.py`.
- Orquestra operações de negócio, coordena componentes de lógica de negócio, gerencia limites de transação.
- Exemplos: `UserService`, `ProfileService`, `FoodService`, `TrackerService`.

### Camada Business Logic
- Localizada em `services.py` (implementações concretas) e `dependencies.py` (fábricas).
- Fornece capacidades específicas de domínio (geração de tokens, envio de email, cálculo de TMB).

### Camada de Persistência de Dados
- **Models**: Definidos em `models.py` (Django ORM).
- **Repositories**: Localizados em `repositories.py` (acesso abstrato a dados, ex.: `UserRepository`).
- **Migrations**: Geradas automaticamente pelo Django em diretórios `migrations/`.

### Injeção de Dependência
- Arquivos `dependencies.py` contêm funções fábrica decoradas com `@cache` que instanciam serviços.
- Garante baixo acoplamento e testabilidade.

## Arquivos de Configuração

### `pyproject.toml`
Define dependências Python, configurações de ferramentas (Ruff, Mypy, pytest) e metadados do projeto. Inclui `google-genai` para integração com LLM e `pydantic` para validação de dados. Usa `uv` para resolução rápida de dependências.

### `docker-compose.yml`
Stack de desenvolvimento: banco de dados PostgreSQL, aplicação Django e serviços opcionais (Redis, Celery). Inclui montagens de volume para hot‑reload.

### `docker-compose-prod.yml`
Stack de produção com configurações otimizadas, serviços separados para web e arquivos estáticos, e injeção de variáveis de ambiente.

### `Dockerfile`
Build multi‑estágio: imagem base com Python 3.12, instalação de dependências, coleta de arquivos estáticos e Gunicorn pronto para produção.

## Ferramentas de Desenvolvimento

- **Ruff**: Linting e formatação (configurado em `pyproject.toml`).
- **pyright**: Verificação estática de tipos.
- **pytest**: Framework de testes com plugin Django.
- **uv**: Instalador e resolvedor rápido de pacotes Python.

## Variáveis de Ambiente

Variáveis de ambiente chave (veja `.env‑example`):

- `SECRET_KEY`: Chave secreta do Django.
- `DEBUG`: Habilita/desabilita modo debug.
- `ALLOWED_HOSTS`: Hostnames separados por vírgula.
- `POSTGRES_*`: Detalhes de conexão PostgreSQL.
- `EMAIL_*`: Configuração SMTP para ativação de conta e redefinição de senha.
- `ACCOUNT_ACTIVATION_MAX_AGE_SECONDS`: Expiração do token para ativação de conta.
- `PASSWORD_RESET_MAX_AGE_SECONDS`: Expiração do token para redefinição de senha.

## Esquema do Banco de Dados

### Entidades Principais
1. **User** (built‑in do Django): `id`, `username`, `email`, `first_name`, `last_name`, `password`.
2. **NutritionalProfile**: Relação um‑para‑um com User, armazena peso, altura, idade, sexo, nível de atividade, objetivo, TMB calculado e meta calórica diária.
3. **FoodRestriction**: Muitos‑para‑um com NutritionalProfile, armazena tipo de restrição alimentar e descrição opcional.
4. **Food**: Itens alimentares com valores nutricionais por 100g (kcal, proteína, carboidratos, gordura, fibra) e fonte (USDA, manual, OFF).
5. **Meal** (app tracker): Rótulo da refeição (café da manhã, almoço, etc.) e timestamp.
6. **MealItem** (app tracker): Muitos‑para‑um com Meal, referencia Food, armazena quantidade e total de kcal calculado.
