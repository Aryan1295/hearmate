import requests
import os
import groq_errors

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_KEY = "PUT_YOUR_GROQ_API_KEY_HERE"

def transcribe(audio_path):
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    
    with open(audio_path, "rb") as f:
        files = {"file": (audio_path, f, "audio/wav")}
        data = {"model": "whisper-large-v3"}
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        
        res = requests.post(url, headers=headers, data=data, files=files)

    # If Groq returns an error

    if res.status_code != 200:
        groq_errors.inc()
        return f"[ERROR] Groq API responded with {res.status_code}: {res.text}"

    # If response JSON does not contain 'text'
    j = res.json()
    if "text" not in j:
        return f"[ERROR] Unexpected response: {j}"

    return j["text"]
