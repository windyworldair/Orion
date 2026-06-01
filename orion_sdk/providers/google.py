"""
Orion SDK - Google Gemini Provider
"""

from typing import Iterator

try:
    import google.generativeai as genai
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False

from .base import (
    Provider, ProviderConfig, Response, StreamChunk,
    Message, ToolDefinition, ToolCall,
)
from ..exceptions import ProviderError


class GoogleProvider(Provider):
    """Google Gemini API provider."""

    NAME = "google"
    MODELS = {
        "gemini-2.5-pro": {"context": 1048576, "output": 65536},
        "gemini-2.5-flash": {"context": 1048576, "output": 65536},
        "gemini-2.0-flash": {"context": 1048576, "output": 8192},
        "gemini-2.0-flash-lite": {"context": 1048576, "output": 8192},
        "gemini-1.5-pro": {"context": 2097152, "output": 8192},
        "gemini-1.5-flash": {"context": 1048576, "output": 8192},
        "gemini-1.5-flash-8b": {"context": 1048576, "output": 8192},
    }

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        if not HAS_GOOGLE:
            raise ImportError(
                "google-generativeai package is required. "
                "Install with: pip install google-generativeai"
            )
        genai.configure(api_key=config.api_key)

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

        gen_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=self._extract_system(messages),
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
            tools=[t.to_gemini_tools() for t in tools] if tools else None,
        )

        chat = gen_model.start_chat(history=self._to_gemini_history(messages))

        try:
            last_user_msg = self._get_last_user_message(messages)
            raw = chat.send_message(last_user_msg)
        except Exception as e:
            raise ProviderError(self.NAME, str(e)) from e

        return self._parse_response(raw, model)

    # ── helpers ──────────────────────────────────────────────────────

    def _extract_system(self, messages: list[Message]) -> str:
        """Extract system messages from the beginning."""
        parts: list[str] = []
        for msg in messages:
            if msg.role == "system":
                parts.append(msg.content if isinstance(msg.content, str) else str(msg.content))
            else:
                break
        return "\n".join(parts)

    def _to_gemini_history(self, messages: list[Message]) -> list:
        """Convert messages to Gemini chat history format."""
        history = []
        for msg in messages:
            if msg.role == "system":
                continue
            if msg.role == "user":
                history.append({"role": "user", "parts": [msg.content]})
            elif msg.role == "assistant":
                history.append({"role": "model", "parts": [msg.content]})
        # Remove last message (it's the current user message)
        return history[:-1] if history else []

    @staticmethod
    def _get_last_user_message(messages: list[Message]) -> str:
        """Get the last user message content."""
        for msg in reversed(messages):
            if msg.role == "user":
                return msg.content if isinstance(msg.content, str) else str(msg.content)
        return ""

    def _parse_response(self, raw, model: str) -> Response:
        content_parts: list[str] = []
        tool_calls: list[ToolCall] = []

        for candidate in raw.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    content_parts.append(part.text)
                elif hasattr(part, "function_call"):
                    tool_calls.append(ToolCall(
                        id=f"call_{part.function_call.name}",
                        name=part.function_call.name,
                        arguments=dict(part.function_call.args),
                    ))

        usage = {}
        if raw.usage_metadata:
            usage = {
                "prompt_tokens": raw.usage_metadata.prompt_token_count,
                "completion_tokens": raw.usage_metadata.candidates_token_count,
            }

        finish = "stop"
        if raw.candidates:
            cand = raw.candidates[0]
            finish = getattr(cand, "finish_reason", None)
            if finish:
                finish = str(finish).replace("FinishReason.", "")

        return Response(
            content="".join(content_parts),
            tool_calls=tool_calls,
            model=model,
            provider=self.NAME,
            usage=usage,
            finish_reason=finish,
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

        gen_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=self._extract_system(messages),
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
            tools=[t.to_gemini_tools() for t in tools] if tools else None,
        )

        chat = gen_model.start_chat(history=self._to_gemini_history(messages))

        try:
            last_user_msg = self._get_last_user_message(messages)
            response_stream = chat.send_message(last_user_msg, stream=True)

            for chunk in response_stream:
                content = ""
                if hasattr(chunk, "text"):
                    content = chunk.text

                finish = "stop"
                if chunk.candidates:
                    cand = chunk.candidates[0]
                    finish = getattr(cand, "finish_reason", None)
                    if finish:
                        finish = str(finish).replace("FinishReason.", "")

                yield StreamChunk(
                    content=content,
                    finish_reason=finish,
                    model=model,
                    provider=self.NAME,
                )
        except Exception as e:
            raise ProviderError(self.NAME, str(e)) from e

    def list_models(self) -> list[dict]:
        return [
            {"id": mid, "name": mid, "context": info["context"], "output": info["output"]}
            for mid, info in self.MODELS.items()
        ]
