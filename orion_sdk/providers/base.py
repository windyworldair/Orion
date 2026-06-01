"""
Orion SDK - Base Provider Interface
All providers must implement this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Iterator


@dataclass
class Message:
    """A chat message.

    Supports the standard roles: ``system``, ``user``, ``assistant``, ``tool``.

    Example::

        msg = Message.user("Hello!")
        msg = Message.system("You are a helpful assistant.")
        msg = Message.assistant("Hi there!")
    """

    role: str  # "system", "user", "assistant", "tool"
    content: str | list

    def to_dict(self) -> dict:
        """Serialize to a plain dict suitable for provider APIs."""
        return {"role": self.role, "content": self.content}

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """Deserialize from a plain dict."""
        return cls(role=data["role"], content=data["content"])

    @classmethod
    def system(cls, content: str) -> "Message":
        """Create a system message."""
        return cls(role="system", content=content)

    @classmethod
    def user(cls, content: str) -> "Message":
        """Create a user message."""
        return cls(role="user", content=content)

    @classmethod
    def assistant(cls, content: str) -> "Message":
        """Create an assistant message."""
        return cls(role="assistant", content=content)

    @classmethod
    def tool(cls, content: str, tool_call_id: str = "") -> "Message":
        """Create a tool-result message."""
        return cls(role="tool", content=content)


@dataclass
class ToolDefinition:
    """A tool / function definition for the model.

    Example::

        tool = ToolDefinition(
            name="get_weather",
            description="Get the current weather for a location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                },
                "required": ["location"],
            },
        )
    """

    name: str
    description: str
    parameters: dict = field(
        default_factory=lambda: {"type": "object", "properties": {}}
    )

    def to_openai(self) -> dict:
        """Format for OpenAI / OpenRouter API."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def to_anthropic(self) -> dict:
        """Format for Anthropic API."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }

    def to_google(self) -> dict:
        """Format for Google Gemini API."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }

    def to_gemini_tools(self) -> dict:
        """Wrap in Gemini *tools* envelope."""
        return {"function_declarations": [self.to_google()]}


@dataclass
class ToolCall:
    """A tool call requested by the model."""

    id: str
    name: str
    arguments: dict

    def to_openai(self) -> dict:
        """Format for OpenAI API."""
        return {
            "id": self.id,
            "type": "function",
            "function": {
                "name": self.name,
                "arguments": str(self.arguments),
            },
        }

    @classmethod
    def from_openai(cls, data: dict) -> "ToolCall":
        """Parse from an OpenAI-format tool-call object."""
        func = data.get("function", {})
        raw_args = func.get("arguments", "{}")
        if isinstance(raw_args, dict):
            args = raw_args
        else:
            try:
                import json
                args = json.loads(raw_args)
            except (json.JSONDecodeError, TypeError):
                args = {}
        return cls(
            id=data.get("id", ""),
            name=func.get("name", ""),
            arguments=args,
        )


@dataclass
class Response:
    """A completion response from a provider.

    Attributes:
        content: The text content of the response.
        tool_calls: Any tool calls the model requested.
        model: The model identifier used.
        provider: The provider name (e.g. ``"openai"``).
        usage: Token usage dict with keys like ``prompt_tokens``, ``completion_tokens``.
        finish_reason: Why generation stopped (``"stop"``, ``"tool_calls"``, etc.).
        raw: The raw response object from the underlying SDK.
    """

    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    model: str = ""
    provider: str = ""
    usage: dict = field(default_factory=dict)
    finish_reason: str = ""
    raw: Any = None

    @property
    def has_tool_calls(self) -> bool:
        """Whether the response contains tool calls."""
        return len(self.tool_calls) > 0


@dataclass
class StreamChunk:
    """A single chunk in a streaming response."""

    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: Optional[str] = None
    model: str = ""
    provider: str = ""


@dataclass
class ProviderConfig:
    """Configuration for a provider."""

    api_key: str = ""
    base_url: str = ""
    organization: str = ""  # For OpenAI org header
    timeout: float = 120.0
    max_retries: int = 3
    verify_ssl: bool = True


class Provider(ABC):
    """Abstract base class for all model providers.

    To add a new provider:

    1. Subclass :class:`Provider`
    2. Implement :meth:`complete`, :meth:`stream`, and :meth:`list_models`
    3. Set the ``NAME`` and ``MODELS`` class attributes
    4. Register with :meth:`OrionClient.add_provider` or :func:`register_provider`
    """

    NAME: str = ""
    MODELS: dict[str, dict] = {}  # {"model_name": {"context": 128000, "output": 4096}}

    def __init__(self, config: ProviderConfig):
        self.config = config
        self._client = None

    @abstractmethod
    def complete(
        self,
        messages: list[Message],
        model: str = "",
        tools: list[ToolDefinition] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> Response:
        """Send a completion request to the provider.

        Args:
            messages: List of chat messages.
            model: Model name (uses provider default if empty).
            tools: Available tool definitions.
            temperature: Sampling temperature (0.0 – 2.0).
            max_tokens: Max output tokens.
            **kwargs: Provider-specific options.

        Returns:
            A :class:`Response` object.
        """
        ...

    @abstractmethod
    def stream(
        self,
        messages: list[Message],
        model: str = "",
        tools: list[ToolDefinition] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> Iterator[StreamChunk]:
        """Stream a completion response.

        Args:
            Same as :meth:`complete`.

        Returns:
            An iterator of :class:`StreamChunk` objects.
        """
        ...

    @abstractmethod
    def list_models(self) -> list[dict]:
        """List available models.

        Returns:
            A list of dicts, each with keys ``id``, ``name``, ``context``, ``output``.
        """
        ...

    def get_model_info(self, model: str) -> dict:
        """Get info about a specific model."""
        if model in self.MODELS:
            return {"id": model, **self.MODELS[model]}
        return {"id": model, "context": None, "output": None}

    def validate_model(self, model: str) -> str:
        """Validate and return the canonical model name.

        Performs fuzzy matching so partial names like ``"gpt-4o"`` resolve
        to the full model ID.
        """
        if not model:
            return list(self.MODELS.keys())[0] if self.MODELS else ""

        model_lower = model.lower()
        for m in self.MODELS:
            if model_lower in m.lower() or m.lower() in model_lower:
                return m

        return model  # Allow unknown models (user might know what they're doing)

    @property
    def default_model(self) -> str:
        """Default model for this provider."""
        return list(self.MODELS.keys())[0] if self.MODELS else ""

    @property
    def requires_api_key(self) -> bool:
        """Whether this provider requires an API key."""
        return True
