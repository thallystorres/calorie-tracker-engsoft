from django.contrib.auth.models import User
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

from langgraph.prebuilt import create_react_agent

from apps.foods.models import Food


@tool
def buscar_alimentos_no_banco(termo_pesquisa: str, limite: int = 5) -> str:
  """
  Use esta ferramenta SEMPRE que precisar de sugerir um alimento.
  Passe um termo_pesquisa (ex: 'frango', 'arroz', 'leite').
  Retorna uma lista de alimentos disponíveis no sistema com as suas calorias.
  """
  alimentos = Food.objects.filter(name__icontains=termo_pesquisa)[:limite]

  if not alimentos.exists():
    return f"Nenhum alimento encontrado com o termo '{termo_pesquisa}'. Tente outro sinônimo."

  resultados = []
  for a in alimentos:
    resultados.append(f"- {a.name}: {a.kcal_per_100g} kcal/100g")

  return "\n".join(resultados)


class DietAssistantService:
  def __init__(self):
    self.llm = ChatGoogleGenerativeAI(
      model="gemini-3.1-flash-lite-preview",
      temperature=0.7,
    )
    self.tools = [buscar_alimentos_no_banco]

  def generate_diet_suggestion(self, user: User, user_message: str = "") -> str:
    try:
      perfil = user.nutritional_profile
    except Exception:
      return "Erro: O seu perfil nutricional ainda não foi configurado."

    calorias = perfil.daily_calorie_target
    objetivo = perfil.goal
    idade = perfil.age
    peso = perfil.weight_kg
    altura = perfil.height_cm
    sexo = perfil.sex
    atividade = perfil.activity_level

    restricoes_lista = perfil.dietary_restrictions or []
    restricoes = ", ".join(restricoes_lista) if restricoes_lista else "Nenhuma"

    system_prompt = f"""Você é o assistende de nutricionista do aplicativo CalorAI. Você é conhecido por ser empático, criativo e dar excelentes dicas de culinária saudável.
            Sua missão é criar uma dieta com precisão matemática usando o nosso banco de dados, mas apresentá-la de forma humana, apetitosa e instrutiva.

            DADOS DO UTILIZADOR:
            - Meta Calórica: {calorias} kcal ({objetivo})
            - Restrições / Alergias: {restricoes}
            - Idade: {idade}
            - Peso: {peso}
            - Altura: {altura}
            - Sexo: {sexo}
            - Nível de atividade: {atividade}


            REGRAS DE BUSCA (RAG):
            1. Você DEVE usar a ferramenta 'buscar_alimentos_no_banco'.
            2. Se você usar alimentos que não está na nossa base de dados, realce que as informações acerca das kcal podem divergir um pouco.
            3. A quantidade de calorias pode passar um pouco pra cima ou pra baixo, dependendo do objetivo ({objetivo})
            usuário.
            4. Seja direto, não embeleze demais as respostas, seja prático.

            REGRAS DE LIMPEZA DE DADOS (CRÍTICO):
            3. Oculte marcas e nomes comerciais bizarros do banco de dados na resposta final!
            """


    agent_executor = create_react_agent(
      self.llm,
      self.tools,
      prompt=system_prompt
    )

    if not user_message or not user_message.strip():
      user_message = "Por favor, monte uma sugestão de dieta para hoje com os alimentos do banco."

    try:
      response = agent_executor.invoke({"messages": [("user", user_message)]})

      resposta_final = response["messages"][-1].content

      if isinstance(resposta_final, list):
        pedacos_de_texto = []
        for bloco in resposta_final:
          if isinstance(bloco, dict) and "text" in bloco:
            pedacos_de_texto.append(bloco["text"])
          else:
            pedacos_de_texto.append(str(bloco))
        return "".join(pedacos_de_texto)

      return str(resposta_final)

    except Exception as e:
      print(f"Erro detalhado na execução do Agente LangGraph: {e}")
      return "Desculpe, tive um problema ao tentar aceder ao banco de dados de alimentos."
