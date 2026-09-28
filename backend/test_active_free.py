import httpx
import asyncio

async def test_working_free_models():
    api_key = "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"
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/vickydecodes/ai_resume_simulator",
        "X-Title": "HireFit AI",
        "Content-Type": "application/json"
    }

    models = [
        "inclusionai/ling-3.0-flash-sante:free",
        "dots-studio/dots-3-note-preview:free",
        "liquid/lfm-2.5-2.6b:free",
        "nvidia/nemotron-3.5-lightning:free",
        "thinkingmachines/inkling-small:free"
    ]

    async with httpx.AsyncClient(timeout=25.0) as client:
        for model in models:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "Hello! Reply with 'AI IS WORKING GREAT!'"}],
            }
            print(f"Testing free model: {model}...")
            try:
                res = await client.post(url, headers=headers, json=payload)
                print(f"Status: {res.status_code}")
                if res.status_code == 200:
                    data = res.json()
                    text = data["choices"][0]["message"]["content"]
                    print(f"✅ SUCCESS! Model {model} is LIVE and WORKING!")
                    print(f"Response: {text}\n")
                    return model, text
                else:
                    print(f"Status error: {res.text[:200]}\n")
            except Exception as e:
                print(f"Exception: {e}\n")

if __name__ == "__main__":
    asyncio.run(test_working_free_models())
