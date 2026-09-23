from app.agents.provider import AIProvider
from app.agents.providers.groq_provider import GroqProvider
from app.agents.providers.huggingface_provider import HuggingFaceProvider
from app.agents.providers.openai_provider import OpenAIProvider
from app.core.logging import logger


class AIRouter:
    """
    Router and registry for AI providers.
    Decouples business agents from concrete AI provider implementations.
    Allows dynamic selection and switching between providers per restaurant or per request.
    """

    def __init__(self, default_provider: str = "openai"):
        self._providers: dict[str, AIProvider] = {}
        self._default_provider_name: str = default_provider

        # Initialize default providers (in Phase 1, unconfigured stubs)
        self.register_provider(OpenAIProvider())
        self.register_provider(GroqProvider())
        self.register_provider(HuggingFaceProvider())

    def register_provider(self, provider: AIProvider) -> None:
        """Register a concrete AIProvider instance."""
        self._providers[provider.name.lower()] = provider
        logger.info(f"Registered AI Provider: {provider.name}")

    def get_provider(self, name: str | None = None) -> AIProvider:
        """
        Retrieve provider by name.
        Falls back to default provider if name is None or not found.
        """
        provider_name = (name or self._default_provider_name).lower()
        if provider_name not in self._providers:
            logger.warning(
                f"Requested AI provider '{provider_name}' not found. "
                f"Falling back to default '{self._default_provider_name}'."
            )
            provider_name = self._default_provider_name

        return self._providers[provider_name]

    def list_providers(self) -> list[str]:
        """List registered provider names."""
        return list(self._providers.keys())


# Singleton router instance
ai_router = AIRouter()
