from pathlib import Path

from pptx import Presentation

from urva.assistant import Urva
from urva.notes import Notes

DATA = Path(__file__).resolve().parent.parent / "sample_data" / "sales.csv"


def make(tmp_path):
    return Urva(notes=Notes(tmp_path / "notes.json"), out_dir=tmp_path)


def test_analyze_and_answer(tmp_path):
    u = make(tmp_path)
    assert "120 rows" in u.handle(f"analyze {DATA}")
    assert u.handle("what is the total Revenue").startswith("Total Revenue is")


def test_presentation_built(tmp_path):
    u = make(tmp_path)
    u.handle(f"analyze {DATA}")
    reply = u.handle("make a presentation")
    deck = next(tmp_path.glob("*.pptx"))
    assert deck.name in reply
    assert len(Presentation(deck).slides) == 4


def test_sticky_notes_roundtrip(tmp_path):
    u = make(tmp_path)
    u.handle("add review the Q3 budget")
    u.handle("remind me to call the vendor")
    assert "2 pending" in u.handle("what's pending")
    u.handle("done budget")
    assert "1 pending" in u.handle("what's pending")
