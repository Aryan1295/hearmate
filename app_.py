# import streamlit as st
# from groq import Groq
# import sounddevice as sd
# import soundfile as sf
# import numpy as np
# import tempfile
# import time
# from collections import deque
# import os

# # Disable TensorFlow for now to avoid compatibility issues
# # We'll use a simplified sound detection approach
# USE_YAMNET = False

# # ==================== CONFIGURATION ====================
# GROQ_API_KEY = "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"
# client = Groq(api_key=GROQ_API_KEY)

# SAMPLE_RATE = 16000
# CHUNK_DURATION = 3  # seconds per chunk
# CAPTION_HISTORY_SIZE = 10
# MAX_CONTINUOUS_DURATION = 60  # Maximum continuous recording time

# # Important keywords for context-aware alerts
# IMPORTANT_KEYWORDS = {
#     'names': ['help', 'emergency', 'fire', 'stop', 'wait', 'danger', 'careful', 'watch out', 'aryan'],
#     'questions': ['what', 'who', 'where', 'when', 'why', 'how', 'can you', 'could you', 'would you'],
#     'locations': ['door', 'phone', 'behind', 'front', 'left', 'right', 'upstairs', 'downstairs'],
#     'urgency': ['quick', 'hurry', 'now', 'urgent', 'important', 'immediately', 'asap']
# }

# # ==================== AUDIO DEVICE DETECTION ====================
# def get_default_device_channels():
#     """Detect the number of channels supported by default input device"""
#     try:
#         default_device = sd.query_devices(kind='input')
#         max_channels = default_device['max_input_channels']
#         # Prefer stereo if available, otherwise mono
#         return min(2, max_channels)
#     except:
#         return 1  # Fallback to mono

# CHANNELS = get_default_device_channels()

# # ==================== MUSIC TO VIBRATION ANALYSIS ====================
# def analyze_music_rhythm(audio_chunk, sample_rate=SAMPLE_RATE):
#     """Analyze music for rhythm and create vibration patterns"""
#     if audio_chunk is None or not isinstance(audio_chunk, np.ndarray):
#         return None
    
#     try:
#         # Convert to mono if stereo
#         if audio_chunk.ndim > 1:
#             mono_audio = np.mean(audio_chunk, axis=1)
#         else:
#             mono_audio = audio_chunk
        
#         # Calculate energy in different frequency bands
#         # Low frequencies (bass) - 20-250 Hz
#         # Mid frequencies - 250-2000 Hz
#         # High frequencies - 2000-8000 Hz
        
#         # Simple energy-based beat detection
#         # Calculate short-term energy
#         frame_length = int(0.05 * sample_rate)  # 50ms frames
#         hop_length = int(0.025 * sample_rate)   # 25ms hop
        
#         energy_values = []
#         for i in range(0, len(mono_audio) - frame_length, hop_length):
#             frame = mono_audio[i:i+frame_length]
#             energy = np.sum(frame ** 2)
#             energy_values.append(energy)
        
#         energy_values = np.array(energy_values)
        
#         # Detect peaks (beats)
#         if len(energy_values) > 0:
#             mean_energy = np.mean(energy_values)
#             std_energy = np.std(energy_values)
#             threshold = mean_energy + 0.5 * std_energy
            
#             beats = energy_values > threshold
#             beat_count = np.sum(beats)
            
#             # Calculate average energy
#             avg_energy = np.mean(energy_values)
            
#             # Calculate rhythm intensity (0-100)
#             max_possible_beats = len(energy_values)
#             rhythm_intensity = int((beat_count / max_possible_beats) * 100) if max_possible_beats > 0 else 0
            
#             # Determine vibration pattern
#             if rhythm_intensity > 70:
#                 pattern = "🔴 Strong - Fast vibrations"
#             elif rhythm_intensity > 40:
#                 pattern = "🟡 Moderate - Medium vibrations"
#             elif rhythm_intensity > 15:
#                 pattern = "🟢 Gentle - Slow vibrations"
#             else:
#                 pattern = "⚪ Minimal - Very light vibrations"
            
#             return {
#                 'intensity': rhythm_intensity,
#                 'pattern': pattern,
#                 'beat_count': beat_count,
#                 'avg_energy': avg_energy
#             }
        
#         return None
#     except Exception as e:
#         return None

# # ==================== AUDIO PROCESSING ====================
# def record_audio_chunk(duration=CHUNK_DURATION, sample_rate=SAMPLE_RATE, channels=CHANNELS):
#     """Record a single audio chunk synchronously"""
#     try:
#         audio = sd.rec(
#             int(duration * sample_rate),
#             samplerate=sample_rate,
#             channels=channels,
#             dtype='float32',
#             blocking=True
#         )
#         sd.wait()  # Ensure recording completes
#         return audio, channels
#     except Exception as e:
#         # Try fallback to mono if stereo fails
#         if channels > 1:
#             try:
#                 st.warning(f"Stereo recording failed, trying mono...")
#                 audio = sd.rec(
#                     int(duration * sample_rate),
#                     samplerate=sample_rate,
#                     channels=1,
#                     dtype='float32',
#                     blocking=True
#                 )
#                 sd.wait()
#                 return audio, 1
#             except Exception as e2:
#                 st.error(f"Recording error: {str(e2)}")
#                 return None, 0
#         else:
#             st.error(f"Recording error: {str(e)}")
#             return None, 0

# def transcribe_audio(audio_chunk, sample_rate=SAMPLE_RATE):
#     """Transcribe audio chunk using Groq API"""
#     if audio_chunk is None or not isinstance(audio_chunk, np.ndarray):
#         return "[No audio to transcribe]"
    
#     try:
#         # Convert to mono for transcription
#         if audio_chunk.ndim > 1:
#             mono_audio = np.mean(audio_chunk, axis=1)
#         else:
#             mono_audio = audio_chunk
        
#         # Check if audio has content
#         if np.max(np.abs(mono_audio)) < 0.001:
#             return "[Silent audio detected]"
        
#         # Save to temporary file
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
#             sf.write(tmp.name, mono_audio, sample_rate)
#             tmp_path = tmp.name
        
#         # Transcribe
#         with open(tmp_path, "rb") as f:
#             result = client.audio.transcriptions.create(
#                 file=(tmp_path, f.read()),
#                 model="whisper-large-v3",
#                 response_format="json"
#             )
        
#         # Clean up
#         os.unlink(tmp_path)
        
#         return result.text.strip() if result.text.strip() else "[No speech detected]"
#     except Exception as e:
#         return f"[Error: {str(e)}]"

