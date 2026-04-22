import os
from typing import Callable

from google import genai
from google.genai import types

from ..exceptions import LLMAPIKeyNotSetError
from .base import BaseLLMClient


class GeminiLLMClient(BaseLLMClient):
    def __init__(
        self, model_name: str = "gemini-3-flash-preview", temperature: float = 0.7
    ):
        super().__init__(model_name, temperature)

        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key or api_key == "$GEMINI_API_KEY":
            raise LLMAPIKeyNotSetError("Chave de API não encontrada.")

        self.client = genai.Client()

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: type,
        tools: list[Callable] | None = None,
    ) -> str:
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=self.temperature,
            tools=tools or [],
        )

        # Chat para manter o contexto das chamadas de função
        chat = self.client.chats.create(model=self.model_name, config=config)
        response = chat.send_message(user_prompt)

        # Loop para executar ferramentas até a IA estar satisfeita e retornar o texto
        while response.function_calls:
            function_responses = []

            for call in response.function_calls:
                # Busca a função no array de tools pelo nome
                tool_func = next(
                    (t for t in (tools or []) if t.__name__ == call.name), None
                )

                if tool_func:
                    try:
                        # Executa a tool localmente passando os argumentos que a IA enviou
                        result = tool_func(**call.args)
                        function_responses.append(
                            types.Part.from_function_response(
                                name=call.name, response={"result": result}
                            )
                        )
                    except Exception as e:
                        # Se a tool falhar, avisa a IA para que ela possa tentar de novo ou contornar
                        function_responses.append(
                            types.Part.from_function_response(
                                name=call.name, response={"error": str(e)}
                            )
                        )

            # Devolve as respostas das ferramentas para a IA
            response = chat.send_message(function_responses)

        # Quando sair do loop, a IA finalmente retornou o conteúdo final
        return str(response.text)
