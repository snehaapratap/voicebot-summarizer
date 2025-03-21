from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def save_audio(file_name, audio_bytes, transcript):
    """Save audio and transcription to MongoDB."""
    record = {
        "file_name": file_name,
        "audio_data": audio_bytes,
        "transcript": transcript
    }
    collection.insert_one(record)
    print("Audio saved successfully!")

def get_all_transcripts():
    """Retrieve all transcriptions from MongoDB."""
    return collection.find({}, {"file_name": 1, "transcript": 1, "_id": 0})
