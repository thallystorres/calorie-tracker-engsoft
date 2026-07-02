from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any
from django.contrib.auth.models import User
from .clients.base import BaseLLMClient

class BaseAIGeneratorService(ABC):
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client

    def generate(self, user: User | None, user_prompt: str, **kwargs) -> Any:
        context = self.build_context(user, **kwargs)
        system_prompt = self.get_system_prompt(context)
        augmented_prompt = self.augment_user_prompt(user, user_prompt)
        tools = self.get_tools()
        schema = self.get_response_schema()

        if schema:
            raw_json = self.llm_client.generate_json(
                system_prompt=system_prompt,
                user_prompt=augmented_prompt,
                response_schema=schema,
                tools=tools,
            )
            return self.format_response(raw_json, context)
        else:
            raw_text = self.llm_client.generate_text(
                system_prompt=system_prompt,
                user_prompt=augmented_prompt,
                tools=tools,
            )
            return self.format_response(raw_text, context)

    @abstractmethod
    def build_context(self, user: User | None, **kwargs) -> dict:
        pass

    @abstractmethod
    def get_system_prompt(self, context: dict) -> str:
        pass

    def get_response_schema(self) -> type | None:
        return None

    def augment_user_prompt(self, user: User | None, prompt: str) -> str:
        return prompt

    def get_tools(self) -> list[Callable] | None:
        return None

    def format_response(self, raw_data: Any, context: dict) -> Any:
        return raw_data
