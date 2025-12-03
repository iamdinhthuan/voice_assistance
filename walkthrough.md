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
    *   **Install System Dependencies:**
        ```bash
        sudo apt-get update
        sudo apt-get install espeak-ng portaudio19-dev python3-pyaudio python3-full
        ```
    *   **Create and Activate Virtual Environment (Recommended):**
        Raspberry Pi OS Bookworm requires a virtual environment for pip.
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   **Install Python Requirements:**
        ```bash
        cd client
        pip install -r requirements.txt
        ```
    *   **Set PYTHONPATH (Important):**
        Since `wekws` is included in this repository, you need to tell Python where to find it.
        ```bash
        export PYTHONPATH=$PYTHONPATH:$(pwd)/../wekws
        ```
        *(Run this from the `client` directory, or adjust path accordingly)*

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
    python -m client.main --server_uri ws://<SERVER_IP>:8000/ws --checkpoint wekws/exp/wake_mdtc_noaug_avg/2.pt --config wekws/exp/wake_mdtc_noaug_avg/config.yaml
    ```
    *   **Note:** Use forward slashes `/` for paths on Linux/Raspberry Pi.
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
*   **"Unable to locate package" Error:**
    *   Run `sudo apt-get update --fix-missing`.
    *   Try searching for the package: `apt-cache search espeak`.
*   **"Unable to locate package" Error (Advanced Fix):**
    If the above doesn't work, your package lists might be corrupted. Try this "nuclear" option:
    ```bash
    sudo rm -rf /var/lib/apt/lists/*
    sudo apt-get clean
    sudo apt-get update
    ```
    Then try installing again:
    ```bash
    sudo apt-get install portaudio19-dev python3-pyaudio
    ```

*   **"fatal error: portaudio.h: No such file or directory":**
    This means the development headers are missing. You MUST install `portaudio19-dev`:
    ```bash
    sudo apt-get install portaudio19-dev
    ```
