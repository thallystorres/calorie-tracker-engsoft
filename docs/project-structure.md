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

```
src/
├── core/                      # Configurações e setup principal do Django
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py
├── apps/
│   ├── accounts/              # Autenticação e gerenciamento de contas
│   ├── ai_engine/             # Sugestões de IA e listas de compras (unificado do antigo assistant)
│   ├── foods/                 # Banco de dados de alimentos
│   ├── profiles/              # Perfis nutricionais e restrições
│   └── tracker/               # Rastreamento de refeições
├── manage.py
└── __init__.py
```

## Aplicações

### 1. Accounts (`apps/accounts/`)
Autenticação de usuários, registro, login, logout, redefinição de senha e ativação de conta.

```
accounts/
├── __init__.py
├── admin.py
├── apps.py
├── dependencies.py            # Fábricas DI (get_user_repository, get_user_service)
├── repositories.py            # UserRepository (acesso a dados)
├── serializers.py             # DRF serializers (AccountRegister, Account, Login, etc.)
├── services.py                # UserService, ActivationTokenService, email services
├── validators.py              # Validadores de senha
├── views.py                   # API views (register, me, login, logout, activate, password reset)
├── ui_views.py                # UI views (páginas renderizadas no servidor)
├── urls.py                    # Rotas da API
├── ui_urls.py                 # Rotas da UI
├── tests.py
└── templates/
    ├── base.html
    └── accounts/
        ├── login.html
        ├── register.html
        ├── profile.html
        ├── verify_email.html
        ├── password_reset_request.html
        ├── password_reset_request_done.html
        ├── password_reset_confirm.html
        └── password_reset_success.html
```

### 2. AI Engine (`apps/ai_engine/`)
IA para sugestão de refeições, chat dietético, edição de conteúdo e geração de listas de compras. Antigo app `assistant` unificado aqui.

```
ai_engine/
├── __init__.py
├── admin.py
├── apps.py
├── dependencies.py            # Fábricas DI (GeminiLLMClient, serviços de IA)
├── exceptions.py              # AIEngineError, ProfileRequiredError, InsufficientDataError
├── schemas.py                 # Schemas Pydantic (DietResponseSchema, MealSuggestionSchema)
├── services.py                # DietAssistantService, MealSuggesterService, ShoppingListService
├── views.py                   # API + UI views (suggest_meal, chat, save/edit/delete, shopping_list)
├── urls.py                    # Rotas da API
├── ui_urls.py                 # Rotas da UI
├── tests.py
├── clients/
│   ├── __init__.py
│   ├── base.py                # BaseLLMClient (abstract)
│   └── gemini.py              # GeminiLLMClient (Google Gemini)
├── prompts/
│   ├── diet_suggestion.txt
│   ├── edit_diet.txt
│   ├── meal_suggestion.txt
│   └── shopping_list.txt
├── utils/
│   ├── __init__.py
│   ├── ai_tools.py            # Funções tool calling (search_food, adjust_future_targets)
│   └── context_builder.py     # ContextBuilder (dados do usuário para prompts)
└── templates/
    └── ai_engine/
        ├── chat.html
        ├── saved_items.html
        └── shopping_list.html
```

### 3. Profiles (`apps/profiles/`)
Perfis nutricionais (peso, altura, idade, sexo, nível de atividade, objetivo), restrições alimentares e conteúdos salvos (SavedDiet/SavedRecipe).

```
profiles/
├── __init__.py
├── admin.py
├── apps.py
├── dependencies.py            # Fábricas DI (get_profile_repository)
├── models.py                  # NutritionalProfile, FoodRestriction, SavedDiet, SavedRecipe
├── repositories.py            # ProfileRepository (CRUD perfil + saved diets/recipes)
├── restrictions.py            # Funções utilitárias (extract_user_restriction_codes)
├── serializers.py
├── services.py                # ProfileService (cálculo TMB, upsert)
├── views.py                   # API views
├── ui_views.py                # UI views (página de perfil nutricional)
├── urls.py
├── ui_urls.py
├── tests.py
└── templates/
    └── profiles/
        └── nutritional_profile.html
```

### 4. Foods (`apps/foods/`)
Banco de dados de alimentos com informação nutricional por 100g.

