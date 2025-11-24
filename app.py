# # app.py
# import certifi
# import ssl
# ssl_context = ssl.create_default_context(cafile=certifi.where())

# import streamlit as st

# from audio_utils import record_audio, save_audio_temp
# from stt_groq import transcribe
# from translate_utils import translate
# from sound_detector import detect_event

# st.set_page_config(page_title="HearMate", layout="wide")

# st.title("👂 HearMate - Assistive AI (Laptop MVP)")

# duration = st.slider("Recording duration (seconds)", 2, 10, 5)

# if st.button("Record & Process"):
#     audio, fs = record_audio(duration)
#     wav_path = save_audio_temp(audio, fs)

#     st.info("Processing speech-to-text...")
#     text = transcribe(wav_path)
#     st.write("### 📝 Captions")
#     st.success(text)

#     translated = translate(text, "es")
#     st.write("### 🌎 Spanish Translation")
#     st.write(translated)

#     st.info("Detecting alerts...")
#     alert, score = detect_event(wav_path)

#     if alert:
#         st.error(f"🚨 ALERT! Critical sound detected. Score: {score:.3f}")
#     else:
#         st.success(f"✅ No alert. Score: {score:.3f}")

import streamlit as st
import soundfile as sf
import tempfile

from stt_groq import transcribe
from translate_utils import translate
from sound_detector import detect_event
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Metrics
recordings_total = Counter("hearmate_recordings_total", "Total recordings processed")
stt_latency = Histogram("hearmate_stt_latency_seconds", "STT processing time")
groq_errors = Counter("hearmate_groq_errors_total", "Errors during Groq API calls")
cpu_temp = Gauge("hearmate_cpu_temp_celsius", "CPU Temperature")

# Start Prometheus metrics server on port 9000
start_http_server(9000)


st.set_page_config(page_title="HearMate – Assistive AI", layout="wide")

st.title("👂 HearMate – Assistive AI (Docker MVP)")
st.write("Upload an audio file (WAV, MP3, M4A) to process captions + alerts.")

uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])

if uploaded_file is not None:
    # Save uploaded file to temporary location
    

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    st.audio(tmp_path)

    st.info("Transcribing using Groq Whisper...")
    # text = transcribe(tmp_path)
    with stt_latency.time():
        text = transcribe(tmp_path)

    recordings_total.inc()

    st.subheader("📝 Captions")
    st.success(text)

    st.info("Translating to Spanish...")
    translated = translate(text, "es")
    st.subheader("🌎 Spanish Translation")
    st.write(translated)

    st.info("Running sound event detection...")
    alert, score = detect_event(tmp_path)

    recordings_total.inc()

    if alert:
        st.error(f"🚨 ALERT DETECTED! (score: {score:.3f})")
    else:
        st.success(f"✅ No alert detected. (score: {score:.3f})")
