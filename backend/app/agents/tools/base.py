from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """Schema describing an individual parameter expected by an AI tool."""

    name: str
    type: str
    description: str
    required: bool = True


class ToolDefinition(BaseModel):
    """Metadata and parameter schema definition for function calling."""

    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class BaseTool(ABC):
    """
    Abstract Base Class for AI agent tools.
    Future restaurant tools will inherit from this base class.

    Future tool definitions (Phase 2+):
    - search_menu()
    - get_item()
    - check_availability()
    - create_cart()
    - add_to_cart()
    - remove_from_cart()
    - calculate_total()
    - create_order()
    - get_order_status()
    - handoff_to_human()
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The tool name as recognized by LLM function calling."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool accomplishes."""
        pass

    @abstractmethod
    def get_definition(self) -> ToolDefinition:
        """Return the function call definition schema."""
        pass

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Execute the tool action."""
        pass
