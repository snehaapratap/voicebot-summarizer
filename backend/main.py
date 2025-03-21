from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
from database import Database
from audio_processor import AudioProcessor

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and audio processor
db = Database()
audio_processor = AudioProcessor()

# Ensure audio storage directory exists
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.post("/process-audio/")
async def process_audio(file: UploadFile = File(...)):
    # Save audio file
    audio_path = os.path.join(AUDIO_DIR, file.filename)
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    # Transcribe audio
    transcription = audio_processor.transcribe_audio(audio_path)

    # Save to database
    db.save_transcription(audio_path, transcription)

    return {"transcription": transcription}

@app.get("/transcriptions/")
async def get_transcriptions():
    return db.get_all_transcriptions()
