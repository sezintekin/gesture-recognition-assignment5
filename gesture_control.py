import cv2
import mediapipe as mp
import math

# MediaPipe hazırlıkları
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)

# Kamera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Pencere boyutunu orta büyüklükte ayarla
cv2.namedWindow("Gesture Control", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Gesture Control", 960, 540)

# Butonlar
button_texts = ["Play", "Pause", "Next", "Prev", "Vol +", "Vol -"]
base_colors = [
    (0, 120, 255),
    (0, 255, 0),
    (255, 0, 0),
    (255, 255, 0),
    (128, 0, 255),
    (255, 128, 0)
]

bar_height = 100
bar_color = (0, 0, 0)
alpha_bar = 0.5

frame_width = 1280
frame_height = 720
bar_y = (frame_height - bar_height) // 2

button_radius = 40
spacing = 50
button_count = len(button_texts)
total_buttons_width = button_count * (button_radius*2) + (button_count-1)*spacing
start_x = (frame_width - total_buttons_width) // 2

buttons = []
for i, text in enumerate(button_texts):
    cx = start_x + (button_radius + i*(2*button_radius+spacing))
    cy = bar_y + bar_height // 2
    base_color = base_colors[i % len(base_colors)]
    buttons.append({"cx": cx, "cy": cy, "r": button_radius, "text": text, "base_color": base_color})

def draw_circle_button(overlay, button, cursor_x, cursor_y, pinch_detected):
    cx, cy, r = button["cx"], button["cy"], button["r"]
    text = button["text"]
    base_color = button["base_color"]

    dist = math.hypot(cursor_x - cx, cursor_y - cy)
    hovered = dist < r
    clicked = hovered and pinch_detected

    # Hover ve click durumunda rengi daha belirgin yap
    if clicked:
        color = (min(base_color[0]+80, 255), min(base_color[1]+80, 255), min(base_color[2]+80, 255))
        cv2.putText(overlay, f"{text} Clicked!", (50, frame_height - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    elif hovered:
        color = (min(base_color[0]+50, 255), min(base_color[1]+50, 255), min(base_color[2]+50, 255))
        cv2.circle(overlay, (cx, cy), r+10, (255, 255, 255), 2)  # Ek bir çerçeveyle hover'ı vurgula
    else:
        color = base_color

    # Gölge
    shadow_offset = 3
    shadow_color = (30, 30, 30)
    cv2.circle(overlay, (cx+shadow_offset, cy+shadow_offset), r, shadow_color, -1)

    # Buton dairesi
    cv2.circle(overlay, (cx, cy), r, color, -1)

    # Metin
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    text_size = cv2.getTextSize(text, font, font_scale, 2)[0]
    text_x = cx - text_size[0]//2
    text_y = cy + text_size[1]//2
    cv2.putText(overlay, text, (text_x+1, text_y+1), font, font_scale, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(overlay, text, (text_x, text_y), font, font_scale, (255, 255, 255), 2, cv2.LINE_AA)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    cursor_x, cursor_y = -1, -1
    pinch_detected = False

    if result.multi_hand_landmarks:
        for hand_landmark in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame,
                hand_landmark,
                mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4),
                mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2)
            )

            index_tip = hand_landmark.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmark.landmark[mp_hands.HandLandmark.THUMB_TIP]
            cursor_x = int(index_tip.x * frame.shape[1])
            cursor_y = int(index_tip.y * frame.shape[0])
            distance = math.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
            if distance < 0.05:
                pinch_detected = True

    overlay = frame.copy()
    bar_overlay = overlay.copy()
    cv2.rectangle(bar_overlay, (0, bar_y), (frame_width, bar_y + bar_height), bar_color, -1)
    cv2.addWeighted(bar_overlay, alpha_bar, overlay, 1 - alpha_bar, 0, overlay)

    for btn in buttons:
        draw_circle_button(overlay, btn, cursor_x, cursor_y, pinch_detected)

    cv2.addWeighted(overlay, 1, frame, 0, 0, frame)

    if cursor_x != -1 and cursor_y != -1:
        cv2.circle(frame, (cursor_x, cursor_y), 10, (255, 255, 0), -1)

    cv2.imshow("Gesture Control", frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
