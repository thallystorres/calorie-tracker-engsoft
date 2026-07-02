import os
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import pydantic
from django.contrib.auth.models import User
from google import genai
from google.genai.types import GenerateContentConfig, GenerateContentResponse, Part
from pydantic import TypeAdapter, ValidationError

from core.apps import (
    LLMAPIKeyNotSetError,
    LLMAttemptsExhaustedError,
    LLMRequestError,
    LLMResponseError,
)


class BaseLLMClient(ABC):
    def __init__(self, model_name: str, temperature: float):
        self.model_name = model_name
        self.temperature = temperature

    @abstractmethod
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[pydantic.BaseModel],
        tools: list[Callable] | None = None,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: list[Callable] | None = None,
    ) -> str:
        pass


class BaseAIGeneratorService(ABC):
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client

    # The Template Method
    def generate(self, user: User, user_prompt: str, **kwargs) -> Any:
        context = self.build_context(user, **kwargs)
        system_prompt = self.get_system_prompt(context)
        augmented_prompt = self.augment_user_prompt(user, user_prompt)
        tools = self.get_tools()
        schema = self.get_response_schema()

        raw_json = self.llm_client.generate_json(
            system_prompt=system_prompt,
            user_prompt=augmented_prompt,
            response_schema=schema,
            tools=tools,
        )
        return self.format_response(raw_json, context)

    @abstractmethod
    def build_context(self, user: User, **kwargs) -> dict:
        pass

    @abstractmethod
    def get_system_prompt(self, context: dict) -> str:
        pass

    @abstractmethod
    def get_response_schema(self) -> type:
        pass

    def augment_user_prompt(self, user: User, prompt: str) -> str:
        return prompt  # Default implementation

    def get_tools(self) -> list:
        return []  # Default implementation

    def format_response(self, raw_json: dict, context: dict) -> Any:
        return raw_json  # Default implementation


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
                except (ValueError, KeyError, TypeError) as e:
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

                function_call_count = 0
                max_function_calls = 10

                while (
                    response.function_calls and function_call_count < max_function_calls
                ):
                    function_call_count += 1
                    function_responses = self.__process_function_calls(response, tools)
                    response = chat.send_message(function_responses)

                return adapter.validate_json(str(response.text))
            except ValidationError as e:
                raise LLMResponseError(
                    "Resposta da IA não corresponde ao esquema esperado."
                ) from e
            except (ConnectionError, TimeoutError, ValueError) as e:
                if attempt == max_attempts:
                    raise LLMAttemptsExhaustedError(
                        "Falha ao gerar resposta JSON da IA após múltiplas tentativas."
                    ) from e
                time.sleep(0.5 * (2 ** (attempt - 1)))

        raise LLMAttemptsExhaustedError("Falha inesperada ao gerar resposta JSON da IA")

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

                function_call_count = 0
                max_function_calls = 10

                while (
                    response.function_calls and function_call_count < max_function_calls
                ):
                    print(f"response is {response.text}")
                    function_call_count += 1
                    function_responses = self.__process_function_calls(response, tools)
                    response = chat.send_message(function_responses)

                return str(response.text)
            except ValidationError:
                raise LLMResponseError(
                    "Resposta da IA não corresponde ao esquema esperado."
                ) from None
            except (ConnectionError, TimeoutError, ValueError) as e:
                if attempt == max_attempts:
                    raise LLMAttemptsExhaustedError(
                        "Falha ao gerar texto da IA após múltiplas tentativas."
                    ) from e
                time.sleep(0.5 * (2 ** (attempt - 1)))

        raise LLMAttemptsExhaustedError("Falha inesperada ao gerar texto da IA")

    def get_embedding(self, text: str, task_type: str = "search_query") -> list[float]:
        formatted_prompt = f"task: {task_type} | query: {text}"

        try:
            result = self.client.models.embed_content(
                model="gemini-embedding-2",
                contents=formatted_prompt,
            )
            return result.embeddings[0].values
        except (ConnectionError, TimeoutError) as e:
            raise LLMRequestError("Falha de conexão ao gerar embedding.") from e
        except Exception as e:
            raise LLMRequestError("Erro inesperado ao gerar embedding.") from e
