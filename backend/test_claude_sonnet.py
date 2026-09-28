import httpx
import asyncio

async def test_target_models():
    api_key = "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"
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/vickydecodes/ai_resume_simulator",
        "X-Title": "HireFit AI",
        "Content-Type": "application/json"
    }

    test_models = [
        "anthropic/claude-sonnet-5",
        "qwen/qwen3.8-27b:free",
        "nvidia/nemotron-3.5-lightning:free"
    ]

    async with httpx.AsyncClient(timeout=20.0) as client:
        for model in test_models:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "Say 'AI IS WORKING GREAT!' and introduce yourself in one sentence."}],
            }
            print(f"\n--- Testing Model: {model} ---")
            res = await client.post(url, headers=headers, json=payload)
            print(f"Status: {res.status_code}")
            if res.status_code == 200:
                text = res.json()["choices"][0]["message"]["content"]
                print(f"🎉 SUCCESS! Response from {model}:\n{text}")
                return model, text
            else:
                print(f"Error output: {res.text}")

if __name__ == "__main__":
    asyncio.run(test_target_models())
