import websockets
import asyncio
import json

class NetworkClient:
    def __init__(self, uri="ws://localhost:8000/ws"):
        self.uri = uri
        self.websocket = None

    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.uri)
            print(f"Connected to server at {self.uri}")
        except Exception as e:
            print(f"Connection failed: {e}")

    async def send_audio(self, audio_data: bytes):
        if self.websocket:
            await self.websocket.send(audio_data) # Send raw bytes

    async def send_text(self, text: str):
        if self.websocket:
            message = json.dumps({"text": text})
            await self.websocket.send(message)

    async def receive(self):
        if self.websocket:
            try:
                message = await self.websocket.recv()
                return message
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                return None
        return None

    async def close(self):
        if self.websocket:
            await self.websocket.close()