# def calculate_direction(audio_chunk, num_channels):
#     """Calculate sound direction from stereo channels"""
#     if num_channels < 2 or audio_chunk.ndim < 2 or audio_chunk.shape[1] < 2:
#         return "⬆️ MONO", 0.5
    
#     left_channel = audio_chunk[:, 0]
#     right_channel = audio_chunk[:, 1]
    
#     left_energy = np.sum(left_channel ** 2)
#     right_energy = np.sum(right_channel ** 2)
    
#     total_energy = left_energy + right_energy
#     if total_energy < 1e-6:  # silence
#         return "⬆️ CENTER", 0.5
    
#     # Calculate balance (0 = full left, 1 = full right)
#     balance = right_energy / total_energy
    
#     if balance < 0.4:
#         direction = "⬅️ LEFT"
#     elif balance > 0.6:
#         direction = "➡️ RIGHT"
#     else:
#         direction = "⬆️ CENTER"
    
#     return direction, balance

# def detect_loud_sounds(audio_chunk, threshold=0.1):
#     """Simple amplitude-based loud sound detection"""
#     if audio_chunk is None or not isinstance(audio_chunk, np.ndarray):
#         return []
    
#     try:
#         # Calculate RMS amplitude
#         rms = np.sqrt(np.mean(audio_chunk ** 2))
        
#         alerts = []
#         if rms > threshold:
#             alerts.append(("Loud Sound Detected", rms))
        
#         return alerts
#     except Exception as e:
#         return []

# def deduplicate_caption(new_caption, last_caption):
#     """Remove duplicate captions"""
#     if not new_caption or len(new_caption) < 3:
#         return None
    
#     # Remove if exactly the same
#     if new_caption == last_caption:
#         return None
    
#     # Remove if very similar
#     if last_caption and new_caption.lower() in last_caption.lower():
#         return None
    
#     return new_caption

# # ==================== CONTEXT-AWARE FEATURES ====================
# def analyze_speech_context(text):
#     """Analyze speech for important context"""
#     if not text or len(text) < 3:
#         return None
    
#     text_lower = text.lower()
    
#     context = {
#         'has_question': False,
#         'has_urgency': False,
#         'has_location': False,
#         'has_name_call': False,
#         'importance_score': 0,
#         'keywords_found': []
#     }
    
#     # Check for questions
#     for q_word in IMPORTANT_KEYWORDS['questions']:
#         if q_word in text_lower:
#             context['has_question'] = True
#             context['importance_score'] += 2
#             context['keywords_found'].append(q_word)
#             break
    
#     # Check for urgency
#     for urgent_word in IMPORTANT_KEYWORDS['urgency']:
#         if urgent_word in text_lower:
#             context['has_urgency'] = True
#             context['importance_score'] += 3
#             context['keywords_found'].append(urgent_word)
    
#     # Check for locations
#     for loc_word in IMPORTANT_KEYWORDS['locations']:
#         if loc_word in text_lower:
#             context['has_location'] = True
#             context['importance_score'] += 1
#             context['keywords_found'].append(loc_word)
    
#     # Check for important keywords
#     for name_word in IMPORTANT_KEYWORDS['names']:
#         if name_word in text_lower:
#             context['has_name_call'] = True
#             context['importance_score'] += 3
#             context['keywords_found'].append(name_word)
    
#     # Check for question marks
#     if '?' in text:
#         context['has_question'] = True
#         context['importance_score'] += 1
    
#     return context if context['importance_score'] > 0 else None

# def detect_speaker_emotion(text):
#     """Simple emotion detection from text"""
#     if not text or len(text) < 3:
#         return None
    
#     text_lower = text.lower()
    
#     # Emotion indicators
#     positive_words = ['happy', 'great', 'good', 'excellent', 'wonderful', 'love', 'thanks', 'thank you', 'awesome']
#     negative_words = ['sad', 'bad', 'terrible', 'hate', 'angry', 'mad', 'upset', 'disappointed']
#     excited_words = ['wow', 'amazing', 'incredible', 'fantastic', 'yay', 'yes']
    
#     # Check for exclamation (excitement/emphasis)
#     has_exclamation = '!' in text
    
#     emotion = None
#     confidence = 0
    
#     for word in positive_words:
#         if word in text_lower:
#             emotion = "😊 Positive"
#             confidence += 1
    
#     for word in negative_words:
#         if word in text_lower:
#             emotion = "😟 Negative"
#             confidence += 1
    
#     for word in excited_words:
#         if word in text_lower:
#             emotion = "🎉 Excited"
#             confidence += 1
    
#     if has_exclamation:
#         if not emotion:
#             emotion = "❗ Emphasis"
#         confidence += 1
    
#     return {'emotion': emotion, 'confidence': confidence} if emotion else None

# def estimate_speaker_distance(audio_chunk):
#     """Estimate how far the speaker is based on audio intensity"""
#     if audio_chunk is None or not isinstance(audio_chunk, np.ndarray):
#         return None
    
#     try:
#         # Calculate RMS amplitude
#         rms = np.sqrt(np.mean(audio_chunk ** 2))
        
#         # Estimate distance category
#         if rms > 0.15:
#             return "🔴 Very Close (< 1ft)"
#         elif rms > 0.08:
#             return "🟡 Close (1-3ft)"
#         elif rms > 0.03:
#             return "🟢 Moderate (3-6ft)"
#         elif rms > 0.01:
#             return "🔵 Far (6-10ft)"
#         else:
#             return "⚪ Very Far (>10ft)"
#     except:
#         return None

# def create_conversation_summary(caption_history):
#     """Create a summary of the conversation"""
#     if not caption_history or len(caption_history) < 2:
#         return None
    
#     total_captions = len(caption_history)
#     total_words = sum(len(caption.split()) for caption in caption_history)
#     avg_words_per_caption = total_words / total_captions if total_captions > 0 else 0
    
#     # Count questions
#     questions = sum(1 for caption in caption_history if '?' in caption or any(q in caption.lower() for q in ['what', 'who', 'where', 'when', 'why', 'how']))
    
#     return {
#         'total_captions': total_captions,
#         'total_words': total_words,
#         'avg_words_per_caption': avg_words_per_caption,
#         'questions_asked': questions
#     }

# # ==================== STREAMLIT UI ====================
# st.set_page_config(page_title="HearMate", page_icon="🎧", layout="wide")

