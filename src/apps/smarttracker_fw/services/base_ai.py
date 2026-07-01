from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import pydantic


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
