from fastapi import FastAPI, File, UploadFile
from voice_to_text import speech_to_text
from summarizer import summarize_text

app = FastAPI()

@app.post("/process-audio/")
async def process_audio(file: UploadFile = File(...)):
    audio_path = f"data/{file.filename}"
    
    with open(audio_path, "wb") as f:
        f.write(file.file.read())

    text = speech_to_text(audio_path)
    summary = summarize_text(text)

    return {"transcription": text, "summary": summary}
