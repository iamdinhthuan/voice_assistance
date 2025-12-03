import json
import numpy as np
import os

def convert_voices():
    print("Loading voices.json...")
    with open("server/voices.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"Found {len(data)} voices.")
    
    voices = {}
    for name, embedding in data.items():
        # Embedding is a list of lists or similar. 
        # Kokoro expects numpy array.
        # Based on voices.json header "af": [[...]], it looks like 2D array?
        # Let's convert to float32 array.
        voices[name] = np.array(embedding, dtype=np.float32)
        
    print("Saving to server/voices.bin...")
    # Use savez to save as compressed npz (or uncompressed)
    # We name it .bin because that's what some docs suggested, but np.load handles it.
    np.savez("server/voices.bin", **voices)
    print("Conversion complete.")

if __name__ == "__main__":
    convert_voices()
