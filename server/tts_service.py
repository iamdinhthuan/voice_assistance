import soundfile as sf
from kokoro_onnx import Kokoro
import numpy as np
import io

class TTSService:
    def __init__(self, model_path="kokoro-v0_19.onnx", voices_path="voices.bin.npz"):
        # Assuming model and voices are downloaded/available locally or we need to handle that.
        # For now, we'll initialize assuming the files exist or will be provided.
        # If the user hasn't provided them, we might need a setup script or instructions.
        # But for the code structure:
        try:
             self.kokoro = Kokoro(model_path, voices_path)
        except Exception as e:
            print(f"TTS Init Warning: {e}. Make sure model files are present.")
            self.kokoro = None

    def generate_audio(self, text: str, voice="af_sarah") -> bytes:
        """
        Generate audio from text using Kokoro ONNX.
        Returns raw audio bytes (PCM).
        """
        if not self.kokoro:
            print("TTS model not initialized.")
            return b""

        try:
            # generate returns (audio, sample_rate)
            audio, sample_rate = self.kokoro.create(
                text, voice=voice, speed=1.0, lang="en-us"
            )
            
            # Convert float32 numpy array to int16 bytes for transmission
            # Audio is typically float32 in [-1, 1]
            audio_int16 = (audio * 32767).astype(np.int16)
            
            return audio_int16.tobytes()
        except Exception as e:
            print(f"TTS Generation Error: {e}")
            return b""