# # Custom CSS
# st.markdown("""
#     <style>
#     .main-header {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 20px;
#         border-radius: 10px;
#         color: white;
#         text-align: center;
#         margin-bottom: 20px;
#     }
#     .caption-box {
#         background-color: #e8f4f8;
#         border-left: 4px solid #1f77b4;
#         border-radius: 5px;
#         padding: 15px;
#         margin: 10px 0;
#         font-size: 18px;
#     }
#     .alert-box {
#         background-color: #fff3cd;
#         border-left: 4px solid #ffc107;
#         border-radius: 5px;
#         padding: 15px;
#         margin: 10px 0;
#     }
#     .wearable-display {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 40px;
#         border-radius: 20px;
#         text-align: center;
#         color: white;
#         min-height: 300px;
#     }
#     .direction-indicator {
#         font-size: 48px;
#         margin: 20px 0;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # Initialize session state
# if 'caption_history' not in st.session_state:
#     st.session_state.caption_history = deque(maxlen=CAPTION_HISTORY_SIZE)
# if 'last_caption' not in st.session_state:
#     st.session_state.last_caption = ""
# if 'mode' not in st.session_state:
#     st.session_state.mode = "demo"
# if 'recording_active' not in st.session_state:
#     st.session_state.recording_active = False
# if 'continuous_mode' not in st.session_state:
#     st.session_state.continuous_mode = False
# if 'continuous_stop' not in st.session_state:
#     st.session_state.continuous_stop = False
# if 'total_chunks_processed' not in st.session_state:
#     st.session_state.total_chunks_processed = 0
# if 'important_alerts' not in st.session_state:
#     st.session_state.important_alerts = []
# if 'user_name' not in st.session_state:
#     st.session_state.user_name = ""
# if 'custom_keywords' not in st.session_state:
#     st.session_state.custom_keywords = []

# # ==================== SIDEBAR ====================
# with st.sidebar:
#     st.markdown("""
#         <div style='text-align: center; padding: 20px;'>
#             <h1 style='color: #667eea;'>🎧 HearMate</h1>
#             <p style='color: #666;'>AI-Powered Hearing Assistance</p>
#         </div>
#     """, unsafe_allow_html=True)
    
#     # Show audio device info
#     st.markdown("### 🎤 Audio Device")
#     device_info = sd.query_devices(kind='input')
#     st.info(f"**Input:** {device_info['name']}\n\n**Channels:** {CHANNELS} ({'Stereo' if CHANNELS == 2 else 'Mono'})")
    
#     mode = st.radio(
#         "Select Mode:",
#         ["📁 File Upload Demo", "🎙️ Live Streaming", "⌚ Wearable Simulation"],
#         key="mode_selector"
#     )
    
#     st.markdown("---")
#     st.markdown("### Features")
#     enable_direction = st.checkbox("📍 Direction Detection", value=(CHANNELS == 2))
#     enable_captions = st.checkbox("💬 Live Captions", value=True)
#     enable_sound_alert = st.checkbox("🔔 Loud Sound Alerts", value=True)
#     enable_music_vibration = st.checkbox("🎵 Music Vibration Analysis", value=False, 
#                                          help="Analyze music rhythm for vibration patterns (accessibility feature)")
#     enable_context_aware = st.checkbox("🧠 Smart Context Detection", value=True,
#                                        help="Detect questions, urgency, and important keywords")
#     enable_emotion = st.checkbox("😊 Emotion Detection", value=False,
#                                  help="Detect speaker emotion from text")
#     enable_speaker_distance = st.checkbox("📏 Speaker Distance", value=False,
#                                          help="Estimate how far away the speaker is")
    
#     if CHANNELS == 1 and enable_direction:
#         st.warning("⚠️ Direction detection requires stereo input. Your device only supports mono.")
    
#     st.markdown("---")
#     st.markdown("### Settings")
#     caption_font_size = st.slider("Caption Font Size", 12, 32, 20)
#     sound_threshold = st.slider("Sound Alert Threshold", 0.05, 0.3, 0.1, 0.05)
#     continuous_duration = st.slider("Continuous Recording Duration (seconds)", 10, 60, 10, 10)
    
#     # Personalization
#     st.markdown("---")
#     st.markdown("### 👤 Personalization")
#     user_name = st.text_input("Your Name (for name detection)", value=st.session_state.user_name, 
#                                placeholder="e.g., John")
#     if user_name != st.session_state.user_name:
#         st.session_state.user_name = user_name
#         if user_name:
#             IMPORTANT_KEYWORDS['names'].append(user_name.lower())
    
#     custom_keywords_input = st.text_area("Custom Alert Keywords (one per line)", 
#                                          value="\n".join(st.session_state.custom_keywords),
#                                          placeholder="meeting\nappointment\ncall",
#                                          height=100)
#     if custom_keywords_input:
#         st.session_state.custom_keywords = [kw.strip().lower() for kw in custom_keywords_input.split('\n') if kw.strip()]
#         IMPORTANT_KEYWORDS['custom'] = st.session_state.custom_keywords
    
#     st.markdown("---")
#     st.info("💡 **Tip:** Speak clearly near your microphone for best results.")

# # ==================== MAIN CONTENT ====================

# if mode == "📁 File Upload Demo":
#     st.markdown("<div class='main-header'><h1>📁 Audio File Analysis</h1></div>", unsafe_allow_html=True)
#     st.write("Upload an audio file to get transcription and analysis.")
    
#     # Tabs for better organization
#     tab1, tab2 = st.tabs(["📤 Upload & Analyze", "📊 Smart Insights"])
    
#     with tab1:
#         uploaded = st.file_uploader("Upload audio (.wav, .mp3, .m4a)", type=["wav", "mp3", "m4a"])
        
#         if uploaded:
#             # Save uploaded file
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
#                 tmp.write(uploaded.read())
#                 temp_path = tmp.name
            
#             st.audio(uploaded, format="audio/wav")
            
#             col1, col2 = st.columns([1, 3])
            
#             with col1:
#                 analyze_button = st.button("🎯 Analyze Audio", type="primary", use_container_width=True)
            
#             if analyze_button:
#                 with st.spinner("🔄 Processing audio..."):
#                     # Load audio
#                     audio_data, sr = sf.read(temp_path)
                    
#                     # Transcribe
#                     transcript = transcribe_audio(audio_data, sr)
                    
#                     # Display results
#                     st.success("✅ Analysis Complete!")
                    
#                     st.subheader("📝 Transcript:")
#                     st.markdown(f"<div style='font-size:{caption_font_size}px; padding:20px; background-color:#f0f2f6; border-radius:10px;'>{transcript}</div>", 
#                                unsafe_allow_html=True)
                    
