import streamlit as st
from groq import Groq
import soundfile as sf
import numpy as np
import tempfile
import os
from datetime import datetime
from collections import deque

# ==================== CONFIGURATION ====================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("⚠️ GROQ_API_KEY not found. Please configure it in Streamlit secrets.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# Important keywords for context-aware alerts
IMPORTANT_KEYWORDS = {
    'names': ['help', 'emergency', 'fire', 'stop', 'wait', 'danger'],
    'questions': ['what', 'who', 'where', 'when', 'why', 'how'],
    'urgency': ['quick', 'hurry', 'now', 'urgent', 'important'],
    'smart_home': ['doorbell', 'ring', 'knock', 'alarm', 'timer', 'phone']
}

# ==================== UI STYLING ====================
def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        * { font-family: 'Inter', sans-serif; }
        
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .modern-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            border-radius: 20px;
            color: white;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        
        .modern-header h1 {
            font-size: 48px;
            font-weight: 700;
            margin: 0;
        }
        
        .caption-box {
            background: linear-gradient(135deg, #e8f4f8 0%, #ffffff 100%);
            border-left: 5px solid #667eea;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            font-size: 18px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .alert-box-urgent {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            border-left: 5px solid #c92a2a;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            color: white;
            box-shadow: 0 4px 15px rgba(255,0,0,0.3);
        }
        
        .alert-box-question {
            background: linear-gradient(135deg, #ffd93d 0%, #ffb703 100%);
            border-left: 5px solid #f77f00;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            color: #1a1a1a;
            box-shadow: 0 4px 15px rgba(255,193,7,0.3);
        }
        
        .metric-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            color: #667eea;
        }
        
        .metric-label {
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
        }
        </style>
    """, unsafe_allow_html=True)

# ==================== AUDIO PROCESSING ====================
def transcribe_audio(audio_data, sample_rate=16000):
    try:
        if audio_data.ndim > 1:
            mono_audio = np.mean(audio_data, axis=1)
        else:
            mono_audio = audio_data
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            sf.write(tmp.name, mono_audio, sample_rate)
            tmp_path = tmp.name
        
        with open(tmp_path, "rb") as f:
            result = client.audio.transcriptions.create(
                file=(tmp_path, f.read()),
                model="whisper-large-v3",
                response_format="json"
            )
        
        os.unlink(tmp_path)
        return result.text.strip() if result.text.strip() else "[No speech detected]"
    except Exception as e:
        return f"[Error: {str(e)}]"

def analyze_speech_context(text):
    if not text or len(text) < 3:
        return None
    
    text_lower = text.lower()
    context = {
        'has_question': False,
        'has_urgency': False,
        'has_smart_home': False,
        'importance_score': 0,
        'keywords_found': []
    }
    
    for q_word in IMPORTANT_KEYWORDS['questions']:
        if q_word in text_lower:
            context['has_question'] = True
            context['importance_score'] += 2
            break
    
    for urgent_word in IMPORTANT_KEYWORDS['urgency']:
        if urgent_word in text_lower:
            context['has_urgency'] = True
            context['importance_score'] += 3
    
    for sh_word in IMPORTANT_KEYWORDS['smart_home']:
        if sh_word in text_lower:
            context['has_smart_home'] = True
            context['importance_score'] += 3
    
    return context if context['importance_score'] > 0 else None

def detect_smart_home_events(text):
    if not text or len(text) < 3:
        return None
    
    text_lower = text.lower()
    events = {
        'doorbell': ['doorbell', 'door bell', 'ring'],
        'phone': ['phone', 'ringing', 'call'],
        'alarm': ['alarm', 'beeping', 'timer'],
        'smoke': ['smoke', 'fire alarm'],
    }
    
    detected = []
    for event_type, keywords in events.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected.append({'type': event_type, 'keyword': keyword})
                break
    
    return detected if detected else None

# ==================== STREAMLIT APP ====================
st.set_page_config(page_title="HearMate Cloud", page_icon="🎧", layout="wide")
load_custom_css()

# Initialize session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# Header
st.markdown("""
    <div class='modern-header'>
        <h1>🎧 HearMate Cloud</h1>
        <p>AI-Powered Audio Analysis (Cloud Demo Version)</p>
    </div>
""", unsafe_allow_html=True)

# Info banner
st.info("""
    ☁️ **Cloud Demo Version** - This version runs on Streamlit Cloud and supports audio file uploads only.
    For live microphone recording, please run the full version locally.
""")

# Sidebar
with st.sidebar:
    st.markdown("### 🎧 HearMate Cloud")
    st.markdown("---")
    st.markdown("### ✨ Features")
    enable_captions = st.checkbox("💬 Transcription", value=True)
    enable_context_aware = st.checkbox("🧠 Smart Context", value=True)
    enable_smart_home = st.checkbox("🏠 Smart Home Detection", value=True)
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    caption_font_size = st.slider("Caption Font Size", 12, 32, 20)
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.analysis_history.clear()
        st.rerun()

# Main content
tab1, tab2 = st.tabs(["📤 Upload & Analyze", "📊 History"])

with tab1:
    st.markdown("### Upload Audio File")
    
    uploaded = st.file_uploader(
        "Choose an audio file",
        type=["wav", "mp3", "m4a", "flac", "ogg"],
        help="Upload any audio file for AI-powered transcription and analysis"
    )
    
    if uploaded:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.audio(uploaded)
        
        with col2:
            st.info(f"""
                **File:** {uploaded.name}
                **Size:** {uploaded.size / 1024:.1f} KB
            """)
        
        if st.button("🎯 Analyze Audio", type="primary", use_container_width=True):
            with st.spinner("🎧 Processing audio..."):
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                        tmp.write(uploaded.read())
                        temp_path = tmp.name
                    
                    # Read audio
                    audio_data, sr = sf.read(temp_path)
                    
                    # Transcribe
                    if enable_captions:
                        transcript = transcribe_audio(audio_data, sr)
                        
                        # Save to history
                        analysis = {
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'filename': uploaded.name,
                            'transcript': transcript,
                            'context': None,
                            'smart_home': None
                        }
                        
                        st.success("✅ Analysis Complete!")
                        
                        # Display transcript
                        st.markdown(f"""
                            <div class='caption-box' style='font-size:{caption_font_size}px;'>
                                {transcript}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Context analysis
                        if enable_context_aware:
                            context = analyze_speech_context(transcript)
                            if context:
                                analysis['context'] = context
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Importance", f"{context['importance_score']}/10")
                                with col2:
                                    st.metric("Question?", "Yes" if context['has_question'] else "No")
                                with col3:
                                    st.metric("Urgent?", "Yes" if context['has_urgency'] else "No")
                                
                                if context['has_urgency']:
                                    st.markdown(f"""
                                        <div class='alert-box-urgent'>
                                            <h4>🚨 URGENT CONTENT DETECTED</h4>
                                            <p>This audio may contain time-sensitive information</p>
                                        </div>
                                    """, unsafe_allow_html=True)
                                elif context['has_question']:
                                    st.markdown(f"""
                                        <div class='alert-box-question'>
                                            <h4>❓ QUESTION DETECTED</h4>
                                            <p>This audio contains a question</p>
                                        </div>
                                    """, unsafe_allow_html=True)
                        
                        # Smart home detection
                        if enable_smart_home:
                            sh_events = detect_smart_home_events(transcript)
                            if sh_events:
                                analysis['smart_home'] = sh_events
                                st.warning(f"🏠 Smart Home Events Detected: {', '.join([e['type'] for e in sh_events])}")
                        
                        # Add to history
                        st.session_state.analysis_history.append(analysis)
                        
                        # Download option
                        st.download_button(
                            "📥 Download Transcript",
                            transcript,
                            f"transcript_{uploaded.name}.txt",
                            "text/plain",
                            use_container_width=True
                        )
                    
                    # Cleanup
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                
                except Exception as e:
                    st.error(f"❌ Error processing audio: {str(e)}")

with tab2:
    st.markdown("### 📊 Analysis History")
    
    if st.session_state.analysis_history:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>Total Files</div>
                    <div class='metric-value'>{len(st.session_state.analysis_history)}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            urgent_count = sum(1 for a in st.session_state.analysis_history 
                             if a['context'] and a['context']['has_urgency'])
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>Urgent</div>
                    <div class='metric-value'>{urgent_count}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            sh_count = sum(1 for a in st.session_state.analysis_history 
                         if a['smart_home'])
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>Smart Home</div>
                    <div class='metric-value'>{sh_count}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Display history
        for i, analysis in enumerate(reversed(st.session_state.analysis_history)):
            with st.expander(f"📄 {analysis['filename']} - {analysis['timestamp']}"):
                st.markdown(f"**Transcript:**")
                st.markdown(f"<div class='caption-box'>{analysis['transcript']}</div>", 
                          unsafe_allow_html=True)
                
                if analysis['context']:
                    st.info(f"Importance Score: {analysis['context']['importance_score']}/10")
                
                if analysis['smart_home']:
                    st.warning(f"🏠 Detected: {', '.join([e['type'] for e in analysis['smart_home']])}")
        
        # Export all
        all_transcripts = "\n\n".join([
            f"[{a['timestamp']}] {a['filename']}\n{a['transcript']}"
            for a in st.session_state.analysis_history
        ])
        
        st.download_button(
            "📥 Export All Transcripts",
            all_transcripts,
            "hearmate_all_transcripts.txt",
            "text/plain",
            use_container_width=True
        )
    else:
        st.info("No analysis history yet. Upload and analyze an audio file to get started!")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>🎧 HearMate Cloud v1.0</strong> — AI-Powered Audio Analysis</p>
        <p style='font-size: 14px;'>Built with Streamlit • Groq Whisper • Python</p>
        <p style='font-size: 12px; margin-top: 10px;'>
            <em>Making sound visible for everyone</em>
        </p>
    </div>
""", unsafe_allow_html=True)
