"""AI provider selection (port of config/ai-provider.config.ts).

If the requested provider has no API key, falls back to ``noop`` — the agent
makes ZERO network calls and produces a deterministic digest instead.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class AiProviderConfig:
    name: str  # claude | openai | noop
    model: str
    dry_run: bool
    reason: str


def resolve_provider(env: dict[str, str] | None = None) -> AiProviderConfig:
    env = env if env is not None else dict(os.environ)
    requested = (env.get("AI_PROVIDER", "claude")).strip().lower()

    if requested == "noop":
        return AiProviderConfig("noop", "noop", True, "AI_PROVIDER=noop")

    if requested == "openai":
        if env.get("OPENAI_API_KEY"):
            return AiProviderConfig("openai", env.get("OPENAI_MODEL", "gpt-4o-mini"), False, "AI_PROVIDER=openai")
        return AiProviderConfig("noop", "noop", True, "AI_PROVIDER=openai but OPENAI_API_KEY is not set — falling back to noop.")

    # default: claude
    if env.get("ANTHROPIC_API_KEY"):
        return AiProviderConfig("claude", env.get("ANTHROPIC_MODEL", "claude-opus-4-8"), False, "AI_PROVIDER=claude")
    return AiProviderConfig("noop", "noop", True, "ANTHROPIC_API_KEY is not set — falling back to noop.")
