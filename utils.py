import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Load Unicode text for musical notes
def put_unicode_text(frame, text, position, font_size=30, color=(255, 255, 0)):
    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(frame_pil)

    # Construct the font path dynamically
    font_path = os.path.join(os.path.abspath(os.getcwd()), "fonts", "Arial.ttf")

    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        return None  # Return None if font is missing

    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

# Detect V-sign gesture
def is_v_sign(hand_landmarks):
    index_extended = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
    middle_extended = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
    ring_folded = hand_landmarks.landmark[16].y > hand_landmarks.landmark[14].y
    pinky_folded = hand_landmarks.landmark[20].y > hand_landmarks.landmark[18].y
    return index_extended and middle_extended and ring_folded and pinky_folded

# Detect Thumbs Up gesture
def is_thumbs_up(hand_landmarks):
    thumb_extended = hand_landmarks.landmark[4].y < hand_landmarks.landmark[3].y
    other_fingers_folded = all(
        hand_landmarks.landmark[finger_tip].y > hand_landmarks.landmark[finger_dip].y
        for finger_tip, finger_dip in [
            (8, 6), (12, 10), (16, 14), (20, 18)
        ]
    )
    return thumb_extended and other_fingers_folded

# Interpolate color for falling notes (Blue → Green → Red)

def note_color_gradient(y_pos, key_y_position, is_closest):
    """
    Determines the note color based on position and closest note logic.
    - If closest note: Turns RED.
    - Otherwise: Transitions from GREEN (high) to BLUE (low).
    """
    if is_closest:
        return (255, 0, 0)  # RED for the closest note

    # Gradient transition from GREEN (top) to BLUE (closer to keys)
    top_y = 0
    bottom_y = key_y_position - 100
    blend_factor = min(1, max(0, (y_pos - top_y) / (bottom_y - top_y)))
    
    start_color = (0, 255, 0)  # Green
    end_color = (0, 0, 255)    # Blue
    
    return (
        int(start_color[0] + blend_factor * (end_color[0] - start_color[0])),
        int(start_color[1] + blend_factor * (end_color[1] - start_color[1])),
        int(start_color[2] + blend_factor * (end_color[2] - start_color[2]))
    )

# Find the closest note to the keys
def find_closest_note(notes, key_y_position, threshold=100):
    closest_note_index = None
    closest_distance = float('inf')

    for i, (_, y_pos) in enumerate(notes):
        if key_y_position - threshold <= y_pos < key_y_position:
            if y_pos < closest_distance:
                closest_note_index = i
                closest_distance = y_pos

    return closest_note_index

# Load sound files
import pygame
def load_sounds():
    pygame.mixer.init()
    key_sounds = [
        pygame.mixer.Sound("sounds/C4.wav"),
        pygame.mixer.Sound("sounds/D#4.wav"),
        pygame.mixer.Sound("sounds/D4.wav"),
        pygame.mixer.Sound("sounds/D#4.wav"),
        pygame.mixer.Sound("sounds/E4.wav"),
        pygame.mixer.Sound("sounds/F4.wav"),
        pygame.mixer.Sound("sounds/G4.wav"),
        pygame.mixer.Sound("sounds/G#4.wav"),
        pygame.mixer.Sound("sounds/A4.wav"),
        pygame.mixer.Sound("sounds/B4.wav")
    ]
    return key_sounds

# Load songs (melodies and timings)
def load_songs():
    return {
        "Happy Birthday": {
            "melody": ["G", "G", "A", "G", "C", "B", "G", "G", "A", "G", "D", "C", 
                       "G", "G", "G", "E", "C", "B", "A", "F", "F", "E", "C", "D", "C"],
            "timing": [0.5, 0.5, 1.0, 1.0, 1.0, 2.0, 0.5, 0.5, 1.0, 1.0, 1.0, 2.0,
                       0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 2.0, 0.5, 0.5, 1.0, 1.0, 1.0, 2.0]
        },
        "Fur Elise": {
            "melody": ["E", "D#", "E", "D#", "E", "B", "D", "C", "A", "C", "E", "A", "B", "E", "G#", "B", "C"],
            "timing": [0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 0.5, 0.5, 2.0, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 0.5, 2.0]
        },
        "Twinkle Twinkle": {
            "melody": ["C", "C", "G", "G", "A", "A", "G", "F", "F", "E", "E", "D", "D", "C",
                       "G", "G", "F", "F", "E", "E", "D", "G", "G", "F", "F", "E", "E", "C"],
            "timing": [0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 2.0, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 2.0,
                       0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 2.0, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 2.0]
        },
        "Mary Had a Little Lamb": {
            "melody": ["E", "D", "C", "D", "E", "E", "E", "D", "D", "D", "E", "G", "G",
                       "E", "D", "C", "D", "E", "E", "E", "E", "D", "D", "E", "D", "C"],
            "timing": [0.5, 0.5, 0.5, 0.5, 1.0, 0.5, 2.0, 0.5, 0.5, 0.5, 1.0, 0.5, 2.0,
                       0.5, 0.5, 0.5, 0.5, 1.0, 0.5, 2.0, 0.5, 0.5, 0.5, 1.0, 0.5, 2.0]
        },
        "Jingle Bells": {
            "melody": ["E", "E", "E", "E", "E", "E", "E", "G", "C", "D", "E", "F", "F", "F", "F", "F",
                       "E", "E", "E", "E", "D", "D", "E", "D", "G"],
            "timing": [0.5, 0.5, 1.0, 0.5, 0.5, 1.0, 0.5, 0.5, 0.5, 0.5, 2.0, 0.5, 0.5, 0.5, 1.0, 0.5,
                       0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 2.0]
        }
    }
