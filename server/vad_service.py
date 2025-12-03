import torch
import numpy as np

class VADService:
    def __init__(self, threshold=0.5, sampling_rate=16000):
        self.model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                           model='silero_vad',
                                           force_reload=False,
                                           onnx=False)
        (self.get_speech_timestamps,
         self.save_audio,
         self.read_audio,
         self.VADIterator,
         self.collect_chunks) = utils
        
        self.threshold = threshold
        self.sampling_rate = sampling_rate
        self.vad_iterator = self.VADIterator(self.model)
        
    def process_chunk(self, audio_chunk: bytes) -> dict:
        """
        Process a raw audio chunk (bytes) and return VAD status.
        Assumes 16kHz, 16-bit mono audio.
        """
        # Convert bytes to float32 tensor
        audio_int16 = np.frombuffer(audio_chunk, dtype=np.int16)
        audio_float32 = audio_int16.astype(np.float32) / 32768.0
        tensor = torch.from_numpy(audio_float32)
        
        # Get speech probability/status
        # VADIterator keeps state, so we just feed it chunks
        speech_dict = self.vad_iterator(tensor, return_seconds=True)
        
        # vad_iterator returns a dict when a speech segment starts or ends
        # e.g., {'start': 0.5} or {'end': 1.2}
        # If nothing interesting happens, it returns None
        
        return speech_dict

    def reset(self):
        self.vad_iterator.reset_states()
