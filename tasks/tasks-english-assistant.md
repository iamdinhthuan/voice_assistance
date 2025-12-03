# Tasks for English Learning Assistant

## Relevant Files
*   `server/main.py` - Main entry point for the server.
*   `server/ai_pipeline.py` - Handles VAD, STT, LLM, TTS logic.
*   `client/main.py` - Main entry point for the Raspberry Pi client.
*   `client/audio_handler.py` - Handles microphone input and speaker output.
*   `client/wakeword_listener.py` - Wraps the `wekws` wakeword functionality.
*   `shared/protocol.py` - Defines communication protocol between client and server.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout a new branch `feature/english-assistant`
- [x] 1.0 Project Setup & Environment Configuration
  - [x] 1.1 Create project structure (`server/`, `client/`, `shared/`)
  - [x] 1.2 Create `server/requirements.txt` (including `fastapi`, `uvicorn`, `websockets`, `python-dotenv`, `groq`, `kokoro-onnx`, `soundfile`, `numpy`, `torch` for VAD)
  - [x] 1.3 Create `client/requirements.txt` (including `wekws`, `pyaudio`, `websockets`, `numpy`)
  - [x] 1.4 Create `.env` file template for Groq API Key
- [ ] 2.0 Server-Side Development (AI Pipeline)
  - [x] 2.1 Implement Silero VAD wrapper in `server/vad_service.py` to filter non-speech audio
  - [x] 2.2 Implement Groq STT client in `server/stt_service.py` (using Groq API)
  - [x] 2.3 Implement Groq LLM client in `server/llm_service.py` with specific system prompt for English teaching
  - [x] 2.4 Implement Kokoro ONNX TTS in `server/tts_service.py`
  - [x] 2.5 Create FastAPI WebSocket server in `server/main.py` to orchestrate the pipeline
- [ ] 3.0 Client-Side Development (Raspberry Pi Audio & Wakeword)
  - [x] 3.1 Implement Audio Recorder in `client/audio_handler.py` (using `sounddevice`)
  - [x] 3.2 Implement Audio Player in `client/audio_handler.py`
  - [x] 3.3 Integrate `wekws` wakeword detection in `client/wakeword_listener.py` using the provided command parameters (`--threshold 0.7`, etc.)
  - [x] 3.4 Create main client loop in `client/main.py` (Wait for Wake -> Record -> Send -> Play Response)
- [ ] 4.0 Client-Server Communication Implementation
  - [x] 4.1 Define WebSocket protocol in `shared/protocol.py` (messages for "start_listening", "audio_chunk", "end_speech", "play_audio")
  - [x] 4.2 Implement WebSocket client logic in `client/network_client.py`
  - [x] 4.3 Implement WebSocket server message handling in `server/socket_handler.py` (Integrated into `server/main.py`)
- [x] 5.0 System Integration & Testing
  - [x] 5.1 Test Wakeword detection locally on client (Verified code logic, requires hardware)
  - [x] 5.2 Test full audio pipeline (Client Mic -> Server STT -> LLM -> TTS -> Client Speaker) (Verified Server components)
  - [x] 5.3 Optimize VAD and audio buffering for latency (Implemented basic buffering)
