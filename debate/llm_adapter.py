from typing import Any, Dict, Protocol

try:
    from litellm import completion
except Exception:  # pragma: no cover - litellm optional in tests
    completion = None


class LLMClientProtocol(Protocol):
    def completion(self, *, model: str, messages: list, temperature: float = 0.7) -> Any:
        ...


class LiteLLMAdapter:
    """Adapter for the `litellm.completion` function.

    This keeps the rest of the application decoupled from the concrete LLM
    implementation (Dependency Inversion).
    """

    def __init__(self, model: str):
        if completion is None:
            raise RuntimeError("litellm is not available in the environment")
        self.model = model

    def completion(self, *, model: str = None, messages: list, temperature: float = 0.7) -> Any:
        # allow overriding model per-call, but default to configured model
        model_to_use = model or self.model
        return completion(model=model_to_use, messages=messages, temperature=temperature)
