
🎧 HearMate — AI Hearing Assistant

Real-time speech-to-text, sound awareness & smart environment alerts.

📝 Abstract

HearMate is an AI-powered auditory awareness system built for individuals with hearing challenges, elderly users, and real-world safety monitoring. It listens to the environment in real time, converts speech to text using Groq Whisper, detects alarms, knocks, phone rings, and urgent cues, and visually displays live captions.

The project demonstrates end-to-end AI system lifecycle — data collection, model integration, context reasoning, UI deployment and future hardware scalability.

🔍 Problem Statement

Millions of users struggle to maintain awareness in dynamic environments due to hearing limitations. Existing aids amplify sound but fail to understand sound meaning or urgency.

HearMate solves this by transforming sound → understanding → actionable awareness.

🎯 Core Features
Feature	Description
🔴 Real-time transcription	Groq Whisper live captioning
🧠 Context Understanding	Detects questions, urgency, warnings
🏠 Smart Home Awareness	Doorbell, smoke alarm, phone ringing, water leak
🔊 Loud Sound Alerts	Firecracker, shouting, sudden noise spike
🔁 Rolling Caption Memory	Duplicate prevention & readable conversation history
↔ Direction Detection	LEFT / RIGHT / CENTER based on stereo signal
📏 Speaker Distance Estimation	Voice amplitude→distance mapping
📆 Predictive Scheduling	Reminds user before meetings, alarms, tasks
📱 Wearable Display Mode	Future integration for watch hardware
📤 Export Transcript	One-click save .txt history
⚙️ Tech Stack
Layer	Technology
Speech-to-Text	Groq Whisper-large-v3
Backend	Python
UI	Streamlit
Audio Processing	numpy, sounddevice, soundfile
Scheduling	Predictive alert queue system
📌 Workflow
🎤 Audio → Chunk Capture → Whisper Transcription
 → Context Analysis → Smart Event Detection
 → UI Alerts + Direction + Emotion + Loudness
 → (Optional) Wearable Output → Saved Transcript

🗂 Install & Run
git clone <repo_link>
cd HearMate
pip install -r requirements.txt
export GROQ_API_KEY="your_api_key_here"
streamlit run hearmate.py


Windows command:

setx GROQ_API_KEY "your_api_key_here"
streamlit run hearmate.py

🧠 Future Expansion (v2)

🚀 Offline Faster-Whisper
🚀 BLE vibration wristband
🚀 Always-on Raspberry Pi Home Node
🚀 Speaker recognition & diarization
🚀 Emergency escalation → SMS/IoT

💰 Hardware Proposal (For professors/funding)
Component	Cost
Raspberry Pi 5 / Zero	$60-$95
ReSpeaker Microphone Array	$25-$55
ESP32 BLE Wearable Unit	$10-$15
Edge TPU Accelerator	$95-$130
Estimated Prototype Budget	$240-$360 total
📎 Demo Material (Optional Attach)

🌐 Live App URL
🎥 Demo Video
📄 Poster PDF
📂 GitHub Repo
📱 QR Code for scanning

🏁 Summary

HearMate demonstrates how AI can expand perception, turning sound into text, warnings and meaning — not just volume. With future hardware integration, it becomes a real-world assistive product capable of improving accessibility, awareness and independence.
