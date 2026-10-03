"""
Gemini LLM client for Scholar-Loop.

Uses Google's OpenAI-compatible endpoint. The primary model is the
`gemini-flash-latest` alias, which Google moves forward to each new Flash
release, so the pipeline does not break when a pinned version is retired.
A pinned Flash version is kept as a backup.
"""

import os
import re
import sys
import time
from typing import Optional

from openai import OpenAI

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
DEFAULT_MODELS = ["gemini-flash-latest", "gemini-3.8-flash"]
PROVIDER_NAME = "Gemini"

MAX_ATTEMPTS = 3
MAX_RATE_LIMIT_WAIT_S = 30.0


def get_api_key() -> Optional[str]:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def get_models() -> list[str]:
    """Model candidates in order. LLM_MODEL (if set) is tried first."""
    models = list(DEFAULT_MODELS)
    preferred = os.environ.get("LLM_MODEL")
    if preferred:
        if preferred in models:
            models.remove(preferred)
        models.insert(0, preferred)
    return models


def chat_completion_with_fallback(
    messages: list[dict],
    temperature: float = 0.3,
    max_tokens: int = 2048,
    response_format: Optional[dict] = None,
) -> tuple[str, str, str]:
    """
    Run a chat completion against Gemini, trying each candidate model in turn.

    Returns:
        (content, provider_name, model_name)
    Raises:
        RuntimeError if no API key is set or every model fails.
    """
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")

    client = OpenAI(base_url=GEMINI_BASE_URL, api_key=api_key)
    errors = []

    for model in get_models():
        for attempt in range(MAX_ATTEMPTS):
            try:
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    # Gemini Flash "thinks" before answering, and those hidden tokens
                    # count against max_tokens. Low effort keeps answers from coming
                    # back empty and keeps calls cheap.
                    "extra_body": {"reasoning_effort": "low"},
                }
                if response_format:
                    kwargs["response_format"] = response_format

                resp = client.chat.completions.create(**kwargs)
                raw_content = resp.choices[0].message.content or ""

                # Defensive: strip any reasoning blocks if a model ever emits them inline.
                clean_content = re.sub(
                    r"<think>.*?</think>", "", raw_content, flags=re.DOTALL
                ).strip()
                if clean_content:
                    return clean_content, PROVIDER_NAME, model

                errors.append(f"[{model}] attempt {attempt + 1}: empty response")
                break

            except Exception as e:
                err_str = str(e).lower()
                errors.append(f"[{model}] attempt {attempt + 1}: {e}")

                # Model retired / unknown -> try the next model.
                if any(kw in err_str for kw in ["404", "not_found", "no longer available",
                                                "not found", "decommission"]):
                    print(f"  [warn] {PROVIDER_NAME} model '{model}' unavailable, "
                          "trying next...", file=sys.stderr)
                    break

                # Rate limit / overloaded -> back off and retry the same model.
                if any(kw in err_str for kw in ["429", "rate", "resource_exhausted",
                                                "503", "overloaded", "unavailable"]):
                    wait_match = re.search(r"retry in ([\d.]+)s|try again in ([\d.]+)s", err_str)
                    if wait_match:
                        wait = float(next(g for g in wait_match.groups() if g)) + 1.0
                    else:
                        wait = 5.0 * (attempt + 1)
                    if attempt < MAX_ATTEMPTS - 1 and wait <= MAX_RATE_LIMIT_WAIT_S:
                        print(f"  [warn] {PROVIDER_NAME} busy on '{model}', "
                              f"retrying in {wait:.0f}s...", file=sys.stderr)
                        time.sleep(wait)
                        continue
                    break

                # Auth or other errors: retrying another model won't help much, but try.
                break

    error_summary = "\n".join(errors)
    raise RuntimeError(f"All Gemini models failed:\n{error_summary}")
