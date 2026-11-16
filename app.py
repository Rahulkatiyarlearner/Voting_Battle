import streamlit as st
import random
import time
import io
import wave
import struct
import math
import base64
from gtts import gTTS
from PIL import Image

st.set_page_config(page_title="Voting Battle Match", layout="wide")

# --- Audio & TTS Helpers ---

def generate_dice_sound_bytes():
    """Generates a short synthesized dice-rattle WAV sound in memory."""
    sample_rate = 22050
    duration = 0.7  # seconds
    num_samples = int(sample_rate * duration)
    buf = io.BytesIO()
    
    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = i / sample_rate
            bounce = abs(math.sin(2 * math.pi * 14 * t)) ** 3
            envelope = math.exp(-3.5 * t)
            noise = random.uniform(-1, 1)
            sample = int(32767 * 0.6 * noise * bounce * envelope)
            wav_file.writeframes(struct.pack('<h', sample))
            
    return buf.getvalue()

def get_hindi_tts_bytes(text):
    """Converts Hindi text into MP3 audio bytes using gTTS."""
    tts = gTTS(text=text, lang='hi', slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()

def autoplay_audio(audio_bytes, audio_format="mp3"):
    """Embeds an invisible HTML5 audio player that plays immediately."""
    b64 = base64.b64encode(audio_bytes).decode()
    md = f"""
        <audio autoplay="true" style="display:none;">
            <source src="data:audio/{audio_format};base64,{b64}" type="audio/{audio_format}">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

def render_dice_html(value, rolling=False):
    """Renders a visual CSS dice face (1 to 6) with optional shake animation."""
    pip_positions = {
        1: [4],
        2: [0, 8],
        3: [0, 4, 8],
        4: [0, 2, 6, 8],
        5: [0, 2, 4, 6, 8],
        6: [0, 2, 3, 5, 6, 8],
    }
    active_pips = pip_positions.get(value, [4])
    anim_style = "animation: shake 0.35s infinite;" if rolling else ""
    
    pips_html = ""
    for idx in range(9):
        if idx in active_pips:
            pips_html += '<div style="width:16px; height:16px; background:#111; border-radius:50%; margin:auto;"></div>'
        else:
            pips_html += '<div></div>'
            
    return f"""
    <style>
        @keyframes shake {{
            0% {{ transform: rotate(0deg) scale(1.05); }}
            25% {{ transform: rotate(12deg) scale(1.1); }}
            50% {{ transform: rotate(0deg) scale(1.05); }}
            75% {{ transform: rotate(-12deg) scale(1.1); }}
            100% {{ transform: rotate(0deg) scale(1.05); }}
        }}
    </style>
    <div style="
        width: 90px; height: 90px; 
        background: #ffffff; 
        border: 3px solid #222; 
        border-radius: 14px; 
        display: grid; 
        grid-template-columns: repeat(3, 1fr); 
        grid-template-rows: repeat(3, 1fr); 
        padding: 10px; 
        margin: 15px auto;
        box-shadow: 0 6px 14px rgba(0,0,0,0.18);
        {anim_style}
    ">
        {pips_html}
    </div>
    """

def get_placeholder_image(name):
    """Creates a clean fallback image if the user doesn't upload one."""
    return Image.new("RGB", (300, 300), color=(230, 236, 245))

# --- Session State Initialization ---

if "page" not in st.session_state:
    st.session_state.page = "main"
if "max_score" not in st.session_state:
    st.session_state.max_score = 20
if "competitors" not in st.session_state:
    st.session_state.competitors = []
if "turn_index" not in st.session_state:
    st.session_state.turn_index = 0
if "dice_value" not in st.session_state:
    st.session_state.dice_value = 1
if "winner" not in st.session_state:
    st.session_state.winner = None
if "game_started" not in st.session_state:
    st.session_state.game_started = False

# ==========================================
# PAGE 1: MAIN PAGE (SETUP)
# ==========================================
if st.session_state.page == "main":
    st.markdown("<h1 style='text-align: center;'>Main Page</h1>", unsafe_allow_html=True)
    st.write("---")

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        max_score = st.number_input(
            "What should be maximum score", 
            min_value=1, 
            max_value=1000, 
            value=15, 
            step=1
        )
        num_competitors = st.number_input(
            "Provide number of competitors", 
            min_value=2, 
            max_value=10, 
            value=2, 
            step=1
        )

        st.markdown("### Based on number of competitors (Enter Name and Image)")
        
        competitor_inputs = []
        for i in range(int(num_competitors)):
            c1, c2 = st.columns([1, 1])
            with c1:
                name = st.text_input(f"Name {i+1}", value=f"Competitor {i+1}", key=f"name_{i}")
            with c2:
                uploaded_file = st.file_uploader(
                    f"Upload Image {i+1}", 
                    type=["png", "jpg", "jpeg", "webp"], 
                    key=f"img_{i}"
                )
            competitor_inputs.append((name, uploaded_file))

        st.write("")
        if st.button("Start Competition", type="primary", use_container_width=True):
            comp_list = []
            for idx, (cname, cfile) in enumerate(competitor_inputs):
                clean_name = cname.strip() if cname.strip() else f"Competitor {idx+1}"
                if cfile is not None:
                    img = Image.open(cfile)
                else:
                    img = get_placeholder_image(clean_name)
                
                comp_list.append({
                    "name": clean_name,
                    "image": img,
                    "score": 0
                })
            
            st.session_state.max_score = int(max_score)
            st.session_state.competitors = comp_list
            st.session_state.turn_index = 0
            st.session_state.dice_value = 1
            st.session_state.winner = None
            st.session_state.game_started = True
            st.session_state.page = "battle"
            st.rerun()

# ==========================================
# PAGE 2: VOTING BATTLE MATCH (AUTOMATED)
# ==========================================
elif st.session_state.page == "battle":
    st.markdown("<h1 style='text-align: center;'>Voting Battle Match</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align: center; font-size: 18px;'>Target Maximum Score: <b>{st.session_state.max_score}</b></p>", 
        unsafe_allow_html=True
    )
    st.write("---")

    # Inject CSS to enforce a fixed, uniform image box size for all competitors
    st.markdown(
        """
        <style>
        .competitor-img-container img {
            width: 180px !important;
            height: 180px !important;
            object-fit: cover !important;
            border-radius: 10px !important;
            display: block !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    competitors = st.session_state.competitors
    num_comps = len(competitors)
    current_idx = st.session_state.turn_index

    board_placeholder = st.empty()
    dice_placeholder = st.empty()
    status_placeholder = st.empty()
    audio_placeholder = st.empty()

    def draw_board(active_index=None):
        with board_placeholder.container():
            cols = st.columns(num_comps)
            for idx, comp in enumerate(competitors):
                with cols[idx]:
                    is_active = (idx == active_index) and (st.session_state.winner is None)
                    border_color = "#ff4b4b" if is_active else "#e0e0e0"
                    bg_color = "#000000" if is_active else "#444444"
                    
                    st.markdown(
                        f"""
                        <div style="
                            border: 3px solid {border_color}; 
                            background-color: {bg_color};
                            border-radius: 12px; 
                            padding: 15px; 
                            text-align: center;
                        ">
                            <h3 style="margin-bottom: 10px;">{comp['name']}</h3>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Render image inside the fixed-size CSS container
                    st.markdown('<div class="competitor-img-container">', unsafe_allow_html=True)
                    st.image(comp["image"])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown(
                        f"<h3 style='text-align: center;'>Total Vote: {comp['score']}</h3>", 
                        unsafe_allow_html=True
                    )

    draw_board(active_index=current_idx)

    if st.session_state.winner is None:
        current_comp = competitors[current_idx]
        
        status_placeholder.info(f"🎲 Rolling dice automatically for **{current_comp['name']}**...")
        with dice_placeholder.container():
            st.markdown(render_dice_html(random.randint(1, 6), rolling=True), unsafe_allow_html=True)
        
        with audio_placeholder.container():
            dice_wav = generate_dice_sound_bytes()
            autoplay_audio(dice_wav, audio_format="wav")
        
        time.sleep(1.5)

        rolled_votes = random.randint(1, 6)
        st.session_state.dice_value = rolled_votes
        competitors[current_idx]["score"] += rolled_votes
        new_score = competitors[current_idx]["score"]

        draw_board(active_index=current_idx)
        with dice_placeholder.container():
            st.markdown(render_dice_html(rolled_votes, rolling=False), unsafe_allow_html=True)

        hindi_vote_text = f"{current_comp['name']} को {rolled_votes} वोट मिले"
        status_placeholder.success(f"🗳️ **{current_comp['name']}** got **{rolled_votes}** votes! (Total: {new_score})")
        
        with audio_placeholder.container():
            tts_mp3 = get_hindi_tts_bytes(hindi_vote_text)
            autoplay_audio(tts_mp3, audio_format="mp3")

        time.sleep(3.5)

        if new_score >= st.session_state.max_score:
            st.session_state.winner = current_comp["name"]
            st.rerun()
        else:
            st.session_state.turn_index = (current_idx + 1) % num_comps
            st.rerun()

    else:
        winner_name = st.session_state.winner
        with dice_placeholder.container():
            st.markdown(render_dice_html(st.session_state.dice_value, rolling=False), unsafe_allow_html=True)
            
        st.balloons()
        status_placeholder.markdown(
            f"""
            <div style="
                background-color: #d4edda; 
                border: 2px solid #28a745; 
                color: #155724; 
                padding: 20px; 
                border-radius: 12px; 
                text-align: center;
                margin-top: 15px;
            ">
                <h2>🏆 {winner_name} wins the competition! 🏆</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        hindi_win_text = f"{winner_name} ने यह प्रतियोगिता जीत ली है"
        with audio_placeholder.container():
            win_mp3 = get_hindi_tts_bytes(hindi_win_text)
            autoplay_audio(win_mp3, audio_format="mp3")

        st.write("")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Back to Main Page", use_container_width=True):
                st.session_state.page = "main"
                st.session_state.winner = None
                st.rerun()