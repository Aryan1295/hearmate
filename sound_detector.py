import torch
import numpy as np
import soundfile as sf

model = torch.hub.load('harritaylor/torchvggish', 'vggish')
model.eval()

def load_audio_mono(file, target_sr=16000):
    audio, sr = sf.read(file)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)  # convert to mono

    if sr != target_sr:
        ratio = target_sr / sr
        audio = np.interp(
            np.linspace(0, len(audio), int(len(audio) * ratio)),
            np.arange(len(audio)),
            audio
        )

    return torch.tensor(audio, dtype=torch.float32).unsqueeze(0)

def detect_event(filename):
    wav = load_audio_mono(filename)

    with torch.no_grad():
        features = model(wav)

    score = features.mean().item()

    return (score > 0.10), score