```
foods/
├── __init__.py
├── admin.py
├── allergens.py               # Utilitários de alérgenos
├── apps.py
├── dependencies.py            # Fábricas DI (get_food_repository)
├── models.py                  # Food (kcal, proteína, carboidratos, gordura, fibra, fonte)
├── repositories.py            # FoodRepository (CRUD + busca)
├── serializers.py
├── services.py                # FoodService
├── views.py                   # API views (listagem, criação, detalhe)
├── ui_views.py                # UI views (página de novo alimento)
├── urls.py
├── ui_urls.py
├── tests.py
├── management/
│   └── commands/
│       └── import_foods.py    # Comando para importar alimentos
└── templates/
    └── foods/
        └── new_food.html
```

### 5. Tracker (`apps/tracker/`)
Rastreamento de refeições com múltiplos itens (Meal e MealItem).

```
tracker/
├── __init__.py
├── admin.py
├── apps.py
├── dependencies.py            # Fábricas DI (get_meal_repository)
├── models.py                  # Meal, MealItem
├── repositories.py            # TrackerRepository (CRUD refeições + consultas históricas)
├── serializers.py
├── services.py                # TrackerService (log_meal com validação de metas)
├── views.py                   # API views (criação de refeições)
├── ui_views.py                # UI views (página de rastreamento)
├── urls.py
├── ui_urls.py
└── templates/
    └── tracker/
        └── tracker.html
```

## Core (`core/`)

```
core/
├── __init__.py
├── settings/
│   ├── __init__.py
│   ├── base.py                # Configurações comuns (DB, apps, middleware, REST, email, segurança)
│   ├── dev.py                 # Desenvolvimento (DEBUG=True, DB local)
│   └── prod.py                # Produção (DEBUG=False, headers segurança)
├── urls.py                    # Roteamento principal (UI + API routes)
├── wsgi.py                    # Ponto de entrada WSGI
├── asgi.py                    # Ponto de entrada ASGI
└── celery.py                  # Configuração Celery
```

## Camadas da Arquitetura

### Controller (Views)
- `views.py` em cada app, classes `APIView` do DRF.
- Processa HTTP, valida entrada via serializers, delega a services, retorna Response.

### Service
- `services.py` em cada app.
- Orquestra lógica de negócio, coordena componentes.
- Ex: `UserService`, `ProfileService`, `FoodService`, `TrackerService`, `DietAssistantService`.

### Helpers / Utilitários
- `BaseLLMClient` + `GeminiLLMClient`: clientes LLM.
- `ContextBuilder`: monta contexto do usuário para prompts.
- `ai_tools.py`: funções tool calling para LLM (`search_food`, `adjust_future_targets`).
- `BaseSignedTokenService` / `BaseEmailService`: tokens e email.

### Persistência
- **Models**: `models.py` (Django ORM).
- **Repositories**: `repositories.py` (abstração de acesso a dados).
- **Migrations**: `migrations/`.

### Injeção de Dependência
- `dependencies.py` com funções fábrica `@cache`.
- Garante baixo acoplamento e testabilidade.

## Ferramentas de Desenvolvimento

- **Ruff**: Linting e formatação.
- **pyright**: Verificação estática de tipos.
- **pytest**: Framework de testes com plugin Django.
- **uv**: Instalador e resolvedor rápido de pacotes Python.

## Variáveis de Ambiente

- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `POSTGRES_*`: Conexão PostgreSQL
- `EMAIL_*`: Configuração SMTP
- `ACCOUNT_ACTIVATION_MAX_AGE_SECONDS`, `PASSWORD_RESET_MAX_AGE_SECONDS`
- `GEMINI_API_KEY`: Chave da API Gemini

## Esquema do Banco de Dados

### Entidades Principais
1. **User** (built-in Django): `id`, `username`, `email`, `first_name`, `last_name`, `password`.
2. **NutritionalProfile**: 1:1 com User, armazena peso, altura, idade, sexo, nível atividade, objetivo, TMB, meta calórica.
3. **FoodRestriction**: N:1 com NutritionalProfile, tipo de restrição + descrição.
4. **SavedDiet**: N:1 com User, título + conteúdo Markdown (dieta salva).
5. **SavedRecipe**: N:1 com User, título + conteúdo Markdown (receita salva).
6. **Food**: Itens alimentares com valores nutricionais por 100g (kcal, proteína, carboidratos, gordura, fibra) e fonte (USDA, manual, OFF).
7. **Meal** (tracker): Rótulo da refeição + timestamp.
8. **MealItem** (tracker): N:1 com Meal, referencia Food, armazena quantidade + kcal total.
