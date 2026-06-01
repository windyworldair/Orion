"""
Orion SDK — Streaming Example
================================
Stream responses in real-time from any provider.
"""

from orion_sdk import create_client

# ── Set up client (works with any provider) ───────────────────────
client = create_client("openai", api_key="sk-YOUR_OPENAI_KEY")

# ── Basic streaming ───────────────────────────────────────────────
print("=== Basic Streaming ===")
print("Assistant: ", end="", flush=True)

for chunk in client.stream(
    "Tell me a very short story (2-3 sentences) about a robot learning to paint.",
    model="gpt-4o-mini",
):
    if chunk.content:
        print(chunk.content, end="", flush=True)
    if chunk.finish_reason:
        print(f"\n[Finished: {chunk.finish_reason}]")

print()

# ── Streaming with a system prompt ────────────────────────────────
print("\n=== Streaming with System Prompt ===")
print("Assistant: ", end="", flush=True)

for chunk in client.stream(
    "Explain recursion to a 5-year-old.",
    system="You speak like a friendly pirate. Keep it very short.",
    temperature=0.8,
):
    if chunk.content:
        print(chunk.content, end="", flush=True)

print("\n")

# ── Streaming from a different provider (same interface) ──────────
# Just change the provider name — the streaming code stays identical
# client = create_client("anthropic", api_key="sk-ant-YOUR_KEY")
# for chunk in client.stream("Tell me a joke.", model="claude-3-5-haiku-20241022"):
#     print(chunk.content, end="", flush=True)

# ── Collect streaming into a full response ────────────────────────
print("=== Collect Stream into String ===")

full_response = ""
for chunk in client.stream("What is the capital of France? Be very brief."):
    if chunk.content:
        full_response += chunk.content

print(f"Full response: {full_response}")
