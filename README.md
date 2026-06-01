<div align="center">

```
    ____                  __        ____
   / __ \__  _____  ____/ /__     / __ )____  _  __
  / /_/ / / / / _ \/ __  / _ \   / __  / __ \| |/_/
 / _, _/ /_/ /  __/ /_/ /  __/  / /_/ / /_/ />  <
/_/ |_|\__,_/\___/\__,_/\___/  /_____/____/_/|_|
```

**The Model-Agnostic AI SDK**

*One interface. Every LLM.*

Python 3.9+ &nbsp;|&nbsp; 5 Providers &nbsp;|&nbsp; 100+ Models &nbsp;|&nbsp; Zero Dependencies Required

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)](pyproject.toml)

</div>

---

## What is Orion SDK?

Orion SDK gives you **one unified Python API** to talk to every major LLM provider. Write your code once, switch models instantly. No more rewriting prompts for every provider.

```python
from orion_sdk import create_client

client = create_client("openrouter", api_key="sk-or-...")
response = client.complete("Explain quantum computing in one sentence.")
print(response.content)
```

Switch to Claude, GPT, Gemini, or a local model — **just change one word**.

---

## Features

| Feature | Description |
|---|---|
| **Provider Abstraction** | One API for OpenAI, Anthropic, Google, OpenRouter, and Ollama |
| **Fallback Chains** | Automatic failover across providers — if one fails, try the next |
| **Streaming** | Real-time token-by-token streaming from any provider |
| **Tool Calling** | Send tool definitions, receive tool calls — works with all providers |
| **Token Counting** | Accurate counting with tiktoken, or character-based estimation |
| **Rate Limiting** | Built-in token-bucket rate limiter per provider |
| **Context Limits** | Automatic context window validation before sending requests |
| **100+ Models** | Access GPT-4o, Claude, Gemini, Llama, Mistral, DeepSeek, and more |
| **Zero Required Deps** | Core SDK has no dependencies — install only what you use |
| **Custom Providers** | Build and register your own provider classes |
| **OpenAI-Compatible** | Works with vLLM, LiteLLM, Together AI, and any OpenAI-compatible endpoint |

---

## Installation

```bash
# Core SDK (zero dependencies)
pip install orion-sdk

# Install with provider support
pip install orion-sdk[openai]          # OpenAI GPT / o1 / o3
pip install orion-sdk[anthropic]       # Claude
pip install orion-sdk[google]          # Gemini
pip install orion-sdk[openrouter]      # 100+ models via OpenRouter
pip install orion-sdk[ollama]          # Local models (Ollama)
pip install orion-sdk[all]             # Everything

# From source
pip install git+https://github.com/zalcus/orion-sdk.git
```

---

## Quick Start

### 1. Basic Usage

```python
from orion_sdk import create_client

# Set up a client with OpenRouter (free models available)
client = create_client(
    "openrouter",
    api_key="sk-or-v1-...",  # Get yours at openrouter.ai/keys
)

response = client.complete("What is machine learning?")
print(response.content)
print(f"Model: {response.model}")
print(f"Tokens: {response.usage}")
```

### 2. With System Prompt

```python
response = client.complete(
    "Translate 'Hello, world!' to French.",
    system="You are a professional translator. Be concise.",
    temperature=0.3,
)
print(response.content)
```

### 3. Conversation Mode

```python
from orion_sdk import Message

messages = [
    Message.user("What is 2 + 2?"),
    Message.assistant("4."),
    Message.user("What about 3 + 3?"),
]

response = client.complete(messages=messages)
print(response.content)  # "6."
```

---

## Provider Setup

### OpenAI

```python
from orion_sdk import create_client

client = create_client("openai", api_key="sk-...")

response = client.complete("Hello!", model="gpt-4o")
```

**Install:** `pip install orion-sdk[openai]`
**Get API key:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

**Supported models:** `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo`, `o1`, `o1-mini`, `o1-preview`, `o3-mini`, `o3`

