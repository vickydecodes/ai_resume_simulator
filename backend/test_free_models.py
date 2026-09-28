import httpx
import asyncio

async def test_free_models():
    api_key = "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"
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/vickydecodes/ai_resume_simulator",
        "X-Title": "HireFit AI",
        "Content-Type": "application/json"
    }

    free_models = [
        "meta-llama/llama-3.3-70b-instruct:free",
        "google/gemini-2.0-flash-exp:free",
        "deepseek/deepseek-r1:free",
        "qwen/qwen-2.5-coder-32b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "nousresearch/hermes-3-llama-3.1-8b:free"
    ]

    async with httpx.AsyncClient(timeout=20.0) as client:
        for model in free_models:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "Say 'AI IS WORKING!' and state your model name."}],
            }
            print(f"Testing free model: {model}...")
            try:
                res = await client.post(url, headers=headers, json=payload)
                print(f"Status: {res.status_code}")
                if res.status_code == 200:
                    data = res.json()
                    text = data["choices"][0]["message"]["content"]
                    print(f"✅ WORKING! Model: {model}")
                    print(f"Response: {text}\n")
                    return model, text
                else:
                    print(f"Error body: {res.text[:200]}\n")
            except Exception as e:
                print(f"Exception: {e}\n")

if __name__ == "__main__":
    asyncio.run(test_free_models())
