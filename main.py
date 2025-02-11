import cv2
import mediapipe as mp
import time
from utils import (
    load_songs, put_unicode_text, is_v_sign, load_sounds,
    find_closest_note, note_color_gradient
)

# ----------------------------- Initialization -----------------------------
# Screen settings
screen_width = 1280
screen_height = 832
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)

# ----------------------------- Load Songs & Sounds -----------------------------
# From utils.py
songs = load_songs()
key_sounds = load_sounds()

# ----------------------------- UI Elements -----------------------------
# Stop Button Position
BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT = 10, 10, 100, 70

# Song Selection Boxes
song_boxes = [
    (int(screen_width / 2 - 500 + i * 210), 10, 200, 50, name)
    for i, name in enumerate(songs.keys())
]

# ----------------------------- Key Positions -----------------------------
# Piano Keys
NUM_KEYS = 10
MARGIN = 200
KEY_Y_POSITION = int(screen_height // 1.25)
KEY_WIDTH = (screen_width - 2 * MARGIN) // NUM_KEYS
piano_keys = [(MARGIN + i * KEY_WIDTH, KEY_Y_POSITION, KEY_WIDTH, 100) for i in range(NUM_KEYS)]

# Note Mapping
KEY_NAMES = ["C", "C#", "D", "D#", "E", "F", "G", "G#", "A", "B"]
NOTE_TO_KEY = {note: index for index, note in enumerate(KEY_NAMES)}

# ----------------------------- Hand Recognition -----------------------------
# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# ----------------------------- Control Variables -----------------------------
song_selected = None
note_flowing = False
stopped = True
notes = []
start_time = time.time()
note_index = 0
note_speed = 4
active_keys = set()

# ----------------------------- Main Loop -----------------------------
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.resize(frame, (screen_width, screen_height))
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # -------------------------- Draw Piano Keys --------------------------
    for i, (x, y, w, h) in enumerate(piano_keys):
        overlay = frame.copy()
        alpha = 0.5
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (255, 255, 255), -1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 1)
        cv2.putText(frame, KEY_NAMES[i], (x + 10, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)

    # -------------------------- Detect Key Taps --------------------------
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get index finger position
            x_finger = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * screen_width)
            y_finger = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * screen_height)

            # Play sound when keys are tapped
            for i, (x, y, w, h) in enumerate(piano_keys):
                if x < x_finger < x + w and y < y_finger < y + h:
                    if i not in active_keys:
                        key_sounds[i].stop()
                        key_sounds[i].play()
                        active_keys.add(i)
                elif i in active_keys and not (x < x_finger < x + w and y < y_finger < y + h):
                    active_keys.remove(i)

    # -------------------------- Song Selection Screen --------------------------
    if song_selected is None:
        for box_x, box_y, box_width, box_height, song_name in song_boxes:
            cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), (0, 255, 0), -1)
            cv2.putText(frame, song_name, (box_x + 10, box_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Detect song selection
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                x_finger = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * screen_width)
                y_finger = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * screen_height)

                # Check if finger taps a song box
                for box_x, box_y, box_width, box_height, song_name in song_boxes:
                    if box_x < x_finger < box_x + box_width and box_y < y_finger < box_y + box_height:
                        song_selected = song_name
                        melody, timing = songs[song_selected]["melody"], songs[song_selected]["timing"]
                        start_time = time.time()
                        note_index = 0
                        notes = []
                        break

    # -------------------------- A Song is Selected --------------------------
    else:
        # Display the selected song name
        cv2.putText(frame, song_selected, (screen_width // 2 - 100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Draw the Stop button
        cv2.rectangle(frame, (BUTTON_X, BUTTON_Y), (BUTTON_X + BUTTON_WIDTH, BUTTON_Y + BUTTON_HEIGHT), (0, 0, 255), -1)
        cv2.putText(frame, "Stop", (BUTTON_X + 20, BUTTON_Y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Detect hand interactions
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness_data in zip(results.multi_hand_landmarks, results.multi_handedness):
                x_finger = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * screen_width)
                y_finger = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * screen_height)

                # Detect Stop button tap
                if BUTTON_X <= x_finger <= BUTTON_X + BUTTON_WIDTH and BUTTON_Y <= y_finger <= BUTTON_Y + BUTTON_HEIGHT:
                    note_flowing = False
                    stopped = True
                    song_selected = None
                    notes = []
                    break

                # Start notes flow if V-sign detected
                if is_v_sign(hand_landmarks) and stopped:
                    note_flowing = True
                    stopped = False
                    start_time = time.time()
                    note_index = 0
                    notes = []


    # -------------------------- Handle Notes Falling --------------------------
    if note_flowing:
        if note_index < len(melody) and time.time() - start_time >= sum(timing[:note_index + 1]):
            notes.append((NOTE_TO_KEY[melody[note_index]], 0))
            note_index += 1

        # Find closest note within 100 pixels of the keys
        closest_note_index = find_closest_note(notes, KEY_Y_POSITION, 100)

        for i, note in enumerate(notes):
            key_index, y_pos = note
            y_pos += note_speed
            x = MARGIN + key_index * KEY_WIDTH + KEY_WIDTH // 2

            # Use interpolate_note_color() from utils.py
            note_color = note_color_gradient(y_pos, KEY_Y_POSITION, i == closest_note_index)

            # Draw the note
            frame = put_unicode_text(frame, "♪", (x - 15, int(y_pos) - 15), font_size=50, color=note_color)

            notes[i] = (key_index, y_pos)

    # Show frame
    cv2.imshow("Virtual Piano with Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
