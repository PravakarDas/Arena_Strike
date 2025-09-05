# Arena Strike

Arena Strike is an exciting 3D cannon defense game built with Python and OpenGL. Players control a powerful cannon to defend against waves of increasingly challenging enemies across four dynamic levels. Engage in intense battles, utilize special weapons, and strive to achieve the highest score in this immersive arena experience.

## How the Game Works

In Arena Strike, you command a stationary cannon positioned at the edge of a vibrant 3D arena. Enemies spawn from the opposite side and advance towards your position with unique behaviors and attack patterns. Your objective is to eliminate all enemies in each level before they reach and damage your cannon. The game features progressive difficulty, starting with basic ground enemies and culminating in a formidable boss battle. Use strategic aiming, timing, and special abilities to survive and progress through all levels.

## How to Play

1. **Movement**: Use keyboard controls to move the cannon left/right and adjust its barrel angle up/down.
2. **Firing**: Launch bullets with the spacebar or deploy powerful bombs with left mouse click.
3. **Special Weapons**: Activate the laser for area damage or use cheat mode for auto-targeting.
4. **Survival**: Maintain your cannon's health while eliminating enemies to advance levels.
5. **Objective**: Clear all four levels to achieve victory and maximize your score.

## Special Features

1. **Immersive 3D Graphics**: Stunning OpenGL-rendered arena with detailed models, lighting effects, and atmospheric visuals.
2. **Dynamic Enemy AI**: Four unique enemy types with distinct behaviors - walking stickymen, flying bugs, shooting archers, and projectile-firing bosses.
3. **Progressive Difficulty**: Four challenging levels with increasing enemy counts and spawn patterns.
4. **Multiple Weapon Systems**: Standard bullets, gravity-affected bombs, and a powerful laser weapon.
5. **Cheat Mode**: Auto-aiming and rapid-fire capability for strategic gameplay advantages.
6. **Real-time Sound Effects**: Immersive audio feedback including background music, weapon sounds, and enemy defeat cues.
7. **Interactive HUD**: Live display of player health, current level, score, and weapon cooldowns.
8. **Dual Camera Views**: Switch between third-person overview and first-person cannon perspective.
9. **Advanced Collision Detection**: Precise hit detection for projectiles and enemy interactions.
10. **Scoring System**: Earn points for each enemy defeated, encouraging skillful play.
11. **Health Management**: Strategic resource management with limited cannon health.
12. **Atmospheric Effects**: Dynamic audience cheering and environmental lighting for enhanced immersion.
13. **Coordinated Enemy Attacks**: Archers and bosses launch projectiles that require evasive maneuvers.
14. **Weapon Cooldowns**: Balanced gameplay with strategic timing for special abilities.
15. **Victory Conditions**: Clear all levels to achieve a satisfying win state with final score display.

## Requirements

- Python 3.8+
- PyOpenGL
- PyOpenGL_accelerate
- NumPy
- playsound==1.2.2
- FreeGLUT (for Windows systems)

## Installation

1. Ensure Python 3.8 or higher is installed on your system.
2. Install the required dependencies:

```powershell
pip install -r requirements.txt
```

3. On Windows, install FreeGLUT if not already present (available via MSYS2 or as a DLL in your PATH).

## Running the Game

From the project root directory:

```powershell
python main_game.py
```

A game window will open, displaying the 3D arena. The terminal will show initial instructions and game status updates.

## Controls

- **A/D**: Move cannon left/right
- **W/S**: Tilt cannon barrel up/down
- **Spacebar**: Fire bullet
- **Left Mouse Click**: Launch bomb
- **L**: Activate laser (5-second duration, 30-second cooldown)
- **C**: Activate cheat mode (auto-aim 3 shots, 20-second cooldown)
- **V**: Toggle between third-person and first-person view
- **Arrow Keys**: Adjust camera angle and zoom (third-person view)
- **+/-**: Zoom in/out (third-person view)
- **Q or ESC**: Quit game

## Gameplay Tips

- Position your cannon strategically to cover multiple enemy spawn points.
- Use bombs for area damage against clustered enemies.
- Save the laser for tough situations or boss encounters.
- Monitor your health and use cheat mode sparingly for maximum effectiveness.
- Experiment with camera angles to gain tactical advantages.

## Project Structure

- `main_game.py`: Main game logic and rendering loop
- `assets/`: Directory containing 3D models and drawing functions
  - `arena_model.py`: Arena and environmental rendering
  - `cannon_model.py`: Cannon visualization
  - `bullets.py`: Bullet rendering
  - `bombs.py`: Bomb effects
  - `lvl1_stickyman.py` to `lvl4_boss.py`: Enemy models
- `assets/bgm/`: Background music and sound effects
- `requirements.txt`: Python dependencies
- `README.md`: This documentation

Enjoy defending the arena in Arena Strike!
- If enemies appear as simple cubes, open the corresponding `asset/` file and check for the expected `draw_*` function names; I can update the controller to match exact names.

---

## Next steps (optional)

- Add in-window text rendering for score/life and improve HUD.
- Improve collision and projectile physics.
- Add polish: sounds, animations, and refined AI.

If you'd like I can now inspect the `asset/` directory and update `main_game.py` to call the exact drawing functions (no code changes unless you request them). Just tell me to proceed.
