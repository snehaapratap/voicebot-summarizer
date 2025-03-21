import streamlit as st
import time
import io
from database import save_audio, get_all_transcripts
from audio_processing import convert_audio_to_text

st.title("🎙️ Real-Time Audio Recorder & Transcriber")

# Audio recording widget
audio_bytes = st.audio("record")  # This requires a plugin like WebRTC for real-time recording

if st.button("Save & Transcribe"):
    if audio_bytes:
        file_name = f"audio_{int(time.time())}.wav"
        
        # Convert bytes to text
        transcript = convert_audio_to_text(audio_bytes)
        
        # Save audio and transcript
        save_audio(file_name, audio_bytes, transcript)
        
        st.success("Audio saved successfully!")
        st.text_area("Transcription:", transcript)

# Display all transcriptions
st.subheader("All Transcriptions")
for record in get_all_transcripts():
    st.write(f"**{record['file_name']}**: {record['transcript']}")
