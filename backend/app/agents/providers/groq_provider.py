from typing import Any

from app.agents.provider import AIProvider, AIResponse


class GroqProvider(AIProvider):
    """
    Groq Provider abstraction.
    Provides ultra-low latency inference for restaurant voice/chat ordering in later phases.
    In Phase 1, acts as an architectural stub.
    """

    def __init__(
        self, api_key: str | None = None, default_model: str = "llama-3.3-70b-versatile"
    ):
        self._api_key = api_key
        self.default_model = default_model

    @property
    def name(self) -> str:
        return "groq"

    def is_configured(self) -> bool:
        return bool(self._api_key)

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AIResponse:
        return AIResponse(
            content=f"[Groq Stub] Received prompt of length {len(prompt)}",
            provider=self.name,
            model=kwargs.get("model", self.default_model),
            metadata={"status": "stub", "phase": 1},
        )

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> AIResponse:
        return AIResponse(
            content=f"[Groq Stub] Chat turn processed with {len(messages)} messages",
            provider=self.name,
            model=kwargs.get("model", self.default_model),
            metadata={"status": "stub", "message_count": len(messages)},
        )
