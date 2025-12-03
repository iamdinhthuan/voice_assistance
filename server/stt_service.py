import os
from groq import Groq
import io
import soundfile as sf
import numpy as np

class STTService:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def transcribe(self, audio_data: bytes, sample_rate=16000) -> str:
        """
        Transcribe audio bytes using Groq API (Whisper).
        """
        try:
            # Convert raw bytes to a file-like object that Groq API accepts
            # We need to wrap the raw PCM data into a WAV container or similar for the API
            audio_int16 = np.frombuffer(audio_data, dtype=np.int16)
            
            # Create an in-memory file
            buffer = io.BytesIO()
            sf.write(buffer, audio_int16, sample_rate, format='WAV')
            buffer.seek(0)
            buffer.name = "audio.wav" # Groq client checks filename extension

            transcription = self.client.audio.transcriptions.create(
                file=(buffer.name, buffer.read()),
                model="whisper-large-v3-turbo", # Or distil-whisper-large-v3-en
                response_format="text",
                language="en"
            )
            return transcription
        except Exception as e:
            print(f"STT Error: {e}")
            return ""
