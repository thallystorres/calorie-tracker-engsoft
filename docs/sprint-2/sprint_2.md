# Sprint 2 — CalorIA

**Período:** 10/04 a 23/04
**Objetivo:** Evoluir a interação do usuário com o sistema, consolidar a base de dados nutricional e introduzir inteligência preditiva para recomendações e automações.

---

# 1. Objetivo da Sprint

- Unificar o modelo de dados alimentar
- Integrar fontes externas de alimentos
- Implementar recomendações via IA
- Melhorar experiência do usuário no dashboard
- Habilitar geração automatizada de lista de compras

---

# 2. User Stories

## US07 — Sugestão Inteligente de Refeição

**Como** usuário
**Quero** receber sugestões de refeições com base no meu histórico alimentar
**Para** manter minha dieta dentro da meta calórica

**Critérios de Aceitação:**

- Considera histórico dos últimos 7 dias
- Sugestão inclui estimativa de calorias e macronutrientes
- Respeita restrições alimentares do usuário
- Tempo de resposta < 3 segundos

---

## US08 — Geração de Lista de Compras

**Como** usuário
**Quero** gerar uma lista de compras baseada nas sugestões de refeições
**Para** facilitar o planejamento alimentar

**Critérios de Aceitação:**

- Lista contém alimentos existentes no banco (`Food.name`)
- Quantidades são definidas em gramas (`quantity_grams`)
- Exportação disponível em Markdown e PDF
- Usuário pode receber a lista por e-mail

---

## US09 — Feedback de Restrições Alimentares

**Como** usuário
**Quero** ser alertado ao selecionar alimentos incompatíveis com minhas restrições
**Para** evitar consumo indevido

**Critérios de Aceitação:**

- Alertas visuais exibidos no dashboard
- Validação ocorre em tempo real
- Integração com dados de alérgenos das bases externas

---

## US10 — Dashboard Dinâmico

**Como** usuário
**Quero** visualizar meu progresso calórico em tempo real
**Para** acompanhar minha dieta

**Critérios de Aceitação:**

- Exibe calorias consumidas vs meta diária
- Atualização sem reload (HTMX)
- Feedback imediato ao adicionar alimentos

---

# 3. Dívidas Técnicas (Prioridade Alta)

## DT01 — Remoção de Modelo Duplicado (`MealLog`)

**Descrição:**
Eliminar duplicidade entre `MealLog` e `Meal/MealItem`

**Ações:**

- Remover modelo `MealLog` (apps/foods)
- Remover serializers e views associadas
- Migrar dados existentes (se necessário)

**Impacto:** Alto
**Risco:** Inconsistência de dados

---

## DT02 — Padronização de Alérgenos

**Descrição:**
Unificar tratamento de alérgenos entre fontes externas e regras internas

**Ações:**

- Ajustar `TrackerService`
- Mapear estrutura USDA/OFF → modelo interno

**Impacto:** Alto
**Risco:** Regras de negócio inconsistentes

---

# 4. Integração de Dados Externos

## T01 — Importação USDA

- Criar comando:

  ```bash
  python manage.py import_usda
  ```

- Popular tabela `Food`

---

## T02 — Integração Open Food Facts

- Consulta em tempo real para alimentos não encontrados
- Cache automático no banco local

---

## T03 — Normalização Nutricional

Garantir mapeamento consistente:

- Calorias (kcal)
- Proteínas
- Carboidratos
- Gorduras
- Fibras (por 100g)

---

# 5. Módulo de Inteligência Artificial

## Estrutura

```
apps/
  ai_engine/
    services/
    prompts/
    clients/
```

---

## T04 — Integração com LLM

- Configuração via variáveis de ambiente
- Suporte para OpenAI ou Gemini

---

## T05 — Contrato de IA

### Input

```json
{
  "calorias_restantes": int,
  "macros_consumidos": {
    "carb": float,
    "protein": float,
    "fat": float
  },
  "restricoes": ["gluten", "lactose"]
}
```

### Output esperado

```json
{
  "meal_name": "string",
  "ingredients": [
    {
      "name": "string",
      "quantity_grams": float
    }
  ],
  "estimated_calories": float
}
```

---

## T06 — Prompt Base

```
Com base no consumo alimentar do usuário nos últimos 7 dias,
sugira uma refeição que:

- Respeite as restrições alimentares
- Mantenha o usuário dentro da meta calórica
- Seja composta por alimentos comuns

Retorne ingredientes com quantidades em gramas.
```

---

# 6. UX/UI & Frontend

## T07 — Dashboard com HTMX

- Atualização parcial sem reload
- Integração com endpoints DRF

---

## T08 — Feedback Visual de Restrições

- Badges de alerta
- Destaque de alimentos incompatíveis

---

# 7. Dependências

- US07 depende de:
  - T03 (normalização nutricional)
  - T02 (Open Food Facts)

- US08 depende de:
  - US07 (sugestões da IA)

- US09 depende de:
  - DT02 (padronização de alérgenos)

---

# 8. Planejamento da Sprint

| ID   | Tarefa                     | Tipo    | Responsável | Prioridade |
| ---- | -------------------------- | ------- | ----------- | ---------- |
| DT01 | Remover MealLog            | Técnica | Backend     | Alta       |
| DT02 | Padronizar alérgenos       | Técnica | Backend     | Alta       |
| T01  | Importação USDA            | Dados   | Backend     | Alta       |
| T02  | Integração Open Food Facts | Dados   | Backend     | Alta       |
| T04  | Setup LLM                  | IA      | Backend     | Alta       |
| US07 | Sugestão de refeições      | Feature | IA          | Alta       |
| US08 | Lista de compras           | Feature | Backend     | Média      |
| US09 | Feedback de restrições     | UX      | Frontend    | Média      |
| US10 | Dashboard HTMX             | UX      | Frontend    | Média      |

---

# 9. Métricas de Sucesso

- ≥ 80% das sugestões da IA utilizáveis sem edição
- Tempo de resposta da IA < 3s
- Dashboard sem reload funcionando corretamente
- Alertas de restrição acionados corretamente
- Lista de compras exportável e enviada por e-mail

---

# 10. Definition of Done (DoD)

- Dashboard exibe calorias consumidas vs meta diária
- Atualização dinâmica via HTMX funcional
- Usuário recebe sugestões de refeições em tempo real
- Sistema alerta ingestão de alergênicos
- Lista de compras pode ser exportada (MD/PDF)
- Lista pode ser enviada por e-mail

---

# 11. Arquitetura da Sprint

```
apps/
  accounts/    → autenticação
  ai_engine/   → integração com IA
  foods/       → base nutricional (USDA/OFF)
  profiles/    → registro e cálculo de métricas personalizadas do usuário
  tracker/     → consumo alimentar (core)
```

---

# 12. Regra de Negócio Crítica

**RN09:**
As listas de compras geradas pela IA devem obrigatoriamente utilizar alimentos existentes no banco (`Food.name`) para garantir rastreabilidade.
