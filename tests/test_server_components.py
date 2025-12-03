import sys
import os
import asyncio
import numpy as np
import soundfile as sf
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from server.vad_service import VADService
from server.stt_service import STTService
from server.llm_service import LLMService
from server.tts_service import TTSService

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def test_vad():
    print("\n--- Testing VAD Service ---")
    vad = VADService()
    # Generate silence
    silence = np.zeros(16000, dtype=np.float32) # 1 sec silence
    # Convert to bytes (int16)
    silence_int16 = (silence * 32767).astype(np.int16).tobytes()
    
    # Process chunks of 512 samples
    chunk_size = 512 * 2 # bytes
    for i in range(0, len(silence_int16), chunk_size):
        chunk = silence_int16[i:i+chunk_size]
        if len(chunk) < chunk_size: break
        result = vad.process_chunk(chunk)
        if result:
            print(f"VAD Result: {result}")
    print("VAD Test Finished (Should see no speech detected for silence)")

def test_stt():
    print("\n--- Testing STT Service ---")
    if not GROQ_API_KEY:
        print("Skipping STT test: No API Key")
        return

    stt = STTService(api_key=GROQ_API_KEY)
    # We need a real audio file or something that sounds like speech.
    # Since we can't easily generate speech without TTS, let's skip or try to use TTS output later.
    print("STT Test: Requires audio input. Skipping for now.")

def test_llm():
    print("\n--- Testing LLM Service ---")
    if not GROQ_API_KEY:
        print("Skipping LLM test: No API Key")
        return

    llm = LLMService(api_key=GROQ_API_KEY)
    response = llm.get_response("Hello, how are you?")
    print(f"LLM Response: {response}")
    assert len(response) > 0

def test_tts():
    print("\n--- Testing TTS Service ---")
    if not os.path.exists("server/kokoro-v0_19.onnx") or not os.path.exists("server/voices.bin.npz"):
        print("Skipping TTS test: Models not found in server/")
        return

    tts = TTSService(model_path="server/kokoro-v0_19.onnx", voices_path="server/voices.bin.npz")
    audio_bytes = tts.generate_audio("Hello world")
    print(f"Generated Audio Bytes: {len(audio_bytes)}")
    assert len(audio_bytes) > 0
    
    # Save to file to check
    audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
    sf.write("tests/test_tts_output.wav", audio_np, 24000) # Kokoro is usually 24khz
    print("Saved test_tts_output.wav")

    # Now we can test STT with this audio!
    # But STT expects 16khz. We might need to resample.
    # Let's just verify TTS works for now.

if __name__ == "__main__":
    test_vad()
    test_llm()
    test_tts()
