import asyncio
import argparse
import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from client.wakeword_listener import WakewordListener
from client.audio_handler import AudioHandler
from client.network_client import NetworkClient

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default=r".\exp\wake_mdtc_noaug_avg\2.pt", help="wakeword model checkpoint")
    parser.add_argument("--config", default=r".\exp\wake_mdtc_noaug_avg\config.yaml", help="wakeword model config")
    parser.add_argument("--server_uri", default="ws://localhost:8000/ws", help="server websocket uri")
    args = parser.parse_args()

    # Initialize components
    wakeword = WakewordListener(
        checkpoint_path=args.checkpoint,
        config_path=args.config,
        threshold=0.7
    )
    
    audio_handler = AudioHandler()
    network_client = NetworkClient(uri=args.server_uri)
    
    # Connect to server
    await network_client.connect()
    
    try:
        while True:
            # 1. Wait for Wakeword (Blocking)
            # Note: listen() is blocking, but we are in async main.
            # Ideally we run it in executor or it handles itself.
            # Our listen() is blocking. For simple loop, this is fine.
            print("\n--- Idle Mode ---")
            if wakeword.listen():
                print("--- Active Mode ---")
                
                # 2. Start Recording & Streaming
                audio_handler.start_recording()
                
                # We need to stream audio until... when?
                # The server has VAD. We can just stream for a fixed time or until server says stop?
                # Or we stream until silence is detected locally?
                # For simplicity, let's stream for a fixed duration or until silence (simple energy based).
                # Or better: stream until server sends back a response (which implies it detected end of speech).
                # But server needs end of speech to generate response.
                # So we rely on server VAD to detect end of speech.
                # But we need to know when to STOP sending.
                # Let's send for a fixed max duration (e.g. 5s) or until we get a response.
                
                # Actually, the server logic I wrote accumulates audio until silence.
                # But it doesn't tell client to stop.
                # So client should probably just record for X seconds or use local VAD.
                # Let's use a simple timeout for now: Record for 5 seconds.
                
                print("Recording command...")
                for _ in range(50): # 50 * 0.1s = 5 seconds (approx)
                    chunk = audio_handler.get_chunk()
                    if chunk:
                        await network_client.send_audio(chunk)
                    await asyncio.sleep(0.1)
                
                audio_handler.stop_recording()
                print("Finished recording. Waiting for response...")
                
                # 3. Wait for Response
                # We expect audio bytes back
                response = await network_client.receive()
                
                if response:
                    if isinstance(response, bytes):
                        print(f"Received audio response: {len(response)} bytes")
                        audio_handler.play_audio(response)
                    elif isinstance(response, str):
                        # Could be text message
                        print(f"Received text: {response}")
                        # If text, maybe audio follows?
                        # My server sends text then audio.
                        # So receive again.
                        response_audio = await network_client.receive()
                        if isinstance(response_audio, bytes):
                             audio_handler.play_audio(response_audio)
                
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        await network_client.close()

if __name__ == "__main__":
    asyncio.run(main())
