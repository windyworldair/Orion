"""
Orion SDK - OpenAI Provider
Also serves as the base for OpenAI-compatible endpoints.
"""

from typing import Iterator

try:
    from openai import OpenAI, Stream
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from .base import (
    Provider, ProviderConfig, Response, StreamChunk,
    Message, ToolDefinition,
)
from ..exceptions import (
    AuthenticationError, RateLimitError, ProviderError,
)


class OpenAIProvider(Provider):
    """OpenAI GPT API provider.

    Also works with any OpenAI-compatible endpoint by setting ``base_url``
    (e.g. vLLM, LiteLLM, Together AI).
    """

    NAME = "openai"
    MODELS = {
        "gpt-4o": {"context": 128000, "output": 16384},
        "gpt-4o-mini": {"context": 128000, "output": 16384},
        "gpt-4-turbo": {"context": 128000, "output": 4096},
        "gpt-4": {"context": 8192, "output": 4096},
        "gpt-3.5-turbo": {"context": 16385, "output": 4096},
        "o1": {"context": 200000, "output": 100000},
        "o1-mini": {"context": 128000, "output": 65536},
        "o1-preview": {"context": 128000, "output": 4096},
        "o3-mini": {"context": 200000, "output": 100000},
        "o3": {"context": 200000, "output": 100000},
    }

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        if not HAS_OPENAI:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )

        client_kwargs: dict = {
            "api_key": config.api_key,
            "timeout": config.timeout,
            "max_retries": config.max_retries,
        }
        if config.base_url:
            client_kwargs["base_url"] = config.base_url
        if config.organization:
            client_kwargs["organization"] = config.organization
        self._client = OpenAI(**client_kwargs)

    def complete(
        self,
        messages: list[Message],
        model: str = "",
        tools: list[ToolDefinition] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> Response:
        model = self.validate_model(model)

        kwargs_body: dict = {
            "model": model,
            "messages": [m.to_dict() for m in messages],
            "max_tokens": max_tokens,
        }

        # o1/o3 models don't support temperature in the same way
        model_lower = model.lower()
        if not any(x in model_lower for x in ("o1", "o3")):
            kwargs_body["temperature"] = temperature

        if tools:
            kwargs_body["tools"] = [t.to_openai() for t in tools]

        # Merge provider-specific kwargs
        kwargs_body.update({k: v for k, v in kwargs.items() if v is not None})

        try:
            raw = self._client.chat.completions.create(**kwargs_body)
        except Exception as e:
            err_str = str(e).lower()
            if "auth" in err_str or "api_key" in err_str or "401" in err_str:
                raise AuthenticationError(self.NAME) from e
            if "429" in str(e) or "rate" in err_str:
                raise RateLimitError(self.NAME) from e
            raise ProviderError(self.NAME, str(e)) from e

        return self._parse_response(raw)

    def _parse_response(self, raw) -> Response:
        choice = raw.choices[0] if raw.choices else None
        message = choice.message if choice else None

        content = message.content if message else ""
        tool_calls = []

        if message and hasattr(message, "tool_calls") and message.tool_calls:
            from .base import ToolCall
            for tc in message.tool_calls:
                tool_calls.append(ToolCall.from_openai(tc.__dict__))

        usage = {}
        if raw.usage:
            usage = {
                "prompt_tokens": raw.usage.prompt_tokens,
                "completion_tokens": raw.usage.completion_tokens,
            }
            if hasattr(raw.usage, "total_tokens"):
                usage["total_tokens"] = raw.usage.total_tokens

        return Response(
            content=content or "",
            tool_calls=tool_calls,
            model=raw.model,
            provider=self.NAME,
            usage=usage,
            finish_reason=choice.stop_reason if choice else "",
            raw=raw,
        )

    def stream(
        self,
        messages: list[Message],
        model: str = "",
        tools: list[ToolDefinition] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> Iterator[StreamChunk]:
        model = self.validate_model(model)

        kwargs_body: dict = {
            "model": model,
            "messages": [m.to_dict() for m in messages],
            "max_tokens": max_tokens,
            "stream": True,
        }

        model_lower = model.lower()
        if not any(x in model_lower for x in ("o1", "o3")):
            kwargs_body["temperature"] = temperature

        if tools:
            kwargs_body["tools"] = [t.to_openai() for t in tools]

        kwargs_body.update({k: v for k, v in kwargs.items() if v is not None})

        try:
            raw_stream = self._client.chat.completions.create(**kwargs_body)
            for chunk in raw_stream:
                choice = chunk.choices[0] if chunk.choices else None
                if not choice:
                    continue

                delta = choice.delta
                content = ""
                if hasattr(delta, "content") and delta.content:
                    content = delta.content
                finish = choice.finish_reason if hasattr(choice, "finish_reason") else None

                tc_list = []
                if hasattr(delta, "tool_calls") and delta.tool_calls:
                    from .base import ToolCall
                    for tc in delta.tool_calls:
                        tc_list.append(ToolCall.from_openai(tc.__dict__))

                yield StreamChunk(
                    content=content,
                    tool_calls=tc_list,
                    finish_reason=finish,
                    model=chunk.model if hasattr(chunk, "model") else model,
                    provider=self.NAME,
                )
        except Exception as e:
            raise ProviderError(self.NAME, str(e)) from e

    def list_models(self) -> list[dict]:
        return [
            {"id": mid, "name": mid, "context": info["context"], "output": info["output"]}
            for mid, info in self.MODELS.items()
        ]