#                     # Context analysis
#                     if enable_context_aware:
#                         context = analyze_speech_context(transcript)
#                         if context:
#                             st.subheader("🧠 Smart Analysis:")
#                             insight_cols = st.columns(4)
#                             with insight_cols[0]:
#                                 st.metric("Importance", f"{context['importance_score']}/10")
#                             with insight_cols[1]:
#                                 st.metric("Question?", "Yes" if context['has_question'] else "No")
#                             with insight_cols[2]:
#                                 st.metric("Urgent?", "Yes" if context['has_urgency'] else "No")
#                             with insight_cols[3]:
#                                 st.metric("Keywords", len(context['keywords_found']))
                            
#                             if context['keywords_found']:
#                                 st.info(f"🔑 Keywords detected: {', '.join(context['keywords_found'])}")
                    
#                     # Emotion detection
#                     if enable_emotion:
#                         emotion = detect_speaker_emotion(transcript)
#                         if emotion:
#                             st.success(f"😊 Detected emotion: {emotion['emotion']}")
                    
#                     if enable_direction and audio_data.ndim > 1:
#                         st.subheader("📍 Direction Analysis:")
#                         direction, balance = calculate_direction(audio_data, audio_data.shape[1] if audio_data.ndim > 1 else 1)
#                         col1, col2 = st.columns(2)
#                         with col1:
#                             st.metric("Primary Direction", direction)
#                         with col2:
#                             if direction != "⬆️ MONO":
#                                 st.progress(balance, text=f"Balance: {balance:.1%}")
            
#             # Clean up
#             if os.path.exists(temp_path):
#                 os.unlink(temp_path)
    
#     with tab2:
#         st.markdown("### 📊 Smart Insights Dashboard")
        
#         if st.session_state.important_alerts:
#             st.subheader("⚠️ Important Alerts")
#             for alert in reversed(st.session_state.important_alerts[-5:]):  # Show last 5
#                 st.error(alert)
#         else:
#             st.info("No important alerts yet. Enable 'Smart Context Detection' and start capturing audio.")
        
#         st.markdown("---")
#         st.markdown("### 🎯 What Gets Flagged as Important?")
#         col1, col2 = st.columns(2)
#         with col1:
#             st.markdown("""
#             **High Priority (3 points):**
#             - Urgency words: *urgent, emergency, help, danger*
#             - Your name mentioned
#             - Words like: *fire, stop, wait, careful*
#             """)
#         with col2:
#             st.markdown("""
#             **Medium Priority (2 points):**
#             - Questions: *what, who, where, when, why, how*
#             - Location mentions: *door, phone, behind, front*
#             - Custom keywords you added
#             """)
        
#         if st.session_state.custom_keywords:
#             st.success(f"✅ Your custom keywords: {', '.join(st.session_state.custom_keywords)}")

# elif mode == "🎙️ Live Streaming":
#     st.markdown("<div class='main-header'><h1>🎙️ Live Audio Streaming</h1></div>", unsafe_allow_html=True)
#     st.write("Real-time transcription with sound alerts and direction detection.")
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         if st.button("🎤 Capture One Chunk", type="primary", use_container_width=True):
#             st.session_state.recording_active = True
    
#     with col2:
#         if st.button("🔴 Start Continuous", type="secondary", use_container_width=True, 
#                     disabled=st.session_state.continuous_mode):
#             st.session_state.continuous_mode = True
#             st.session_state.continuous_stop = False
#             st.session_state.total_chunks_processed = 0
#             st.rerun()
    
#     with col3:
#         if st.button("⏹️ Stop Continuous", use_container_width=True, 
#                     disabled=not st.session_state.continuous_mode):
#             st.session_state.continuous_stop = True
#             st.session_state.continuous_mode = False
#             st.rerun()
    
#     with col4:
#         if st.button("🗑️ Clear Captions", use_container_width=True):
#             st.session_state.caption_history.clear()
#             st.session_state.last_caption = ""
#             st.session_state.total_chunks_processed = 0
#             st.rerun()
    
#     # Continuous Mode Processing
#     if st.session_state.continuous_mode and not st.session_state.continuous_stop:
#         st.info(f"🔴 **LIVE CONTINUOUS MODE** - Recording for {continuous_duration} seconds...")
        
#         progress_bar = st.progress(0, text="Starting...")
#         status_container = st.empty()
        
#         num_chunks = continuous_duration // CHUNK_DURATION
        
#         for chunk_num in range(num_chunks):
#             if st.session_state.continuous_stop:
#                 break
            
#             # Update progress
#             progress = (chunk_num + 1) / num_chunks
#             elapsed_time = (chunk_num + 1) * CHUNK_DURATION
#             progress_bar.progress(progress, text=f"Recording... {elapsed_time}/{continuous_duration}s")
            
#             # Record chunk
#             audio_chunk, actual_channels = record_audio_chunk()
            
#             if audio_chunk is not None:
#                 st.session_state.total_chunks_processed += 1
                
#                 # Process in background with status updates
#                 status_container.info(f"Processing chunk {chunk_num + 1}/{num_chunks}...")
                
#                 # Transcription
#                 if enable_captions:
#                     transcript = transcribe_audio(audio_chunk)
#                     clean_transcript = deduplicate_caption(transcript, st.session_state.last_caption)
#                     if clean_transcript:
#                         st.session_state.caption_history.append(clean_transcript)
#                         st.session_state.last_caption = clean_transcript
                
#                 # Music vibration analysis
#                 if enable_music_vibration:
#                     vibration_data = analyze_music_rhythm(audio_chunk)
#                     if vibration_data:
#                         status_container.success(
#                             f"🎵 Rhythm detected: {vibration_data['pattern']} "
#                             f"(Intensity: {vibration_data['intensity']}%)"
#                         )
                
#                 # Sound alerts
#                 if enable_sound_alert:
#                     alerts = detect_loud_sounds(audio_chunk, sound_threshold)
#                     if alerts:
#                         for sound, intensity in alerts:
#                             status_container.warning(f"🔔 {sound}: {intensity:.2f}")
        
#         # Completed
#         progress_bar.progress(1.0, text="✅ Continuous recording completed!")
#         status_container.success(f"Processed {st.session_state.total_chunks_processed} chunks successfully!")
#         st.session_state.continuous_mode = False
    
#     # Single Chunk Mode Processing
#     if st.session_state.recording_active:
#         with st.spinner("🎧 Recording... Please speak now!"):
#             # Record audio chunk
#             audio_chunk, actual_channels = record_audio_chunk()
            
#             if audio_chunk is not None:
#                 # Process audio
#                 results_container = st.container()
                
