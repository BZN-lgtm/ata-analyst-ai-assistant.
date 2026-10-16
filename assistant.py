"""Intent router: maps an utterance to a skill and returns a spoken reply."""
from __future__ import annotations

import re
from pathlib import Path

from urva import llm
from urva.analyst import Analysis, analyze, answer, load
from urva.notes import Notes
from urva.slides import build_deck


class Urva:
    def __init__(self, notes: Notes | None = None, out_dir: Path = Path(".")):
        self.notes = notes or Notes()
        self.out_dir = Path(out_dir)
        self.current: Analysis | None = None

    def handle(self, text: str) -> str:
        t = text.strip()
        low = t.lower()

        if m := re.match(r"(?:analy[sz]e|open|load)\s+(.+)", t, re.I):
            path = m.group(1).strip().strip('"')
            df = load(path)
            self.current = analyze(df, Path(path).stem.replace("_", " ").title())
            a = self.current
            lead = a.insights[0] if a.insights else ""
            return f"Loaded {a.rows} rows and {a.cols} columns. {lead}"

        if ("presentation" in low or "ppt" in low or "slides" in low) and self.current:
            out = build_deck(self.current, self.out_dir / f"{self.current.name.replace(' ', '_')}.pptx")
            return f"Your presentation is ready: {out.name}"

        if ("insight" in low or "summar" in low) and self.current:
            return " ".join(self.current.insights) or "Nothing stood out."

        if m := re.match(r"(?:add|note|remind me to)\s+(?:a task\s+)?(?:to\s+)?(.+)", t, re.I):
            return self.notes.add(m.group(1))

        if "pending" in low or "my tasks" in low or "to do" in low:
            items = self.notes.pending()
            if not items:
                return "You're all clear — nothing pending."
            return f"You have {len(items)} pending: " + "; ".join(f"{i}. {x}" for i, x in enumerate(items, 1))

        if m := re.match(r"(?:done|complete|finished)\s+(.+)", t, re.I):
            return self.notes.complete(m.group(1))

        if self.current is not None and (ans := answer(self.current.df, t)):
            return ans

        ctx = ""
        if self.current:
            ctx = f"Loaded dataset '{self.current.name}' columns: {list(self.current.df.columns)}. "
        return llm.ask(ctx + t)
