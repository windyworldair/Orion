"""
Orion SDK — Quick Start Example
================================
Send your first completion in 3 lines.

Get a free OpenRouter API key at https://openrouter.ai/keys
"""

from orion_sdk import create_client

# ── Set up the client ──────────────────────────────────────────────
# Using OpenRouter so you can access 100+ models with one key
client = create_client(
    "openrouter",
    api_key="sk-or-v1-YOUR_KEY_HERE",  # Replace with your key
    model="meta-llama/llama-3.1-8b-instruct",  # Free model on OpenRouter
)

# ── Simple completion ──────────────────────────────────────────────
response = client.complete("Explain quantum computing in one sentence.")
print("Answer:", response.content)
print("Model:", response.model)
print("Provider:", response.provider)
print("Usage:", response.usage)
print()

# ── With a system prompt ──────────────────────────────────────────
response = client.complete(
    "Translate 'Good morning' to Japanese.",
    system="You are a professional translator. Reply with only the translation.",
    temperature=0.1,
)
print("Translation:", response.content)
print()

# ── Conversation mode ─────────────────────────────────────────────
from orion_sdk import Message

messages = [
    Message.user("My favorite color is blue."),
    Message.assistant("Blue is a great color! It's calming and versatile."),
    Message.user("What's my favorite color?"),
]
response = client.complete(messages=messages)
print("Memory test:", response.content)
