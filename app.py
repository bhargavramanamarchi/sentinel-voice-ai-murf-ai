import google.generativeai as genai
from murf import Murf
import gradio as gr
import os
import speech_recognition as sr
from pydub import AudioSegment
import requests
import re

# CONFIGURATION


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")
murf_client = Murf(api_key=MURF_API_KEY)

# Multilingual Configuration
LANG_CONFIGS = {
    'English': {'sr_code': 'en-US', 'murf_voice': 'en-US-natalie', 'display_name': 'English'},
    'Hindi': {'sr_code': 'hi-IN', 'murf_voice': 'hi-IN-amit', 'display_name': 'Hindi'},
    'Telugu': {'sr_code': 'te-IN', 'murf_voice': 'te-IN-sai', 'display_name': 'Telugu'},
    'Tamil': {'sr_code': 'ta-IN', 'murf_voice': 'ta-IN-vikram', 'display_name': 'Tamil'},
    'Kannada': {'sr_code': 'kn-IN', 'murf_voice': 'kn-IN-ravi', 'display_name': 'Kannada'},
    'Malayalam': {'sr_code': 'ml-IN', 'murf_voice': 'ml-IN-arjun', 'display_name': 'Malayalam'}
}

def sentinel_logic(audio_path, language_selection):
    """Processes audio input to detect scams and return a multilingual voice response and escape score."""
    try:
        if audio_path is None:
            return None, "Please record audio first.", 0

        # 1. Retrieve language settings from global LANG_CONFIGS
        config = LANG_CONFIGS[language_selection]
        sr_code = config['sr_code']
        murf_voice_id = config['murf_voice']
        display_lang = config['display_name']

        # 2. Speech to Text
        recognizer = sr.Recognizer()
        audio = AudioSegment.from_file(audio_path)
        audio.export("temp.wav", format="wav")
        with sr.AudioFile("temp.wav") as source:
            user_text = recognizer.recognize_google(recognizer.record(source), language=sr_code)

        # 3. Gemini Analysis (using gemini-2.5-flash)
        # UPDATED PROMPT: Requesting a 'Scam Escape Score' (0-100)
        prompt = f"""Analyze this potential scam: {user_text}.
        Provide your response in this exact format in {display_lang}:
        TIP: [A factual 20-word tip]
        SCORE: [A numeric Scam Escape Score from 0 to 100, where 100 means a high probability of successfully identifying or avoiding the scam and 0 means a low probability]"""

        response = model.generate_content(prompt)
        raw_text = response.text

        # 4. Parsing logic using regex
        tip_match = re.search(r"TIP:\s*(.*)", raw_text)
        score_match = re.search(r"SCORE:\s*(\d+)", raw_text)

        ai_script = tip_match.group(1).strip() if tip_match else "Potential threat detected. Be cautious."
        # Metric now represents an 'Escape Score'
        escape_score = int(score_match.group(1)) if score_match else 50

        # 5. Murf Voice Generation
        res = murf_client.text_to_speech.generate(
            text=ai_script,
            voice_id=murf_voice_id
        )

        # 6. Download and Save Murf response
        audio_data = requests.get(res.audio_file).content
        with open("response.mp3", "wb") as f:
            f.write(audio_data)

        return "response.mp3", ai_script, escape_score

    except Exception as e:
        return None, f"Error occurred: {str(e)}", 0

print('sentinel_logic function successfully updated with Scam Escape Score logic.')

#Advanced Glassm# 1. Finalized orphism CSS
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');

.gradio-container {
    background: linear-gradient(135deg, #0f172a 0%, #020617 100%) !important;
    color: #f8fafc !important;
    font-family: 'Inter', sans-serif !important;
    backdrop-filter: blur(15px) !important;
}

.security-group {
    border: 1px solid rgba(59, 130, 246, 0.5) !important;
    border-radius: 20px !important;
    background: rgba(17, 24, 39, 0.6) !important;
    padding: 24px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(20px);
}

h1, h2, h3 {
    font-weight: 800 !important;
    color: #00f2ff !important;
    text-shadow: 0 0 15px rgba(0, 242, 255, 0.7) !important;
}

.analyze-btn {
    background: linear-gradient(90deg, #00f2ff, #3b82f6) !important;
    color: #020617 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 12px !important;
    transition: all 0.4s ease !important;
}

.analyze-btn:hover {
    transform: scale(1.05);
    box_shadow: 0 0 30px rgba(0, 242, 255, 0.6) !important;
}
"""

# 2. Reconstruct Polished Gradio Interface
with gr.Blocks(css=custom_css) as demo:
    # System Status Header
    gr.HTML("""
    <div style='background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; border-radius: 8px; padding: 10px; margin-bottom: 20px; text-align: center;'>
        <span style='color: #10b981; font-weight: bold;'>● SYSTEM STATUS: ACTIVE MONITORING</span>
    </div>
    """)

    gr.HTML("<h1 style='text-align: center;'>🛡️ SENTINEL VOICE AI</h1>")

    # 3. Optimized Dual-Column Layout
    with gr.Row():
        # Left Column: Input
        with gr.Column(scale=1):
            with gr.Group(elem_classes='security-group'):
                gr.Markdown("### 🎙️ Input Interface")
                input_mic = gr.Audio(sources='microphone', type='filepath', label='Record Suspicious Audio')
                language_dropdown = gr.Dropdown(
                    label='Select Language',
                    choices=list(LANG_CONFIGS.keys()),
                    value='English'
                )
                btn = gr.Button('RUN THREAT ANALYSIS', variant='primary', elem_classes='analyze-btn')

        # Right Column: Results
        with gr.Column(scale=1):
            with gr.Group(elem_classes='security-group'):
                gr.Markdown("### 🔍 Analysis Report")
                output_audio = gr.Audio(label='Sentinel Voice Feedback', autoplay=True)
                output_text = gr.Markdown(label='Safety Tip')
                # Updated label to 'Scam Escape Score'
                output_score = gr.Label(label='Scam Escape Score', num_top_classes=1)

    # 4. Logic Mapping
    btn.click(
        fn=sentinel_logic,
        inputs=[input_mic, language_dropdown],
        outputs=[output_audio, output_text, output_score]
    )

# 5. Launch with share enabled and custom CSS
demo.launch(share=True)
print('Sentinel Voice AI dashboard launched successfully.')