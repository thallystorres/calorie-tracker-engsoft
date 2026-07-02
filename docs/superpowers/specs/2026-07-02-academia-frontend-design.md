# Design: Frontend da Academia

**Data:** 2026-07-02
**Contexto:** Projeto CalorIA — app Django com frontend HTMX + Tailwind + vanilla JS
**Escopo:** Criar interface web para consumir as APIs REST do app `academia`
**Padrão visual:** Idêntico ao frontend do app `tracker` (calorai)

---

## 1. Contexto

O app `academia` já possui APIs REST completas (CRUD de treinos, métricas de volume, metas, geração de rotina com IA, busca de exercícios), mas **não possui nenhuma interface web**. O app `tracker` já tem um frontend funcional com padrão visual consolidado. Este design replica esse padrão para a academia.

### APIs existentes do app academia
- `GET /api/academia/workouts/` — lista paginada de treinos
- `POST /api/academia/workouts/` — cria novo treino
- `GET /api/academia/metrics/volume/?muscle_group=X` — volume por grupo
- `GET /api/academia/metrics/volume/weekly/` — volume semanal de todos os grupos
- `GET /api/academia/goals/` — metas ativas
- `POST /api/academia/goals/recalculate/` — recalcula metas
- `POST /api/academia/ai/generate-routine/` — gera rotina com IA
- `GET /api/academia/exercises/?q=` — busca de exercícios (semântica ou texto)

---

## 2. Arquitetura

### 2.1. Novos arquivos
```
src/apps/academia/
├── ui_urls.py                              # rotas de UI
├── ui_views.py                             # views de UI
└── templates/
    └── academia/
        ├── academia.html                    # página principal
        └── partials/
            ├── volume_dashboard.html         # métricas de volume
            ├── workout_history.html           # histórico de treinos
            └── goals.html                     # metas de volume
```

### 2.2. Rotas de UI (ui_urls.py)
```python
app_name = "academia-ui"
```

| Rota | View | Nome | Método |
|------|------|------|--------|
| `/academia/` | `academia_page` | `academia` | GET |
| `/academia/dashboard/` | `volume_dashboard_partial` | `dashboard` | GET |
| `/academia/history/` | `workout_history_partial` | `history` | GET |
| `/academia/goals/` | `goals_partial` | `goals` | GET |

### 2.3. Integração com URLs globais
Adicionar em `src/core/urls.py`:
```python
path("academia/", include("apps.academia.ui_urls")),
```

### 2.4. Navbar
Adicionar link "Treinos" em `src/apps/accounts/templates/base.html`, entre "Registros" e "Cadastrar alimento", apontando para `{% url 'academia-ui:academia' %}`.

---

## 3. Design da Página Principal (`academia.html`)

Herda de `base.html`. Estrutura: `min-h-screen py-12 px-4`, `max-w-3xl mx-auto`.

### Seções (de cima para baixo)

#### 3.1. Título
- Texto: "Área de Treinos"
- Ícone/estilo: mesmo padrão do tracker (text-3xl font-bold text-slate-900)

#### 3.2. Métricas de Volume Semanal (HTMX partial)
- Container: `<div id="volume-panel">` com `hx-get="{% url 'academia-ui:dashboard' %}"` trigger `load, workoutsUpdated from:body`
- Loading state: card slate-50 com "Carregando métricas..."
- Renderiza `partials/volume_dashboard.html`

#### 3.3. Gerador de Rotina com IA (vanilla JS)
- Card gradiente **slate/indigo** (diferente do emerald do tracker) — `from-slate-800 to-indigo-950`
- Inputs:
  - `split_type`: select (full_body, upper_lower, push_pull_legs)
  - `days_per_week`: select (1 a 7)
- Botão "Gerar Rotina" com loading spinner
- Resultado: lista de dias da rotina, cada um com exercícios (nome, séries, reps)
- Usa `fetch()` POST para `/api/academia/ai/generate-routine/`

#### 3.4. Registro de Treino (vanilla JS)
- Formulário com `data-endpoint="{% url 'academia:workout-list-create' %}"`
- Campos:
  - Nome do treino (texto, obrigatório)
  - Duração em minutos (number, opcional)
- Séries dinâmicas (mesmo padrão dos itens de refeição no tracker):
  - Busca de exercício: input com dropdown de resultados de `/api/academia/exercises/?q=`
  - Reps (integer, >0)
  - Peso em kg (float, >=0)
  - Botão "Remover" (escondido se só houver uma série)
  - Botão "+ Adicionar série"
- Feedback inline (success/error) no topo do formulário
- Após sucesso, dispara `htmx.trigger(document.body, "workoutsUpdated")` para recarregar partials

#### 3.5. Histórico de Treinos (HTMX partial)
- Container: `<div id="history-panel">` com `hx-get="{% url 'academia-ui:history' %}"` trigger `load, workoutsUpdated from:body`
- Loading state: card slate-50 com "Carregando histórico..."
- Renderiza `partials/workout_history.html`
- Lista paginada de treinos
- Cada card mostra: nome, data/hora, duração, volume total, resumo das séries

