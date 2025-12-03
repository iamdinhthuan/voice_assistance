import os
import urllib.request
import json
import numpy as np

def download_file(url, dest_path):
    print(f"Downloading {url} to {dest_path}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print("Download complete.")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def convert_voices():
    print("Converting voices.json to voices.bin.npz...")
    try:
        with open("server/voices.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        voices = {}
        for name, embedding in data.items():
            voices[name] = np.array(embedding, dtype=np.float32)
            
        np.savez("server/voices.bin.npz", **voices)
        print("Conversion complete.")
    except Exception as e:
        print(f"Error converting voices: {e}")

def main():
    # Ensure server directory exists
    if not os.path.exists("server"):
        os.makedirs("server")

    # 1. Download Kokoro ONNX model
    kokoro_url = "https://huggingface.co/hexgrad/Kokoro-82M/resolve/e9d173129d407bf1378c402aba163de4dde2615e/kokoro-v0_19.onnx"
    kokoro_path = "server/kokoro-v0_19.onnx"
    if not os.path.exists(kokoro_path):
        download_file(kokoro_url, kokoro_path)
    else:
        print(f"{kokoro_path} already exists.")

    # 2. Download voices.json
    voices_url = "https://huggingface.co/NeuML/kokoro-base-onnx/resolve/main/voices.json"
    voices_path = "server/voices.json"
    if not os.path.exists(voices_path):
        download_file(voices_url, voices_path)
    else:
        print(f"{voices_path} already exists.")

    # 3. Convert voices.json to voices.bin.npz
    if os.path.exists(voices_path) and not os.path.exists("server/voices.bin.npz"):
        convert_voices()
    elif os.path.exists("server/voices.bin.npz"):
         print("server/voices.bin.npz already exists.")
    else:
        print("Skipping conversion because voices.json is missing.")

if __name__ == "__main__":
    main()
