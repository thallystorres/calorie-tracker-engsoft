<!-- Totalmente Gerado por IA, use como referência por sua própria conta e risco-->
# Documentação da API

Este documento lista exaustivamente todos os endpoints da API do Sistema Inteligente de Contador de Calorias. A API está organizada em quatro domínios principais: Accounts, Profiles, Foods e Tracker. Cada endpoint é descrito com seu método HTTP, URL, requisitos de autenticação, parâmetros de requisição, esquema do corpo da requisição, formato de resposta e possíveis códigos de erro.

## URL Base

Todos os endpoints da API são prefixados com `/api/`. A URL base depende do ambiente de implantação (por exemplo, `http://localhost:8000/api/` em desenvolvimento).

## Autenticação

A maioria dos endpoints requer autenticação por sessão (via sessão do Django). O cliente deve incluir o cookie de sessão obtido após o login. Exceções são explicitamente marcadas como "Sem autenticação necessária".

## Formato de Resposta

Respostas bem‑sucedidas normalmente retornam JSON com a seguinte estrutura:

```json
{
  "detail": "Mensagem legível para humanos",
  // campos de dados adicionais
}
```

Respostas de erro seguem o formato:

```json
{
  "detail": "Descrição do erro",
  // erros específicos por campo (opcional)
}
```

## Códigos de Status HTTP Comuns

- `200 OK`: Requisição bem‑sucedida.
- `201 Created`: Recurso criado com sucesso.
- `204 No Content`: Requisição bem‑sucedida, sem corpo retornado.
- `400 Bad Request`: Parâmetros ou corpo da requisição inválidos.
- `401 Unauthorized`: Autenticação necessária ou falhou.
- `403 Forbidden`: Usuário autenticado não possui permissões.
- `404 Not Found`: Recurso não encontrado.
- `500 Internal Server Error`: Erro interno do servidor.

---

## API de Accounts

### Registrar uma Nova Conta

**Endpoint:** `POST /api/accounts/register/`

**Autenticação:** Sem autenticação necessária (apenas usuários não autenticados).

**Descrição:** Cria uma nova conta de usuário. Um email de ativação é enviado para o endereço de email fornecido. A conta deve ser ativada antes de fazer login.

**Corpo da Requisição:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `username` | string | Sim | Nome de usuário único (case‑sensitive). |
| `email` | string | Sim | Endereço de email válido (será convertido para minúsculas). |
| `first_name` | string | Não | Primeiro nome do usuário. |
| `last_name` | string | Não | Sobrenome do usuário. |
| `password` | string | Sim | Senha (deve satisfazer o validador de senha forte). |
| `confirm_password` | string | Sim | Deve corresponder a `password`. |

