"""
Orion SDK - Anthropic Provider
"""

from typing import Iterator

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

from .base import (
    Provider, ProviderConfig, Response, StreamChunk,
    Message, ToolDefinition, ToolCall,
)
from ..exceptions import (
    AuthenticationError, RateLimitError, ProviderError,
)


class AnthropicProvider(Provider):
    """Anthropic Claude API provider."""

    NAME = "anthropic"
    MODELS = {
        "claude-opus-4-20250514": {"context": 200000, "output": 32000},
        "claude-sonnet-4-20250514": {"context": 200000, "output": 16000},
        "claude-3-5-sonnet-20241022": {"context": 200000, "output": 8192},
        "claude-3-5-haiku-20241022": {"context": 200000, "output": 8192},
        "claude-3-opus-20240229": {"context": 200000, "output": 4096},
        "claude-3-sonnet-20240229": {"context": 200000, "output": 4096},
        "claude-3-haiku-20240307": {"context": 200000, "output": 4096},
    }

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        if not HAS_ANTHROPIC:
            raise ImportError(
                "anthropic package is required. Install with: pip install anthropic"
            )
        self._client = anthropic.Anthropic(
            api_key=config.api_key,
            timeout=config.timeout,
        )

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

        # Anthropic separates system messages
        system_msg = ""
        chat_messages = []
        for msg in messages:
            if msg.role == "system":
                system_msg += msg.content + "\n"
            else:
                chat_messages.append(msg.to_dict())

        kwargs_body: dict = {
            "model": model,
            "messages": chat_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_msg:
            kwargs_body["system"] = system_msg.strip()
        if tools:
            kwargs_body["tools"] = [t.to_anthropic() for t in tools]
        kwargs_body.update(kwargs)

        try:
            raw = self._client.messages.create(**kwargs_body)
        except anthropic.AuthenticationError as e:
            raise AuthenticationError(self.NAME) from e
        except anthropic.RateLimitError as e:
            retry_after = None
            if hasattr(e, "response") and hasattr(e.response, "headers"):
                retry_after = e.response.headers.get("retry-after")
            raise RateLimitError(self.NAME, retry_after=retry_after) from e
        except Exception as e:
            raise ProviderError(self.NAME, str(e)) from e

        return self._parse_response(raw)

    def _parse_response(self, raw) -> Response:
        content_parts = []
        tool_calls = []

        for block in raw.content:
            if block.type == "text":
                content_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input,
                ))

        return Response(
            content="".join(content_parts),
            tool_calls=tool_calls,
            model=raw.model,
            provider=self.NAME,
            usage={
                "prompt_tokens": raw.usage.input_tokens,
                "completion_tokens": raw.usage.output_tokens,
            },
            finish_reason=raw.stop_reason,
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

        system_msg = ""
        chat_messages = []
        for msg in messages:
            if msg.role == "system":
                system_msg += msg.content + "\n"
            else:
                chat_messages.append(msg.to_dict())

        kwargs_body: dict = {
            "model": model,
            "messages": chat_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_msg:
            kwargs_body["system"] = system_msg.strip()
        if tools:
            kwargs_body["tools"] = [t.to_anthropic() for t in tools]
        kwargs_body.update(kwargs)

        try:
            with self._client.messages.stream(**kwargs_body) as stream:
                for event in stream:
                    if event.type == "content_block_delta":
                        if hasattr(event.delta, "text"):
                            yield StreamChunk(
                                content=event.delta.text,
                                model=model,
                                provider=self.NAME,
                            )
                    elif event.type == "message_stop":
                        yield StreamChunk(
                            finish_reason="stop", model=model, provider=self.NAME,
                        )
        except Exception as e:
            raise ProviderError(self.NAME, str(e)) from e

    def list_models(self) -> list[dict]:
        return [
            {"id": mid, "name": mid, "context": info["context"], "output": info["output"]}
            for mid, info in self.MODELS.items()
        ]
