# audio_utils.py
import sounddevice as sd
import numpy as np
import soundfile as sf
import tempfile

def record_audio(duration=5, fs=16000):
    print("🎙️ Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=np.int16)
    sd.wait()
    return audio, fs

def save_audio_temp(audio, fs):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(tmp.name, audio, fs)
    return tmp.name
