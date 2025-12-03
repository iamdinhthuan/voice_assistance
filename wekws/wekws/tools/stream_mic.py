#!/usr/bin/env python3
"""
Simple realtime wake word monitor from microphone.

Example:
PYTHONPATH=. python -m wekws.tools.stream_mic \
  --checkpoint exp/wake_ds_tcn/19.pt \
  --config exp/wake_ds_tcn/config.yaml \
  --threshold 0.7
"""

import argparse
import collections
import queue
import sys
import time

import numpy as np
import sounddevice as sd
import torch
import torchaudio
import torchaudio.compliance.kaldi as kaldi
import yaml

from wekws.model.kws_model import init_model
from wekws.utils.checkpoint import load_checkpoint


def load_kws_model(config_path, ckpt_path, device):
    with open(config_path, "r") as fin:
        configs = yaml.load(fin, Loader=yaml.FullLoader)
    model = init_model(configs["model"])
    load_checkpoint(model, ckpt_path)
    model = model.to(device)
    model.eval()
    return model


def compute_fbank(waveform, sample_rate, feat_dim=40):
    """Return fbank features Tensor[T, D]."""
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True, help="trained model pt")
    parser.add_argument("--config", required=True, help="model config yaml")
    parser.add_argument(
        "--threshold", type=float, default=0.7, help="wake prob threshold"
    )
    parser.add_argument(
        "--buffer_sec",
        type=float,
        default=2.0,
        help="sliding window seconds for detection",
    )
    parser.add_argument(
        "--chunk_sec",
        type=float,
        default=0.5,
        help="audio chunk size seconds for processing",
    )
    parser.add_argument(
        "--device_index", type=int, default=None, help="sounddevice input index"
    )
    args = parser.parse_args()

    device = torch.device("cpu")
    torch.set_num_threads(max(1, torch.get_num_threads()))
    model = load_kws_model(args.config, args.checkpoint, device)
    input_dim = model.idim

    sample_rate = 16000
    buffer_samples = int(args.buffer_sec * sample_rate)
    chunk_samples = int(args.chunk_sec * sample_rate)
    audio_buf = collections.deque(maxlen=buffer_samples)
    q_in = queue.Queue()

    def audio_cb(indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        q_in.put(indata.copy())

    print(
        f"Listening... threshold={args.threshold} sr={sample_rate} "
        f"buffer={args.buffer_sec}s chunk={args.chunk_sec}s"
    )
    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
        blocksize=chunk_samples,
        callback=audio_cb,
        device=args.device_index,
    ):
        last_trigger = 0.0
        cooldown = args.buffer_sec
        while True:
            try:
                chunk = q_in.get(timeout=1.0)
            except queue.Empty:
                continue
            audio_buf.extend(chunk[:, 0])
            if len(audio_buf) < chunk_samples:
                continue
            waveform = torch.tensor(np.array(audio_buf), dtype=torch.float32).unsqueeze(0)
            feats = compute_fbank(waveform, sample_rate, feat_dim=input_dim)
            feats = feats.unsqueeze(0)  # (1, T, D)
            with torch.no_grad():
                logits, _ = model(feats)
                probs = logits.squeeze(0).squeeze(1)  # (T,)
                max_prob = float(probs.max().item())
            now = time.time()
            if max_prob >= args.threshold and (now - last_trigger) > cooldown:
                print(
                    f"[TRIGGER] prob={max_prob:.3f} "
                    f"time={time.strftime('%H:%M:%S')}"
                )
                last_trigger = now
            else:
                print(f"prob={max_prob:.3f}", end="\r", flush=True)


if __name__ == "__main__":  # pragma: no cover
    main()