**Exemplo de Requisição:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "StrongPass123!",
  "confirm_password": "StrongPass123!"
}
```

**Resposta:**

- `201 Created` – Conta criada com sucesso.

```json
{
  "detail": "Conta criada com sucesso. Verifique seu e-mail para ativar.",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

**Erros:**
- `400 Bad Request` – Erros de validação (username/email já em uso, senhas não coincidem, senha fraca).

### Login

**Endpoint:** `POST /api/accounts/login/`

**Autenticação:** Sem autenticação necessária.

**Descrição:** Autentica um usuário e estabelece uma sessão.

**Corpo da Requisição:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `username_or_email` | string | Sim | Nome de usuário ou endereço de email (case‑insensitive para email). |
| `password` | string | Sim | Senha do usuário. |

**Exemplo de Requisição:**
```json
{
  "username_or_email": "johndoe",
  "password": "StrongPass123!"
}
```

**Resposta:**

- `200 OK` – Login bem‑sucedido.

```json
{
  "detail": "Login realizado com sucesso."
}
```

**Erros:**
- `400 Bad Request` – Credenciais inválidas.

### Logout

**Endpoint:** `POST /api/accounts/logout/`

**Autenticação:** Necessária (apenas usuários autenticados).

**Descrição:** Encerra a sessão atual do usuário.

**Corpo da Requisição:** Nenhum.

**Resposta:**

- `200 OK` – Logout bem‑sucedido.

```json
{
  "detail": "Logout realizado com sucesso."
}
```

### Obter Perfil do Usuário Atual

**Endpoint:** `GET /api/accounts/me/`

**Autenticação:** Necessária.

**Descrição:** Recupera as informações do perfil do usuário autenticado.

**Resposta:**

- `200 OK`

```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Atualizar Perfil do Usuário Atual

**Endpoint:** `PATCH /api/accounts/me/`

**Autenticação:** Necessária.

**Descrição:** Atualiza os campos do perfil do usuário autenticado. Se o email for alterado, a conta é desativada e um email de ativação é enviado; a sessão é terminada.

**Corpo da Requisição:** Campos parciais permitidos.

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `email` | string | Não | Novo endereço de email (deve ser único). |
| `first_name` | string | Não | Novo primeiro nome. |
| `last_name` | string | Não | Novo sobrenome. |

**Exemplo de Requisição:**
```json
{
  "email": "newjohn@example.com",
  "first_name": "Johnathan"
}
```

**Resposta:**

- `200 OK` – Atualização bem‑sucedida.

```json
{
  "detail": "Conta atualizada com sucesso. Sua sessão foi encerrada. Verifique seu e-mail para reativar a conta.",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "newjohn@example.com",
    "first_name": "Johnathan",
    "last_name": "Doe"
  }
}
```

**Erros:**
- `400 Bad Request` – Erros de validação (email já em uso).

### Excluir Conta do Usuário Atual

**Endpoint:** `DELETE /api/accounts/me/`

**Autenticação:** Necessária.

**Descrição:** Exclui permanentemente a conta do usuário autenticado. Requer confirmação da senha.

**Corpo da Requisição:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `password` | string | Sim | Senha atual do usuário. |

**Exemplo de Requisição:**
```json
{
  "password": "StrongPass123!"
}
```

**Resposta:**

- `204 No Content` – Conta excluída com sucesso.

**Erros:**
- `400 Bad Request` – Senha incorreta.

### Ativar Conta

**Endpoint:** `GET /api/accounts/activate/`

**Autenticação:** Sem autenticação necessária (apenas usuários não autenticados).

**Descrição:** Ativa uma conta de usuário usando o token enviado por email.

**Parâmetros de Consulta:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `token` | string | Sim | Token de ativação (enviado no email de ativação). |

**Exemplo de Requisição:** `GET /api/accounts/activate/?token=abcdef123456`

**Resposta:**

- `200 OK` – Conta ativada.

```json
{
  "detail": "Conta ativada com sucesso."
}
```

**Erros:**
- `400 Bad Request` – Token inválido ou expirado.

### Solicitar Redefinição de Senha

**Endpoint:** `POST /api/accounts/password-reset/request/`

**Autenticação:** Sem autenticação necessária.

**Descrição:** Envia um email de redefinição de senha para o endereço de email fornecido (se cadastrado).

**Corpo da Requisição:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `email` | string | Sim | Endereço de email associado à conta. |

**Exemplo de Requisição:**
```json
{
  "email": "john@example.com"
}
```

**Resposta:**

- `200 OK` – Email enviado (ou não, para evitar vazamento de emails cadastrados).

```json
{
  "detail": "Se o e-mail informado estiver cadastrado, você receberá instruções para redefinir a senha."
}
```

### Confirmar Redefinição de Senha

**Endpoint:** `POST /api/accounts/password-reset/confirm/`

**Autenticação:** Sem autenticação necessária.

**Descrição:** Define uma nova senha usando o token recebido por email.

**Parâmetros de Consulta:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `token` | string | Sim | Token de redefinição de senha (enviado no email). |

**Corpo da Requisição:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `new_password` | string | Sim | Nova senha (deve satisfazer o validador de senha forte). |
| `confirm_password` | string | Sim | Deve corresponder a `new_password`. |

**Exemplo de Requisição:** `POST /api/accounts/password-reset/confirm/?token=abcdef123456`

```json
{
  "new_password": "NewStrongPass456!",
  "confirm_password": "NewStrongPass456!"
}
```

**Resposta:**

- `200 OK` – Senha atualizada.

```json
{
  "detail": "Senha definida com sucesso"
}
```

**Erros:**
- `400 Bad Request` – Token inválido, senhas não coincidem ou senha fraca.

---

## API de Profiles

### Criar Perfil Nutricional

**Endpoint:** `POST /api/profiles/`

**Autenticação:** Necessária.

**Descrição:** Cria um perfil nutricional para o usuário autenticado. Cada usuário pode ter apenas um perfil.

**Corpo da Requisição:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `weight_kg` | decimal | Sim | Peso em quilogramas (máximo 5 dígitos, 2 casas decimais). |
| `height_cm` | integer | Sim | Altura em centímetros. |
| `age` | integer | Sim | Idade em anos. |
| `sex` | string | Sim | `"M"` (Masculino) ou `"F"` (Feminino). |
| `activity_level` | string | Sim | Um de: `"SEDENTARIO"`, `"LEVE"`, `"MODERADA"`, `"ALTA"`, `"MUITO_ALTA"`. |
| `goal` | string | Sim | Um de: `"PERDA"`, `"MANUTENCAO"`, `"GANHO"`. |

**Exemplo de Requisição:**
```json
{
  "weight_kg": 70.5,
  "height_cm": 175,
  "age": 30,
  "sex": "M",
  "activity_level": "MODERADA",
  "goal": "MANUTENCAO"
}
```

**Resposta:**

- `201 Created` – Perfil criado.

```json
{
  "weight_kg": 70.5,
  "height_cm": 175,
  "age": 30,
  "sex": "M",
  "activity_level": "MODERADA",
  "goal": "MANUTENCAO",
  "bmr": 1667.25,
  "daily_calorie_target": 2500.88,
  "updated_at": "2026-04-11T11:29:11Z"
}
```

**Erros:**
- `400 Bad Request` – Erros de validação ou perfil já existe.

### Atualizar Perfil Nutricional

**Endpoint:** `PATCH /api/profiles/`

**Autenticação:** Necessária.

**Descrição:** Atualiza o perfil nutricional do usuário autenticado. Recalcula TMB e meta calórica diária com base nos campos atualizados.

**Corpo da Requisição:** Campos parciais permitidos (mesmos da criação).

**Exemplo de Requisição:**
```json
{
  "weight_kg": 72.0,
  "activity_level": "ALTA"
}
```

**Resposta:**

- `200 OK` – Perfil atualizado.

```json
{
  "weight_kg": 72.0,
  "height_cm": 175,
  "age": 30,
  "sex": "M",
  "activity_level": "ALTA",
  "goal": "MANUTENCAO",
  "bmr": 1700.50,
  "daily_calorie_target": 2800.75,
  "updated_at": "2026-04-11T11:30:00Z"
}
```

**Erros:**
- `404 Not Found` – Perfil nutricional não existe.

### Adicionar Restrição Alimentar

**Endpoint:** `POST /api/profiles/me/restrictions/`

**Autenticação:** Necessária.

**Descrição:** Adiciona uma restrição alimentar ao perfil nutricional do usuário.

**Corpo da Requisição:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `restriction_type` | string | Sim | Um de: `"CELIACO"`, `"INTOLERANTE_A_LACTOSE"`, `"DIABETICO"`, `"VEGANO"`, `"VEGETARIANO"`, `"OUTRO"`. |
| `description` | string | Condicional | Obrigatório quando `restriction_type` é `"OUTRO"`; caso contrário, ignorado. |

**Exemplo de Requisição:**
```json
{
  "restriction_type": "VEGANO",
  "description": ""
}
```

**Resposta:**

- `201 Created` – Restrição adicionada.

```json
{
  "restriction_type": "VEGANO",
  "description": ""
}
```

**Erros:**
- `400 Bad Request` – Descrição ausente para `"OUTRO"`, ou perfil nutricional não existe.
- `404 Not Found` – Perfil nutricional não encontrado.

### Remover Restrição Alimentar

**Endpoint:** `DELETE /api/profiles/me/restrictions/<id>/`

**Autenticação:** Necessária.

**Descrição:** Exclui uma restrição alimentar específica pertencente ao perfil nutricional do usuário.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `id` | integer | Sim | ID da restrição alimentar. |

**Resposta:**

- `204 No Content` – Restrição excluída.

**Erros:**
- `404 Not Found` – Restrição não encontrada ou não pertence ao usuário.

---

## API de Foods

### Listar Alimentos

**Endpoint:** `GET /api/foods/`

**Autenticação:** Necessária.

**Descrição:** Retorna uma lista paginada de alimentos. Pode ser filtrada por termo de busca.

**Parâmetros de Consulta:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `q` | string | Não | Termo de busca para filtrar alimentos por nome (case‑insensitive). |
| `page` | integer | Não | Número da página para paginação (padrão: 1). |

**Resposta:**

- `200 OK`

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/foods/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Apple",
      "kcal_per_100g": 52.0,
      "protein_per_100g": 0.3,
      "carbs_per_100g": 13.8,
      "fat_per_100g": 0.2,
      "fiber_per_100g": 2.4,
      "source": "manual"
    },
    // ...
  ]
}
```