#### 3.6. Metas de Volume Muscular (HTMX partial)
- Container: `<div id="goals-panel">` com `hx-get="{% url 'academia-ui:goals' %}"` trigger `load, workoutsUpdated from:body`
- Loading state: card slate-50 com "Carregando metas..."
- Renderiza `partials/goals.html`
- Cada meta: grupo muscular, valor atual, meta, unidade, barra de progresso, status
- Botão "Recalcular Metas" usa HTMX `hx-post="/api/academia/goals/recalculate/"` com `hx-target="#goals-panel"` e `hx-swap="innerHTML"`. A API retorna JSON; o handler `afterRequest` do HTMX (já configurado em `base.html`) mostra feedback de sucesso/erro. Após sucesso, um segundo trigger HTMX recarrega o partial goals.

---

## 4. Partials HTMX

### 4.1. `volume_dashboard.html`
- Se `profile_required` (se houver perfil fitness necessário no futuro): mensagem informativa
- Grid responsivo (1 col mobile, 2 cols tablet, 3 cols desktop)
- Cada card: grupo muscular em português, volume total formatado com `floatformat:0`, unidade "kg·rep"

### 4.2. `workout_history.html`
- Se não houver treinos: mensagem "Nenhum treino registrado."
- Lista de cards. Cada card:
  - Cabeçalho: nome do treino + data formatada + badge com duração
  - Corpo: lista de séries (exercício, reps × peso, volume individual)
  - Rodapé: volume total do treino

### 4.3. `goals.html`
- Se não houver metas: mensagem "Nenhuma meta ativa."
- Cada card:
  - Grupo muscular + badge de status (ativo/atingido)
  - Barra de progresso visual (div com width% = current/target * 100)
  - Valores: atual / alvo (unidade)
  - Período: início → fim
- Botão "Recalcular Metas" com `hx-post` + `hx-target="#goals-panel"` + `hx-swap="innerHTML"`

---

## 5. Fluxo de Dados

```
Usuário acessa /academia/
  → academia.html carrega
    → hx-trigger="load" em cada partial
      → dashboard: chama VolumeMetricsService.get_weekly_volume_breakdown()
      → history: chama WorkoutRepository.list_sessions_for_user() + paginação
      → goals: chama GoalsService.get_active_goals()

Usuário registra treino
  → JS fetch POST /api/academia/workouts/
  → Sucesso → htmx.trigger(document.body, "workoutsUpdated")
    → Todos os partials recarregam automaticamente

Usuário recalcula metas
  → HTMX POST /api/academia/goals/recalculate/
  → Partial goals recarrega
```

---

## 6. Padrões Visuais (copiar do tracker)

- **Background:** `bg-[#F8FAFC]`
- **Cards:** `bg-white rounded-[2rem] shadow-sm border border-slate-100 p-8`
- **Cards internos (stats):** `bg-slate-50 rounded-xl border border-slate-200 p-4`
- **Botões primários:** `bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl`
- **Botões secundários:** `bg-emerald-50 text-emerald-700 border border-emerald-200`
- **Inputs:** `bg-slate-50 border border-slate-200 rounded-xl focus:ring-emerald-500`
- **Tipografia:** text-slate-900 (títulos), text-slate-500 (labels), text-emerald-600 (valores positivos)
- **Gradiente IA:** `from-slate-800 to-indigo-950` (diferente do emerald do tracker)
- **Fonte:** Tailwind padrão (sem custom fonts)

---

## 7. Decisões Tomadas

1. **Página única empilhada (Abordagem A):** Mantém consistência com o tracker. Se escalar demais, migração para abas é trivial.
2. **HTMX para reads, JS para writes:** Dashboard/histórico/metas são leituras (HTMX é ideal). Registro de treino e geração de IA são ações complexas com estado local (JS é melhor).
3. **Evento `workoutsUpdated`:** Mesmo padrão do evento `mealsUpdated` do tracker. Garante sincronização entre partials após mutação.
4. **Gradiente indigo para IA:** Diferencia visualmente a academia da nutrição, mas mantém a mesma estrutura de card.
5. **Busca de exercícios com dropdown:** Mesmo padrão de busca de alimentos no tracker — input com `mousedown` no dropdown para evitar blur, debounce de 300ms.

---

## 8. Fora de Escopo

- Edição/exclusão de treinos existentes (APIs não existem ainda)
- Perfil fitness obrigatório (o tracker tem isso; academia ainda não — implementamos sem gate)
- Notificações push ou email para treinos
- Gráficos/charts de volume (apenas cards numéricos por enquanto)

---

## 9. Testes

- Testes manuais de integração: registrar treino via UI, verificar se partials recarregam, verificar busca de exercícios, verificar geração de rotina IA.
- Não adicionar testes automatizados de UI nesta iteração (o tracker também não tem).

---

## 10. Dependências

- `apps.academia` já está em `INSTALLED_APPS` e as APIs já funcionam
- `base.html` precisa de uma linha nova para o link de navegação
- `core.urls.py` precisa incluir `apps.academia.ui_urls`

---

## 11. Implementação Futura

Se a página crescer muito, a migração para a **Abordagem B (navegação por abas)** é trivial: basta mover cada seção para sua própria rota e adicionar um menu de navegação HTMX no topo da página.
