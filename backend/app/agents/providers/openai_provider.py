from typing import Any

from app.agents.provider import AIProvider, AIResponse


class OpenAIProvider(AIProvider):
    """
    OpenAI Provider abstraction.
    In Phase 1, this acts as an architectural stub conforming to the AIProvider interface.
    No live external API calls are executed.
    """

    def __init__(self, api_key: str | None = None, default_model: str = "gpt-4o-mini"):
        self._api_key = api_key
        self.default_model = default_model

    @property
    def name(self) -> str:
        return "openai"

    def is_configured(self) -> bool:
        return bool(self._api_key)

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AIResponse:
        # Phase 1 architectural placeholder: Real API call will be wired in Phase 3
        return AIResponse(
            content=f"[OpenAI Stub] Received prompt of length {len(prompt)}",
            provider=self.name,
            model=kwargs.get("model", self.default_model),
            metadata={"status": "stub", "phase": 1},
        )

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> AIResponse:
        # Phase 1 architectural placeholder
        return AIResponse(
            content=f"[OpenAI Stub] Chat turn processed with {len(messages)} messages",
            provider=self.name,
            model=kwargs.get("model", self.default_model),
            metadata={"status": "stub", "message_count": len(messages)},
        )
