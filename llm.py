"""LLM backend: local Ollama first (offline), Claude API when online."""
from __future__ import annotations

import json
import os
import urllib.request

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
CLAUDE_MODEL = os.getenv("URVA_CLAUDE_MODEL", "claude-sonnet-5-5")
SYSTEM = "You are Urva, a concise voice assistant and data analyst. Answer in 1-3 spoken sentences."


def _ollama(prompt: str) -> str | None:
    body = json.dumps({"model": OLLAMA_MODEL, "prompt": f"{SYSTEM}\n\n{prompt}", "stream": False}).encode()
    req = urllib.request.Request(OLLAMA_URL, body, {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["response"].strip()
    except Exception:
        return None


def _claude(prompt: str) -> str | None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic
        msg = anthropic.Anthropic().messages.create(
            model=CLAUDE_MODEL, max_tokens=300, system=SYSTEM,
            messages=[{"role": "user", "content": prompt}])
        return msg.content[0].text.strip()
    except Exception:
        return None


def ask(prompt: str, prefer: str = os.getenv("URVA_BACKEND", "ollama")) -> str:
    order = (_ollama, _claude) if prefer == "ollama" else (_claude, _ollama)
    for fn in order:
        out = fn(prompt)
        if out:
            return out
    return "I'm offline and no local model is running right now."
