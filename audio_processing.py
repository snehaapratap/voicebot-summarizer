import speech_recognition as sr
import io
from pydub import AudioSegment

def convert_audio_to_text(audio_bytes):
    """Convert audio to text using SpeechRecognition."""
    recognizer = sr.Recognizer()
    
    # Convert bytes to audio file
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
    audio.export("temp.wav", format="wav")
    
    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Could not understand the audio."
        except sr.RequestError:
            return "Speech-to-text service unavailable."
