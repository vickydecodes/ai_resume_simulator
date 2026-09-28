import asyncio
import os
from app.core.config import settings
from app.core.llm import llm_client

async def test_live_openrouter():
    print("Testing OpenRouter Live API Connection...")
    print(f"Provider: {settings.LLM_PROVIDER}")
    print(f"Model: {settings.LLM_MODEL}")
    print(f"API Key present: {bool(settings.OPENROUTER_API_KEY)}")

    prompt = "Hello! Please confirm you are working and state your name in one sentence."
    response = await llm_client.chat([{"role": "user", "content": prompt}], system_prompt="You are a helpful AI assistant.")
    print("\n--- OPENROUTER RESPONSE ---")
    print(response)
    print("---------------------------\n")

if __name__ == "__main__":
    asyncio.run(test_live_openrouter())
