# Proposta de Framework - SmartTracker-FW

## Recapitulando: Fase 1

Na Fase 1 do projeto, foi implementado uma aplicação Web para rastreio de refeições e acompanhamento de metas nutricionais. Nessa aplicação, foram implementadas as seguintes funcionalidades:

- **Autenticação:** Auteticação, alteração de dados de cadastro e envio de emails para troca de senha.
- **Criação e Gerenciamento de Perfil:** Perfil biométrico do Usuário, usado para calcular as metas do mesmo e guardar restrições alimentares
- **Armazenamento de Histórico:** Armazena o Histórico de Refeições do Usuário e permite consultas tanto pelos componentes internos da aplicação quanto pelo próprio Usuário (de forma resumida)
- **Sistema de Engajamento:** Notificações periódicas opt-in via email
- **Sugestão Preditiva de Refeições e Dietas** Analisa o Pedido do Usuário e tenta sugerir algo relevante com base no Histórico, adequando quantidades para condizer com a meta do mesmo.
- **Geração Automática de Listas de Compras** Gera uma lista de compras em PDF para uma Dieta ou Refeição em Específico
- **Criação de Planos Semanais** Plano Detalhado e Estruturado com duração de 1 semana gerado com feedback do Usuário.

## Abstraindo para um Framework

O Framework a ser gerado deve ser extraído das funcionalidades implementadas na aplicação da Fase 1, o domínio do Framework será centrado em:

### Pontos Fixos (Estáticos de uma Aplicação para Outra)

- **Autenticação e Autorização:** Lógica de Cadastro, Login e Alteração de Credenciais
- **Envio de Emails:** Sistema de Envio de Emails para Notificar o Usuário.
- **Perfil do Usuário:** Perfil com Informações Relevantes do Usuário
- **Armazenamento de Histórico:** Armazenar Ações Relevantes do Usuário
- **Sugestão Preditiva:** Geração de Sugestões Baseadas no Perfil, Metas e Histórico do Usuário por meio de LLM.

### Pontos Variáveis (A ser Extendido pela Aplicação Implementada)

- **Métricas a Serem Rastreadas:s** Métricas relevantes no Domínio da Aplicação Implementada.
- **Metas do Usuário:** Metas Concretas do Usuário, estabelecidas por meio de uma meta abstrata do Usuário + Análise de Perfil.
- **Tipo de Sugestão da IA:** Tipos de Conteúdos a serem Gerados pela LLM.

## Aplicações a Serem Implementadas (Instâncias do Framework)

### CalorIA (Já implementada na Fase 1 - A ser refatorada para Utilizar o Framework Criado)

Aplicação para acompanhamento nutricional.

- Rastreia o histórico de refeições do Usuário.
- Calcula a TMB do Usuário de acordo com o seu perfil biométrico (altura, peso, idade, sexo)
- Gera Metas Concretas baseadas no objetivo pessoal do usuário + a TMB
- Permite a geração de sugestões de Refeições e Dietas usando uma LLM que tem acesso à:
  - O Histórico do Usuário
  - Suas metas
  - A Situação atual do Usuário (Quantas calorias e macronutriente já foram consumidos hoje)
  - Um Prompt do Usuário Descrevendo o tipo de refeição/dieta que ele quer
  - Uma Ferramenta de busca semântica em um banco de Dados de Alimentos, com nomes e informações nutricionais de cada alimento.

### AcademIA

Aplicação para Acompanhamento Fitness.

-
### EstudaAI

Aplicação para Acompanhamento Acadêmico.

-

## Comaparativo entre instâncias

| Característica    | CalorIA           | AcademIA           | EstudaAI         |
| ----------------- | ----------------- | ------------------ | ---------------- |
| Entidade          | Refeição          | Exercício          | Sessão de Estudo |
| Métrica Principal | Calorias (Kcal)   | Volume (Kg\*rep)   | Tempo (minutos)  |
| Meta              | Superavit/Deficit | Progessão de Carga | Retenção/Foco    |
| Saída de IA       | Plano de Dieta    | Periodização       | Questionários    |
