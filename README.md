<div align="center">
  <img src="orion_logo.png" alt="Orion SDK" width="50"/>

# 🌟 Orion SDK

### **Unified AI Provider Interface — One API to Rule Them All**

<p>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/status-beta-yellow?style=for-the-badge" alt="Status"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License"/>
  <img src="https://img.shields.io/badge/version-0.1.0-blue?style=for-the-badge" alt="Version"/>
  <img src="https://img.shields.io/badge/providers-5-purple?style=for-the-badge" alt="Providers"/>
  <img src="https://img.shields.io/badge/models-150+-orange?style=for-the-badge" alt="Models"/>
  <img src="https://img.shields.io/badge/streaming-yes-brightgreen?style=for-the-badge" alt="Streaming"/>
</p>

<p>
  <a href="https://github.com/windyworldair/Orion"><img src="https://img.shields.io/badge/GitHub-windyworldair/Orion-181717?style=flat-square&logo=github" alt="GitHub"/></a>
  <a href="https://github.com/windyworldair/Orion/issues"><img src="https://img.shields.io/github/issues/windyworldair/Orion?style=flat-square&color=red" alt="Issues"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License"/></a>
</p>

<p>
  <img src="https://img.shields.io/badge/OpenAI-GPT--4o%20%7C%20o1%20%7C%20o3-412991?style=flat-square&logo=openai"/>
  <img src="https://img.shields.io/badge/Anthropic-Claude%20Opus%204%20%7C%20Sonnet%204-D4A574?style=flat-square&logo=anthropic"/>
  <img src="https://img.shields.io/badge/Google-Gemini%202.5%20Pro%20%7C%20Flash-4285F4?style=flat-square&logo=google"/>
  <img src="https://img.shields.io/badge/OpenRouter-21%2B%20models-7C3AED?style=flat-square"/>
  <img src="https://img.shields.io/badge/Ollama-Local%20Models-3E8C72?style=flat-square"/>
</p>

**Stop juggling 5 different SDKs. Start building with one.**

