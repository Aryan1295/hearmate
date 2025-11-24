import sounddevice as sd
import soundfile as sf

def record_wav(filename="output.wav", duration=10, samplerate=16000):
    print("🎙️ Recording...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    sf.write(filename, audio, samplerate)
    print(f"✅ Saved: {filename}")

if __name__ == "__main__":
    record_wav()
