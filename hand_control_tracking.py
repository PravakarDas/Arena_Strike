import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import math

# Hand and gesture tracker for game controls
# - Detects: right-hand fist, victory (index+middle), shaka (thumb+pinky)
# - Tracks motion direction (left/right/up/down) for each hand
# - Detects both-hands waving/shaking (bye) -> marks quit gesture
# - Filters hands to only those belonging to the nearest face (person closest to camera)

mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_detection
mp_draw = mp.solutions.drawing_utils

hands_detector = mp_hands.Hands(
    max_num_hands=2,
    model_complexity=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.5
)

face_detector = mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.6)

# Parameters (tweakable)
MOVE_HISTORY = 8  # frames to keep for motion estimation
MOVE_THRESHOLD = 0.015  # movement threshold to consider as motion (x/y)
DEPTH_THRESHOLD = 0.02  # movement threshold to consider as depth motion (z)
FACE_HAND_DIST_THRESH = 0.6  # max normalized distance from face center to hand center to consider same person

# History buffers
hand_history = {"Left": deque(maxlen=MOVE_HISTORY), "Right": deque(maxlen=MOVE_HISTORY)}

cap = cv2.VideoCapture(0)


def get_hand_center(landmarks):
    # Use average of MCP joints and wrist for more stable center
    idxs = [0, 5, 9, 13, 17]
    x = np.mean([landmarks[i].x for i in idxs])
    y = np.mean([landmarks[i].y for i in idxs])
    z = np.mean([landmarks[i].z for i in idxs])
    return x, y, z


def finger_extended(landmarks, finger_tip_idx, finger_pip_idx):
    # For most fingers: tip.y < pip.y -> extended (camera coordinates: y grows downward)
    return landmarks[finger_tip_idx].y < landmarks[finger_pip_idx].y


def thumb_extended(landmarks, handedness_label):
    tip_x = landmarks[4].x
    ip_x = landmarks[3].x
    if handedness_label == 'Right':
        return tip_x < ip_x
    else:
        return tip_x > ip_x


def detect_gesture(landmarks, label):
    # Returns a string describing the gesture
    idx_ext = finger_extended(landmarks, 8, 6)
    mid_ext = finger_extended(landmarks, 12, 10)
    ring_ext = finger_extended(landmarks, 16, 14)
    pinky_ext = finger_extended(landmarks, 20, 18)
    thb_ext = thumb_extended(landmarks, label)

    extended_count = sum([idx_ext, mid_ext, ring_ext, pinky_ext, thb_ext])

    if extended_count == 0:
        return 'Fist'
    if idx_ext and mid_ext and not (ring_ext or pinky_ext or thb_ext):
        return 'Victory'
    if thb_ext and pinky_ext and not (idx_ext or mid_ext or ring_ext):
        return 'Shaka'
    if idx_ext and mid_ext:
        tip_idx = np.array([landmarks[8].x, landmarks[8].y])
        tip_mid = np.array([landmarks[12].x, landmarks[12].y])
        if np.linalg.norm(tip_idx - tip_mid) < 0.05:
            return 'Two-Finger Pair'
        return 'Index+Middle'
    if extended_count >= 4:
        return 'Open Palm'
    return 'Partial'


def motion_from_history(history):
    # history: deque of (x,y,z) normalized
    if len(history) < 2:
        return 'Stationary', 0.0, 0.0, 0.0
    x0, y0, z0 = history[0]
    x1, y1, z1 = history[-1]
    dx = x1 - x0
    dy = y1 - y0
    dz = z1 - z0
    # Depth (z) in MediaPipe: more negative means closer to camera. We treat dz<0 as moving forward.
    if abs(dz) > max(abs(dx), abs(dy)) and abs(dz) > DEPTH_THRESHOLD:
        return ('Forward' if dz < 0 else 'Backward'), dx, dy, dz
    if abs(dx) > abs(dy) and abs(dx) > MOVE_THRESHOLD:
        return ('Right' if dx > 0 else 'Left'), dx, dy, dz
    elif abs(dy) > MOVE_THRESHOLD:
        return ('Down' if dy > 0 else 'Up'), dx, dy, dz
    else:
        return 'Stationary', dx, dy, dz


