# Sistema de Contador de Calorias

## Ideia

> Um sistema que calcula, armazena e cataloga a alimentação do usuário

## *"Frameworkzação"*:
Um framework de Nutrition Tracking, fornecendo módulos prontos para registro alimentar, cálculo nutricional, recomendações e etc... Dessa forma, qualquer dev poderia criar apps de dieta, nutrição e voltados para pessoas com necessidades alimentares específicas.

## Diferenciais:

> Sugestão inteligente de refeições baseadas no histórico do usuário:
- O sistema aprende com o padrão alimentar do usuário e sugere refeições
- Analisa histórico alimentar
- Sugere refeições equilibradas
- Exemplo: Usuário que costuma comer mais carboidrato no início do dia

> Lista de compras com base na dieta recomendada:
- A aplicação sugere uma lista de compras baseada na dieta semanal
- Gera cálculos semanais do peso das refeições sugeridas
- Exporta a lista para diferentes tipos de arquivos (`.xlsx`, `.pdf`, `.md`)

## Casos de uso:

### Base do usuário (triviais)
- UC01 - Cadastro de usuário (peso, altura, idade, sexo, credenciais de acesso)
- UC02 - Configuração de perfil nutricional e cálculo (TMB + objetivo da dieta + restrição alimentar)
- UC03 - Registro manual de refeição (busca na base de dados)

### Tracking e acompanhamento
- UC04 - Dashboard diário (consumo calórico vs meta + registro de macros)
- UC05 - Histórico alimentar com visualização filtrada (semanal/mensal)
- UC06 - Notificações e artigos nutricionais por e-mail (Celery beat + SendGrid)

### IA e inovação (diferenciais)
- UC07 - Sugestão inteligente de refeições baseada no histórico do usuário
- UC08 - Gerar lista de compras automática
- UC09 - Geração de plano alimentar semanal personalizado com contexto de histórico e prompt

### Expansão do projeto (framework)
- UC10a - API pública do framework com endpoints documentados (Swagger)
- UC10b - Modularização de componentes da aplicação

## Framework na segunda fase: **Transformar um app que apenas conta calorias em uma aplicação com componentes reutilizáveis para qualquer sistema de nutrição e saúde alimentar, abrangendo apps de restritamente fitness, clínicas de reabilitação alimentar, nutricionistas e etc...**

## Tecnologias pretendidas:

### Backend:
- Python = 3.12.x
- Django = 5.0.x
- DRF = 3.15.x
- Postgres = 16
- Redis = 7
- Celery = 5.4

### IA:
- anthropic || google ai || openai
- [USDA FoodData Central](https://fdc.nal.usda.gov/download-datasets)
- Pandas = 3.0.x
- Sugestões??

### Infraestrutura:
- Docker
- Github

### Qualidade de código:
- Pytest
- Black
- Ruff
- uv

### Frontend:
- Django Templates
- HTMX
- Tailwind CSS

## Sprints

### 20/03 - 09/04 (Fundação)
- Setup do projeto
  - Criação do repositório remoto
  - Criação das imagens de containers e orquestração
  - Criação do `pyproject.toml`
  - Configuração básica do Django
- Levantamento de requisitos
  - Modelagem de banco de dados
  - Configurações do PostgreSQL
  - Documentação
- Funcionamentos básicos
  - Cadastro completo de usuário
  - Cálculo da TMB
  - Registro de refeição

- [x] UC01 - Cadastro de usuário (peso, altura, idade, sexo, credenciais de acesso)
- [x] UC02 - Configuração de perfil nutricional e cálculo (TMB + objetivo da dieta + restrição alimentar)
- [x] UC03 - Registro manual de refeição (busca na base de dados)

> App funcional com tracker e cadastro completo entregue

### 10/04 - 23/04 (Maior interação com o usuário)
- Registro de histórico do usuário
  - Análise das metas
  - Filtragem semanal/mensal
- Visualização de todos os dados obtidos no UC05
  - Macros
  - Calorias
  - Contagem em tempo real
- Notificações
  - Em caso de muito tempo sem registro (+3h)
  - Em caso de numero excessivo de calorias/carboidratos/gordura
  - Artigos nutricionais
  - Motivação para continuar com a dieta

- [x] UC04 - Dashboard diário (consumo calórico vs meta + registro de macros)
- [x] UC05 - Histórico alimentar com visualização filtrada (semanal/mensal)
- [x] UC06 - Notificações e artigos nutricionais por e-mail (Celery beat + SendGrid)

> Desenvolvimento de interações com o usuário via frontend e notificação
> Registro de métricas e histórico

### 24/04 - 12/05 (Implementação da IA de análise)
- IA gerando refeições e dietas
  - Análise do histórico do usuário
  - Compreensão de contexto e prompt
  - Integração com a base de dados
  - Sugestão de refeição e dieta completa
- Geração de lista de compras automática
  - Quantidades em peso
  - Diferentes tipos de arquivos e relatórios (`.md`, `.xslx`, `.pdf`)
  - Integrar com a IA geradora de dietas

- [x] UC07 - Sugestão inteligente de refeições baseada no histórico do usuário
- [x] UC08 - Gerar lista de compras automática
- [x] UC09 - Geração de plano alimentar semanal personalizado com contexto de histórico e prompt

> Foco na automação e inteligência do sistema