### Criar Alimento

**Endpoint:** `POST /api/foods/`

**Autenticação:** Necessária.

**Descrição:** Adiciona um novo item alimentar ao banco de dados. Se `kcal_per_100g` for omitido, é calculado a partir de proteína, carboidratos e gordura (4‑4‑9 kcal/g).

**Corpo da Requisição:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `name` | string | Sim | Nome do alimento. |
| `kcal_per_100g` | decimal | Não | Quilocalorias por 100g (máximo 5 dígitos, 2 casas decimais). |
| `protein_per_100g` | decimal | Condicional | Obrigatório se `kcal_per_100g` for omitido. |
| `carbs_per_100g` | decimal | Condicional | Obrigatório se `kcal_per_100g` for omitido. |
| `fat_per_100g` | decimal | Condicional | Obrigatório se `kcal_per_100g` for omitido. |
| `fiber_per_100g` | decimal | Não | Fibra alimentar por 100g. |

**Exemplo de Requisição (kcal explícita):**
```json
{
  "name": "Banana",
  "kcal_per_100g": 89.0,
  "protein_per_100g": 1.1,
  "carbs_per_100g": 22.8,
  "fat_per_100g": 0.3,
  "fiber_per_100g": 2.6
}
```

**Exemplo de Requisição (kcal calculada):**
```json
{
  "name": "Banana",
  "protein_per_100g": 1.1,
  "carbs_per_100g": 22.8,
  "fat_per_100g": 0.3,
  "fiber_per_100g": 2.6
}
```

