import speech_recognition as sr
from pydub import AudioSegment
import os
import time

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Adjust recognition settings for better accuracy
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.8

    def enhance_audio(self, audio_path):
        """Enhance audio file for better recognition"""
        try:
            # Load and convert audio
            audio = AudioSegment.from_wav(audio_path)
            
            # Convert to mono if stereo
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Normalize audio (reduce noise and adjust volume)
            audio = audio.normalize()
            
            # Export enhanced audio
            enhanced_path = audio_path.replace('.wav', '_enhanced.wav')
            audio.export(enhanced_path, format='wav')
            return enhanced_path
        except Exception as e:
            print(f"Error enhancing audio: {e}")
            return audio_path

    def transcribe_audio(self, audio_path):
        """Transcribe audio using multiple recognition engines"""
        # Enhance the audio first
        enhanced_path = self.enhance_audio(audio_path)
        
        transcription_methods = [
            (self.recognize_google, "Google Speech Recognition"),
            (self.recognize_sphinx, "Sphinx"),
            (self.recognize_wit, "Wit.ai"),
        ]
        
        final_transcription = ""
        
        try:
            with sr.AudioFile(enhanced_path) as source:
                # Record audio for processing
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = self.recognizer.record(source)
                
                # Try each transcription method
                for transcribe_method, method_name in transcription_methods:
                    try:
                        result = transcribe_method(audio_data)
                        if result:
                            final_transcription = result
                            print(f"Successfully transcribed using {method_name}")
                            break
                    except sr.UnknownValueError:
                        print(f"{method_name} could not understand audio")
                        continue
                    except sr.RequestError as e:
                        print(f"{method_name} error; {e}")
                        continue
                    except Exception as e:
                        print(f"Error with {method_name}: {e}")
                        continue
            
            # Clean up enhanced audio file
            if os.path.exists(enhanced_path) and enhanced_path != audio_path:
                os.remove(enhanced_path)
            
            return final_transcription if final_transcription else "Could not transcribe audio"
            
        except Exception as e:
            return f"Error processing audio: {str(e)}"

    def recognize_google(self, audio_data):
        """Use Google Speech Recognition"""
        try:
            return self.recognizer.recognize_google(audio_data, language="en-US")
        except Exception as e:
            print(f"Google Speech Recognition error: {e}")
            return None

    def recognize_sphinx(self, audio_data):
        """Use CMU Sphinx (offline)"""
        try:
            return self.recognizer.recognize_sphinx(audio_data)
        except Exception as e:
            print(f"Sphinx error: {e}")
            return None

    def recognize_wit(self, audio_data):
        """Use Wit.ai"""
        try:
            WIT_AI_KEY = os.getenv('WIT_AI_KEY', '')  # Get from environment variables
            if WIT_AI_KEY:
                return self.recognizer.recognize_wit(audio_data, key=WIT_AI_KEY)
            return None
        except Exception as e:
            print(f"Wit.ai error: {e}")
            return None 