import streamlit as st
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import requests
import os

st.title("Doctor's Voice-to-Text Summary")

# Audio Recording Parameters
samplerate = 44100  # Audio sample rate
duration = 5  # Recording duration

def get_audio_devices():
    """List all available audio devices"""
    devices = sd.query_devices()
    st.sidebar.write("Available Audio Devices:")
    for i, device in enumerate(devices):
        st.sidebar.write(f"{i}: {device['name']}")
    return devices

def record_audio():
    try:
        st.write("🎤 Recording... Speak now")
        # Using mono recording (1 channel) instead of stereo (2 channels)
        audio_data = sd.rec(
            int(samplerate * duration),
            samplerate=samplerate,
            channels=1,  # Changed to mono
            dtype=np.int16
        )
        sd.wait()
        return audio_data
    except sd.PortAudioError as e:
        st.error(f"Error recording audio: {str(e)}")
        st.info("Please check your microphone settings and try again")
        return None

# Show available devices in sidebar
devices = get_audio_devices()

# Device selection
device_index = st.sidebar.selectbox(
    "Select Input Device",
    range(len(devices)),
    format_func=lambda x: devices[x]['name']
)

# Set the selected device
sd.default.device = device_index

# Recording duration selector
duration = st.slider("Recording Duration (seconds)", min_value=3, max_value=30, value=5)

if st.button("🎙️ Record Voice"):
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    audio_data = record_audio()
    
    if audio_data is not None:
        audio_path = "data/temp_audio.wav"
        wav.write(audio_path, samplerate, audio_data)
        
        st.success("Recording complete! Processing...")
        
        try:
            # Send to Backend
            with open(audio_path, "rb") as audio_file:
                response = requests.post(
                    "http://127.0.0.1:8001/process-audio/",
                    files={"file": audio_file}
                )
            
            if response.status_code == 200:
                result = response.json()
                
                st.write("### Transcription")
                st.write(result["transcription"])
                
                st.write("### Summary")
                st.write(result["summary"])
                
                # Add a download button for the transcription
                st.download_button(
                    label="Download Transcription",
                    data=result["transcription"],
                    file_name="transcription.txt",
                    mime="text/plain"
                )
            else:
                st.error(f"Failed to process audio. Status code: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend server. Please make sure it's running.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