**Resposta:**

- `201 Created`

```json
{
  "id": 2,
  "name": "Banana",
  "kcal_per_100g": 89.0,
  "protein_per_100g": 1.1,
  "carbs_per_100g": 22.8,
  "fat_per_100g": 0.3,
  "fiber_per_100g": 2.6,
  "source": "manual"
}
```

**Erros:**
- `400 Bad Request` – Erros de validação (campos obrigatórios ausentes, valores inválidos).

### Obter Detalhes do Alimento

**Endpoint:** `GET /api/foods/<food_id>/`

**Autenticação:** Necessária.

**Descrição:** Recupera informações detalhadas para um alimento específico.

**Parâmetros de Caminho:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `food_id` | integer | Sim | ID do alimento. |

**Resposta:**

- `200 OK`

```json
{
  "id": 2,
  "name": "Banana",
  "kcal_per_100g": 89.0,
  "protein_per_100g": 1.1,
  "carbs_per_100g": 22.8,
  "fat_per_100g": 0.3,
  "fiber_per_100g": 2.6,
  "source": "manual"
}
```

**Erros:**
- `404 Not Found` – Alimento não existe.

---

## API de Tracker

### Criar uma Refeição com Múltiplos Itens

**Endpoint:** `POST /api/tracker/meals/`

**Autenticação:** Necessária.

**Descrição:** Cria uma refeição (café da manhã, almoço, jantar, lanche ou outro) consistindo de múltiplos itens alimentares. O total de calorias de cada item é calculado automaticamente.

**Corpo da Requisição:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `label` | string | Sim | Rótulo da refeição: `"cafe"`, `"almoco"`, `"jantar"`, `"lanche"`, `"outro"`. |
| `items` | array | Sim | Lista de itens da refeição (pelo menos um). |

**Objeto Item:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `food_id` | integer | Sim | ID do alimento. |
| `quantity_grams` | decimal | Sim | Quantidade em gramas (mínimo 0.1). |

**Exemplo de Requisição:**
```json
{
  "label": "almoco",
  "items": [
    {
      "food_id": 2,
      "quantity_grams": 200.0
    },
    {
      "food_id": 5,
      "quantity_grams": 100.0
    }
  ]
}
```

**Resposta:**

- `201 Created`

```json
{
  "detail": "Refeição registrada com sucesso.",
  "meal": {
    "id": 1,
    "label": "almoco",
    "eaten_at": "2026-04-11T11:40:00Z",
    "items": [
      {
        "id": 1,
        "food": 2,
        "food_name": "Banana",
        "quantity_grams": 200.0,
        "kcal_total": 178.0
      },
      {
        "id": 2,
        "food": 5,
        "food_name": "Chicken Breast",
        "quantity_grams": 100.0,
        "kcal_total": 165.0
      }
    ]
  },
  "warnings": []
}
```

