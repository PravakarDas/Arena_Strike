import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import math
import threading
import time

# Hand tracker runs in background and exposes a small action API consumed by the game.

mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_detection
mp_draw = mp.solutions.drawing_utils


class HandTracker:
    """Threaded hand tracker that exposes get_actions().

    Usage:
      tracker = HandTracker(device=0)
      tracker.start()
      # wait for tracker.ready
      actions = tracker.get_actions()  # called each frame
      tracker.stop()
    """

    def __init__(self, device=0):
        # Parameters
        self.MOVE_HISTORY = 8
        self.MOVE_THRESHOLD = 0.015
        self.DEPTH_THRESHOLD = 0.02
        self.FACE_HAND_DIST_THRESH = 0.6

        self.device = device
        self.cap = None

        self.hands_detector = mp_hands.Hands(
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )
        self.face_detector = mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.6)

        # history per hand
        self.hand_history = {"Left": deque(maxlen=self.MOVE_HISTORY), "Right": deque(maxlen=self.MOVE_HISTORY)}

        # thread control
        self._thread = None
        self._stop_event = threading.Event()
        self.ready = False

        # action state
        self._lock = threading.Lock()
        # edge actions will be cleared when consumed by get_actions()
        self._edge_actions = {"fire": False, "laser_toggle": False, "cheat_toggle": False, "quit": False, "view_toggle": False}
        # continuous controls
        self._continuous = {"zoom": 0.0, "cannon_z_delta": 0.0, "cannon_angle_delta": 0.0, "camera_angle_delta": 0.0, "camera_height_delta": 0.0}

        # debouncing / cooldowns
        self._last_time = {}
        self._cooldowns = {"fire": 0.35, "laser_toggle": 1.0, "cheat_toggle": 1.0, "quit": 1.0, "view_toggle": 1.0}

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        # wait briefly for camera initialization
        start = time.time()
        while not self.ready and (time.time() - start) < 5.0:
            time.sleep(0.05)

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass

    # --- helpers copied & adapted from original script ---
    def _get_hand_center(self, landmarks):
        idxs = [0, 5, 9, 13, 17]
        x = np.mean([landmarks[i].x for i in idxs])
        y = np.mean([landmarks[i].y for i in idxs])
        z = np.mean([landmarks[i].z for i in idxs])
        return x, y, z

    @staticmethod
    def _finger_extended(landmarks, finger_tip_idx, finger_pip_idx):
        return landmarks[finger_tip_idx].y < landmarks[finger_pip_idx].y

    @staticmethod
    def _thumb_extended(landmarks, handedness_label):
        tip_x = landmarks[4].x
        ip_x = landmarks[3].x
        if handedness_label == 'Right':
            return tip_x < ip_x
        else:
            return tip_x > ip_x

    def _detect_gesture(self, landmarks, label):
        idx_ext = self._finger_extended(landmarks, 8, 6)
        mid_ext = self._finger_extended(landmarks, 12, 10)
        ring_ext = self._finger_extended(landmarks, 16, 14)
        pinky_ext = self._finger_extended(landmarks, 20, 18)
        thb_ext = self._thumb_extended(landmarks, label)
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

    def _motion_from_history(self, history):
        if len(history) < 2:
            return 'Stationary', 0.0, 0.0, 0.0
        x0, y0, z0 = history[0]
        x1, y1, z1 = history[-1]
        dx = x1 - x0
        dy = y1 - y0
        dz = z1 - z0
        if abs(dz) > max(abs(dx), abs(dy)) and abs(dz) > self.DEPTH_THRESHOLD:
            return ('Forward' if dz < 0 else 'Backward'), dx, dy, dz
        if abs(dx) > abs(dy) and abs(dx) > self.MOVE_THRESHOLD:
            return ('Right' if dx > 0 else 'Left'), dx, dy, dz
        elif abs(dy) > self.MOVE_THRESHOLD:
            return ('Down' if dy > 0 else 'Up'), dx, dy, dz
        else:
            return 'Stationary', dx, dy, dz

    def _detect_shake(self, history):
        if len(history) < 4:
            return False
        xs = [p[0] for p in history]
        dxs = [xs[i+1] - xs[i] for i in range(len(xs)-1)]
        signs = [1 if d > 0 else (-1 if d < 0 else 0) for d in dxs]
        changes = 0
        for i in range(len(signs)-1):
            if signs[i] != 0 and signs[i+1] != 0 and signs[i] != signs[i+1]:
                changes += 1
        max_dx = max(abs(d) for d in dxs) if dxs else 0.0
        return (changes >= 2) and (max_dx > 0.02)

    # Public: retrieve actions and clear edge events
    def get_actions(self):
        with self._lock:
            actions = {
                # edges
                'fire': self._edge_actions['fire'],
                'laser_toggle': self._edge_actions['laser_toggle'],
                'cheat_toggle': self._edge_actions['cheat_toggle'],
                'quit': self._edge_actions['quit'],
                'view_toggle': self._edge_actions['view_toggle'],
                # continuous
                'zoom': self._continuous['zoom'],
                'cannon_z_delta': self._continuous['cannon_z_delta'],
                'cannon_angle_delta': self._continuous['cannon_angle_delta'],
                'camera_angle_delta': self._continuous['camera_angle_delta'],
                'camera_height_delta': self._continuous['camera_height_delta'],
            }
            # clear edge events
            for k in self._edge_actions:
                self._edge_actions[k] = False
            # continuous values are kept until next frame update (they are overwritten in _run)
        return actions

    def _cooldown_ok(self, name):
        now = time.time()
        last = self._last_time.get(name, 0)
        cd = self._cooldowns.get(name, 0.0)
        if now - last >= cd:
            self._last_time[name] = now
            return True
        return False

    def _run(self):
        try:
            self.cap = cv2.VideoCapture(self.device)
        except Exception:
            self.cap = None
        if not self.cap or not self.cap.isOpened():
            self.ready = False
            return
        self.ready = True

        while not self._stop_event.is_set():
            success, frame = self.cap.read()
            if not success:
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_results = self.face_detector.process(rgb)
            results = self.hands_detector.process(rgb)

            centers = {}
            nearest_face = None

            # find nearest face
            if getattr(face_results, 'detections', None):
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

            # reset continuous controls for this frame
            with self._lock:
                self._continuous = {k: 0.0 for k in self._continuous}

            if getattr(results, 'multi_hand_landmarks', None) and getattr(results, 'multi_handedness', None):
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    label = handedness.classification[0].label  # 'Left' or 'Right'
                    score = handedness.classification[0].score

                    lm = hand_landmarks.landmark
                    cx, cy, cz = self._get_hand_center(lm)

                    # filter by nearest face if available
                    if face_center is not None:
                        fx, fy = face_center
                        dist = math.hypot(cx - fx, cy - fy)
                        if dist > self.FACE_HAND_DIST_THRESH:
                            # ignore
                            continue

                    centers[label] = (cx, cy)
                    # update history
                    self.hand_history[label].append((cx, cy, cz))

                    gesture = self._detect_gesture(lm, label)
                    motion, dx, dy, dz = self._motion_from_history(self.hand_history[label])

                    # Map gestures to edge actions
                    with self._lock:
                        if label == 'Right':
                            # Fire on fist
                            if gesture == 'Fist' and self._cooldown_ok('fire'):
                                self._edge_actions['fire'] = True
                            # Laser on victory (two fingers)
                            if gesture in ('Victory', 'Two-Finger Pair') and self._cooldown_ok('laser_toggle'):
                                self._edge_actions['laser_toggle'] = True
                            # Cheat on shaka
                            if gesture == 'Shaka' and self._cooldown_ok('cheat_toggle'):
                                self._edge_actions['cheat_toggle'] = True
                            # View toggle on strong forward motion (large negative dz)
                            if dz < -0.08 and self._cooldown_ok('view_toggle'):
                                self._edge_actions['view_toggle'] = True

                            # Right hand used for cannon control (relative dx/dy -> angle/z)
                            # scale factors tuned experimentally
                            self._continuous['cannon_z_delta'] += dx * 40.0  # moves cannon z
                            self._continuous['cannon_angle_delta'] += -dy * 80.0  # tilt
                        else:  # Left hand controls camera movement / zoom
                            # Zoom using significant dz
                            if dz < -0.06:
                                # forward (closer) -> zoom in
                                self._continuous['zoom'] = -1.0
                            elif dz > 0.06:
                                self._continuous['zoom'] = 1.0
                            # camera rotation / height from left hand motion
                            self._continuous['camera_angle_delta'] += dx * 180.0
                            self._continuous['camera_height_delta'] += -dy * 30.0

            # detect both-hands shake for quit
            with self._lock:
                if 'Left' in centers and 'Right' in centers:
                    left_shake = self._detect_shake(self.hand_history['Left'])
                    right_shake = self._detect_shake(self.hand_history['Right'])
                    if left_shake and right_shake and self._cooldown_ok('quit'):
                        self._edge_actions['quit'] = True

            # small sleep so tracker doesn't hog CPU
            time.sleep(0.01)


if __name__ == '__main__':
    print('Starting hand control tracking. Press q in window to quit.')
    t = HandTracker()
    try:
        t.start()
        # show a small debug window while running
        while True:
            actions = t.get_actions()
            # simple console output for debugging
            print(actions)
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        t.stop()