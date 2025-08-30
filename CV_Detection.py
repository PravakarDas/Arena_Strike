import cv2
import mediapipe as mp
import numpy as np
import math

# Initialize MediaPipe Hands and Face Detection
mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_detection
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=2,
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)

face_detection = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.6
)

# OpenCV webcam capture
cap = cv2.VideoCapture(0)

PINCH_THRESHOLD = 0.05  # distance between thumb and index tip
ZOOM_MIN_DIST = 0.05    # minimum hand spread (open palm)
ZOOM_MAX_DIST = 0.35    # maximum hand spread (very open)

zoom_level = 0.0  # Default zoom

def calc_distance(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

def get_max_hand_spread(landmarks):
    max_dist = 0
    for i in range(len(landmarks)):
        for j in range(i + 1, len(landmarks)):
            dist = calc_distance(landmarks[i], landmarks[j])
            max_dist = max(max_dist, dist)
    return max_dist

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = frame.shape

    # Process hands
    hand_results = hands.process(rgb_frame)
    # Process face
    face_results = face_detection.process(rgb_frame)

    # Default display text values
    right_hand_status = "Idle"
    current_zoom_text = "Zoom: 0.00x"
    zoom_level = 0.0

    # -------- HAND DETECTION --------
    if hand_results.multi_hand_landmarks and hand_results.multi_handedness:
        for hand_landmarks, handedness in zip(hand_results.multi_hand_landmarks, hand_results.multi_handedness):
            label = handedness.classification[0].label  # 'Left' or 'Right'
            score = handedness.classification[0].score

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2)
            )

            wrist = hand_landmarks.landmark[0]
            wrist_x, wrist_y = int(w * wrist.x), int(h * wrist.y)

            cv2.putText(
                frame,
                f'{label} Hand ({score:.2f})',
                (wrist_x - 60, wrist_y - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2
            )

            if label == 'Right':
                # ---- THUMBS UP/DOWN LOGIC ----
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]

                if thumb_tip.y < thumb_mcp.y:
                    right_hand_status = "Ready"   # Thumbs up
                elif thumb_tip.y > thumb_mcp.y:
                    right_hand_status = "Shooting"  # Thumbs down
                else:
                    right_hand_status = "Idle"

            elif label == 'Left':
                spread = get_max_hand_spread(hand_landmarks.landmark)
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]
                pinch_distance = calc_distance(thumb_tip, index_tip)

                if pinch_distance < PINCH_THRESHOLD:
                    zoom_level = 0.0
                else:
                    norm_spread = np.clip((spread - ZOOM_MIN_DIST) / (ZOOM_MAX_DIST - ZOOM_MIN_DIST), 0.0, 1.0)
                    zoom_level = round(norm_spread * 5.0, 2)

                current_zoom_text = f"Zoom: {zoom_level:.2f}x"

    # -------- FACE DETECTION --------
    if face_results.detections:
        for detection in face_results.detections:
            bboxC = detection.location_data.relative_bounding_box
            x, y, w_box, h_box = int(bboxC.xmin * w), int(bboxC.ymin * h), \
                                 int(bboxC.width * w), int(bboxC.height * h)

            cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), (255, 0, 255), 2)
            cv2.putText(
                frame,
                f"Face Detected ({detection.score[0]:.2f})",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 255),
                2
            )

    # -------- DISPLAY STATUS TEXT --------
    cv2.putText(
        frame,
        f"Right Action: {right_hand_status}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0) if right_hand_status == "Ready" else (0, 0, 255) if right_hand_status == "Shooting" else (255, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Left Action: {current_zoom_text}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    # Show the webcam feed
    cv2.imshow("Hand + Face Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
