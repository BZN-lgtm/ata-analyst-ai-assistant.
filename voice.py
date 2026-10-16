"""Always-on voice loop with the "Hey Urva" wake phrase.

Speech-to-text: SpeechRecognition (Google online, or Vosk offline if installed)
Text-to-speech: pyttsx3 (fully offline)
"""
from __future__ import annotations

WAKE = ("hey urva", "hey orva", "hey irva")


def speak(engine, text: str) -> None:
    print(f"Urva: {text}")
    engine.say(text)
    engine.runAndWait()


def listen(rec, source, timeout=None) -> str:
    import speech_recognition as sr
    try:
        audio = rec.listen(source, timeout=timeout, phrase_time_limit=10)
        try:
            return rec.recognize_vosk(audio).lower()  # offline, if model present
        except Exception:
            return rec.recognize_google(audio).lower()
    except (sr.WaitTimeoutError, sr.UnknownValueError):
        return ""


def run(assistant) -> None:
    import pyttsx3
    import speech_recognition as sr

    engine, rec = pyttsx3.init(), sr.Recognizer()
    with sr.Microphone() as mic:
        rec.adjust_for_ambient_noise(mic, duration=1)
        speak(engine, "Urva is listening.")
        while True:
            heard = listen(rec, mic)
            if not any(w in heard for w in WAKE):
                continue
            command = heard.split("urva", 1)[-1].strip() or listen(rec, mic, timeout=6)
            if not command:
                speak(engine, "Yes?")
                command = listen(rec, mic, timeout=6)
            if command in ("stop", "goodbye", "exit"):
                speak(engine, "Goodbye.")
                break
            try:
                speak(engine, assistant.handle(command))
            except Exception as e:
                speak(engine, f"Sorry, that failed: {e}")
