"""
Multi-Provider LLM Fallback Router for Scholar-Loop
Cascades seamlessly across Groq -> Google Gemini -> OpenRouter
with automatic retry on rate limits (429) and instant failover on 404/5xx errors.
"""

import os
import re
import sys
import time
from typing import Optional
from openai import OpenAI


# Provider Definitions with their respective candidate models
def get_provider_chain() -> list[dict]:
    chain = []

    # 1. Primary: Groq (Ultra-fast, generous free tier)
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        preferred = os.environ.get("LLM_MODEL")
        groq_models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "qwen/qwen3.6-27b",
            "groq/compound-mini",
        ]
        if preferred and preferred in groq_models:
            groq_models.remove(preferred)
            groq_models.insert(0, preferred)
        elif preferred:
            groq_models.insert(0, preferred)

        chain.append({
            "name": "Groq",
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": groq_key,
            "models": groq_models,
        })

    # 2. Secondary: Google Gemini (High reasoning, multi-turn reliability)
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if gemini_key:
        chain.append({
            "name": "Google Gemini",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "api_key": gemini_key,
            "models": [
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-flash",
            ],
        })

    # 3. Tertiary: OpenRouter (Universal model hub fallback)
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if openrouter_key:
        chain.append({
            "name": "OpenRouter",
            "base_url": "https://openrouter.ai/api/v1",
            "api_key": openrouter_key,
            "models": [
                "meta-llama/llama-3.3-70b-instruct",
                "qwen/qwen-2.5-72b-instruct",
                "google/gemini-2.0-flash-001",
            ],
        })

    return chain


def chat_completion_with_fallback(
    messages: list[dict],
    temperature: float = 0.3,
    max_tokens: int = 2048,
    response_format: Optional[dict] = None,
) -> tuple[str, str, str]:
    """
    Executes a chat completion across the provider/model fallback matrix.
    Returns:
        tuple (content_string, successful_provider_name, successful_model_name)
    Raises:
        RuntimeError if all providers and models in the chain fail.
    """
    providers = get_provider_chain()
    if not providers:
        raise RuntimeError("No LLM API keys configured (set GROQ_API_KEY, GEMINI_API_KEY, or OPENROUTER_API_KEY).")

    errors = []

    for provider in providers:
        p_name = provider["name"]
        client = OpenAI(base_url=provider["base_url"], api_key=provider["api_key"])

        for model in provider["models"]:
            for attempt in range(2):
                try:
                    kwargs = {
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    }
                    if response_format:
                        kwargs["response_format"] = response_format

                    resp = client.chat.completions.create(**kwargs)
                    raw_content = resp.choices[0].message.content or ""

                    # Strip reasoning / thinking blocks from reasoning models (Qwen / DeepSeek)
                    clean_content = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL).strip()
                    if clean_content:
                        return clean_content, p_name, model

                except Exception as e:
                    err_str = str(e).lower()
                    errors.append(f"[{p_name}:{model}] attempt {attempt+1}: {e}")

                    # 404 / Decommission / Not Found -> immediately skip to next model
                    if any(kw in err_str for kw in ["404", "model_not_found", "decommission", "does not exist"]):
                        print(f"  [warn] {p_name} model '{model}' not found (404), falling back...", file=sys.stderr)
                        break

                    # 429 Rate Limit -> backoff if first attempt, else cascade to next model/provider
                    if "429" in err_str or "rate_limit" in err_str:
                        wait_match = re.search(r"try again in ([\d.]+)s", err_str)
                        wait = float(wait_match.group(1)) + 1.0 if wait_match else 2.0
                        if attempt == 0 and wait <= 5.0:
                            time.sleep(wait)
                            continue
                        else:
                            print(f"  [warn] {p_name} rate limit on '{model}', switching candidate...", file=sys.stderr)
                            break

                    # Any other error -> try next model
                    break

    error_summary = "\n".join(errors)
    raise RuntimeError(f"All LLM providers and models failed in the fallback chain:\n{error_summary}")
