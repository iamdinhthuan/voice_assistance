import sys
import collections
import queue
import time
import numpy as np
import sounddevice as sd
import torch
import torchaudio.compliance.kaldi as kaldi
import yaml
import os

# Adjust path to ensure wekws can be imported
# Structure is: project_root/client/wakeword_listener.py
#               project_root/wekws/wekws/__init__.py
# We need to add project_root/wekws to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
wekws_path = os.path.join(project_root, 'wekws')
if wekws_path not in sys.path:
    sys.path.append(wekws_path)

from wekws.model.kws_model import init_model
from wekws.utils.checkpoint import load_checkpoint

class WakewordListener:
    def __init__(self, checkpoint_path, config_path, threshold=0.7, buffer_sec=2.0, chunk_sec=0.5, device_index=None):
        self.checkpoint_path = checkpoint_path
        self.config_path = config_path
        self.threshold = threshold
        self.buffer_sec = buffer_sec
        self.chunk_sec = chunk_sec
        self.device_index = device_index
        
        self.device = torch.device("cpu")
        self.model = self._load_kws_model()
        self.input_dim = self.model.idim
        self.sample_rate = 16000
        
    def _load_kws_model(self):
        with open(self.config_path, "r") as fin:
            configs = yaml.load(fin, Loader=yaml.FullLoader)
        
        # Fix CMVN path to be absolute relative to wekws root
        if "model" in configs and "cmvn" in configs["model"] and "cmvn_file" in configs["model"]["cmvn"]:
            cmvn_file = configs["model"]["cmvn"]["cmvn_file"]
            if not os.path.isabs(cmvn_file):
                # Assuming cmvn_file is relative to wekws root
                # wekws_path is defined globally above
                abs_cmvn_path = os.path.join(wekws_path, cmvn_file)
                if os.path.exists(abs_cmvn_path):
                    configs["model"]["cmvn"]["cmvn_file"] = abs_cmvn_path
                else:
                    print(f"Warning: CMVN file not found at {abs_cmvn_path}")

        model = init_model(configs["model"])
        load_checkpoint(model, self.checkpoint_path)
        model = model.to(self.device)
        model.eval()
        return model

    def _compute_fbank(self, waveform, sample_rate, feat_dim=40):
        waveform = waveform * (1 << 15)
        mat = kaldi.fbank(
            waveform,
            num_mel_bins=feat_dim,
            frame_length=25,
            frame_shift=10,
            dither=0.0,
            energy_floor=0.0,
            sample_frequency=sample_rate,
        )
        return mat

    def listen(self):
        """
        Blocks until wakeword is detected.
        """
        buffer_samples = int(self.buffer_sec * self.sample_rate)
        chunk_samples = int(self.chunk_sec * self.sample_rate)
        audio_buf = collections.deque(maxlen=buffer_samples)
        q_in = queue.Queue()

        def audio_cb(indata, frames, time_info, status):
            if status:
                print(status, file=sys.stderr)
            q_in.put(indata.copy())

        print(f"Waiting for wakeword... (threshold={self.threshold})")
        
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=chunk_samples,
            callback=audio_cb,
            device=self.device_index,
        ):
            cooldown = self.buffer_sec
            last_trigger = 0.0
            
            while True:
                try:
                    chunk = q_in.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                audio_buf.extend(chunk[:, 0])
                if len(audio_buf) < chunk_samples:
                    continue
                
                waveform = torch.tensor(np.array(audio_buf), dtype=torch.float32).unsqueeze(0)
                feats = self._compute_fbank(waveform, self.sample_rate, feat_dim=self.input_dim)
                feats = feats.unsqueeze(0)
                
                with torch.no_grad():
                    logits, _ = self.model(feats)
                    probs = logits.squeeze(0).squeeze(1)
                    max_prob = float(probs.max().item())
                
                now = time.time()
                if max_prob >= self.threshold and (now - last_trigger) > cooldown:
                    print(f"\nWakeword detected! prob={max_prob:.3f}")
                    return True
                else:
                    print(f"prob={max_prob:.3f}", end="\r", flush=True)
