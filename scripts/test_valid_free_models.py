#!/usr/bin/env python3
"""
Test Valid Free Models from OpenRouter and Embed in .env
--------------------------------------------------------
Fetches currently active free models (:free) from OpenRouter API,
tests them with a lightweight prompt using the configured OPENROUTER_API_KEY,
and automatically updates LLM_MODEL in backend/.env.
"""

import os
import sys
import re
import argparse
from pathlib import Path
import httpx

def find_env_path() -> Path:
    """Locate the backend/.env file relative to this script or repo root."""
    possible_paths = [
        Path(__file__).resolve().parent.parent / "backend" / ".env",
        Path(__file__).resolve().parent / "backend" / ".env",
        Path.cwd() / "backend" / ".env",
        Path.cwd() / ".env"
    ]
    for p in possible_paths:
        if p.exists():
            return p
    # Default fallback
    return Path(__file__).resolve().parent.parent / "backend" / ".env"

def read_env_file(env_path: Path) -> dict:
    """Parse key-value pairs from .env."""
    env_vars = {}
    if not env_path.exists():
        return env_vars
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip().strip('"').strip("'")
    return env_vars

def update_env_variable(env_path: Path, key: str, value: str) -> None:
    """Update or insert a key-value in .env while preserving formatting and comments."""
    if not env_path.exists():
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")
        return

    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    found = False
    new_lines = []
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*=")

    for line in lines:
        if pattern.match(line):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines.append("\n")
        new_lines.append(f"{key}={value}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

def fetch_openrouter_free_models() -> list:
    """Retrieve all models ending with ':free' from OpenRouter API."""
    url = "https://openrouter.ai/api/v1/models"
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                models = [m["id"] for m in data.get("data", []) if ":free" in m.get("id", "")]
                return models
    except Exception as e:
        print(f"[!] Warning: Failed to fetch live models from OpenRouter: {e}")

    # Fallback to curated known free models
    return [
        "google/gemma-4-31b-it:free",
        "google/gemma-4-26b-a4b-it:free",
        "nvidia/nemotron-3.5-lightning:free",
        "liquid/lfm-2.5-2.6b:free",
        "cohere/north-mini-code:free",
        "dots-studio/dots-3-note-preview:free",
        "thinkingmachines/inkling:free",
        "poolside/laguna-s-2.1:free"
    ]

def filter_and_prioritize_models(models: list) -> list:
    """Filter out non-text/safety models and prioritize fast general instruct/chat models."""
    avoid_keywords = ["content-safety", "moderation", "embed", "vision-only"]
    filtered = [m for m in models if not any(k in m.lower() for k in avoid_keywords)]

    # Prioritize popular and coding/instruct free models first
    def priority_score(m: str) -> int:
        m_lower = m.lower()
        if "nemotron" in m_lower or "gemma" in m_lower or "llama" in m_lower:
            return 0
        if "code" in m_lower or "flash" in m_lower or "mini" in m_lower:
            return 1
        return 2

    filtered.sort(key=priority_score)
    return filtered

def test_model(api_key: str, model_id: str) -> tuple:
    """Send a lightweight test completion request to verify model viability. Returns (success, is_auth_error)."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/vickydecodes/ai_resume_simulator",
        "X-Title": "HireFit AI Model Tester",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": "Respond with the single word: OK"}
        ],
        "max_tokens": 10,
        "temperature": 0.0
    }

    try:
        with httpx.Client(timeout=8.0) as client:
            res = client.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                data = res.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    return (True, False)
            elif res.status_code == 401:
                print(f"[!] Authentication Error (401): OpenRouter API key is invalid or unauthorized.")
                return (False, True)
            else:
                print(f"    [-] Model {model_id} returned status {res.status_code}")
    except Exception as ex:
        print(f"    [-] Model {model_id} error: {ex}")

    return (False, False)

def main():
    parser = argparse.ArgumentParser(description="Test OpenRouter free models and embed in .env")
    parser.add_argument("--key", type=str, default=None, help="OpenRouter API Key override")
    parser.add_argument("--env-path", type=str, default=None, help="Path to backend/.env file")
    args = parser.parse_args()

    env_path = Path(args.env_path) if args.env_path else find_env_path()
    print(f"[*] Target .env path: {env_path}")

    env_vars = read_env_file(env_path)
    api_key = args.key or env_vars.get("OPENROUTER_API_KEY", "") or env_vars.get("LLM_API_KEY", "")

    if not api_key or api_key in ["your_openrouter_api_key_here", "sk-or-v1-xxx"]:
        print("[!] No active OpenRouter API key found in .env.")
        print("[*] Setting default verified model and mock fallback in .env...")
        update_env_variable(env_path, "LLM_PROVIDER", "mock")
        update_env_variable(env_path, "LLM_MODEL", "nvidia/nemotron-3.5-lightning:free")
        print("[+] Embedded default model and provider=mock into .env.")
        return 0

    print("[*] Fetching currently active free models from OpenRouter...")
    all_free_models = fetch_openrouter_free_models()
    prioritized = filter_and_prioritize_models(all_free_models)
    print(f"[*] Found {len(prioritized)} eligible free models to test.")

    valid_model = None
    for idx, model_id in enumerate(prioritized[:8], start=1):
        print(f"    [{idx}/{min(len(prioritized), 8)}] Testing model: {model_id} ...")
        success, is_auth_error = test_model(api_key, model_id)
        if success:
            valid_model = model_id
            print(f"[+] Model {model_id} verified successfully!")
            break
        if is_auth_error:
            print("[!] Aborting model iteration due to invalid API key credentials.")
            break

    if valid_model:
        print(f"\n[SUCCESS] Selected valid free model: {valid_model}")
        update_env_variable(env_path, "LLM_MODEL", valid_model)
        update_env_variable(env_path, "LLM_PROVIDER", "openrouter")
        print(f"[+] Successfully embedded LLM_MODEL={valid_model} into {env_path}")
        print(f"[+] Successfully ensured LLM_PROVIDER=openrouter in {env_path}")
        return 0
    else:
        print("\n[!] Could not verify a live OpenRouter free model with the provided key.")
        print("[*] Falling back to smart mock provider in .env to prevent application timeouts...")
        update_env_variable(env_path, "LLM_PROVIDER", "mock")
        update_env_variable(env_path, "LLM_MODEL", "nvidia/nemotron-3.5-lightning:free")
        print(f"[+] Embedded LLM_PROVIDER=mock and default LLM_MODEL into {env_path}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
