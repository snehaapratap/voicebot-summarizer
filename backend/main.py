from fastapi import FastAPI, File, UploadFile
from pymongo import MongoClient
import speech_recognition as sr
from transformers import pipeline
import os
from datetime import datetime

app = FastAPI()

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["medical_records"]
collection = db["patient_records"]

# Initialize the summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def speech_to_text(audio_file_path):
    """Convert speech to text using Google Speech Recognition"""
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(audio_file_path) as source:
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source)
        # Record the audio
        audio = recognizer.record(source)
        
    try:
        # Use Google Speech Recognition
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Speech Recognition could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results from Speech Recognition service; {str(e)}"

def summarize_text(text):
    """Generate a summary of the text"""
    try:
        # Check if text is too short
        if len(text.split()) < 30:
            return text
        
        summary = summarizer(text, 
                           max_length=130, 
                           min_length=30, 
                           do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Error in summarization: {str(e)}"

@app.post("/process-audio/")
async def process_audio(file: UploadFile = File(...)):
    try:
        # Create temporary directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        
        # Save uploaded file temporarily
        temp_audio_path = f"temp/{file.filename}"
        with open(temp_audio_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Convert speech to text
        transcription = speech_to_text(temp_audio_path)
        
        # Generate summary
        summary = summarize_text(transcription)
        
        # Create record for MongoDB
        record = {
            "timestamp": datetime.now(),
            "original_filename": file.filename,
            "transcription": transcription,
            "summary": summary
        }
        
        # Store in MongoDB
        collection.insert_one(record)
        
        # Clean up temporary file
        os.remove(temp_audio_path)
        
        return {
            "transcription": transcription,
            "summary": summary,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}