#                 with results_container:
#                     col1, col2 = st.columns([2, 1])
                    
#                     with col1:
#                         # Transcription
#                         if enable_captions:
#                             with st.spinner("💬 Transcribing..."):
#                                 transcript = transcribe_audio(audio_chunk)
                                
#                                 # Deduplicate and add to history
#                                 clean_transcript = deduplicate_caption(transcript, st.session_state.last_caption)
#                                 if clean_transcript:
#                                     st.session_state.caption_history.append(clean_transcript)
#                                     st.session_state.last_caption = clean_transcript
                        
#                         # Music vibration analysis
#                         if enable_music_vibration:
#                             vibration_data = analyze_music_rhythm(audio_chunk)
#                             if vibration_data:
#                                 st.success(f"🎵 **Rhythm Analysis:**")
#                                 st.write(f"Pattern: {vibration_data['pattern']}")
#                                 st.write(f"Intensity: {vibration_data['intensity']}%")
#                                 st.write(f"Beats detected: {vibration_data['beat_count']}")
                                
#                                 # Visual representation
#                                 intensity_norm = vibration_data['intensity'] / 100.0
#                                 st.progress(intensity_norm, text=f"Vibration Strength: {vibration_data['intensity']}%")
                    
#                     with col2:
#                         # Direction detection
#                         if enable_direction and actual_channels == 2:
#                             direction, balance = calculate_direction(audio_chunk, actual_channels)
#                             st.markdown(f"<div class='direction-indicator'>{direction}</div>", unsafe_allow_html=True)
#                             st.progress(balance, text=f"{balance:.1%}")
#                         elif enable_direction and actual_channels == 1:
#                             st.info("📍 Mono input - direction unavailable")
                        
#                         # Speaker distance estimation
#                         if enable_speaker_distance:
#                             distance = estimate_speaker_distance(audio_chunk)
#                             if distance:
#                                 st.metric("Speaker Distance", distance)
                        
#                         # Sound alerts
#                         if enable_sound_alert:
#                             alerts = detect_loud_sounds(audio_chunk, sound_threshold)
#                             if alerts:
#                                 for sound, intensity in alerts:
#                                     st.warning(f"🔔 {sound}: {intensity:.2f}")
                
#                 st.success("✅ Chunk processed!")
        
#         st.session_state.recording_active = False
    
#     # Display caption history
#     if st.session_state.caption_history:
#         st.markdown("---")
        
#         # Show conversation summary
#         summary = create_conversation_summary(st.session_state.caption_history)
#         if summary:
#             col1, col2, col3, col4 = st.columns(4)
#             with col1:
#                 st.metric("Total Captions", summary['total_captions'])
#             with col2:
#                 st.metric("Total Words", summary['total_words'])
#             with col3:
#                 st.metric("Avg Words/Caption", f"{summary['avg_words_per_caption']:.1f}")
#             with col4:
#                 st.metric("Questions Asked", summary['questions_asked'])
        
#         st.subheader("💬 Caption History")
        
#         # Export button
#         export_col1, export_col2 = st.columns([3, 1])
#         with export_col2:
#             if st.button("📥 Export Transcript", use_container_width=True):
#                 transcript_text = "\n\n".join([f"[{i+1}] {caption}" for i, caption in enumerate(st.session_state.caption_history)])
#                 st.download_button(
#                     label="Download TXT",
#                     data=transcript_text,
#                     file_name="hearmate_transcript.txt",
#                     mime="text/plain"
#                 )
        
#         # Display captions with context highlighting
#         for i, caption in enumerate(reversed(list(st.session_state.caption_history))):
#             context = analyze_speech_context(caption) if enable_context_aware else None
            
#             # Highlight important captions
#             if context and context['importance_score'] >= 2:
#                 st.markdown(f"<div class='alert-box' style='font-size:{caption_font_size}px;'><strong>⚠️ IMPORTANT:</strong> {caption}</div>", 
#                            unsafe_allow_html=True)
#             else:
#                 st.markdown(f"<div class='caption-box' style='font-size:{caption_font_size}px;'>{caption}</div>", 
#                            unsafe_allow_html=True)
#     else:
#         st.info("👆 Click 'Capture One Chunk' for single recording or 'Start Continuous' for extended capture.")

# else:  # Wearable Simulation
#     st.markdown("<div class='main-header'><h1>⌚ Wearable Mode</h1></div>", unsafe_allow_html=True)
    
#     # Simple toggle button
#     toggle_col1, toggle_col2, toggle_col3 = st.columns([2, 1, 1])
    
#     with toggle_col1:
#         if st.button("🎤 Capture & Display", type="primary", use_container_width=True):
#             with st.spinner("Recording..."):
#                 audio_chunk, actual_channels = record_audio_chunk(duration=3)
                
#                 if audio_chunk is not None:
#                     transcript = transcribe_audio(audio_chunk)
                    
#                     # Check for loud sounds
#                     alerts = detect_loud_sounds(audio_chunk, sound_threshold)
#                     alert_text = ""
#                     if alerts:
#                         alert_text = f"🚨 {alerts[0][0]}"
                    
#                     # Music vibration if enabled
#                     if enable_music_vibration:
#                         vibration_data = analyze_music_rhythm(audio_chunk)
#                         if vibration_data:
#                             st.session_state.vibration_pattern = vibration_data['pattern']
                    
#                     # Store latest caption
#                     st.session_state.last_caption = transcript
                    
#                     # Update display
#                     st.rerun()
    
#     with toggle_col2:
#         if st.button("🗑️ Clear", use_container_width=True):
#             st.session_state.last_caption = ""
#             st.session_state.vibration_pattern = ""
#             st.rerun()
    
#     with toggle_col3:
#         continuous_wearable = st.button("🔴 Continuous", use_container_width=True)
    
#     # Wearable display
#     display_text = st.session_state.last_caption if st.session_state.last_caption else "Ready to listen..."
#     vibration_display = st.session_state.get('vibration_pattern', '')
    
#     st.markdown(f"""
#         <div class='wearable-display'>
#             <div style='font-size: 24px; margin-bottom: 20px; opacity: 0.9;'>
#                 🎧 HearMate Active
#             </div>
#             <div style='font-size: {caption_font_size + 8}px; line-height: 1.4; min-height: 150px; display: flex; align-items: center; justify-content: center;'>
#                 {display_text}
#             </div>
#             {f"<div style='font-size: 18px; margin-top: 20px; opacity: 0.8;'>{vibration_display}</div>" if vibration_display else ""}
#         </div>
#     """, unsafe_allow_html=True)
    