**Erros:**
- `400 Bad Request` – Erros de validação (itens vazios, IDs de alimento inválidos, quantidades inválidas).

---

## API de AI Engine

### Sugerir Refeição

**Endpoint:** `POST /api/ai/suggest_meal/`

**Autenticação:** Necessária.

**Descrição:** Gera uma sugestão de refeição personalizada com base no perfil do usuário e um prompt opcional.

**Corpo da Requisição:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `user_prompt` | string | Não | Preferências ou ingredientes que o usuário deseja incluir. |

**Exemplo de Requisição:**
```json
{
  "user_prompt": "Quero algo com frango e batata doce"
}
```

**Resposta:**

- `200 OK`

```json
{
  "meal_name": "Frango Grelhado com Purê de Batata Doce",
  "ingredients": [
    { "name": "Peito de Frango", "quantity_grams": 150.0 },
    { "name": "Batata Doce", "quantity_grams": 200.0 }
  ],
  "estimated_calories": 450.0,
  "target_adjustments": {
    "applied": true,
    "description": "Meta ajustada para compensar o déficit de ontem."
  },
  "warning": "..."
}
```

---

## API de Assistant

### Chat com Assistente de Dieta

**Endpoint:** `POST /api/assistant/api/chat/`

**Autenticação:** Necessária.

**Descrição:** Conversa com a IA para obter sugestões de dietas, receitas ou esclarecer dúvidas.

**Corpo da Requisição:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `message` | string | Sim | Mensagem do usuário para a IA. |

**Resposta:**

- `200 OK`

```json
{
  "reply": "Aqui está uma sugestão de receita...",
  "type": "receita"
}
```

### Salvar Conteúdo Gerado por IA

**Endpoint:** `POST /api/assistant/api/save-content/`

**Autenticação:** Necessária.

**Descrição:** Salva uma dieta ou receita gerada pela IA no perfil do usuário.

**Corpo da Requisição:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `type` | string | Sim | `"dieta"` ou `"receita"`. |
| `content` | string | Sim | Conteúdo em Markdown a ser salvo. |
| `title` | string | Não | Título opcional. |

**Resposta:**

- `201 Created`

```json
{
  "status": "success",
  "message": "Salvo com sucesso!"
}
```

---

## Endpoints UI (Páginas Renderizadas no Servidor)

Estes endpoints retornam páginas HTML para a interface web. Eles não fazem parte da API REST, mas são listados aqui para completude.

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `GET /accounts/register/` | GET | Página de registro. |
| `GET /accounts/login/` | GET | Página de login. |
| `GET /accounts/verify‑email/<token>/` | GET | Página de verificação de email (ativa a conta). |
| `GET /accounts/me/` | GET | Página de perfil do usuário. |
| `GET /accounts/password‑reset/` | GET | Página de solicitação de redefinição de senha. |
| `GET /accounts/password‑reset/done/` | GET | Página de confirmação após solicitação de redefinição de senha. |
| `GET /accounts/password‑reset/confirm/<token>/` | GET | Página para definir nova senha. |
| `GET /accounts/password‑reset/success/` | GET | Página de sucesso após redefinição de senha. |
| `GET /profiles/nutritional‑profile/` | GET | Página de gerenciamento de perfil nutricional. |
| `GET /tracker/` | GET | Painel de rastreamento de refeições. |
| `GET /assistant/chat/` | GET | Página do chat do assistente de dieta. |
| `GET /assistant/salvos/` | GET | Página de itens (dietas/receitas) salvos. |
| `GET /assistant/lista-compras/` | GET | Página de geração de lista de compras. |

Todos os endpoints UI requerem autenticação por sessão (exceto registro, login, verify‑email e páginas de password‑reset). Eles são destinados à interação humana via navegador web.

---

## Notas

- **Paginação:** Endpoints de listagem (ex.: `GET /api/foods/`) usam o `PageNumberPagination` do Django REST Framework com tamanho de página padrão de 20.
- **Precisão Decimal:** Todos os campos decimais são representados como strings em JSON para preservar a precisão. O servidor retorna valores com duas casas decimais.
- **Fusos Horários:** Todos os timestamps estão em UTC e formatados de acordo com ISO 8601.
- **Idioma:** Mensagens de erro e textos de detalhe estão em português brasileiro (pt‑BR).
