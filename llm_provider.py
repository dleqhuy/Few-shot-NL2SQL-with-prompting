"""Shared configuration for OpenAI and OpenAI-compatible chat endpoints."""

import os
from dataclasses import dataclass
from pathlib import Path

import openai
from dotenv import load_dotenv


@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    base_url: str
    model: str

    @classmethod
    def from_env(cls, default_model="gpt-4"):
        # Explicit environment variables take precedence over the local file.
        load_dotenv(Path(__file__).resolve().parent / ".env", override=False)
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Set LLM_API_KEY (or OPENAI_API_KEY) in the environment or .env")
        base_url = (
            os.getenv("LLM_BASE_URL")
            or os.getenv("OPENAI_BASE_URL")
            or os.getenv("OPENAI_API_BASE")
            or "https://api.openai.com/v1"
        )
        model = os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL") or default_model
        return cls(api_key=api_key, base_url=base_url.rstrip("/"), model=model)


def generate(config, prompt, *, max_tokens=600, stop=None):
    response = openai.ChatCompletion.create(
        api_key=config.api_key,
        api_base=config.base_url,
        model=config.model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=max_tokens,
        stop=stop,
        request_timeout=120,
    )
    content = response["choices"][0]["message"]["content"]
    if not content:
        raise ValueError("The LLM returned an empty chat completion")
    return content
