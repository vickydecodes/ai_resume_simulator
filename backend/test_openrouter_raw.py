import httpx
import asyncio

async def test_openrouter_raw():
    api_key = "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"
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/vickydecodes/ai_resume_simulator",
        "X-Title": "HireFit AI",
        "Content-Type": "application/json"
    }

    models_to_test = [
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3-5-sonnet-20241022",
        "anthropic/claude-3.5-sonnet:beta",
        "openai/gpt-4o-mini",
        "google/gemini-flash-1.5"
    ]

    async with httpx.AsyncClient(timeout=15.0) as client:
        for model in models_to_test:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "Say 'AI IS WORKING!' and state your model name."}],
            }
            print(f"Testing model: {model}...")
            res = await client.post(url, headers=headers, json=payload)
            print(f"Status: {res.status_code}")
            if res.status_code == 200:
                data = res.json()
                text = data["choices"][0]["message"]["content"]
                print(f"SUCCESS! Response: {text}\n")
                return model, text
            else:
                print(f"Error body: {res.text}\n")

if __name__ == "__main__":
    asyncio.run(test_openrouter_raw())