#     # Continuous mode for wearable
#     if continuous_wearable:
#         st.info("🔴 Continuous mode starting...")
#         duration = 10  # Fixed 10 seconds for wearable
#         num_chunks = duration // CHUNK_DURATION
        
#         progress_placeholder = st.empty()
#         caption_placeholder = st.empty()
        
#         for i in range(num_chunks):
#             progress_placeholder.progress((i + 1) / num_chunks, text=f"Recording {(i+1)*CHUNK_DURATION}s...")
            
#             audio_chunk, _ = record_audio_chunk(duration=CHUNK_DURATION)
#             if audio_chunk is not None:
#                 transcript = transcribe_audio(audio_chunk)
#                 if transcript and len(transcript) > 3:
#                     st.session_state.last_caption = transcript
#                     caption_placeholder.markdown(f"""
#                         <div class='wearable-display'>
#                             <div style='font-size: {caption_font_size + 8}px;'>{transcript}</div>
#                         </div>
#                     """, unsafe_allow_html=True)
        
#         progress_placeholder.success("✅ Continuous recording complete!")
#         time.sleep(2)
#         st.rerun()

# # ==================== FOOTER ====================
# st.markdown("---")
# st.markdown("""
#     <div style='text-align: center; color: #666; padding: 20px;'>
#         <p><strong>🎧 HearMate v1.0</strong> — AI-Powered Hearing Assistance Tool</p>
#         <p style='font-size: 14px;'>Built with Streamlit • Groq Whisper • Python</p>
#         <p style='font-size: 12px; margin-top: 10px;'>
#             <em>Making sound visible for everyone</em>
#         </p>
#     </div>
# """, unsafe_allow_html=True)



import streamlit as st
from groq import Groq
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import time
from collections import deque
import os
from datetime import datetime, timedelta
import json

# Disable TensorFlow for now to avoid compatibility issues
USE_YAMNET = False

# ==================== CONFIGURATION ====================
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
# if not GROQ_API_KEY:
#     raise RuntimeError("GROQ_API_KEY environment variable not set")
# client = Groq(api_key=GROQ_API_KEY)


SAMPLE_RATE = 16000
CHUNK_DURATION = 3
CAPTION_HISTORY_SIZE = 10
MAX_CONTINUOUS_DURATION = 60

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
        /* Import modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Main gradient background */
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Glassmorphism card effect */
        .glass-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        
        /* Modern header */
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
        
        /* Caption boxes with modern design */
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
        
        /* Alert boxes */
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
        
        /* Metric cards */
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
        
        /* Direction indicator */
        .direction-indicator {
            font-size: 64px;
            text-align: center;
            margin: 20px 0;
            animation: bounce 1s infinite;
        }
        
        /* Wearable display */
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
        
        /* Animations */
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
        
        /* Status badges */
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
        
        .status-paused {
            background: #ff9800;
            color: white;
        }
        
        /* Button enhancements */
        .stButton>button {
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        
        /* Progress bars */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        section[data-testid="stSidebar"] .stMarkdown {
            color: white;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 12px;
            padding: 10px 20px;
            font-weight: 600;
        }
        
        /* Tooltip */
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
        }
        </style>
    """, unsafe_allow_html=True)

# ==================== AUDIO DEVICE DETECTION ====================
def get_default_device_channels():
    try:
        default_device = sd.query_devices(kind='input')
        max_channels = default_device['max_input_channels']
        return min(2, max_channels)
    except:
        return 1

CHANNELS = get_default_device_channels()

# ==================== SMART HOME DETECTION ====================
def detect_smart_home_events(text):
    """Detect smart home related events"""
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

# ==================== PREDICTIVE ALERTS ====================
class PredictiveAlertSystem:
    def __init__(self):
        self.schedule = []
        self.last_alerts = []
    
    def add_schedule_item(self, time_str, event, minutes_before=5):
        """Add item to schedule"""
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
        """Check for upcoming events and generate alerts"""
        now = datetime.now()
        alerts = []
        
        for item in self.schedule:
            if not item['alerted']:
                time_until = (item['time'] - now).total_seconds() / 60
                
                # Alert if within warning window
                if 0 <= time_until <= item['minutes_before']:
                    alerts.append({
                        'event': item['event'],
                        'time': item['time'].strftime("%H:%M"),
                        'minutes': int(time_until)
                    })
                    item['alerted'] = True
        
        return alerts
    
    def clear_old_events(self):
        """Remove past events"""
        now = datetime.now()
        self.schedule = [item for item in self.schedule if item['time'] > now]

# ==================== AUDIO PROCESSING ====================
def record_audio_chunk(duration=CHUNK_DURATION, sample_rate=SAMPLE_RATE, channels=CHANNELS):
    try:
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels,
            dtype='float32',
            blocking=True
        )
        sd.wait()
        return audio, channels
    except Exception as e:
        if channels > 1:
            try:
                audio = sd.rec(
                    int(duration * sample_rate),
                    samplerate=sample_rate,
                    channels=1,
                    dtype='float32',
                    blocking=True
                )
                sd.wait()
                return audio, 1
            except:
                return None, 0
        return None, 0

def transcribe_audio(audio_chunk, sample_rate=SAMPLE_RATE):
    if audio_chunk is None or not isinstance(audio_chunk, np.ndarray):
        return "[No audio to transcribe]"
    
    try:
        if audio_chunk.ndim > 1:
            mono_audio = np.mean(audio_chunk, axis=1)
        else:
            mono_audio = audio_chunk
        
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

def calculate_direction(audio_chunk, num_channels):
    if num_channels < 2 or audio_chunk.ndim < 2 or audio_chunk.shape[1] < 2:
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

def analyze_music_rhythm(audio_chunk, sample_rate=SAMPLE_RATE):
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

def deduplicate_caption(new_caption, last_caption):
    if not new_caption or len(new_caption) < 3:
        return None
    if new_caption == last_caption:
        return None
    if last_caption and new_caption.lower() in last_caption.lower():
        return None
    return new_caption

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
st.set_page_config(page_title="HearMate", page_icon="🎧", layout="wide")

# Load custom CSS
load_custom_css()

# Initialize session state
if 'caption_history' not in st.session_state:
    st.session_state.caption_history = deque(maxlen=CAPTION_HISTORY_SIZE)
if 'last_caption' not in st.session_state:
    st.session_state.last_caption = ""
if 'recording_active' not in st.session_state:
    st.session_state.recording_active = False
if 'continuous_mode' not in st.session_state:
    st.session_state.continuous_mode = False
if 'continuous_stop' not in st.session_state:
    st.session_state.continuous_stop = False
if 'total_chunks_processed' not in st.session_state:
    st.session_state.total_chunks_processed = 0
if 'important_alerts' not in st.session_state:
    st.session_state.important_alerts = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'custom_keywords' not in st.session_state:
    st.session_state.custom_keywords = []
if 'predictive_system' not in st.session_state:
    st.session_state.predictive_system = PredictiveAlertSystem()
if 'smart_home_alerts' not in st.session_state:
    st.session_state.smart_home_alerts = []

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 30px 20px; background: rgba(255,255,255,0.1); border-radius: 15px; margin-bottom: 20px;'>
            <h1 style='color: white; font-size: 36px; margin: 0;'>🎧 HearMate</h1>
            <p style='color: rgba(255,255,255,0.9); font-size: 16px; margin-top: 10px;'>AI-Powered Hearing Assistance</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Audio device info
    st.markdown("### 🎤 Audio Device")
    device_info = sd.query_devices(kind='input')
    st.info(f"**Input:** {device_info['name']}\n\n**Channels:** {CHANNELS} ({'Stereo' if CHANNELS == 2 else 'Mono'})")
    
    mode = st.radio(
        "Select Mode:",
        ["🎙️ Live Streaming", "📁 File Upload Demo", "⌚ Wearable Simulation"],
        key="mode_selector"
    )
    
    st.markdown("---")
    st.markdown("### ✨ Features")
    enable_direction = st.checkbox("📍 Direction Detection", value=(CHANNELS == 2))
    enable_captions = st.checkbox("💬 Live Captions", value=True)
    enable_sound_alert = st.checkbox("🔔 Loud Sound Alerts", value=True)
    enable_music_vibration = st.checkbox("🎵 Music Vibration", value=False)
    enable_context_aware = st.checkbox("🧠 Smart Context", value=True)
    enable_emotion = st.checkbox("😊 Emotion Detection", value=False)
    enable_speaker_distance = st.checkbox("📏 Speaker Distance", value=False)
    enable_smart_home = st.checkbox("🏠 Smart Home Alerts", value=True)
    enable_predictive = st.checkbox("🔮 Predictive Alerts", value=True)
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    caption_font_size = st.slider("Caption Font Size", 12, 32, 20)
    sound_threshold = st.slider("Sound Alert Threshold", 0.05, 0.3, 0.1, 0.05)
    continuous_duration = st.slider("Continuous Duration (sec)", 10, 60, 10, 10)
    
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
    
    # Predictive Schedule
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

# Modern header
st.markdown("""
    <div class='modern-header'>
        <h1>🎧 HearMate</h1>
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

