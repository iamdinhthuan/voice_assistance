# English Learning Assistant - Setup & Run Guide

## Prerequisites

1.  **Hardware:**
    *   Raspberry Pi 4 (8GB) with Microphone and Speaker.
    *   Server PC (Windows/Linux) with GPU recommended for faster processing.

2.  **Software:**
    *   Python 3.8+
    *   `wekws` installed or available in `d:\assitance_voicebot\wekws`.
    *   `kokoro-onnx` model files (`kokoro-v0_19.onnx`, `voices.json`) placed in `server/` directory.

## Installation

1.  **Server Setup:**
    ```bash
    cd server
    pip install -r requirements.txt
    ```
    *   Ensure `.env` file has your `GROQ_API_KEY`.
    *   Run the setup script to download models and prepare files:
        ```bash
        python setup.py
        ```
        This will download `kokoro-v0_19.onnx`, `voices.json`, and create `server/voices.bin.npz`.

2.  **Client Setup (Raspberry Pi):**
    ```bash
    cd client
    pip install -r requirements.txt
    ```
    *   Ensure `wekws` is accessible. You might need to set `PYTHONPATH`.

## Running the System

1.  **Start the Server:**
    ```bash
    # From project root
    python -m server.main
    ```
    The server will start on `0.0.0.0:8000`.

2.  **Start the Client:**
    ```bash
    # From project root
    python -m client.main --server_uri ws://<SERVER_IP>:8000/ws --checkpoint .\exp\wake_mdtc_noaug_avg\2.pt --config .\exp\wake_mdtc_noaug_avg\config.yaml
    ```
    *   Replace `<SERVER_IP>` with the IP address of your server.
    *   Adjust checkpoint/config paths if necessary.

## Usage

1.  Wait for the "Waiting for wakeword..." message.
2.  Say the wakeword.
3.  The client will switch to "Active Mode" and record for 5 seconds.
4.  The server will process the audio (STT -> LLM -> TTS).
5.  The client will play the response.

## Troubleshooting

*   **Audio Issues:** Check `sounddevice` settings and default devices.
*   **Connection Refused:** Check firewall settings and IP address.
*   **Missing Models:** Ensure `wekws` checkpoint and `kokoro` ONNX files are in the correct paths.
