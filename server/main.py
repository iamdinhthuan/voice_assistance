import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
import numpy as np

# Import services
from server.vad_service import VADService
from server.stt_service import STTService
from server.llm_service import LLMService
from server.tts_service import TTSService

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize Services
# Note: In a real app, you might want to initialize these on startup or per connection depending on resource usage.
# For now, we'll initialize global instances where possible.

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not found in .env")

vad_service = VADService()
stt_service = STTService(api_key=GROQ_API_KEY)
llm_service = LLMService(api_key=GROQ_API_KEY)
tts_service = TTSService() # Ensure kokoro-v0_19.onnx and voices.json are in the working directory or path

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    
    # Per-connection state
    audio_buffer = bytearray()
    is_speaking = False
    silence_counter = 0
    SILENCE_THRESHOLD = 10 # chunks of silence to trigger end of speech (approx 0.5s if chunk is 50ms)
    
    try:
        while True:
            # Receive message
            # We expect binary audio chunks or text JSON control messages
            # For simplicity, let's assume client sends binary audio chunks directly
            # or we can use a specific protocol.
            # Let's support mixed: text for control, bytes for audio.
            
            message = await websocket.receive()
            
            if "bytes" in message:
                audio_chunk = message["bytes"]
                
                # 1. VAD Processing
                # vad_service.process_chunk returns dict if speech start/end detected, but we also need to know if current chunk is speech
                # Silero VAD iterator is stateful.
                
                # For simplicity with the VAD wrapper we wrote:
                # It returns a dict with 'start' or 'end' keys if a transition happens.
                # However, we also need to accumulate audio.
                
                speech_status = vad_service.process_chunk(audio_chunk)
                
                if speech_status:
                    if 'start' in speech_status:
                        print("Speech started")
                        is_speaking = True
                        audio_buffer = bytearray(audio_chunk) # Start fresh buffer or keep context?
                        # Usually keep a bit of context.
                    
                    if 'end' in speech_status:
                        print("Speech ended")
                        is_speaking = False
                        # Process the accumulated audio
                        await process_audio_input(websocket, audio_buffer)
                        audio_buffer = bytearray()
                
                # If we are in a speaking state, accumulate
                # Note: Silero VAD iterator handles the "speech" state internally.
                # If we want to capture the audio *during* speech, we need to know if we are currently speaking.
                # The wrapper I wrote returns events.
                # A better approach for the wrapper might be to return "is_speech" boolean for the chunk.
                # But let's stick to the event-based for now.
                # Actually, if 'start' was triggered, we are speaking until 'end' is triggered.
                
                if is_speaking:
                    audio_buffer.extend(audio_chunk)
                else:
                    # We might want to keep a rolling buffer for context if we were doing advanced VAD
                    pass
                    
            elif "text" in message:
                data = json.loads(message["text"])
                print(f"Received control message: {data}")
                # Handle control messages if any

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

async def process_audio_input(websocket: WebSocket, audio_data: bytearray):
    print(f"Processing audio: {len(audio_data)} bytes")
    
    # 2. STT
    text = stt_service.transcribe(audio_data)
    print(f"Transcribed: {text}")
    
    if not text.strip():
        return

    # 3. LLM
    response_text = llm_service.get_response(text)
    print(f"LLM Response: {response_text}")
    
    # 4. TTS
    audio_response = tts_service.generate_audio(response_text)
    
    # 5. Send back to client
    # Send text first (optional)
    await websocket.send_text(json.dumps({"type": "text_response", "data": response_text}))
    
    # Send audio
    await websocket.send_bytes(audio_response)
    print("Sent audio response")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
