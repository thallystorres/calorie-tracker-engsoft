import os
import time
from collections.abc import Callable
from typing import Any

from google import genai
from google.genai.types import GenerateContentConfig, GenerateContentResponse, Part
from pydantic import TypeAdapter, ValidationError

from ..exceptions import LLMAPIKeyNotSetError
from .base import BaseLLMClient


class GeminiLLMClient(BaseLLMClient):
    def __init__(
        self,
        model_name: str = "gemini-3.1-flash-lite-preview",
        temperature: float = 0.7,
    ):
        super().__init__(model_name, temperature)

        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key or api_key == "$GEMINI_API_KEY":
            raise LLMAPIKeyNotSetError("Chave de API não encontrada.")

        self.client = genai.Client()

    def __process_function_calls(
        self, response: GenerateContentResponse, tools: list[Callable]
    ) -> list[Part]:
        function_responses: Part = []

        for call in response.function_calls:
            if not call.name:
                continue

            tool_func = next(
                (t for t in (tools or []) if t.__name__ == call.name), None
            )

            if tool_func:
                try:
                    tool_args = call.args if isinstance(call.args, dict) else {}
                    result = tool_func(**tool_args)
                    function_responses.append(
                        Part.from_function_response(
                            name=call.name, response={"result": result}
                        )
                    )
                except Exception as e:
                    function_responses.append(
                        Part.from_function_response(
                            name=call.name, response={"error": str(e)}
                        )
                    )

        return function_responses

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: type,
        tools: list[Callable] | None = None,
    ) -> dict[str, Any]:
        adapter: TypeAdapter[dict[str, Any]] = TypeAdapter(dict[str, Any])
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                config = GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=self.temperature,
                    tools=tools or [],
                )

                chat = self.client.chats.create(model=self.model_name, config=config)
                response = chat.send_message(user_prompt)

                while response.function_calls:
                    function_responses = self.__process_function_calls(response, tools)

                    response = chat.send_message(function_responses)

                return adapter.validate_json(str(response.text))
            except ValidationError:
                raise
            except Exception:
                if attempt == max_attempts:
                    raise
                time.sleep(0.5 * (2 ** (attempt - 1)))

        raise RuntimeError("Falha inesperada ao gerar resposta da IA")

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: list[Callable] | None = None,
    ) -> str:
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            print(f"Attempt number {attempt} of generating text")
            try:
                config = GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="text/plain",
                    temperature=self.temperature,
                    tools=tools or [],
                )

                chat = self.client.chats.create(model=self.model_name, config=config)
                response = chat.send_message(user_prompt)

                while response.function_calls:
                    print(f"response is {response.text}")
                    function_responses = self.__process_function_calls(response, tools)

                    response = chat.send_message(function_responses)

                return str(response.text)
            except ValidationError:
                raise
            except Exception:
                if attempt == max_attempts:
                    raise
                time.sleep(0.5 * (2 ** (attempt - 1)))

        raise RuntimeError("Falha inesperada ao gerar resposta da IA")

    def get_embedding(self, text: str, task_type: str = "search_query") -> list[float]:
        """
        Gera embeddings usando o modelo gemini-embedding-2.
        Segue as recomendações de prefixo para busca assimétrica.
        """
        # Formata o prompt de acordo com as recomendações do Gemini Embedding 2
        # Use 'task: search query | query: {content}' para consultas
        formatted_prompt = f"task: {task_type} | query: {text}"

        result = self.client.models.embed_content(
            model="gemini-embedding-2",
            contents=formatted_prompt,
        )

        # O modelo Embedding 2 retorna uma lista com um único embedding agregado
        return result.embeddings[0].values
