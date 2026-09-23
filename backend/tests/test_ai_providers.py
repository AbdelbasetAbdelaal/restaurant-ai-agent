import pytest

from app.agents.provider import AIProvider, AIResponse
from app.agents.providers.groq_provider import GroqProvider
from app.agents.providers.huggingface_provider import HuggingFaceProvider
from app.agents.providers.openai_provider import OpenAIProvider
from app.agents.router import AIRouter
from app.agents.tools.base import BaseTool, ToolDefinition


@pytest.mark.parametrize(
    "provider_cls,expected_name",
    [
        (OpenAIProvider, "openai"),
        (GroqProvider, "groq"),
        (HuggingFaceProvider, "huggingface"),
    ],
)
def test_providers_conform_to_interface(provider_cls, expected_name):
    """Verify that all AI providers inherit from AIProvider and implement interface."""
    assert issubclass(provider_cls, AIProvider)

    # Initialize without API key (Phase 1 rule: no keys required)
    instance = provider_cls()
    assert instance.name == expected_name
    assert instance.is_configured() is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "provider_cls",
    [OpenAIProvider, GroqProvider, HuggingFaceProvider],
)
async def test_provider_stub_execution_without_network_calls(provider_cls):
    """Verify provider methods return AIResponse without making external API calls."""
    instance = provider_cls()

    # Test text completion stub
    text_res = await instance.generate_text("List pizza specials")
    assert isinstance(text_res, AIResponse)
    assert text_res.provider == instance.name
    assert len(text_res.content) > 0

    # Test chat completion stub
    chat_res = await instance.chat([{"role": "user", "content": "Hello"}])
    assert isinstance(chat_res, AIResponse)
    assert chat_res.provider == instance.name
    assert len(chat_res.content) > 0


def test_ai_router_registry_and_fallback():
    """Verify AIRouter correctly resolves providers and handles fallbacks."""
    router = AIRouter(default_provider="openai")

    # List providers
    providers = router.list_providers()
    assert "openai" in providers
    assert "groq" in providers
    assert "huggingface" in providers

    # Retrieve specific provider
    groq = router.get_provider("groq")
    assert isinstance(groq, GroqProvider)

    # Retrieve default provider
    default_p = router.get_provider()
    assert isinstance(default_p, OpenAIProvider)

    # Fallback on unknown provider name
    fallback = router.get_provider("unknown_provider_xyz")
    assert isinstance(fallback, OpenAIProvider)


def test_future_tool_interface():
    """Verify BaseTool architectural boundary."""

    class MockMenuTool(BaseTool):
        @property
        def name(self) -> str:
            return "search_menu"

        @property
        def description(self) -> str:
            return "Search available menu items by keyword"

        def get_definition(self) -> ToolDefinition:
            return ToolDefinition(
                name=self.name,
                description=self.description,
                parameters={"query": {"type": "string"}},
            )

        async def execute(self, **kwargs):
            return ["Margherita Pizza", "Pepperoni Pizza"]

    tool = MockMenuTool()
    assert tool.name == "search_menu"
    definition = tool.get_definition()
    assert definition.name == "search_menu"
    assert "query" in definition.parameters
