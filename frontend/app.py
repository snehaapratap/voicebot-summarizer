import streamlit as st
import pyaudio
import wave
import numpy as np
import requests
import os
from datetime import datetime

# Audio recording parameters
SAMPLE_RATE = 44100
CHANNELS = 1
CHUNK = 1024
FORMAT = pyaudio.paInt16
BACKEND_URL = "http://localhost:8000"

def record_audio(duration):
    """Record audio from microphone"""
    try:
        p = pyaudio.PyAudio()
        
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        st.write("🎤 Recording...")
        frames = []
        
        # Create a progress bar
        progress_bar = st.progress(0)
        total_chunks = int(SAMPLE_RATE / CHUNK * duration)
        
        # Record audio
        for i in range(total_chunks):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            # Update progress bar
            progress_bar.progress((i + 1) / total_chunks)
        
        st.write("✅ Recording finished!")
        
        # Cleanup
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        return frames
    
    except Exception as e:
        st.error(f"Error recording audio: {e}")
        return None

def save_audio(frames):
    """Save recorded audio to file"""
    if not frames:
        return None
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return filename
    
    except Exception as e:
        st.error(f"Error saving audio: {e}")
        return None

def send_audio_to_backend(audio_file):
    """Send audio file to backend for processing"""
    if not audio_file:
        return {"transcription": "Error during recording or saving audio"}
    
    try:
        with open(audio_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BACKEND_URL}/process-audio/", files=files)
            return response.json()
    except Exception as e:
        return {"transcription": f"Error sending to backend: {str(e)}"}

def main():
    st.title("Voice Transcription App")
    
    # Recording section
    st.header("Record Audio")
    
    col1, col2 = st.columns(2)
    
    with col1:
        duration = st.slider("Recording duration (seconds)", 1, 30, 5)
    
    with col2:
        if st.button("🎤 Start Recording"):
            # Record audio
            frames = record_audio(duration)
            
            if frames:
                # Save the audio file
                audio_file = save_audio(frames)
                
                if audio_file:
                    st.success(f"Recording saved!")
                    
                    # Play the recorded audio
                    with open(audio_file, 'rb') as audio_data:
                        st.audio(audio_data.read(), format='audio/wav')
                    
                    # Process the audio
                    with st.spinner("Transcribing..."):
                        result = send_audio_to_backend(audio_file)
                        
                    st.write("📝 Transcription:", result["transcription"])
    
    # Recording tips
    with st.expander("📌 Tips for Better Recording"):
        st.markdown("""
        - Speak clearly and at a normal pace
        - Keep the microphone close (6-8 inches from mouth)
        - Record in a quiet environment
        - Avoid background noise
        - Test your microphone volume before recording
        """)

if __name__ == "__main__":
    main()
