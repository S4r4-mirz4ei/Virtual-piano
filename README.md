## **Virtual Piano with Hand Tracking 🎹**

This is a Virtual Piano that uses computer vision to detect hand movements and play notes. You can play freely or choose a song to follow.

## Features
- 🖐️ **Hand Tracking** using MediaPipe for **finger position detection**.
- 🎼 **Song Mode** with pre-selected songs that can be played using **common fourth-octave piano keys**.
- 🎵 **Real-time note display** with **color changes** to indicate when to play:
  - **Green → Blue** as notes approach the keys.
  - **Red** for the next note to be played.
- 🎹 **Freestyle Mode** Play any key at any time without selecting a song.
- 🎯 **Tap-Only Key Activation**: To prevent accidental notes, a key will only play if your finger **moves downward from above**, ensuring intentional key presses.


---

## How to Use

**🎼 Song Selection Mode**
1. On the first screen, available songs appear as buttons at the top of the screen.
2. Select a song by pointing your **index finger** at the desired button on the screen.
3. Once a song is selected, the song title appears at the top.

**🎵 Playing a Song**
1. Show a **V-sign** with your hand to start the song.
2. Notes will begin falling down towards the piano keys.
3. Watch the colors:
   - Green: Notes are far from the keys.
   - Blue: Notes are getting closer.
   - Red: The next note to be played.
4. Tap the keys at the right moment to match the song.

**⏹️ Stopping a Song**
- To stop the song and return to the **song selection screen**, tap the **"Stop" button** at the top left using your index finger.

**🎹 Freestyle Mode**
- If no song is selected, you can play the piano freely.
- Tap the keys by **moving your finger downwards onto them** (prevents accidental key presses).

---

## 🎶 Song List
- 🎂 **Happy Birthday**
- 🎹 **Für Elise**
- ⭐ **Twinkle Twinkle**
- 🎄 **Jingle Bells**
- 🐑 **Mary Had a Little Lamb**
  
---

## 📦 Installation

1. **Clone this repository**
   Open a terminal and run:
   ```
   git clone https://github.com/S4r4-mirz4ei/Virtual-piano.git
   ```
   Then, navigate into the project directory:
   ```
   cd Virtual-piano
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the program:
   ```
   python main.py
   ```

🛠️ Requirements
- Python 3.7+
- OpenCV
- MediaPipe
- Pygame
- Pillow (PIL)


---

 **Author**
👤 Sara Mirzaei
📧 Email: sara.mirz4ei@gmail.com
🔗 GitHub: [S4r4-mirz4ei](https://github.com/S4r4-mirz4ei)
