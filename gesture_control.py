import cv2
import mediapipe as mp
import math
import textwrap

# MediaPipe 
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)

# Kamera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

cv2.namedWindow("Gesture Control", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Gesture Control", 960, 540)
fullscreen = False

frame_width = 1280
frame_height = 720

# Scrollbar özellikleri
scrollbar_thickness = 60
scrollbar_length = 500

horizontal_scroll_pos = 0
vertical_scroll_pos = 0
horizontal_max_scroll = frame_width - scrollbar_length
vertical_max_scroll = frame_height - scrollbar_length

bar_height = 100
bar_color = (0, 0, 0)
alpha_bar = 0.5

# Stage kontrolü: 1 = Butonlar var, 2 = Suggested songs UI + geri butonu
ui_stage = 1

# Stage 1 butonlar
button_texts = ["Play", "Pause", "Next", "Prev", "Vol +", "Vol -"]
base_colors = [
    (0, 120, 255),
    (0, 255, 0),
    (255, 0, 0),
    (255, 255, 0),
    (128, 0, 255),
    (255, 128, 0)
]

button_radius = 40
spacing = 50
button_count = len(button_texts)
total_buttons_width = button_count * (button_radius*2) + (button_count-1)*spacing
start_x = (frame_width - total_buttons_width) // 2
bar_y = (frame_height - bar_height) // 2

buttons = []
for i, text in enumerate(button_texts):
    cx = start_x + (button_radius + i * (2 * button_radius + spacing))
    cy = bar_y + bar_height // 2
    base_color = base_colors[i % len(base_colors)]
    buttons.append({"cx": cx, "cy": cy, "r": button_radius, "text": text, "base_color": base_color})

clicked_button_text = None

# Stage 2 için içerikler
song_titles = [f"Song {i+1} - Awesome Track {i+1}" for i in range(50)]
line_height = 50

long_text = """\
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed feugiat nulla a enim venenatis, ac placerat magna dignissim. Praesent id quam felis. Curabitur vestibulum elit sed nunc hendrerit semper. Aliquam erat volutpat. Suspendisse potenti. Morbi vitae tincidunt ante. Quisque pharetra volutpat magna, vel laoreet ipsum maximus in. Vestibulum dictum lorem ut elementum rhoncus. Nulla facilisi. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.

Donec congue, urna non eleifend blandit, ante risus condimentum metus, non dignissim eros metus sit amet sapien. Nam vel ultricies eros, a ullamcorper elit. Suspendisse vehicula, odio sed posuere aliquam, magna nisi maximus augue, vitae ultrices metus urna nec justo. Vivamus id volutpat nunc, et finibus libero. Etiam maximus nunc vitae pretium efficitur. Vivamus congue risus vel tellus blandit vehicula. Donec metus neque, sollicitudin sit amet purus ac, efficitur vehicula felis. Nulla vulputate vel elit mollis gravida.

Sed facilisis arcu id mauris tristique, at tincidunt lectus viverra. Nullam interdum urna leo, vitae vestibulum velit tristique eu. Proin mattis felis et sapien vestibulum, eget porttitor metus facilisis. Duis ut lectus et urna bibendum molestie vitae non sem. Etiam dapibus id augue in facilisis. Nullam porta blandit sapien, id ultricies nulla mollis a. Fusce ullamcorper, magna eget scelerisque gravida, nunc tortor suscipit massa, sit amet efficitur mi sapien eu risus. Aenean porttitor accumsan nulla, ac viverra nisl venenatis quis. Aliquam porttitor semper metus, quis suscipit velit.
""".strip()

wrapped_text = textwrap.wrap(long_text, width=80)
content_height = 200 + len(song_titles)*line_height + len(wrapped_text)*40

back_button = {
    "cx": frame_width // 2 + 300,
    "cy": 60,
    "r": 40,
    "text": "Back",
    "base_color": (0, 128, 255)  
}