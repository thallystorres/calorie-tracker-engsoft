import json
import re
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

  def generate_diet_suggestion(self, user: User, user_message: str = "") -> dict:
    try:
      perfil = user.nutritional_profile
    except Exception:
      return {"texto": "Erro: O seu perfil nutricional ainda não foi configurado.", "tipo": "chat"}

    calorias = perfil.daily_calorie_target
    objetivo = perfil.goal
    idade = perfil.age
    peso = perfil.weight_kg
    altura = perfil.height_cm
    sexo = perfil.sex
    atividade = perfil.activity_level

    restricoes_lista = perfil.dietary_restrictions or []
    restricoes = ", ".join(restricoes_lista) if restricoes_lista else "Nenhuma"

    system_prompt = f"""Você é o assistente de nutricionista do aplicativo CalorAI. Você é conhecido por ser empático, criativo e dar excelentes dicas de culinária saudável.
        Sua missão é criar uma dieta com precisão matemática usando o nosso banco de dados, mas apresentá-la de forma humana, apetitosa e instrutiva.

        DADOS DO UTILIZADOR:
        - Meta Calórica: {calorias} kcal ({objetivo})
        - Restrições / Alergias: {restricoes}
        - Idade: {idade}
        - Peso: {peso}
        - Altura: {altura}
        - Sexo: {sexo}
        - Nível de atividade: {atividade}

        COMPORTAMENTO E INTENÇÃO (MUITO IMPORTANTE):
        1. Avalie a mensagem do utilizador. Responda de forma humana e conversacional. NÃO gere dietas ou receitas sem que ele peça!
        2. Seja direto e prático, sem embelezar demais o texto.

        REGRAS DE BUSCA (RAG):
        1. Você DEVE usar a ferramenta 'buscar_alimentos_no_banco'.
        2. Se você usar alimentos que não estão na nossa base de dados, realce que as informações acerca das kcal podem divergir um pouco.
        3. A quantidade de calorias pode passar um pouco pra cima ou pra baixo, dependendo do objetivo ({objetivo}) do usuário.
        4. Seja direto, não embeleze demais as respostas, seja prático.

        REGRAS DE LIMPEZA DE DADOS (CRÍTICO):
        5. Oculte marcas e nomes comerciais bizarros do banco de dados na resposta final!

        FORMATO DE SAÍDA OBRIGATÓRIO (JSON):
        Você NÃO deve responder com texto comum. A sua resposta final DEVE ser estritamente um objeto JSON válido, contendo exatamente duas chaves:
        1. "tipo": classifique o conteúdo como "dieta", "receita" ou "chat".
        2. "texto": A sua resposta redigida para o utilizador, formatada em Markdown (use \\n para quebras de linha).

        Exemplo do que devolver (apenas o JSON, sem aspas adicionais ou conversa):
        {{
            "tipo": "dieta",
            "texto": "Olá! Preparei o seu plano... \\n\\n| Refeição | Alimento |..."
        }}
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
        pedacos = [bloco.get("text", str(bloco)) if isinstance(bloco, dict) else str(bloco) for bloco in resposta_final]
        texto_bruto = "".join(pedacos)
      else:
        texto_bruto = str(resposta_final)

      # Limpa blocos de código markdown (```json ... ```) caso a IA adicione
      conteudo_limpo = re.sub(r'^```json\s*', '', texto_bruto, flags=re.MULTILINE | re.IGNORECASE)
      conteudo_limpo = re.sub(r'```\s*$', '', conteudo_limpo, flags=re.MULTILINE).strip()

      try:
        dados = json.loads(conteudo_limpo)
        tipo_resposta = dados.get("tipo", "chat").lower()
        texto_final = dados.get("texto", conteudo_limpo)
      except json.JSONDecodeError:
        tipo_resposta = "chat"
        texto_final = texto_bruto

      return {
        "texto": texto_final,
        "tipo": tipo_resposta
      }

    except Exception as e:
      print(f"Erro detalhado na execução do Agente LangGraph: {e}")
      return {"texto": "Desculpe, tive um problema ao tentar aceder ao banco de dados de alimentos.", "tipo": "chat"}

  def edit_content_with_ai(self, current_content: str, instruction: str) -> str:
    edit_prompt = f"""Você é o Nutricionista Chefe do CalorAI.
    Sua tarefa é editar uma dieta ou receita existente com base no pedido do utilizador.

    CONTEÚDO ATUAL:
    {current_content}

    INSTRUÇÃO DO UTILIZADOR:
    "{instruction}"

    REGRAS:
    1. Altere O MÍNIMO POSSÍVEL do conteúdo atual, focando-se apenas em atender à instrução.
    2. Você DEVE usar a ferramenta 'buscar_alimentos_no_banco'.
    3. Se você usar alimentos que não estão na nossa base de dados, realce que as informações acerca das kcal podem divergir um pouco.
    4. A quantidade de calorias pode passar um pouco pra cima ou pra baixo.
    5. Seja direto, não embeleze demais as respostas, seja prático.
    6. Recalcule os totais se alterar porções ou alimentos.
    7. DEVOLVA APENAS O TEXTO FINAL EM MARKDOWN. Não use tags JSON, não explique o que fez. Apenas a nova dieta pronta.
    """

    try:
      # Cria um agente rápido usando o seu LLM e ferramentas
      agent_executor = create_react_agent(self.llm, self.tools, prompt=edit_prompt)
      response = agent_executor.invoke({"messages": [("user", instruction)]})
      novo_conteudo = response["messages"][-1].content

      # Limpeza rápida caso a IA devolva lista
      if isinstance(novo_conteudo, list):
        pedacos = [bloco.get("text", str(bloco)) if isinstance(bloco, dict) else str(bloco) for bloco in novo_conteudo]
        novo_conteudo = "".join(pedacos)

      # Limpa aspas ou crases de markdown do código
      novo_conteudo = re.sub(r'^```(markdown)?\s*', '', str(novo_conteudo), flags=re.MULTILINE | re.IGNORECASE)
      novo_conteudo = re.sub(r'```\s*$', '', novo_conteudo, flags=re.MULTILINE).strip()

      return novo_conteudo
    except Exception as e:
      print(f"Erro na edição por IA: {e}")
      raise Exception("Falha ao editar com a IA.")