def detect_shake(history):
    # Detect oscillation in x (horizontal waving) in the history deque
    if len(history) < 4:
        return False
    xs = [p[0] for p in history]
    dxs = [xs[i+1] - xs[i] for i in range(len(xs)-1)]
    # count sign changes in dx
    signs = [1 if d > 0 else (-1 if d < 0 else 0) for d in dxs]
    changes = 0
    for i in range(len(signs)-1):
        if signs[i] != 0 and signs[i+1] != 0 and signs[i] != signs[i+1]:
            changes += 1
    max_dx = max(abs(d) for d in dxs)
    return (changes >= 2) and (max_dx > 0.02)


print('Starting hand control tracking. Press q to quit.')

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)  # mirror for natural interaction
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_results = face_detector.process(rgb)
    results = hands_detector.process(rgb)

    # Default HUD values
    left_status = 'No Hand'
    right_status = 'No Hand'
    left_motion = 'Stationary'
    right_motion = 'Stationary'
    quit_gesture = False

    centers = {}
    nearest_face = None

    # Find nearest face (largest bbox area)
    if face_results.detections:
        best_area = 0
        for det in face_results.detections:
            bbox = det.location_data.relative_bounding_box
            area = bbox.width * bbox.height
            if area > best_area:
                best_area = area
                nearest_face = bbox

    face_center = None
    if nearest_face is not None:
        fx = nearest_face.xmin + nearest_face.width / 2.0
        fy = nearest_face.ymin + nearest_face.height / 2.0
        face_center = (fx, fy)
        # draw face box
        x_px = int(nearest_face.xmin * w)
        y_px = int(nearest_face.ymin * h)
        bw = int(nearest_face.width * w)
        bh = int(nearest_face.height * h)
        cv2.rectangle(frame, (x_px, y_px), (x_px + bw, y_px + bh), (255, 0, 255), 2)
        cv2.putText(frame, 'Nearest Face', (x_px, y_px - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,255), 2)

    # Process hands but only consider hands that are near the nearest face
    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = handedness.classification[0].label  # 'Left' or 'Right'
            score = handedness.classification[0].score

            lm = hand_landmarks.landmark
            cx, cy, cz = get_hand_center(lm)

            # If there's a detected nearest face, filter out hands that are not near that face
            if face_center is not None:
                fx, fy = face_center
                dist = math.hypot(cx - fx, cy - fy)
                if dist > FACE_HAND_DIST_THRESH:
                    # ignore this hand (likely another person)
                    # draw faded landmarks
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                           mp_draw.DrawingSpec((100,100,100), 1, 1), mp_draw.DrawingSpec((150,150,150), 1, 1))
                    continue

            # draw active landmarks
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                   mp_draw.DrawingSpec((0,255,0), 2, 2), mp_draw.DrawingSpec((0,0,255), 2, 2))

            centers[label] = (cx, cy)
            # Update history (store z as well)
            hand_history[label].append((cx, cy, cz))

            # Gesture detection
            gesture = detect_gesture(lm, label)
            if label == 'Left':
                left_status = f'{gesture} ({score:.2f})'
            else:
                right_status = f'{gesture} ({score:.2f})'

            # Motion detection
            motion, dx, dy, dz = motion_from_history(hand_history[label])
            if label == 'Left':
                left_motion = f'{motion} dx={dx:.3f} dy={dy:.3f} dz={dz:.3f}'
            else:
                right_motion = f'{motion} dx={dx:.3f} dy={dy:.3f} dz={dz:.3f}'

            # Draw small center dot
            cx_px, cy_px = int(cx * w), int(cy * h)
            cv2.circle(frame, (cx_px, cy_px), 6, (255, 0, 255), -1)

    # Detect both-hands waving/shaking (bye) only if both hands from nearest face present
    if 'Left' in centers and 'Right' in centers:
        left_shake = detect_shake(hand_history['Left'])
        right_shake = detect_shake(hand_history['Right'])
        if left_shake and right_shake:
            quit_gesture = True

    # HUD
    cv2.putText(frame, f"Right: {right_status}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0,255,0) if 'Fist' in right_status or 'Shaka' in right_status else (0,0,255), 2)
    cv2.putText(frame, f"Right Motion: {right_motion}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,0), 2)
    cv2.putText(frame, f"Left: {left_status}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
    cv2.putText(frame, f"Left Motion: {left_motion}", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,0), 2)
    cv2.putText(frame, f"Quit Gesture: {'Yes' if quit_gesture else 'No'}", (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (0,255,0) if quit_gesture else (0,0,255), 2)

    cv2.imshow('Hand Control Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()