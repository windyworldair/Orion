"""
Orion SDK — Multi-Provider Example
===================================
Register multiple providers and switch between them freely.
"""

from orion_sdk import OrionClient

client = OrionClient()

# ── Add your providers ─────────────────────────────────────────────
# Each provider needs its own API key (except Ollama)
client.add_provider("openai", api_key="sk-YOUR_OPENAI_KEY")
client.add_provider("anthropic", api_key="sk-ant-YOUR_ANTHROPIC_KEY")
client.add_provider("google", api_key="AIza-YOUR_GOOGLE_KEY")
client.add_provider("openrouter", api_key="sk-or-v1-YOUR_OPENROUTER_KEY")
client.add_provider("ollama")  # No API key — local only

# ── See what you have ─────────────────────────────────────────────
print("Registered providers:", client.list_providers())
print()

# ── Use any provider by name ──────────────────────────────────────
prompt = "What is 15 * 27?"

# Ask OpenAI
response = client.complete(prompt, provider="openai", model="gpt-4o-mini")
print(f"[OpenAI / gpt-4o-mini] {response.content}")

# Ask Anthropic
response = client.complete(prompt, provider="anthropic", model="claude-3-5-haiku-20241022")
print(f"[Anthropic / claude-3.5-haiku] {response.content}")

# Ask Google
response = client.complete(prompt, provider="google", model="gemini-2.0-flash")
print(f"[Google / gemini-2.0-flash] {response.content}")

# Ask Ollama (local)
# response = client.complete(prompt, provider="ollama", model="llama3.1")
# print(f"[Ollama / llama3.1] {response.content}")

# ── Set a default provider ─────────────────────────────────────────
client.default_provider = "anthropic"

# Now you don't need to specify provider= every time
response = client.complete("Hello, default provider!")
print(f"\n[Default / {client.default_provider}] {response.content}")

# ── List all available models ──────────────────────────────────────
models = client.list_models()
print(f"\nTotal available models: {len(models)}")
for m in models:
    print(f"  - {m['id']} ({m['context']:,} context)")
