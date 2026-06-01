"""
Orion SDK - Ollama Provider (Local Models)
Run models locally via Ollama. No API key needed.
"""

import json
from typing import Iterator

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from .base import (
    Provider, ProviderConfig, Response, StreamChunk,
    Message, ToolDefinition, ToolCall,
)
from ..exceptions import ProviderError


class OllamaProvider(Provider):
    """Ollama local model provider.

    Free, private, no API key required.  Just make sure Ollama is running
    locally (``ollama serve``) and you have pulled the models you want.
    """

    NAME = "ollama"
    MODELS = {
        # Common models — actual list depends on what's installed locally
        "llama3.1": {"context": 131072, "output": 4096},
        "llama3.2": {"context": 131072, "output": 4096},
        "llama3.3": {"context": 131072, "output": 4096},
        "codellama": {"context": 16384, "output": 4096},
        "mistral": {"context": 32768, "output": 4096},
        "mistral-nemo": {"context": 131072, "output": 4096},
        "qwen2.5": {"context": 131072, "output": 4096},
        "qwen2.5-coder": {"context": 131072, "output": 4096},
        "deepseek-coder-v2": {"context": 131072, "output": 4096},
        "phi3": {"context": 131072, "output": 4096},
        "gemma2": {"context": 8192, "output": 4096},
        "command-r": {"context": 131072, "output": 4096},
        "nous-hermes2": {"context": 32768, "output": 4096},
    }

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        if not HAS_REQUESTS:
            raise ImportError(
                "requests package is required. Install with: pip install requests"
            )
        self._base_url = (config.base_url or "http://localhost:11434").rstrip("/")

    @property
    def requires_api_key(self) -> bool:
        return False

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

        payload: dict = {
            "model": model,
            "messages": [m.to_dict() for m in messages],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters,
                    },
                }
                for t in tools
            ]

        try:
            resp = requests.post(
                f"{self._base_url}/api/chat",
                json=payload,
                timeout=self.config.timeout,
            )
            resp.raise_for_status()
            raw = resp.json()
        except requests.exceptions.ConnectionError:
            raise ProviderError(
                self.NAME,
                "Cannot connect to Ollama. Is Ollama running? Install: https://ollama.ai",
            )
        except Exception as e:
            raise ProviderError(self.NAME, str(e)) from e

        return self._parse_response(raw, model)

    def _parse_response(self, raw: dict, model: str) -> Response:
        content = raw.get("message", {}).get("content", "")
        tool_calls: list[ToolCall] = []

        tool_calls_raw = raw.get("message", {}).get("tool_calls", [])
        for tc in tool_calls_raw:
            tool_calls.append(ToolCall(
                id=tc.get("name", ""),
                name=tc.get("name", ""),
                arguments=tc.get("arguments", {}),
            ))

        usage = {}
        prompt_eval = raw.get("prompt_eval_count")
        eval_count = raw.get("eval_count")
        if prompt_eval is not None:
            usage["prompt_tokens"] = prompt_eval
        if eval_count is not None:
            usage["completion_tokens"] = eval_count

        return Response(
            content=content,
            tool_calls=tool_calls,
            model=model,
            provider=self.NAME,
            usage=usage,
            finish_reason=raw.get("done_reason", "stop"),
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

        payload: dict = {
            "model": model,
            "messages": [m.to_dict() for m in messages],
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters,
                    },
                }
                for t in tools
            ]

        try:
            resp = requests.post(
                f"{self._base_url}/api/chat",
                json=payload,
                timeout=self.config.timeout,
                stream=True,
            )
            resp.raise_for_status()

            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    chunk_data = json.loads(line)
                    content = chunk_data.get("message", {}).get("content", "")
                    finish = (
                        chunk_data.get("done_reason")
                        if chunk_data.get("done")
                        else None
                    )

                    yield StreamChunk(
                        content=content,
                        finish_reason=finish,
                        model=model,
                        provider=self.NAME,
                    )
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            raise ProviderError(self.NAME, str(e)) from e

    def list_models(self) -> list[dict]:
        """List models available in the local Ollama installation."""
        try:
            resp = requests.get(f"{self._base_url}/api/tags", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            models = []
            for m in data.get("models", []):
                name = m.get("name", "")
                info = self.MODELS.get(name, {"context": None, "output": None})
                models.append({
                    "id": name,
                    "name": name,
                    "context": info["context"],
                    "output": info["output"],
                    "size": m.get("size"),
                    "modified": m.get("modified_at"),
                })
            return models
        except Exception:
            # Return known models if Ollama isn't reachable
            return [
                {"id": mid, "name": mid, "context": info["context"], "output": info["output"]}
                for mid, info in self.MODELS.items()
            ]
