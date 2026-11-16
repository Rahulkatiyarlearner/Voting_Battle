# 🎲 Automated Voting Battle Match

An interactive, fully automated voting competition web application built with **Streamlit**. Competitors take turns in a dice-based voting battle with sound effects, uniform image cards, and live **Hindi voice announcements** until a winner reaches the target score.

---

## ✨ Features

* **Dynamic Setup ("Main Page"):**
  * Configure the target **Maximum Score** required to win.
  * Set the **Number of Competitors** (supports 2 to 10 participants).
  * Enter custom names and upload profile images for each competitor (includes an automatic fallback placeholder if no image is uploaded).
* **Automated Battle Arena ("Voting Battle Match"):**
  * **Zero Human Involvement:** Once started, the dice rolls automatically turn-by-turn across all competitors.
  * **Uniform Image Sizing:** All competitor images are standardized to a fixed `180x180px` layout with clean cropping (`object-fit: cover`).
  * **Visual Dice & Active Turn Highlighting:** Animated CSS dice shake effects and highlighted borders show whose turn is active.
* **Audio Effects & Hindi Voiceovers:**
  * **Synthesized Dice Sound:** Plays a generated dice-rattle audio effect on every roll.
  * **Hindi Vote Announcements:** Uses Google Text-to-Speech (`gTTS`) to announce *"[Name] को [X] वोट मिले"* after every roll.
  * **Hindi Winner Declaration:** Celebrates with balloons and announces *"[Name] ने यह प्रतियोगिता जीत ली है"* when a competitor hits the maximum score.

---

## 🛠️ Tech Stack

* **Python 3.8+**
* **Streamlit** – Web UI and automated state loop
* **gTTS (Google Text-to-Speech)** – Hindi voice synthesis
* **Pillow (PIL)** – Image handling and fallback placeholders
* **Standard Library (`wave`, `struct`, `math`)** – In-memory WAV dice sound generation

---

## 📂 Project Structure

```text
voting-battle-match/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## 🚀 Installation & Setup

1. **Clone or download** the project files into a local directory.
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate        # On macOS/Linux
   venv\Scripts\activate           # On Windows
   ```
3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

---

## 🎮 How to Use

1. Open the local URL shown in your terminal (typically `http://localhost:8501`).
2. On the **Main Page**, enter the **Maximum Score** and **Number of Competitors**.
3. Fill in each competitor's **Name** and upload their **Image**.
4. Click **Start Competition**.
5. Sit back and watch! The app will automatically roll the dice, play sound effects, announce scores in Hindi, and declare the winner.
6. Click **Back to Main Page** after the match ends to start a new competition.

---

## ⚠️ Notes

* **Internet Connection:** An active internet connection is required for `gTTS` to generate the Hindi audio announcements.
* **Browser Audio Autoplay:** Modern browsers require at least one click on the page before allowing audio to play automatically. Clicking the **Start Competition** button enables seamless autoplay for all subsequent dice rolls and voiceovers.
