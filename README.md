# Arena Strike

Arena Strike is a 3D cannon-defense game implemented in Python and OpenGL. Defend the arena by aiming a powerful cannon, managing special weapons, and surviving waves of enemies across four distinct levels. The project includes traditional keyboard/mouse controls and an optional computer-vision based control mode using OpenCV and MediaPipe.

## Project overview

- Real-time 3D rendering using PyOpenGL.
- Multiple enemy types and a boss with unique behaviors across four progressive levels.
- Weapons include bombs (gravity-affected), and a timed-area laser.
- Interactive HUD, audio feedback, and two camera views (third-person and first-person).
- Optional hand-gesture control using a webcam (OpenCV + MediaPipe).

## Requirements

- Python 3.8+
- PyOpenGL
- PyOpenGL_accelerate (optional, for performance)
- numpy
- playsound==1.2.2
- Optional (for camera gesture controls):
  - opencv-python
  - mediapipe

All Python dependencies are listed in `requirements.txt` and can be installed with pip.

## Installation

1. Install Python 3.8 or later.
2. From the project root, install dependencies:

```powershell
python -m venv env_name
venv\Scripts\activate
pip install -r requirements.txt
```

3. On Windows, ensure FreeGLUT is available (MSYS2 or a DLL in your PATH).

## Running the game

Start the game from the project root:

```powershell
python main_game.py
```

The game opens a window and prints initial instructions to the console. Audio files are under `assets/bgm/` and are played with the `playsound` module.

## Controls (keyboard & mouse)

- A / D — Move cannon left / right
- W / S — Tilt cannon barrel up / down
- Space — Fire bullet
- Left mouse click — Launch bomb
- L — Activate laser (limited duration, cooldown applies)
- C — Cheat / auto-aim toggle (limited uses / cooldown)
- V — Toggle camera view (third-person / first-person)
- Arrow keys — Adjust third-person camera
- + / - — Zoom in / out (third-person)
- Q or Esc — Quit

## OpenCV / Hand-gesture control (optional)

The repository includes a computer-vision control mode that maps webcam-based hand gestures to in-game actions. This is implemented using OpenCV and MediaPipe.

- Files of interest:
  - `hand_control_tracking.py` — A threaded hand tracker that detects gestures and exposes `HandTracker.get_actions()` which the game polls to drive inputs (fire, laser, zoom, camera/cannon deltas, etc.).
  - `CV_Detection.py` — A demonstration script showing hand/face landmarks, pinch detection, and gesture metrics useful for tuning thresholds.

- How it works:
  - The hand tracker captures webcam frames, detects hand landmarks via MediaPipe, and converts gesture states (open/closed hand, pinch, finger positions) into discrete and continuous actions.
  - `main_game.py` polls the tracker each frame and applies edge-triggered actions (single-fire, toggle laser) and continuous controls (aim offsets, zoom) from the tracker output.

- To enable gesture control:
  1. Install the optional packages: `pip install opencv-python mediapipe` (they are not strictly required for keyboard play).
  2. Ensure a webcam is connected and accessible by OpenCV.
  3. Run the game normally; the hand tracker will start if present and will appear as an input source. See `hand_control_tracking.py` for configurable thresholds and mappings.

- Tuning and debugging:
  - Use `CV_Detection.py` to visualize detected landmarks and debug gestures before enabling them in-game.
  - Thresholds and action mappings are defined in `hand_control_tracking.py` — adjust sensitivity, pinch thresholds, and mapping logic there.

## Project structure

- `main_game.py` — Main loop, game state, rendering and input integration
- `hand_control_tracking.py` — Optional MediaPipe/OpenCV hand tracker and action mapping
- `assets/` — Rendering modules, models and audio
  - `arena_model.py`, `cannon_model.py`, `bullets.py`, `bombs.py`, `lvl1_stickyman.py` … `lvl4_boss.py`
  - `bgm/` — audio files
- `requirements.txt` — Python dependencies

## Development notes

- If 3D models render as simple primitives, open the relevant module in `assets/` and ensure the named `draw_*` functions match the calls in `main_game.py`.
- When modifying gesture controls, prefer incremental changes and validate using `CV_Detection.py`.

## Owner & Contact

This project is maintained by Pravakar. For any questions, feature requests, licensing, or collaboration, please contact: pravakar459@gmail.com

## Troubleshooting

- Common issue: Missing FreeGLUT on Windows — install via MSYS2 or place `freeglut.dll` in a directory on your PATH.
- Camera not detected — ensure no other application is using the webcam and that OpenCV can open the device index (try `0`, `1`, etc.).
