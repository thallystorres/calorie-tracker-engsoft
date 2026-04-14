## 1 - Descrição do Sistema

O **CalorIA** é um sistema de rastreamento nutricional inteligente voltado para
usuários que desejam monitorar, analisar e melhorar seus hábitos alimentares. O
sistema vai além do simples cadastro manual de refeições: ele cleta e cruza
dados nutricionais provenientes de bases públicas (como USDA FoodData Central),
aprende com o padrão alimentar do usuário ao longo do tempo e utiliza IA para
gerar sugestões personalizadas de refeições e planos alimentares semanais.

O sistema apoia a melhoria social na área de saúde alimentar, oferecendo suporte
tanto a usuários comuns (buscando melhorar seus hábitos alimentares) quanto a
pessoas com restrições alimentares e até mesmo profissionais da área
(nutricionistas, clínicas de reabilitação e nutrólogos).

Suas principais características incluem:

- **Cadastro e perfil nutricional** com cálculo automático de Taxa Metabólica
  Basal (TMB);
- **Registro e rastreamento** de refeições com base em uma base de dados
  alimentar pública;
- **Dashboard diário** com visualização de macronutrientes e calorias em tempo
  real;
- **Histórico alimentar** com filtros semanal e mensal;
- **Sugestão inteligente de refeições** baseada no histórico do usuário via IA;
- **Geração automática de lista de compras** com exportação de múltiplos
  formatos;
- **Planejamento alimentar semanal personalizado** com contexto de histórico e
  prompt do usuário.

---

## 2 - Modelos de Casos de Uso e Documentação Complementar

### 2.1 - Lista de atores e descrições

| Ator                                     | Descrição                                                                                                                                                                                                          |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Usuário**                              | Pessoa que utiliza o sistema para registrar e acompanhar sua alimentação. Interage diretamente com o cadastro, registro de refeições, dashboard e histórico.                                                       |
| **Nutricionista / Clínica**              | Profissional ou instituição de saúde que pode utilizar o sistema para criar aplicações especializadas voltadas para seus pacientes.                                                                                |
| **Sistema**                              | Módulo interno responsável por gerenciar o histórico alimentar do usuário e enviar informações ao módulo de IA para análise dos dados. Após isso recebe novamente as sugestões da IA e envia apresenta ao usuário. |
| **Serviço de E-mail (Gmail)**            | Serviço externo utilizado para o envio de notificações e artigos nutricionais ao usuário.                                                                                                                          |
| **Base de Dados Nutricional (USDA/OFF)** | Fonte de dados externa (USDA FoodData Central/ Open Foods Facts) utilizada para alimentar o banco de dados de alimentos e refeições do sistema.                                                                    |
| **Sistema de IA**                        | Módulo específico que faz a análise das informações enviadas pelo sistema base, normaliza e agrega às databases externas e inseridas pelo usuários para gerar sugestões de dietas.                                 |

### 2.2 - Lista de funcionalidades

- **F01** - Cadastro de usuários com dados físicos (peso, altura, idade) e credenciais de acesso
- **F02** - Configuração de perfil nutricional: cálculo automático de TMB, restrições alimentares, definição de perfil de atividade e objetivos
- **F03** - Registro manual de alimentos pelo usuário com cálculo automático de kcal
- **F04** - Registro de refeições com a base de dados manual do usuário em conjunto com a base de dados externa
- **F05** - Histórico alimentar com filtro de período (semanal/mensal) e visualização gráfica
- **F06** - Dashboard central diário para exposição de situação in real time, calculando exibindo comparação com as metas estabelecidas
- **F07** - Envio de e-mail para gerenciamento de perfil (verificação de e-mail e redefinição de senha)
- **F08** - Envio automático de notificações por e-mail em rotinas: alertas de tempo de registro, excesso calórico/macros, artigos nutricionais e mensagens motivacionais
- **F09** - Monitoramento de ingestão de substâncias prejudiciais (ex: alerta para celíacos, alérgicos, veganos) e notificação
- **F10** - Sugestão inteligente de refeições geradas por IA que analisa histórico do usuário
- **F11** - Sugestão inteligente de dieta semanal gerada pela IA que analisa histórico do usuário e input via chatbot
- **F12** - Geração automática de lista de compras semanal com quantidades em peso, baseada na dieta recomendada pela IA, com exportação em `.md`, `.xlsx` e `.pdf`.

### 2.3 Lista de regras de negócio

- **RN01** - O sistema só permite o usuário fazer o cadastro de suas refeições após a conclusão do cadastro de perfil nutricional
- **RN02** - O cálculo automático da TMB deve ser feito com base nas fórmulas já conhecidas como Harris-Benedict ou Mifflin-St Jeor, considerando as informações cadastradas pelo usuário como altura, peso, objetivos, nível de atividade e etc...
- **RN03** - O registro de refeição deve referenciar um alimento existente na base de dados nutricional. Alimentos não encontrados podem ser inseridos arbitrariamente pelo usuário com validação mínima de cálculo calórico
- **RN04** - O cálculo calórico devera seguir os valores padrões de kcal para cada macronutriente (1g de gordura possui 9 kcal por exemplo)
- **RN05** - O usuário pode fazer a inserção de produtos que vão contra suas restrições alimentares livremente, mas deverá ser notificado das suas ações com warnings na tela e via e-mail
- **RN06** - O usuário deverá ser notificado sempre que ultrapassar suas metas diárias de calorias e macronutrientes ou passar mais de três horas
- **RN07** - O usuário deve ter a liberdade de optar ou não por receber sugestões de análise feita por IA
- **RN08** - As análises sugestivas só podem ser feitas depois do primeiro registro de histórico após sete dias
- **RN09** - As listas devem conter não apenas os itens a serem comprados como também suas devidas medidas em grama ou litro
- **RN10** - O usuário que deve escolher qual o formato de arquivo da lista a ser enviado