[📚 Documentation](#documentation) • [🚀 Quick Start](#quick-start) • [💡 Examples](#examples) • [🤝 Contributing](#contributing) • [⭐ Support](#-support)

</div>

---

## 📑 Table of Contents

- [Why Orion SDK?](#-why-orion-sdk)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Supported Providers](#-supported-providers)
- [API Reference](#-api-reference)
- [Examples](#-examples)
- [Installation](#-installation)
- [Advanced Usage](#-advanced-usage)
- [Error Handling](#-error-handling)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Why Orion SDK?

Every major AI platform ships its own client library. OpenAI has `openai`, Anthropic has `anthropic`, Google has `google-generativeai`. Orion gives you the same thing — but **unified**.

Instead of juggling 5 different SDKs with 5 different APIs, different error formats, and different tool-calling conventions, you get **one package, one interface, one `complete()` call**.

```python
from orion_sdk import OrionClient

client = OrionClient()
client.add_provider("anthropic", api_key="sk-ant-...")
client.add_provider("openai",   api_key="sk-...")

response = client.complete("Hello, world!")
print(response.content)
```

**That's it.** No provider lock-in, no API format memorization, no 300-page docs.

> [!TIP]
> Use provider aliases to save keystrokes — `"claude"` instead of `"anthropic"`, `"gpt"` instead of `"openai"`, `"local"` instead of `"ollama"`. See the full alias list [below](#provider-aliases).

---

## ✨ Features

- **🔀 5 providers, one API** — OpenAI, Anthropic, Google, OpenRouter, Ollama
- **⛓️ Automatic fallback chains** — provider A fails? Try B, then C, automatically
- **🌊 Streaming support** — async iterator of chunks for real-time output
- **🛠️ Tool/function calling** — unified format, auto-converts between provider schemas
- **⚡ Token counting** — tiktoken when available, smart estimation otherwise
- **📏 Context window validation** — catches overflow before it hits the API
- **🚦 Rate limiting** — per-provider token bucket with configurable RPM
- **🔒 Zero lock-in** — swap providers by changing one string, not your codebase
- **🧩 Custom providers** — subclass `Provider` and register it
- **💾 Message history** — Built-in conversation context management

---

## 🚀 Quick Start

> [!NOTE]
> You only need `pip install orion_sdk` for the core. Provider packages (`openai`, `anthropic`, `google-generativeai`) are optional — install only the ones you actually use.

### Install from Source (PyPI coming soon in 2026)

```bash
git clone https://github.com/windyworldair/Orion.git
cd Orion
pip install -e .
```

> [!IMPORTANT]
> **PyPI coming in 2026!** Once released, you'll use `pip install orion-sdk`. For now, clone from GitHub or wait for the official release.

### One-liner

```python
from orion_sdk import create_client

client = create_client("anthropic", api_key="sk-ant-...")
response = client.complete("What is 2 + 2?")
print(response.content)  # "4"
```

> [!IMPORTANT]
> Never hardcode API keys in your code. Use environment variables — Orion SDK automatically picks up `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, and `OPENROUTER_API_KEY` from your environment.

### Multi-provider with fallback

```python
from orion_sdk import OrionClient

client = OrionClient()
client.add_provider("anthropic", api_key="sk-ant-...")
client.add_provider("openai",   api_key="sk-...")
client.add_provider("google",   api_key="...")

# Try Anthropic → OpenAI → Google automatically
client.set_fallback_chain("anthropic", "openai", "google")

response = client.complete("Write a Python HTTP server")
print(response.content)
print(response.model)       # "claude-sonnet-4-20250514"
print(response.provider)     # "anthropic"
print(response.usage)        # {"prompt_tokens": 42, "completion_tokens": 187}
```

### Streaming

```python
from orion_sdk import OrionClient

client = OrionClient()
client.add_provider("openai", api_key="sk-...", set_default=True)

for chunk in client.stream("Tell me a story"):
    print(chunk.content, end="", flush=True)
```

### Tool calling

```python
from orion_sdk import OrionClient, ToolDefinition

client = OrionClient()
client.add_provider("anthropic", api_key="sk-ant-...")

tools = [
    ToolDefinition(
        name="get_weather",
        description="Get the current weather for a city",
        parameters={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["city"]
        }
    )
]

response = client.complete("What's the weather in Tokyo?", tools=tools)

if response.has_tool_calls:
    for call in response.tool_calls:
        print(f"Call: {call.name}({call.arguments})")
        # {"city": "Tokyo", "unit": "celsius"}
```

---

## 📊 Supported Providers

| Provider | Package | Models | API Key |
|----------|---------|--------|---------|
| **OpenAI** | `openai` | GPT-4o, o1, o3, GPT-4o-mini, GPT-4-turbo | `OPENAI_API_KEY` |
| **Anthropic** | `anthropic` | Claude Opus 4, Claude Sonnet 4, Claude 3.5, Claude 3 | `ANTHROPIC_API_KEY` |
| **Google** | `google-generativeai` | Gemini 2.5 Pro, Gemini 2.5 Flash, Gemini 2.0, Gemini 1.5 | `GEMINI_API_KEY` |
| **OpenRouter** | `openai` | 21+ models (Claude, GPT, Gemini, Grok, Llama, DeepSeek, Qwen...) | `OPENROUTER_API_KEY` |
| **Ollama** | `requests` | Llama 3.3, Mistral, Qwen 2.5, CodeLlama, Phi3, Gemma2... | *None — fully local* |

### Provider Aliases

```python
# These all work
client.add_provider("claude",   ...)  # → anthropic
client.add_provider("gpt",     ...)  # → openai
client.add_provider("gemini",  ...)  # → google
client.add_provider("local",   ...)  # → ollama
```

> [!TIP]
> Aliases also work in `complete()` and `stream()` — just pass `model="claude-opus-4"` and Orion resolves the provider automatically.

---

## 📚 API Reference

### `OrionClient`

```python
client = OrionClient(config={
    "default_provider": "anthropic",
    "default_model": "claude-sonnet-4-20250514",
    "timeout": 120.0,
    "max_retries": 3,
    "rate_limits": {"anthropic": 60, "openai": 120}
})
```

| Method | Description |
|--------|-------------|
| `add_provider(name, api_key, ...)` | Register a provider |
| `remove_provider(name)` | Remove a registered provider |
| `set_fallback_chain(*providers)` | Set failover priority |
| `complete(prompt, ...)` | Synchronous completion |
| `stream(prompt, ...)` | Streaming completion (async iterator) |
| `count_tokens(text, model)` | Count tokens |
| `count_messages_tokens(messages, model)` | Count tokens for a message list |
| `get_context_limit(model)` | Get model's context window size |
| `list_providers()` | List registered providers |
| `list_models(provider)` | List available models |
| `register_custom_provider(name, cls)` | Register a custom provider class |

### Data Types

```python
# Message
msg = Message.user("Hello!")
msg = Message.system("You are helpful.")
msg.to_dict()  # {"role": "user", "content": "Hello!"}

# Response
response.content        # str
response.tool_calls      # list[ToolCall]
response.model           # str
response.provider         # str
response.usage           # {"prompt_tokens": ..., "completion_tokens": ...}
response.has_tool_calls  # bool

# StreamChunk
chunk.content        # str
chunk.finish_reason   # str | None
chunk.model           # str

# ToolDefinition — auto-converts to provider formats
tool.to_openai()       # OpenAI schema
tool.to_anthropic()    # Anthropic schema
tool.to_gemini_tools() # Gemini schema
```

### Exceptions

```python
from orion_sdk import (
    OrionError,                # Base exception
    ProviderError,             # Error from a specific provider
    ProviderNotFoundError,     # Provider not registered
    AuthenticationError,       # Invalid API key
    RateLimitError,            # Rate limit hit
    ContextOverflowError,      # Input exceeds context window
    AllProvidersFailedError,   # All fallback providers failed
    TimeoutError,              # Request timed out
    InvalidConfigError,        # Bad configuration
)

try:
    response = client.complete(prompt)
except ContextOverflowError as e:
    print(f"Too many tokens: {e.tokens} > {e.limit}")
except AllProvidersFailedError as e:
    print(f"All failed:\n{e.errors}")
```

### Rate Limiting

```python
from orion_sdk import OrionClient, RateLimiter

client = OrionClient()
client.add_provider("anthropic", api_key="sk-ant-...")
client.add_provider("openai",   api_key="sk-...")

# Built-in rate limiter (default 60 req/min per provider)
# Or configure at init:
client = OrionClient(config={
    "rate_limits": {"anthropic": 50, "openai": 100}
})
```

---

## 💡 Examples

### Example 1: Hello World

```python
from orion_sdk import OrionClient, AllProvidersFailedError

client = OrionClient()
client.add_provider("anthropic", api_key="sk-ant-...")
client.add_provider("openai", api_key="sk-...")
client.set_fallback_chain("anthropic", "openai")

try:
    response = client.complete("Explain quantum computing in 100 words")
    print(f"✅ Response from {response.provider}:")
    print(f"   {response.content}")
except AllProvidersFailedError as e:
    print(f"❌ All providers failed: {e}")
```

### Example 2: Token Counting & Cost

```python
from orion_sdk import OrionClient

client = OrionClient()
client.add_provider("anthropic", api_key="sk-ant-...")

model = "claude-opus-4-20250514"
tokens = client.count_tokens("Hello world", model=model)
limit = client.get_context_limit(model)

print(f"Tokens: {tokens}, Limit: {limit}")

if tokens > limit:
    print("❌ Input too long!")
else:
    response = client.complete("Hello world", model=model)
    print(f"Cost estimate: ${response.cost_estimate:.4f}")
```

### Example 3: Tool Calling

```python
from orion_sdk import OrionClient, ToolDefinition

client = OrionClient()
client.add_provider("anthropic", api_key="sk-ant-...")

tools = [
    ToolDefinition(
        name="weather",
        description="Get weather",
        parameters={
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        }
    )
]

response = client.complete("What's the weather in Tokyo?", tools=tools)

for call in response.tool_calls:
    print(f"Tool: {call.name}, Args: {call.arguments}")
```

### Example 4: Multi-Provider Comparison

```python
from orion_sdk import OrionClient

client = OrionClient()
client.add_provider("anthropic", api_key="sk-ant-...")
client.add_provider("openai", api_key="sk-...")

for provider in ["anthropic", "openai"]:
    response = client.complete("2+2=?", model=provider)
    print(f"{provider}: {response.content}")
```

### Example 5: Streaming Response

```python
from orion_sdk import OrionClient

client = OrionClient()
client.add_provider("openai", api_key="sk-...", set_default=True)

for chunk in client.stream("Write a haiku"):
    print(chunk.content, end="", flush=True)
```

### Example 6: Handling Context Overflow

```python
from orion_sdk import OrionClient, ContextOverflowError

client = OrionClient()
client.add_provider("anthropic", api_key="sk-ant-...")

try:
    huge_text = "x" * 1000000
    response = client.complete(huge_text)
except ContextOverflowError as e:
    print(f"❌ {e.tokens} tokens > {e.limit} limit")
    print("💡 Solution: Split input or use larger model")
```

### Example 7: Custom Provider

```python
from orion_sdk import OrionClient, Provider, ProviderConfig, Response
from orion_sdk.providers.base import StreamChunk

class MockProvider(Provider):
    NAME = "mock"
    MODELS = {"mock": {"context": 4096, "output": 1024}}

    def complete(self, messages, model="", **kwargs):
        return Response(
            content="Mock response",
            model=model,
            provider=self.NAME,
            usage={"prompt_tokens": 10, "completion_tokens": 5}
        )

    def stream(self, messages, model="", **kwargs):
        yield StreamChunk(content="Mock", model=model, finish_reason="stop")

    def list_models(self):
        return [{"id": m} for m in self.MODELS.keys()]

client = OrionClient()
client.register_custom_provider("mock", MockProvider)
client.add_provider("mock", api_key="test")
response = client.complete("Test")
```

### Example 8: Multi-Turn Conversation

```python
from orion_sdk import OrionClient, Message

client = OrionClient()
client.add_provider("anthropic", api_key="sk-ant-...")

messages = [
    Message.system("You are a Python expert"),
    Message.user("How do I reverse a list?"),
]

response = client.complete(messages=messages)
messages.append(Message.assistant(response.content))

messages.append(Message.user("What about strings?"))
response = client.complete(messages=messages)
print(response.content)
```

### Example 9: Rate Limit Handling

```python
from orion_sdk import OrionClient, RateLimitError
import time

client = OrionClient(config={"rate_limits": {"openai": 3}})
client.add_provider("openai", api_key="sk-...")

for i in range(5):
    try:
        print(f"Request {i+1}...")
        response = client.complete("Hello")
        print("✅ Success")
    except RateLimitError as e:
        print(f"⏳ Rate limited, retry in {e.retry_after}s")
        time.sleep(e.retry_after)
```

### Example 10: Environment Variable Config

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."
```

```python
from orion_sdk import OrionClient

# No API keys needed — reads from environment!
client = OrionClient()
client.add_provider("anthropic")
client.add_provider("openai")
client.add_provider("google")

response = client.complete("Hello!")
```

---

## 📦 Installation

### From Source (Recommended for now)

```bash
git clone https://github.com/windyworldair/Orion.git
cd Orion
pip install -e .
```

> [!NOTE]
> You only need the core package. Provider dependencies are optional and installed on-demand.

### With Specific Providers

```bash
# Just Anthropic
pip install -e ".[anthropic]"

# Anthropic + OpenAI
pip install -e ".[anthropic,openai]"

# All providers
pip install -e ".[all]"

# Development
pip install -e ".[dev]"
```

### Verify Installation

```python
from orion_sdk import OrionClient, __version__

print(f"Orion SDK {__version__} installed!")
client = OrionClient()
print(f"Ready to use!")
```

> [!CAUTION]
> Installing from source requires `git` and `pip`. Make sure you have both installed before proceeding.

---

## 🎯 Advanced Usage

### Rate Limiting Deep Dive

```python
from orion_sdk import OrionClient

client = OrionClient(config={
    "rate_limits": {
        "anthropic": 30,      # 30 requests/min
        "openai": 60,         # 60 requests/min
        "google": 20,         # 20 requests/min
    }
})

# Requests are automatically queued if rate limit hit
response = client.complete("Important request")
```

> [!TIP]
> Adjust rate limits based on your API plan. Check provider dashboards for your current limits.

### Context Window Validation

```python
from orion_sdk import OrionClient, ContextOverflowError

client = OrionClient()
client.add_provider("anthropic", api_key="sk-ant-...")

model = "claude-opus-4-20250514"
limit = client.get_context_limit(model)  # 200,000

# Prevents wasting tokens on failed requests
huge_text = "x" * 500000

try:
    response = client.complete(huge_text)
except ContextOverflowError as e:
    print(f"❌ {e.tokens} > {e.limit}")
    print("💡 Solution: Use streaming, split input, or summarize")
```

> [!WARNING]
> Context limits are checked **before** API calls. Exceeding them raises an error immediately — no tokens wasted.

### Token Caching

```python
from orion_sdk import OrionClient

client = OrionClient(config={
    "enable_cache": True,
    "cache_ttl": 3600  # 1 hour
})

# First call — counts tokens, caches result
tokens1 = client.count_tokens("Hello world", model="claude-opus-4")

# Second call — instant (from cache)
tokens2 = client.count_tokens("Hello world", model="claude-opus-4")
```

> [!NOTE]
> Caching improves performance for repeated token counts. Cache expires after TTL (time-to-live).

### Provider-Specific Configuration

```python
from orion_sdk import OrionClient

client = OrionClient()

# OpenAI settings
client.add_provider("openai", api_key="sk-...", organization="my-org")

# Anthropic settings
client.add_provider("anthropic", api_key="sk-ant-...", max_retries=5)

# Google settings
client.add_provider("google", api_key="...", timeout=30)

# Ollama settings
client.add_provider("ollama", base_url="http://localhost:11434")
```

> [!IMPORTANT]
> Each provider can have different configuration. Set them appropriately for your use case.

---

## 🚨 Error Handling

### Common Errors

```python
from orion_sdk import (
    OrionError,
    ContextOverflowError,
    RateLimitError,
    AllProvidersFailedError,
    AuthenticationError
)

try:
    response = client.complete("Hello")
    
except AuthenticationError as e:
    print(f"❌ Auth failed: {e}")
    print("💡 Check your API key and environment")
    
except ContextOverflowError as e:
    print(f"❌ Input too long: {e.tokens} > {e.limit}")
    
except RateLimitError as e:
    print(f"⏳ Rate limited, retry after {e.retry_after}s")
    
except AllProvidersFailedError as e:
    print(f"❌ All providers failed:")
    for provider, error in e.errors.items():
        print(f"   {provider}: {error}")
        
except OrionError as e:
    print(f"❌ General error: {e}")
```

> [!CAUTION]
> Always catch `AllProvidersFailedError` when using fallback chains — it means all options have failed.

### Graceful Degradation

```python
from orion_sdk import OrionClient, AllProvidersFailedError

client = OrionClient()
client.add_provider("anthropic", api_key="sk-ant-...")
client.add_provider("openai", api_key="sk-...")
client.set_fallback_chain("anthropic", "openai")

try:
    response = client.complete("Important request")
except AllProvidersFailedError as e:
    print("⚠️  All providers down, using fallback")
    response = get_cached_response()  # Your fallback logic
```

---

## 🔧 Troubleshooting

### Issue: "Provider not found"

```python
from orion_sdk import ProviderNotFoundError

try:
    response = client.complete("Hello")
except ProviderNotFoundError as e:
    print(f"Error: {e}")
    print(f"Available: {client.list_providers()}")
```

**Solution:** Use `add_provider()` before making requests

```python
client.add_provider("anthropic", api_key="sk-ant-...")
```

### Issue: "Invalid API key"

**Solution:** 
1. Check your API key is correct
2. Use environment variables instead:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

> [!IMPORTANT]
> Never hardcode API keys. Use environment variables or .env files (ignored by git).

### Issue: "Rate limit exceeded"

**Solution:** Increase rate limit or use fallback chains

```python
client = OrionClient(config={
    "rate_limits": {"anthropic": 120}  # Higher limit
})
```

### Issue: "Context overflow"

**Solution:** Use larger model, split input, or summarize first

```python
# Use model with bigger context
response = client.complete(text, model="claude-opus-4")  # 200K tokens
```

### Issue: "Timeout"

**Solution:** Increase timeout or use streaming

```python
client = OrionClient(config={"timeout": 300})  # 5 minutes
```

> [!NOTE]
> Timeouts are often temporary. Retry with exponential backoff.

---

## ❓ FAQ

<details>
<summary><b>Q: When will this be on PyPI?</b></summary>

**A:** PyPI release is coming in 2026! For now, install from GitHub:
```bash
git clone https://github.com/windyworldair/Orion.git
cd Orion
pip install -e .
```

</details>

<details>
<summary><b>Q: Is this production-ready?</b></summary>

**A:** We're in **Beta**. The core is solid, but we're actively improving. We recommend:
- Setting up error handling
- Using fallback chains
- Monitoring token usage
- Testing with your use case

</details>

<details>
<summary><b>Q: What if all fallback providers fail?</b></summary>

**A:** Orion raises `AllProvidersFailedError` with details on each failure:

```python
from orion_sdk import AllProvidersFailedError

try:
    response = client.complete("Hello")
except AllProvidersFailedError as e:
    for provider, error in e.errors.items():
        print(f"{provider}: {error}")
```

</details>

<details>
<summary><b>Q: Can I use Orion offline?</b></summary>

**A:** Yes! Use Ollama for completely local inference:

```python
client.add_provider("ollama", base_url="http://localhost:11434")
response = client.complete("Hello")  # No internet needed
```

</details>

<details>
<summary><b>Q: Does Orion cache responses?</b></summary>

**A:** Token counts are cached automatically. Response caching coming in v1.1.

</details>

<details>
<summary><b>Q: What about async/await support?</b></summary>

**A:** Coming in v1.1! Streaming provides similar benefits for long requests.

</details>

<details>
<summary><b>Q: How do I report bugs?</b></summary>

**A:** Open an issue on [GitHub](https://github.com/windyworldair/Orion/issues) with:
- What you were doing
- What happened
- Error message
- Python version and OS
- Minimal code to reproduce

> [!NOTE]
> Include as much detail as possible for faster resolution.

</details>

<details>
<summary><b>Q: Can I contribute?</b></summary>

**A:** Absolutely! See [Contributing](#-contributing) section.

</details>

---

## 🏗️ Architecture

### File Structure

```
orion_sdk/
├── __init__.py              # Public API
├── client.py                # OrionClient main class
├── exceptions.py            # 9 exception types
├── ratelimit.py             # Rate limiter
├── tokens.py                # Token counting
└── providers/
    ├── __init__.py          # Registry
    ├── base.py              # Abstract base (✅ Fixed typo: anthropic.py)
    ├── openai.py            # OpenAI
    ├── anthropic.py         # Anthropic Claude
    ├── google.py            # Google Gemini
    ├── openrouter.py        # OpenRouter
    └── ollama.py            # Ollama local
```

### Request Flow

```
Input Prompt
    ↓
Validate Config
    ↓
Count Tokens
    ↓
Check Context Limit ← ContextOverflowError if exceeded
    ↓
Apply Rate Limiter
    ↓
Send to Primary Provider
    ↓
Success? → Return Response
    ↓
No → Try Fallback Provider
    ↓
Success? → Return Response
    ↓
No → Raise AllProvidersFailedError
```

---

## 🧪 Testing

### Run Tests

```bash
pip install -e ".[dev]"
pytest
```

> [!NOTE]
> Tests require mock providers to avoid actual API calls. Contribute tests for new features!

---

## 🤝 Contributing

We love contributions! Here's how:

```bash
# Clone
git clone https://github.com/windyworldair/Orion.git
cd Orion

# Create branch
git checkout -b feature/amazing-thing

# Install dev tools
pip install -e ".[dev]"

# Make changes and test
pytest

# Commit
git commit -m "Add amazing feature"

# Push
git push origin feature/amazing-thing
```

### Areas We Need Help

- ✅ **Tests** — Unit tests for providers
- ✅ **Documentation** — Examples, tutorials
- ✅ **Bug fixes** — Help squash bugs
- ✅ **Features** — Implement ideas
- ✅ **Performance** — Optimize code

> [!IMPORTANT]
> Follow PEP 8, add type hints, and write tests for new features.

---

## 📄 License

MIT License — Use freely for any purpose

See [LICENSE](./LICENSE) for full text.

---

## 🙏 Support

**Questions? Issues? Ideas?**

- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/windyworldair/Orion/issues)
- ⭐ **Show Support:** Star the repo!

> [!TIP]
> For fastest response, include detailed error messages and minimal reproduction code.

---

## ⭐ Show Your Support

If you find Orion SDK useful:

1. ⭐ **Star this repo** — Help others discover us
2. 📢 **Share with others** — Tell your network
3. 💬 **Give feedback** — Tell us what works
4. 🐛 **Report bugs** — Help us improve
5. 🤝 **Contribute** — Send pull requests

---

<div align="center">

Built with ❤️ by [Windyworld](https://github.com/windyworldair)

[GitHub](https://github.com/windyworldair/Orion) • [Issues](https://github.com/windyworldair/Orion/issues) • 

© 2026 Windyworld. MIT License.

</div>
