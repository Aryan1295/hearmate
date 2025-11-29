import streamlit as st
from groq import Groq
import soundfile as sf
import numpy as np
import tempfile
import os
from datetime import datetime, timedelta
from collections import deque
import json

# ==================== CONFIGURATION ====================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("⚠️ GROQ_API_KEY not found. Please configure it in Streamlit secrets.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

CAPTION_HISTORY_SIZE = 10

# Important keywords for context-aware alerts
IMPORTANT_KEYWORDS = {
    'names': ['help', 'emergency', 'fire', 'stop', 'wait', 'danger', 'careful', 'watch out'],
    'questions': ['what', 'who', 'where', 'when', 'why', 'how', 'can you', 'could you', 'would you'],
    'locations': ['door', 'phone', 'behind', 'front', 'left', 'right', 'upstairs', 'downstairs'],
    'urgency': ['quick', 'hurry', 'now', 'urgent', 'important', 'immediately', 'asap'],
    'smart_home': ['doorbell', 'ring', 'knock', 'alarm', 'timer', 'phone', 'beep', 'smoke', 'water', 'leak']
}

# ==================== ENHANCED UI STYLING ====================
def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
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
            animation: fadeIn 0.5s ease-in;
        }
        
        .modern-header h1 {
            font-size: 48px;
            font-weight: 700;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .modern-header p {
            font-size: 18px;
            opacity: 0.9;
            margin-top: 10px;
        }
        
        .caption-box {
            background: linear-gradient(135deg, #e8f4f8 0%, #ffffff 100%);
            border-left: 5px solid #667eea;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            font-size: 18px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            animation: slideIn 0.3s ease-out;
        }
        
        .caption-box:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        .alert-box-urgent {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            border-left: 5px solid #c92a2a;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            color: white;
            box-shadow: 0 4px 15px rgba(255,0,0,0.3);
            animation: pulse 1s infinite;
        }
        
        .alert-box-question {
            background: linear-gradient(135deg, #ffd93d 0%, #ffb703 100%);
            border-left: 5px solid #f77f00;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            color: #1a1a1a;
            box-shadow: 0 4px 15px rgba(255,193,7,0.3);
            animation: slideIn 0.3s ease-out;
        }
        
        .alert-box-smart-home {
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
            border-left: 5px solid #0e7490;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            color: white;
            box-shadow: 0 4px 15px rgba(6,182,212,0.3);
            animation: slideIn 0.3s ease-out;
        }
        
        .metric-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
        }
        
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            color: #667eea;
            margin: 10px 0;
        }
        
        .metric-label {
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .direction-indicator {
            font-size: 64px;
            text-align: center;
            margin: 20px 0;
            animation: bounce 1s infinite;
        }
        
        .wearable-display {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 50px;
            border-radius: 30px;
            text-align: center;
            color: white;
            min-height: 400px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 15px 50px rgba(0,0,0,0.4);
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideIn {
            from { 
                opacity: 0;
                transform: translateX(-20px);
            }
            to { 
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .status-live {
            background: #ff4444;
            color: white;
            animation: pulse 1.5s infinite;
        }
        
        .status-active {
            background: #4caf50;
            color: white;
        }
        
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        section[data-testid="stSidebar"] .stMarkdown {
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

# ==================== PREDICTIVE ALERTS ====================
class PredictiveAlertSystem:
    def __init__(self):
        self.schedule = []
    
    def add_schedule_item(self, time_str, event, minutes_before=5):
        try:
            event_time = datetime.strptime(time_str, "%H:%M").time()
            today = datetime.now().date()
            event_datetime = datetime.combine(today, event_time)
            
            self.schedule.append({
                'time': event_datetime,
                'event': event,
                'minutes_before': minutes_before,
                'alerted': False
            })
        except:
            pass
    
    def check_upcoming_events(self):
        now = datetime.now()
        alerts = []
        
        for item in self.schedule:
            if not item['alerted']:
                time_until = (item['time'] - now).total_seconds() / 60
                
                if 0 <= time_until <= item['minutes_before']:
                    alerts.append({
                        'event': item['event'],
                        'time': item['time'].strftime("%H:%M"),
                        'minutes': int(time_until)
                    })
                    item['alerted'] = True
        
        return alerts
    
    def clear_old_events(self):
        now = datetime.now()
        self.schedule = [item for item in self.schedule if item['time'] > now]

# ==================== AUDIO PROCESSING ====================
def transcribe_audio(audio_data, sample_rate=16000):
    try:
        if audio_data.ndim > 1:
            mono_audio = np.mean(audio_data, axis=1)
        else:
            mono_audio = audio_data
        
        if np.max(np.abs(mono_audio)) < 0.001:
            return "[Silent audio detected]"
        
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

def calculate_direction(audio_chunk):
    if audio_chunk.ndim < 2 or audio_chunk.shape[1] < 2:
        return "⬆️ MONO", 0.5
    
    left_channel = audio_chunk[:, 0]
    right_channel = audio_chunk[:, 1]
    
    left_energy = np.sum(left_channel ** 2)
    right_energy = np.sum(right_channel ** 2)
    total_energy = left_energy + right_energy
    
    if total_energy < 1e-6:
        return "⬆️ CENTER", 0.5
    
    balance = right_energy / total_energy
    
    if balance < 0.4:
        direction = "⬅️ LEFT"
    elif balance > 0.6:
        direction = "➡️ RIGHT"
    else:
        direction = "⬆️ CENTER"
    
    return direction, balance

def detect_loud_sounds(audio_chunk, threshold=0.1):
    if audio_chunk is None or not isinstance(audio_chunk, np.ndarray):
        return []
    
    try:
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        alerts = []
        if rms > threshold:
            alerts.append(("Loud Sound Detected", rms))
        return alerts
    except:
        return []

def analyze_music_rhythm(audio_chunk, sample_rate=16000):
    if audio_chunk is None or not isinstance(audio_chunk, np.ndarray):
        return None
    
    try:
        if audio_chunk.ndim > 1:
            mono_audio = np.mean(audio_chunk, axis=1)
        else:
            mono_audio = audio_chunk
        
        frame_length = int(0.05 * sample_rate)
        hop_length = int(0.025 * sample_rate)
        
        energy_values = []
        for i in range(0, len(mono_audio) - frame_length, hop_length):
            frame = mono_audio[i:i+frame_length]
            energy = np.sum(frame ** 2)
            energy_values.append(energy)
        
        energy_values = np.array(energy_values)
        
        if len(energy_values) > 0:
            mean_energy = np.mean(energy_values)
            std_energy = np.std(energy_values)
            threshold = mean_energy + 0.5 * std_energy
            
            beats = energy_values > threshold
            beat_count = np.sum(beats)
            max_possible_beats = len(energy_values)
            rhythm_intensity = int((beat_count / max_possible_beats) * 100) if max_possible_beats > 0 else 0
            
            if rhythm_intensity > 70:
                pattern = "🔴 Strong - Fast vibrations"
            elif rhythm_intensity > 40:
                pattern = "🟡 Moderate - Medium vibrations"
            elif rhythm_intensity > 15:
                pattern = "🟢 Gentle - Slow vibrations"
            else:
                pattern = "⚪ Minimal - Very light vibrations"
            
            return {
                'intensity': rhythm_intensity,
                'pattern': pattern,
                'beat_count': beat_count
            }
        
        return None
    except:
        return None

def analyze_speech_context(text):
    if not text or len(text) < 3:
        return None
    
    text_lower = text.lower()
    context = {
        'has_question': False,
        'has_urgency': False,
        'has_location': False,
        'has_name_call': False,
        'has_smart_home': False,
        'importance_score': 0,
        'keywords_found': []
    }
    
    for q_word in IMPORTANT_KEYWORDS['questions']:
        if q_word in text_lower:
            context['has_question'] = True
            context['importance_score'] += 2
            context['keywords_found'].append(q_word)
            break
    
    for urgent_word in IMPORTANT_KEYWORDS['urgency']:
        if urgent_word in text_lower:
            context['has_urgency'] = True
            context['importance_score'] += 3
            context['keywords_found'].append(urgent_word)
    
    for loc_word in IMPORTANT_KEYWORDS['locations']:
        if loc_word in text_lower:
            context['has_location'] = True
            context['importance_score'] += 1
            context['keywords_found'].append(loc_word)
    
    for name_word in IMPORTANT_KEYWORDS['names']:
        if name_word in text_lower:
            context['has_name_call'] = True
            context['importance_score'] += 3
            context['keywords_found'].append(name_word)
    
    for sh_word in IMPORTANT_KEYWORDS['smart_home']:
        if sh_word in text_lower:
            context['has_smart_home'] = True
            context['importance_score'] += 3
            context['keywords_found'].append(sh_word)
    
    if '?' in text:
        context['has_question'] = True
        context['importance_score'] += 1
    
    return context if context['importance_score'] > 0 else None

def detect_speaker_emotion(text):
    if not text or len(text) < 3:
        return None
    
    text_lower = text.lower()
    positive_words = ['happy', 'great', 'good', 'excellent', 'wonderful', 'love', 'thanks', 'thank you', 'awesome']
    negative_words = ['sad', 'bad', 'terrible', 'hate', 'angry', 'mad', 'upset', 'disappointed']
    excited_words = ['wow', 'amazing', 'incredible', 'fantastic', 'yay', 'yes']
    
    has_exclamation = '!' in text
    emotion = None
    confidence = 0
    
    for word in positive_words:
        if word in text_lower:
            emotion = "😊 Positive"
            confidence += 1
    
    for word in negative_words:
        if word in text_lower:
            emotion = "😟 Negative"
            confidence += 1
    
    for word in excited_words:
        if word in text_lower:
            emotion = "🎉 Excited"
            confidence += 1
    
    if has_exclamation:
        if not emotion:
            emotion = "❗ Emphasis"
        confidence += 1
    
    return {'emotion': emotion, 'confidence': confidence} if emotion else None

def estimate_speaker_distance(audio_chunk):
    if audio_chunk is None or not isinstance(audio_chunk, np.ndarray):
        return None
    
    try:
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        
        if rms > 0.15:
            return "🔴 Very Close (< 1ft)"
        elif rms > 0.08:
            return "🟡 Close (1-3ft)"
        elif rms > 0.03:
            return "🟢 Moderate (3-6ft)"
        elif rms > 0.01:
            return "🔵 Far (6-10ft)"
        else:
            return "⚪ Very Far (>10ft)"
    except:
        return None

def detect_smart_home_events(text):
    if not text or len(text) < 3:
        return None
    
    text_lower = text.lower()
    
    events = {
        'doorbell': ['doorbell', 'door bell', 'someone at door', 'ring ring'],
        'phone': ['phone', 'ringing', 'call', 'calling'],
        'alarm': ['alarm', 'beeping', 'beep beep', 'timer'],
        'smoke': ['smoke', 'fire alarm', 'smoke detector'],
        'water': ['water', 'leak', 'drip', 'flooding'],
        'knock': ['knock', 'knocking', 'bang'],
        'appliance': ['oven', 'microwave', 'washer', 'dryer', 'dishwasher']
    }
    
    detected = []
    for event_type, keywords in events.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected.append({
                    'type': event_type,
                    'keyword': keyword,
                    'icon': get_smart_home_icon(event_type)
                })
                break
    
    return detected if detected else None

def get_smart_home_icon(event_type):
    icons = {
        'doorbell': '🔔',
        'phone': '📞',
        'alarm': '⏰',
        'smoke': '🔥',
        'water': '💧',
        'knock': '🚪',
        'appliance': '🏠'
    }
    return icons.get(event_type, '🔔')

def create_conversation_summary(caption_history):
    if not caption_history or len(caption_history) < 2:
        return None
    
    total_captions = len(caption_history)
    total_words = sum(len(caption.split()) for caption in caption_history)
    avg_words_per_caption = total_words / total_captions if total_captions > 0 else 0
    questions = sum(1 for caption in caption_history if '?' in caption or any(q in caption.lower() for q in ['what', 'who', 'where', 'when', 'why', 'how']))
    
    return {
        'total_captions': total_captions,
        'total_words': total_words,
        'avg_words_per_caption': avg_words_per_caption,
        'questions_asked': questions
    }

# ==================== STREAMLIT APP ====================
st.set_page_config(page_title="HearMate Cloud", page_icon="🎧", layout="wide")
load_custom_css()

# Initialize session state
if 'caption_history' not in st.session_state:
    st.session_state.caption_history = deque(maxlen=CAPTION_HISTORY_SIZE)
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'smart_home_alerts' not in st.session_state:
    st.session_state.smart_home_alerts = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'custom_keywords' not in st.session_state:
    st.session_state.custom_keywords = []
if 'predictive_system' not in st.session_state:
    st.session_state.predictive_system = PredictiveAlertSystem()
if 'wearable_caption' not in st.session_state:
    st.session_state.wearable_caption = ""

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 30px 20px; background: rgba(255,255,255,0.1); border-radius: 15px; margin-bottom: 20px;'>
            <h1 style='color: white; font-size: 36px; margin: 0;'>🎧 HearMate</h1>
            <p style='color: rgba(255,255,255,0.9); font-size: 16px; margin-top: 10px;'>AI-Powered Audio Analysis</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("☁️ **Cloud Version** - File upload mode only")
    
    st.markdown("---")
    st.markdown("### ✨ Features",GROQ_API_KEY)
    enable_captions = st.checkbox("💬 Live Captions", value=True)
    enable_direction = st.checkbox("📍 Direction Detection", value=True)
    enable_sound_alert = st.checkbox("🔔 Loud Sound Alerts", value=True)
    enable_music_vibration = st.checkbox("🎵 Music Vibration", value=True)
    enable_context_aware = st.checkbox("🧠 Smart Context", value=True)
    enable_emotion = st.checkbox("😊 Emotion Detection", value=True)
    enable_speaker_distance = st.checkbox("📏 Speaker Distance", value=True)
    enable_smart_home = st.checkbox("🏠 Smart Home Alerts", value=True)
    enable_predictive = st.checkbox("🔮 Predictive Alerts", value=True)
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    caption_font_size = st.slider("Caption Font Size", 12, 32, 20)
    sound_threshold = st.slider("Sound Alert Threshold", 0.05, 0.3, 0.1, 0.05)
    
    st.markdown("---")
    st.markdown("### 👤 Personalization")
    user_name = st.text_input("Your Name", value=st.session_state.user_name, placeholder="e.g., John")
    if user_name != st.session_state.user_name:
        st.session_state.user_name = user_name
        if user_name and user_name.lower() not in IMPORTANT_KEYWORDS['names']:
            IMPORTANT_KEYWORDS['names'].append(user_name.lower())
    
    custom_keywords_input = st.text_area("Custom Keywords (one per line)", 
                                         value="\n".join(st.session_state.custom_keywords),
                                         placeholder="meeting\nappointment",
                                         height=80)
    if custom_keywords_input:
        st.session_state.custom_keywords = [kw.strip().lower() for kw in custom_keywords_input.split('\n') if kw.strip()]
        IMPORTANT_KEYWORDS['custom'] = st.session_state.custom_keywords
    
    if enable_predictive:
        st.markdown("---")
        st.markdown("### 🔮 Schedule")
        event_time = st.time_input("Event Time", datetime.now().time())
        event_name = st.text_input("Event Name", placeholder="Meeting")
        warning_mins = st.slider("Warning (min before)", 1, 30, 5)
        
        if st.button("➕ Add to Schedule", use_container_width=True):
            time_str = event_time.strftime("%H:%M")
            st.session_state.predictive_system.add_schedule_item(time_str, event_name, warning_mins)
            st.success(f"✅ Added: {event_name} at {time_str}")

# ==================== MAIN CONTENT ====================
st.markdown("""
    <div class='modern-header'>
        <h1>🎧 HearMate Cloud</h1>
        <p>Intelligent Audio Awareness System</p>
        <span class='status-badge status-active'>SYSTEM ACTIVE</span>
    </div>
""", unsafe_allow_html=True)

# Check predictive alerts
if enable_predictive:
    upcoming = st.session_state.predictive_system.check_upcoming_events()
    if upcoming:
        for alert in upcoming:
            st.markdown(f"""
                <div class='alert-box-urgent'>
                    <h3>🔮 UPCOMING EVENT</h3>
                    <p style='font-size: 20px; margin: 10px 0;'><strong>{alert['event']}</strong></p>
                    <p>Starting at {alert['time']} - in {alert['minutes']} minute(s)!</p>
                </div>
            """, unsafe_allow_html=True)

# Smart home alerts display
if st.session_state.smart_home_alerts:
    st.markdown("### 🏠 Smart Home Alerts")
    for alert in reversed(st.session_state.smart_home_alerts[-3:]):
        st.markdown(f"""
            <div class='alert-box-smart-home'>
                <h4>{alert['icon']} {alert['type'].upper()} DETECTED</h4>
                <p>{alert['text']}</p>
                <small>Detected: {alert['time']}</small>
            </div>
        """, unsafe_allow_html=True)

# Mode selection tabs
tab1, tab2, tab3, tab4 = st.tabs(["📤 File Upload & Analyze", "⌚ Wearable Simulation", "📊 History & Insights", "💬 Caption History"])

# ==================== TAB 1: FILE UPLOAD ====================
with tab1:
    st.markdown("### Upload Audio File for Analysis")
    
    uploaded = st.file_uploader(
        "Choose an audio file",
        type=["wav", "mp3", "m4a", "flac", "ogg"],
        help="Upload any audio file for comprehensive AI-powered analysis"
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
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                        tmp.write(uploaded.read())
                        temp_path = tmp.name
                    
                    audio_data, sr = sf.read(temp_path)
                    
                    analysis = {
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'filename': uploaded.name,
                        'transcript': None,
                        'context': None,
                        'smart_home': None,
                        'emotion': None,
                        'distance': None,
                        'direction': None,
                        'loud_sounds': None,
                        'music_rhythm': None
                    }
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        if enable_captions:
                            transcript = transcribe_audio(audio_data, sr)
                            analysis['transcript'] = transcript
                            
                            st.success("✅ Analysis Complete!")
                            st.markdown(f"""
                                <div class='caption-box' style='font-size:{caption_font_size}px;'>
                                    {transcript}
                                </div>
                            """, unsafe_allow_html=True)
                            
                            if enable_context_aware:
                                context = analyze_speech_context(transcript)
                                if context:
                                    analysis['context'] = context
                                    
                                    col_a, col_b, col_c, col_d = st.columns(4)
                                    with col_a:
                                        st.metric("Importance", f"{context['importance_score']}/10")
                                    with col_b:
                                        st.metric("Question?", "Yes" if context['has_question'] else "No")
                                    with col_c:
                                        st.metric("Urgent?", "Yes" if context['has_urgency'] else "No")
                                    with col_d:
                                        st.metric("Keywords", len(context['keywords_found']))
                                    
                                    if context['has_urgency']:
                                        st.markdown(f"""
                                            <div class='alert-box-urgent'>
                                                <h4>🚨 URGENT MESSAGE</h4>
                                                <p style='font-size: 18px;'>{transcript}</p>
                                            </div>
                                        """, unsafe_allow_html=True)
                                    elif context['has_question']:
                                        st.markdown(f"""
                                            <div class='alert-box-question'>
                                                <h4>❓ QUESTION DETECTED</h4>
                                                <p style='font-size: 18px;'>{transcript}</p>
                                            </div>
                                        """, unsafe_allow_html=True)
                            
                            if enable_smart_home:
                                sh_events = detect_smart_home_events(transcript)
                                if sh_events:
                                    analysis['smart_home'] = sh_events
                                    for event in sh_events:
                                        st.session_state.smart_home_alerts.append({
                                            'type': event['type'],
                                            'icon': event['icon'],
                                            'text': transcript,
                                            'time': datetime.now().strftime("%H:%M:%S")
                                        })
                                        st.markdown(f"""
                                            <div class='alert-box-smart-home'>
                                                <h4>{event['icon']} SMART HOME ALERT</h4>
                                                <p>{event['type'].upper()} detected</p>
                                                <p style='font-size: 16px; margin-top: 10px;'>"{transcript}"</p>
                                            </div>
                                        """, unsafe_allow_html=True)
                            
                            if enable_emotion:
                                emotion = detect_speaker_emotion(transcript)
                                if emotion:
                                    analysis['emotion'] = emotion
                                    st.info(f"{emotion['emotion']} tone (confidence: {emotion['confidence']})")
                    
                    with col2:
                        if enable_direction and audio_data.ndim == 2:
                            direction, balance = calculate_direction(audio_data)
                            analysis['direction'] = {'direction': direction, 'balance': balance}
                            st.markdown(f"<div class='direction-indicator'>{direction}</div>", unsafe_allow_html=True)
                            st.progress(balance, text=f"{balance:.1%}")
                        
                        if enable_speaker_distance:
                            distance = estimate_speaker_distance(audio_data)
                            if distance:
                                analysis['distance'] = distance
                                st.metric("Distance", distance)
                        
                        if enable_sound_alert:
                            alerts = detect_loud_sounds(audio_data, sound_threshold)
                            if alerts:
                                analysis['loud_sounds'] = alerts
                                for sound, intensity in alerts:
                                    st.warning(f"🔔 {sound}")
                                    st.metric("Intensity", f"{intensity:.3f}")
                        
                        if enable_music_vibration:
                            rhythm = analyze_music_rhythm(audio_data, sr)
                            if rhythm:
                                analysis['music_rhythm'] = rhythm
                                st.markdown(f"### 🎵 Music Analysis")
                                st.metric("Rhythm Intensity", f"{rhythm['intensity']}%")
                                st.info(rhythm['pattern'])
                                st.metric("Beat Count", rhythm['beat_count'])
                    
                    st.session_state.analysis_history.append(analysis)
                    st.session_state.caption_history.append(transcript)
                    
                    st.download_button(
                        "📥 Download Transcript",
                        transcript,
                        f"transcript_{uploaded.name}.txt",
                        "text/plain",
                        use_container_width=True
                    )
                    
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                
                except Exception as e:
                    st.error(f"❌ Error processing audio: {str(e)}")

# ==================== TAB 2: WEARABLE SIMULATION ====================
with tab2:
    st.markdown("### ⌚ Wearable Device Simulation")
    st.info("Upload audio to simulate a wearable hearing device display")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        wearable_file = st.file_uploader("Upload Audio for Wearable", type=["wav", "mp3", "m4a"], key="wearable")
    
    with col2:
        if st.button("🎤 Process", type="primary", use_container_width=True):
            if wearable_file:
                with st.spinner("Processing..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                            tmp.write(wearable_file.read())
                            temp_path = tmp.name
                        
                        audio_data, sr = sf.read(temp_path)
                        transcript = transcribe_audio(audio_data, sr)
                        st.session_state.wearable_caption = transcript
                        
                        if enable_smart_home:
                            sh_events = detect_smart_home_events(transcript)
                            if sh_events:
                                st.session_state.smart_home_alerts.append({
                                    'type': sh_events[0]['type'],
                                    'icon': sh_events[0]['icon'],
                                    'text': transcript,
                                    'time': datetime.now().strftime("%H:%M:%S")
                                })
                        
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with col3:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.wearable_caption = ""
            st.rerun()
    
    display_text = st.session_state.wearable_caption if st.session_state.wearable_caption else "Upload and process audio to see captions..."
    
    st.markdown(f"""
        <div class='wearable-display'>
            <div style='font-size: 28px; margin-bottom: 30px; font-weight: 600;'>
                🎧 HearMate Wearable
            </div>
            <div style='font-size: {caption_font_size + 12}px; line-height: 1.5; padding: 20px;'>
                {display_text}
            </div>
        </div>
    """, unsafe_allow_html=True)

# ==================== TAB 3: HISTORY & INSIGHTS ====================
with tab3:
    st.markdown("### 📊 Analysis History & Insights")
    
    if st.session_state.analysis_history:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>Total Files</div>
                    <div class='metric-value'>{len(st.session_state.analysis_history)}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            urgent_count = sum(1 for a in st.session_state.analysis_history 
                             if a.get('context') and a['context'].get('has_urgency'))
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>Urgent Messages</div>
                    <div class='metric-value'>{urgent_count}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            question_count = sum(1 for a in st.session_state.analysis_history 
                               if a.get('context') and a['context'].get('has_question'))
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>Questions</div>
                    <div class='metric-value'>{question_count}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            sh_count = sum(1 for a in st.session_state.analysis_history 
                         if a.get('smart_home'))
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>Smart Home</div>
                    <div class='metric-value'>{sh_count}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📁 Detailed Analysis Records")
        
        for i, analysis in enumerate(reversed(st.session_state.analysis_history)):
            with st.expander(f"📄 {analysis['filename']} - {analysis['timestamp']}", expanded=(i==0)):
                st.markdown(f"**Transcript:**")
                st.markdown(f"<div class='caption-box'>{analysis.get('transcript', 'N/A')}</div>", 
                          unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if analysis.get('context'):
                        ctx = analysis['context']
                        st.info(f"""
                        **Context Analysis:**
                        - Importance: {ctx['importance_score']}/10
                        - Question: {'Yes' if ctx['has_question'] else 'No'}
                        - Urgent: {'Yes' if ctx['has_urgency'] else 'No'}
                        - Keywords: {', '.join(ctx['keywords_found'])}
                        """)
                    
                    if analysis.get('emotion'):
                        em = analysis['emotion']
                        st.success(f"**Emotion:** {em['emotion']} (confidence: {em['confidence']})")
                    
                    if analysis.get('smart_home'):
                        sh = analysis['smart_home']
                        st.warning(f"**Smart Home:** {', '.join([e['type'] for e in sh])}")
                
                with col_b:
                    if analysis.get('direction'):
                        dir_info = analysis['direction']
                        st.metric("Direction", dir_info['direction'])
                        st.progress(dir_info['balance'])
                    
                    if analysis.get('distance'):
                        st.metric("Distance", analysis['distance'])
                    
                    if analysis.get('loud_sounds'):
                        for sound, intensity in analysis['loud_sounds']:
                            st.warning(f"🔔 {sound}: {intensity:.3f}")
                    
                    if analysis.get('music_rhythm'):
                        rhythm = analysis['music_rhythm']
                        st.metric("Music Rhythm", f"{rhythm['intensity']}%")
                        st.caption(rhythm['pattern'])
        
        all_transcripts = "\n\n".join([
            f"[{a['timestamp']}] {a['filename']}\n{a.get('transcript', 'N/A')}"
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
        st.info("📭 No analysis history yet. Upload and analyze audio files to see insights!")

# ==================== TAB 4: CAPTION HISTORY ====================
with tab4:
    st.markdown("### 💬 Live Caption History")
    
    if st.session_state.caption_history:
        summary = create_conversation_summary(st.session_state.caption_history)
        if summary:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div class='metric-label'>Captions</div>
                        <div class='metric-value'>{summary['total_captions']}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div class='metric-label'>Words</div>
                        <div class='metric-value'>{summary['total_words']}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div class='metric-label'>Avg/Caption</div>
                        <div class='metric-value'>{summary['avg_words_per_caption']:.1f}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div class='metric-label'>Questions</div>
                        <div class='metric-value'>{summary['questions_asked']}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            transcript_text = "\n\n".join([f"[{i+1}] {caption}" for i, caption in enumerate(st.session_state.caption_history)])
            st.download_button("📥 Export TXT", transcript_text, "hearmate_captions.txt", "text/plain", use_container_width=True)
        
        for caption in reversed(list(st.session_state.caption_history)):
            context = analyze_speech_context(caption) if enable_context_aware else None
            
            if context and context['importance_score'] >= 3:
                st.markdown(f"<div class='alert-box-urgent'><strong>⚠️</strong> {caption}</div>", unsafe_allow_html=True)
            elif context and context['has_question']:
                st.markdown(f"<div class='alert-box-question'><strong>❓</strong> {caption}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='caption-box'>{caption}</div>", unsafe_allow_html=True)
    else:
        st.info("📭 No captions yet. Analyze audio files to build your caption history!")

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>🎧 HearMate Cloud v2.0</strong> — AI-Powered Audio Analysis</p>
        <p style='font-size: 14px;'>Built with Streamlit • Groq Whisper • Python</p>
        <p style='font-size: 12px; margin-top: 10px;'>
            <em>Making sound visible for everyone</em>
        </p>
    </div>
""", unsafe_allow_html=True)
