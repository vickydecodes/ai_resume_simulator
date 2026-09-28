import httpx
import asyncio

async def list_openrouter_models():
    url = "https://openrouter.ai/api/v1/models"
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get(url)
        if res.status_code == 200:
            data = res.json()["data"]
            print(f"Total models available on OpenRouter: {len(data)}")
            
            # Find free models (pricing prompt=0 and completion=0)
            free_models = []
            for m in data:
                pricing = m.get("pricing", {})
                p_prompt = float(pricing.get("prompt", "0"))
                p_comp = float(pricing.get("completion", "0"))
                if p_prompt == 0 and p_comp == 0:
                    free_models.append(m["id"])
            
            print("\nFree models found on OpenRouter:")
            for fm in free_models[:15]:
                print(f" - {fm}")

            # Find Claude models
            claude_models = [m["id"] for m in data if "claude" in m["id"].lower() or "anthropic" in m["id"].lower()]
            print("\nClaude / Anthropic models found on OpenRouter:")
            for cm in claude_models:
                print(f" - {cm}")

if __name__ == "__main__":
    asyncio.run(list_openrouter_models())
