import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI(title="Speech -> Gemini PoC", version="1.0")

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "uk-UA")

SUMMARY_PROMPT = (
    u"Ти асистент, що конспектує розшифровки аудіо (лекції, зустрічі, нотатки).\n"
    u"На основі транскрипту нижче зроби структурований конспект українською:\n"
    u"1. Короткий зміст (2–3 речення).\n"
    u"2. Ключові тези (булети).\n"
    u"3. Пункти дій / завдання, якщо є.\n\n"
    u"Транскрипт:\n{transcript}"
)


@app.get("/")
def health():
    return {"status": "ok", "service": "speech-gemini-poc"}


@app.post("/process")
async def process(audio: UploadFile = File(...)):
    content = await audio.read()
    if not content:
        raise HTTPException(status_code=400, detail="порожній аудіофайл")

    transcript = transcribe(content)
    if not transcript:
        return JSONResponse({"transcript": "", "summary": "(мову не розпізнано)"})

    summary = summarize(transcript)
    return {"transcript": transcript, "summary": summary}


def transcribe(audio_bytes):
    from google.cloud import speech

    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_bytes)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
        language_code=LANGUAGE_CODE,
        enable_automatic_punctuation=True,
    )
    response = client.recognize(config=config, audio=audio)
    parts = [r.alternatives[0].transcript for r in response.results if r.alternatives]
    return " ".join(parts).strip()


def summarize(transcript):
    import google.generativeai as genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY не заданий")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    resp = model.generate_content(SUMMARY_PROMPT.format(transcript=transcript))
    return resp.text