if mode == "🎙️ Live Streaming":
    st.markdown("### Real-time Audio Processing")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎤 Capture Chunk", type="primary", use_container_width=True):
            st.session_state.recording_active = True
    
    with col2:
        if st.button("🔴 Start Continuous", type="secondary", use_container_width=True, 
                    disabled=st.session_state.continuous_mode):
            st.session_state.continuous_mode = True
            st.session_state.continuous_stop = False
            st.session_state.total_chunks_processed = 0
            st.rerun()
    
    with col3:
        if st.button("⏹️ Stop", use_container_width=True, 
                    disabled=not st.session_state.continuous_mode):
            st.session_state.continuous_stop = True
            st.session_state.continuous_mode = False
            st.rerun()
    
    with col4:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.caption_history.clear()
            st.session_state.last_caption = ""
            st.session_state.total_chunks_processed = 0
            st.session_state.smart_home_alerts.clear()
            st.rerun()
    
    # Continuous mode
    if st.session_state.continuous_mode and not st.session_state.continuous_stop:
        st.markdown("<span class='status-badge status-live'>🔴 LIVE RECORDING</span>", unsafe_allow_html=True)
        
        progress_bar = st.progress(0, text="Starting...")
        status_container = st.empty()
        
        num_chunks = continuous_duration // CHUNK_DURATION
        
        for chunk_num in range(num_chunks):
            if st.session_state.continuous_stop:
                break
            
            progress = (chunk_num + 1) / num_chunks
            elapsed_time = (chunk_num + 1) * CHUNK_DURATION
            progress_bar.progress(progress, text=f"Recording... {elapsed_time}/{continuous_duration}s")
            
            audio_chunk, actual_channels = record_audio_chunk()
            
            if audio_chunk is not None:
                st.session_state.total_chunks_processed += 1
                status_container.info(f"Processing chunk {chunk_num + 1}/{num_chunks}...")
                
                if enable_captions:
                    transcript = transcribe_audio(audio_chunk)
                    clean_transcript = deduplicate_caption(transcript, st.session_state.last_caption)
                    if clean_transcript:
                        st.session_state.caption_history.append(clean_transcript)
                        st.session_state.last_caption = clean_transcript
                        
                        # Smart home detection
                        if enable_smart_home:
                            sh_events = detect_smart_home_events(clean_transcript)
                            if sh_events:
                                for event in sh_events:
                                    st.session_state.smart_home_alerts.append({
                                        'type': event['type'],
                                        'icon': event['icon'],
                                        'text': clean_transcript,
                                        'time': datetime.now().strftime("%H:%M:%S")
                                    })
                                    status_container.warning(f"🏠 {event['icon']} Smart Home Alert: {event['type'].upper()}")
        
        progress_bar.progress(1.0, text="✅ Complete!")
        status_container.success(f"Processed {st.session_state.total_chunks_processed} chunks!")
        st.session_state.continuous_mode = False
    
    # Single chunk processing
    if st.session_state.recording_active:
        with st.spinner("🎧 Recording..."):
            audio_chunk, actual_channels = record_audio_chunk()
            
            if audio_chunk is not None:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if enable_captions:
                        with st.spinner("💬 Transcribing..."):
                            transcript = transcribe_audio(audio_chunk)
                            clean_transcript = deduplicate_caption(transcript, st.session_state.last_caption)
                            
                            if clean_transcript:
                                st.session_state.caption_history.append(clean_transcript)
                                st.session_state.last_caption = clean_transcript
                                
                                # Context analysis
                                if enable_context_aware:
                                    context = analyze_speech_context(clean_transcript)
                                    if context:
                                        if context['has_urgency']:
                                            st.markdown(f"""
                                                <div class='alert-box-urgent'>
                                                    <h4>🚨 URGENT MESSAGE</h4>
                                                    <p style='font-size: 18px;'>{clean_transcript}</p>
                                                </div>
                                            """, unsafe_allow_html=True)
                                        elif context['has_question']:
                                            st.markdown(f"""
                                                <div class='alert-box-question'>
                                                    <h4>❓ QUESTION DETECTED</h4>
                                                    <p style='font-size: 18px;'>{clean_transcript}</p>
                                                </div>
                                            """, unsafe_allow_html=True)
                                
                                # Smart home detection
                                if enable_smart_home:
                                    sh_events = detect_smart_home_events(clean_transcript)
                                    if sh_events:
                                        for event in sh_events:
                                            st.session_state.smart_home_alerts.append({
                                                'type': event['type'],
                                                'icon': event['icon'],
                                                'text': clean_transcript,
                                                'time': datetime.now().strftime("%H:%M:%S")
                                            })
                                            st.markdown(f"""
                                                <div class='alert-box-smart-home'>
                                                    <h4>{event['icon']} SMART HOME ALERT</h4>
                                                    <p>{event['type'].upper()} detected</p>
                                                    <p style='font-size: 16px; margin-top: 10px;'>"{clean_transcript}"</p>
                                                </div>
                                            """, unsafe_allow_html=True)
                                
                                # Emotion
                                if enable_emotion:
                                    emotion = detect_speaker_emotion(clean_transcript)
                                    if emotion:
                                        st.info(f"{emotion['emotion']} tone")
                
                with col2:
                    if enable_direction and actual_channels == 2:
                        direction, balance = calculate_direction(audio_chunk, actual_channels)
                        st.markdown(f"<div class='direction-indicator'>{direction}</div>", unsafe_allow_html=True)
                        st.progress(balance, text=f"{balance:.1%}")
                    
                    if enable_speaker_distance:
                        distance = estimate_speaker_distance(audio_chunk)
                        if distance:
                            st.metric("Distance", distance)
                    
                    if enable_sound_alert:
                        alerts = detect_loud_sounds(audio_chunk, sound_threshold)
                        if alerts:
                            for sound, intensity in alerts:
                                st.warning(f"🔔 {sound}")
                
                st.success("✅ Processed!")
        
        st.session_state.recording_active = False
    
    # Caption history
    if st.session_state.caption_history:
        st.markdown("---")
        
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
        
        st.markdown("### 💬 Caption History")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            transcript_text = "\n\n".join([f"[{i+1}] {caption}" for i, caption in enumerate(st.session_state.caption_history)])
            st.download_button("📥 Export TXT", transcript_text, "hearmate_transcript.txt", "text/plain", use_container_width=True)
        
        for caption in reversed(list(st.session_state.caption_history)):
            context = analyze_speech_context(caption) if enable_context_aware else None
            
            if context and context['importance_score'] >= 3:
                st.markdown(f"<div class='alert-box-urgent'><strong>⚠️</strong> {caption}</div>", unsafe_allow_html=True)
            elif context and context['has_question']:
                st.markdown(f"<div class='alert-box-question'><strong>❓</strong> {caption}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='caption-box'>{caption}</div>", unsafe_allow_html=True)

