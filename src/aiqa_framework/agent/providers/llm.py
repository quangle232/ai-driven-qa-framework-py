"""LLM provider abstraction (port of providers/*). Claude / OpenAI / noop.

`noop` makes ZERO network calls (deterministic). Real providers are used only
when their API key is present (see config.ai_provider.resolve_provider).
"""

from __future__ import annotations

from typing import Protocol

from aiqa_framework.agent.config.ai_provider import AiProviderConfig, resolve_provider


class LLMProvider(Protocol):
    def diagnose(self, prompt: str) -> str: ...


class NoopProvider:
    """Deterministic — returns nothing; the agent falls back to its digest."""

    def diagnose(self, prompt: str) -> str:  # noqa: ARG002
        return ""


class ClaudeProvider:
    def __init__(self, model: str) -> None:
        self._model = model

    def diagnose(self, prompt: str) -> str:
        from anthropic import Anthropic  # imported lazily so noop runs without the SDK

        client = Anthropic()
        msg = client.messages.create(
            model=self._model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in msg.content if getattr(block, "type", "") == "text")


class OpenAIProvider:
    def __init__(self, model: str) -> None:
        self._model = model

    def diagnose(self, prompt: str) -> str:
        from openai import OpenAI

        client = OpenAI()
        resp = client.chat.completions.create(
            model=self._model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or ""


def get_provider(config: AiProviderConfig | None = None) -> tuple[LLMProvider, AiProviderConfig]:
    cfg = config or resolve_provider()
    if cfg.dry_run or cfg.name == "noop":
        return NoopProvider(), cfg
    if cfg.name == "openai":
        return OpenAIProvider(cfg.model), cfg
    return ClaudeProvider(cfg.model), cfg
