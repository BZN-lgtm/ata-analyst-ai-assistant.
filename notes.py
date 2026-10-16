"""Sticky-note to-do list: add by voice, read back pending items next morning."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

DEFAULT = Path.home() / ".urva" / "notes.json"


class Notes:
    def __init__(self, path: Path = DEFAULT):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.items = json.loads(self.path.read_text()) if self.path.exists() else []

    def _save(self):
        self.path.write_text(json.dumps(self.items, indent=2))

    def add(self, text: str) -> str:
        self.items.append({"text": text.strip(), "done": False,
                           "added": datetime.now().isoformat(timespec="minutes")})
        self._save()
        return f"Added: {text.strip()}"

    def pending(self) -> list[str]:
        return [i["text"] for i in self.items if not i["done"]]

    def complete(self, phrase: str) -> str:
        for i in self.items:
            if not i["done"] and phrase.lower() in i["text"].lower():
                i["done"] = True
                self._save()
                return f"Marked done: {i['text']}"
        return "I couldn't find that task."