elif mode == "⌚ Wearable Simulation":
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🎤 Capture", type="primary", use_container_width=True):
            with st.spinner("Recording..."):
                audio_chunk, _ = record_audio_chunk(duration=3)
                if audio_chunk:
                    transcript = transcribe_audio(audio_chunk)
                    st.session_state.last_caption = transcript
                    
                    if enable_smart_home:
                        sh_events = detect_smart_home_events(transcript)
                        if sh_events:
                            st.session_state.smart_home_alerts.append({
                                'type': sh_events[0]['type'],
                                'icon': sh_events[0]['icon'],
                                'text': transcript,
                                'time': datetime.now().strftime("%H:%M:%S")
                            })
                    st.rerun()
    
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.last_caption = ""
            st.rerun()
    
    display_text = st.session_state.last_caption if st.session_state.last_caption else "Tap 'Capture' to start..."
    
    st.markdown(f"""
        <div class='wearable-display'>
            <div style='font-size: 28px; margin-bottom: 30px; font-weight: 600;'>
                🎧 HearMate
            </div>
            <div style='font-size: {caption_font_size + 12}px; line-height: 1.5; padding: 20px;'>
                {display_text}
            </div>
        </div>
    """, unsafe_allow_html=True)

else:  # File Upload
    tab1, tab2 = st.tabs(["📤 Upload & Analyze", "📊 Insights"])
    
    with tab1:
        uploaded = st.file_uploader("Upload audio file", type=["wav", "mp3", "m4a"])
        
        if uploaded:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(uploaded.read())
                temp_path = tmp.name
            
            st.audio(uploaded)
            
            if st.button("🎯 Analyze", type="primary", use_container_width=True):
                with st.spinner("Processing..."):
                    audio_data, sr = sf.read(temp_path)
                    transcript = transcribe_audio(audio_data, sr)
                    
                    st.success("✅ Analysis Complete!")
                    st.markdown(f"<div class='caption-box' style='font-size:{caption_font_size}px;'>{transcript}</div>", unsafe_allow_html=True)
                    
                    if enable_context_aware:
                        context = analyze_speech_context(transcript)
                        if context:
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Importance", f"{context['importance_score']}/10")
                            with col2:
                                st.metric("Question?", "Yes" if context['has_question'] else "No")
                            with col3:
                                st.metric("Urgent?", "Yes" if context['has_urgency'] else "No")
                            with col4:
                                st.metric("Keywords", len(context['keywords_found']))
            
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    with tab2:
        st.markdown("### 📊 System Insights")
        if st.session_state.smart_home_alerts:
            st.subheader("🏠 Recent Smart Home Detections")
            for alert in reversed(st.session_state.smart_home_alerts[-5:]):
                st.info(f"{alert['icon']} {alert['type']} at {alert['time']}")

# Footer
# st.markdown("---")
# st.markdown("""
#     <div style='text-align: center; color: rgba(255,255,255,0.7); padding: 30px;'>
#         <p style='font-size: 18px; font-weight: 600; margin-bottom: 10px;'>🎧 HearMate v2.0</p>
#         <p style='font-size: 14px;'>AI-Powered Hearing Assistance with Smart Home Integration</p>
#         <p style='font-size: 12px; margin-top: 15px;'>Built with ❤️ for accessibility</p>
#     </div>
# """, unsafe_allow_html=True)
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>🎧 HearMate v1.0</strong> — AI-Powered Hearing Assistance Tool</p>
        <p style='font-size: 14px;'>Built with Streamlit • Groq Whisper • Python</p>
        <p style='font-size: 12px; margin-top: 10px;'>
            <em>Making sound visible for everyone</em>
        </p>
    </div>
""", unsafe_allow_html=True)



