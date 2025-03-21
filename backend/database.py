from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGO_URI'))
        self.db = self.client[os.getenv('DB_NAME')]
        self.collection = self.db['audio_transcriptions']

    def save_transcription(self, audio_path, transcription):
        document = {
            'timestamp': datetime.now(),
            'audio_path': audio_path,
            'transcription': transcription
        }
        return self.collection.insert_one(document)

    def get_all_transcriptions(self):
        return list(self.collection.find({}, {'_id': 0})) 