---

### Anthropic (Claude)

```python
from orion_sdk import create_client

client = create_client("anthropic", api_key="sk-ant-...")

response = client.complete("Hello!", model="claude-sonnet-4-20250514")
```

**Install:** `pip install orion-sdk[anthropic]`
**Get API key:** [console.anthropic.com](https://console.anthropic.com/)

**Supported models:** `claude-opus-4-20250514`, `claude-sonnet-4-20250514`, `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`, `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`

---

### Google (Gemini)

```python
from orion_sdk import create_client

client = create_client("google", api_key="AI...")

response = client.complete("Hello!", model="gemini-2.5-pro")
```

**Install:** `pip install orion-sdk[google]`
**Get API key:** [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

**Supported models:** `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-2.0-flash-lite`, `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-1.5-flash-8b`

---

### OpenRouter (100+ Models)

```python
from orion_sdk import create_client

client = create_client("openrouter", api_key="sk-or-v1-...")

# Access any model through one API
response = client.complete("Hello!", model="anthropic/claude-sonnet-4")
```

**Install:** `pip install orion-sdk[openrouter]`
**Get API key:** [openrouter.ai/keys](https://openrouter.ai/keys)

**Supported models (highlights):**
- Anthropic: `claude-opus-4`, `claude-sonnet-4`, `claude-3.5-sonnet`, `claude-3.5-haiku`
- OpenAI: `gpt-4o`, `gpt-4o-mini`, `o1`, `o1-mini`, `o3-mini`
- Google: `gemini-2.5-pro-preview`, `gemini-2.5-flash-preview`, `gemini-2.0-flash-001`
- xAI: `grok-3`, `grok-3-mini`
- Meta: `llama-3.1-405b-instruct`, `llama-3.1-70b-instruct`, `llama-3.1-8b-instruct`
- Mistral: `mistral-large`
- DeepSeek: `deepseek-chat`, `deepseek-r1`
- Qwen: `qwen-2.5-72b-instruct`
- Perplexity: `sonar`

> See all 100+ models at [openrouter.ai/models](https://openrouter.ai/models)

---

### Ollama (Local Models)

```python
from orion_sdk import create_client

# No API key needed — just make sure Ollama is running
client = create_client("ollama")

response = client.complete("Hello!", model="llama3.1")
```

**Install:** `pip install orion-sdk[ollama]`
**Install Ollama:** [ollama.ai](https://ollama.ai)
**Run:** `ollama serve` (then `ollama pull llama3.1`)

**Supported models:** `llama3.1`, `llama3.2`, `llama3.3`, `codellama`, `mistral`, `mistral-nemo`, `qwen2.5`, `qwen2.5-coder`, `deepseek-coder-v2`, `phi3`, `gemma2`, `command-r`, `nous-hermes2`

> Ollama also dynamically lists any models you have pulled locally.

---

## Multi-Provider

Register multiple providers and switch between them freely:

```python
from orion_sdk import OrionClient

client = OrionClient()

# Add all your providers
client.add_provider("openai", api_key="sk-...", set_default=True)
client.add_provider("anthropic", api_key="sk-ant-...")
client.add_provider("google", api_key="AI...")
client.add_provider("ollama")  # No API key needed

# Use any provider by name
response = client.complete("Hello!", provider="anthropic", model="claude-sonnet-4-20250514")
print(response.content)

# Switch to another provider
response = client.complete("Hello!", provider="google", model="gemini-2.5-pro")
print(response.content)

# List all registered providers
print(client.list_providers())  # ['openai', 'anthropic', 'google', 'ollama']
```

---

## Fallback Chains

Set up automatic failover — if one provider fails, Orion tries the next:

```python
from orion_sdk import OrionClient, AllProvidersFailedError

client = OrionClient()

client.add_provider("anthropic", api_key="sk-ant-...")
client.add_provider("openai", api_key="sk-...")
client.add_provider("google", api_key="AI...")

# Priority order: Anthropic → OpenAI → Google
client.set_fallback_chain("anthropic", "openai", "google")

try:
    # Tries Anthropic first, falls back to OpenAI, then Google
    response = client.complete(
        "Write a haiku about AI.",
        model="claude-sonnet-4-20250514",
        use_fallback=True,
    )
    print(response.content)
    print(f"Answered by: {response.provider}")
except AllProvidersFailedError as e:
    print(f"All providers failed:\n{e}")
```

---

## Streaming

Stream responses in real-time from any provider:

```python
from orion_sdk import create_client

client = create_client("openai", api_key="sk-...")

print("Assistant: ", end="", flush=True)
for chunk in client.stream("Tell me a short story about a robot."):
    if chunk.content:
        print(chunk.content, end="", flush=True)
    if chunk.finish_reason:
        print(f"\n\n[Finished: {chunk.finish_reason}]")
```

Works identically with any provider:

```python
# Same streaming interface for all providers
for chunk in client.stream("Hello!", provider="anthropic"):
    print(chunk.content, end="", flush=True)

for chunk in client.stream("Hello!", provider="ollama"):
    print(chunk.content, end="", flush=True)
```

---

## Tool Calling

Define tools and receive structured tool calls from the model:

```python
from orion_sdk import create_client, ToolDefinition, Message

client = create_client("openai", api_key="sk-...")

# Define your tools
tools = [
    ToolDefinition(
        name="get_weather",
        description="Get the current weather for a location",
        parameters={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name, e.g. 'San Francisco'",
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit",
                },
            },
            "required": ["location"],
        },
    ),
]

response = client.complete(
    "What's the weather in Tokyo?",
    tools=tools,
    model="gpt-4o",
)

if response.has_tool_calls:
    for tool_call in response.tool_calls:
        print(f"Tool: {tool_call.name}")
        print(f"Arguments: {tool_call.arguments}")
        # Execute your tool logic here, then send the result back

        # Example: sending the tool result back
        result = {"temperature": 22, "condition": "Sunny"}
        response = client.complete(
            messages=[
                Message.user("What's the weather in Tokyo?"),
                Message.tool(str(result), tool_call_id=tool_call.id),
            ],
            tools=tools,
        )
        print(response.content)
else:
    print(response.content)
```

---

## Token Counting & Context Limits

```python
from orion_sdk import count_tokens, count_messages_tokens, get_context_limit

# Count tokens in text
text = "The quick brown fox jumps over the lazy dog."
print(count_tokens(text))  # 10 (with tiktoken)

# Count tokens in a message list
from orion_sdk import Message
messages = [Message.system("You are helpful."), Message.user("Hello!")]
print(count_messages_tokens(messages))

# Check context limits
print(get_context_limit("gpt-4o"))           # 128000
print(get_context_limit("claude-3.5-sonnet")) # 200000
print(get_context_limit("gemini-2.5-pro"))   # 1048576
```

---

## Rate Limiting

Built-in token-bucket rate limiter to stay within provider limits:

```python
from orion_sdk import OrionClient

client = OrionClient(config={
    "rate_limits": {
        "openai": 60,       # 60 requests/minute
        "anthropic": 40,    # 40 requests/minute
        "google": 30,       # 30 requests/minute
    },
})

client.add_provider("openai", api_key="sk-...")
client.add_provider("anthropic", api_key="sk-ant-...")

# Requests are automatically rate-limited per provider
for i in range(100):
    response = client.complete(f"Say 'hi' number {i}.", provider="openai")
```

---

## OpenAI-Compatible Endpoints

Use any OpenAI-compatible API (vLLM, LiteLLM, Together AI, Groq, etc.):

```python
from orion_sdk import create_client

# vLLM
client = create_client(
    "openai",
    api_key="not-needed",
    base_url="http://localhost:8000/v1",
)

# Together AI
client = create_client(
    "openai",
    api_key="...",
    base_url="https://api.together.xyz/v1",
)
```

---

## Custom Providers

Build and register your own provider:

```python
from orion_sdk import Provider, ProviderConfig, Response, register_provider

class MyProvider(Provider):
    NAME = "custom"
    MODELS = {"my-model-v1": {"context": 32768, "output": 2048}}

    def complete(self, messages, model="", tools=None, temperature=0.7, max_tokens=4096, **kwargs):
        # Your implementation here
        return Response(content="Hello from custom provider!", model=model, provider=self.NAME)

    def stream(self, messages, model="", tools=None, temperature=0.7, max_tokens=4096, **kwargs):
        yield from []

    def list_models(self):
        return [{"id": k, **v} for k, v in self.MODELS.items()]

# Register and use
register_provider("custom", MyProvider)

client = OrionClient()
client.add_provider("custom")
response = client.complete("Hello!")
```

---

## API Reference

### Core Classes

| Class | Description |
|---|---|
| `OrionClient` | Main client — manages providers, completions, streaming, and fallback |
| `create_client(provider, api_key)` | Convenience factory for single-provider setup |
| `Message` | Chat message with roles: `system()`, `user()`, `assistant()`, `tool()` |
| `ToolDefinition` | Tool/function schema for provider APIs |
| `ToolCall` | Tool call returned by the model |
| `Response` | Completion response with `content`, `tool_calls`, `usage`, `model`, `provider` |
| `StreamChunk` | Single streaming chunk with `content`, `finish_reason` |
| `Provider` | Abstract base class — subclass to add a new provider |
| `ProviderConfig` | Provider configuration (API key, base URL, timeout, etc.) |
| `RateLimiter` | Multi-provider token-bucket rate limiter |

### Provider Classes

| Class | Provider |
|---|---|
| `OpenAIProvider` | OpenAI GPT, o1, o3 |
| `AnthropicProvider` | Claude |
| `GoogleProvider` | Gemini |
| `OpenRouterProvider` | 100+ models (extends `OpenAIProvider`) |
| `OllamaProvider` | Local models |

### Functions

| Function | Description |
|---|---|
| `count_tokens(text, model)` | Count tokens for text |
| `count_messages_tokens(messages, model)` | Count tokens for message list |
| `get_context_limit(model)` | Get context window size for a model |
| `register_provider(name, cls)` | Register a custom provider class |
| `list_providers()` | List all registered provider names |

### Exceptions

| Exception | Description |
|---|---|
| `OrionError` | Base exception |
| `ProviderError` | Provider-specific error |
| `ProviderNotFoundError` | Provider not registered |
| `ModelNotFoundError` | Model not available |
| `AuthenticationError` | Invalid/missing API key |
| `RateLimitError` | Rate limit hit |
| `ContextOverflowError` | Input exceeds context window |
| `AllProvidersFailedError` | All fallback providers failed |
| `TimeoutError` | Request timed out |
| `InvalidConfigError` | Invalid configuration |

---

## Provider Support Matrix

| Provider | Models | Streaming | Tool Calling | Rate Limiting | API Key Required |
|---|:---:|:---:|:---:|:---:|:---:|
| **OpenAI** | 10 | ✅ | ✅ | ✅ | ✅ |
| **Anthropic** | 7 | ✅ | ✅ | ✅ | ✅ |
| **Google** | 7 | ✅ | ✅ | ✅ | ✅ |
| **OpenRouter** | 100+ | ✅ | ✅ | ✅ | ✅ |
| **Ollama** | 13+ | ✅ | ✅ | ✅ | ❌ |

---

## Works with Orion V3

Orion SDK is the AI engine built into **Orion V3** by Zalcus. If you're using Orion V3, the SDK is already integrated — you get all these features natively.

Orion V3 adds:
- Visual chat interface
- Conversation history management
- Project-scoped configuration
- Provider health monitoring
- And much more

---

## License

MIT License — see [LICENSE](LICENSE).

Copyright © 2025 Zalcus. All rights reserved.
