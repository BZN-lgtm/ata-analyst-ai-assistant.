# 🎙️ Urva — Voice-Driven Data Analyst AI Assistant

**Urva** is an always-on desktop assistant you talk to. Say **"Hey Urva"**, point it at a
spreadsheet, and it analyses the data, answers questions out loud, and builds a
presentation from the results. It runs **offline on a local LLM (Ollama)** and switches
to **Claude** when online.

## What it can do
| Say | Urva does |
|---|---|
| *"Hey Urva, analyze sales.csv"* | Loads Excel / CSV / a shared Google Sheet, profiles it and reads out the top insight |
| *"What's the total revenue?"* | Answers numeric questions instantly from the data |
| *"Give me the insights"* | Totals, averages, outliers (IQR), top segment share, strong correlations |
| *"Make a presentation"* | Generates a 4-slide navy & gold PPTX: title, insights, chart, stats table |
| *"Remind me to review the budget"* | Adds a sticky-note task |
| *"What's pending?"* | Reads tasks back one by one next morning |
| Anything else | Routed to the LLM with the loaded dataset as context |

## Architecture
```
 mic ─► wake word "Hey Urva" ─► speech-to-text (Vosk offline / Google online)
                                      │
                                      ▼
                           intent router (assistant.py)
          ┌───────────────┬──────────────┼──────────────┬───────────────┐
      analyst.py      slides.py       notes.py        llm.py
   pandas profiling   python-pptx    JSON to-dos   Ollama ⇄ Claude
          └───────────────┴──────────────┴──────────────┴───────────────┘
                                      │
                         text-to-speech (pyttsx3, offline)
```

## Quick start
```bash
pip install -r requirements.txt
python main.py --text          # keyboard mode, no microphone needed
python main.py                 # voice mode — say "Hey Urva"
```
Optional: `ollama pull llama3.1` for offline answers, `ANTHROPIC_API_KEY` for Claude,
`URVA_BACKEND=claude` to prefer the cloud model.

## Tests
```bash
pytest -q
```

## Tech
Python · pandas · matplotlib · python-pptx · SpeechRecognition · Vosk · pyttsx3 ·
Ollama (local LLM) · Anthropic Claude API

## Roadmap
- Meeting mode: live transcription + action-item extraction
- Job-application helper for LinkedIn / X
- Charts on demand ("plot revenue by region")

## Author
**Bilal Zubair Nizam** — MS Artificial Intelligence Engineering
