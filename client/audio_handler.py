import sounddevice as sd
import numpy as np
import queue
import sys

class AudioHandler:
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.q_rec = queue.Queue()
        self.recording = False

    def start_recording(self):
        self.recording = True
        self.q_rec = queue.Queue()
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='int16', # Record as int16 for easier sending
            callback=self._record_callback
        )
        self.stream.start()
        print("Recording started...")

    def stop_recording(self):
        self.recording = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        print("Recording stopped.")

    def _record_callback(self, indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        if self.recording:
            self.q_rec.put(bytes(indata))

    def get_chunk(self):
        try:
            return self.q_rec.get_nowait()
        except queue.Empty:
            return None

    def play_audio(self, audio_data: bytes):
        """
        Play raw audio bytes (int16).
        """
        # Convert bytes back to numpy array
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        print("Playing audio response...")
        sd.play(audio_np, self.sample_rate)
        sd.wait()
        print("Playback finished.")
