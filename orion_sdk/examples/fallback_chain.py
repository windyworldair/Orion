"""
Orion SDK — Fallback Chain Example
====================================
Set up automatic failover: if one provider fails, try the next.
"""

from orion_sdk import OrionClient, AllProvidersFailedError

client = OrionClient()

# ── Register providers ────────────────────────────────────────────
client.add_provider("anthropic", api_key="sk-ant-YOUR_ANTHROPIC_KEY")
client.add_provider("openai", api_key="sk-YOUR_OPENAI_KEY")
client.add_provider("google", api_key="AIza-YOUR_GOOGLE_KEY")

# ── Set the fallback chain ────────────────────────────────────────
# Priority: Anthropic → OpenAI → Google
client.set_fallback_chain("anthropic", "openai", "google")

print("Fallback chain:", client._fallback_chain)
print()

# ── Send a request with automatic failover ────────────────────────
try:
    response = client.complete(
        "Write a haiku about artificial intelligence.",
        model="claude-sonnet-4-20250514",  # Preferred model
        use_fallback=True,  # Enabled by default
    )
    print(f"Response from {response.provider}:")
    print(response.content)
    print()

    if response.provider != "anthropic":
        print("(Note: Anthropic was unavailable, fell back to another provider)")

except AllProvidersFailedError as e:
    print(f"All providers failed:\n{e}")

# ── Without fallback ──────────────────────────────────────────────
# Set use_fallback=False to raise immediately on error
try:
    response = client.complete(
        "Hello!",
        provider="openai",
        use_fallback=False,
    )
    print(response.content)
except Exception as e:
    print(f"Error (no fallback): {e}")

# ── Fallback with different models per provider ───────────────────
# You can also set up a simple retry loop with different models
providers_and_models = [
    ("anthropic", "claude-3-5-haiku-20241022"),
    ("openai", "gpt-4o-mini"),
    ("google", "gemini-2.0-flash"),
]

for prov, mod in providers_and_models:
    try:
        response = client.complete(
            "Say 'hello' in one word.",
            provider=prov,
            model=mod,
            use_fallback=False,
        )
        print(f"[{prov}/{mod}] {response.content}")
        break
    except Exception as e:
        print(f"[{prov}] Failed: {e}")
