from typing import Protocol


class ModelProvider(Protocol):
    def complete(self, prompt: str, *, tier: int) -> str: ...
