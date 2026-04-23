from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import pydantic


class BaseLLMClient(ABC):
    def __init__(self, model_name: str, temperature):
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
        raise NotImplementedError
