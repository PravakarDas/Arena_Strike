import sys
import math
import random
import threading
import time

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from assets.arena_model import *
from assets.cannon_model import *
from assets.bombs import *
from assets.bullets import *
from assets.lvl1_stickyman import *
from assets.lvl2_bug import *
from assets.lvl3_archer import *
from assets.lvl4_boss import *

try:
    from playsound import playsound
except Exception:
    playsound = None  # graceful fallback if not installed

# --- Optional Hand Tracker (auto-fallback to dummy if cv2/mediapipe missing) ---
class _DummyTracker:
    ready = False
    def start(self): pass
    def stop(self): pass
    def get_actions(self): return {}

def _make_hand_tracker():
    try:
        from hand_control_tracking import HandTracker  # may import cv2/mediapipe
        t = HandTracker(device=0)
        t.start()
        waited = 0.0
        while not getattr(t, "ready", False) and waited < 5.0:
            time.sleep(0.05); waited += 0.05
        if not getattr(t, "ready", False):
            print("Warning: Hand tracker not ready; using keyboard only.")
        else:
            print("Hand tracker ready: gesture controls active")
        return t
    except Exception as e:
        print(f"[gesture disabled] {e.__class__.__name__}: {e}")
        print("Falling back to keyboard-only controls.")
        return _DummyTracker()


def main():
    # -------------------------
    # Initial game state
    # -------------------------
    state = {
        'audience_data': generate_audience(),
        'cheer_time': 0.0,

        # Camera / view
        'camera_distance': 35.0,
        'camera_angle': 0.0,
        'camera_height': 24.0,
        'camera_move_speed': 3.0,
        'view_mode': 'third',  # 'third' or 'first'

        # Aiming
        'show_aiming_line': True,
        'aiming_point': [0.0, 0.0, 0.0],

        # Cannon constraints
        'CANNON_MIN_Z': -12.0,
        'CANNON_MAX_Z':  12.0,
        'CANNON_MIN_ANGLE': 0.0,
        'CANNON_MAX_ANGLE': 90.0,

        # Cannon pose
        'cannon_z': 0.0,
        'cannon_angle': 45.0,

        # Projectiles
        'gravity': -0.02,
        'bullets': [],
        'bullet_speed': 1.2,

        # Player
        'PLAYER_LIFE': 20,
        'player_life': 20,

        # Enemies / levels
        'enemies': [],
        'level': 1,
        'level_spawn_time': None,
        'level_second_spawned': False,
        'level_complete': False,
        'spawned_count': 0,
        'max_enemies': 5,
        'spawn_delays': [],

        # Score & abilities
        'score': 0,
        'laser_active': False,
        'laser_start_time': 0.0,
        'laser_cooldown_end': 0.0,
        'laser_duration': 5.0,
        'laser_cooldown': 30.0,

        'cheat_active': False,
        'cheat_start_time': 0.0,
        'cheat_cooldown_end': 0.0,
        'cheat_shots': 0,
        'cheat_max_shots': 3,
        'cheat_cooldown': 20.0,
        'cheat_last_shot_time': 0.0,
        'cheat_shot_delay': 1.0,

        # End/summary + stats
        'game_state': 'playing',    # 'playing' or 'summary'
        'enemies_killed': 0,
        'shots_fired': 0,
        'start_time': 0.0,
        'end_time': 0.0,
        'end_title': None,

        # Gesture tilt toggle (fixes auto-tilt drift)
        'gesture_aim_enabled': False,  # default OFF

        # Zombie allies
        'allies': [],  # list of {'pos':[x,y,z], 'type':str, 'speed':float, 'active':True}
    }

    # Base movement speeds per enemy type (zombies move at half of this)
    BASE_SPEED = {'stickyman': 0.08, 'bug': 0.13, 'archer': 0.06, 'boss': 0.18}

    # -------------------------
    # Background music (optional)
    # -------------------------
    def play_bgm_loop():
        if not playsound:
            return
        while True:
            try:
                playsound('assets/bgm/bgm.mp3')
            except Exception:
                time.sleep(2.0)

    threading.Thread(target=play_bgm_loop, daemon=True).start()

    # -------------------------
    # Hand tracker (auto-fallback)
    # -------------------------
    tracker = _make_hand_tracker()

    # -------------------------
    # Helpers
    # -------------------------
    from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_HELVETICA_12

    def draw_text_2d(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
        glWindowPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))

    def draw_exit_overlay():
        width = glutGet(GLUT_WINDOW_WIDTH)
        height = glutGet(GLUT_WINDOW_HEIGHT)

        glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
        gluOrtho2D(0, width, 0, height)
        glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()

        # Dim layer
        glColor4f(0.0, 0.0, 0.0, 0.60)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(width, 0); glVertex2f(width, height); glVertex2f(0, height)
        glEnd()

        # Panel
        panel_w = min(640, int(width * 0.86)); panel_h = 300
        px = (width - panel_w) // 2; py = (height - panel_h) // 2

        glColor4f(0.08, 0.10, 0.12, 0.85)
        glBegin(GL_QUADS)
        glVertex2f(px, py); glVertex2f(px + panel_w, py)
        glVertex2f(px + panel_w, py + panel_h); glVertex2f(px, py + panel_h)
        glEnd()

        # Border
        glColor4f(1, 1, 1, 0.20); glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(px, py); glVertex2f(px + panel_w, py)
        glVertex2f(px + panel_w, py + panel_h); glVertex2f(px, py + panel_h)
        glEnd()

        # Stats
        title = state.get('end_title') or "Session Summary"
        time_ref = state['end_time'] or (glutGet(GLUT_ELAPSED_TIME) / 1000.0)
        elapsed = max(0.0, time_ref - state['start_time'])
        mins = int(elapsed // 60); secs = int(elapsed % 60)

        draw_text_2d(px + 26, py + panel_h - 42, title, GLUT_BITMAP_HELVETICA_18)
        draw_text_2d(px + 26, py + panel_h - 82, f"Score: {state['score']}")
        draw_text_2d(px + 26, py + panel_h - 112, f"Enemies killed: {state['enemies_killed']}")
        draw_text_2d(px + 26, py + panel_h - 142, f"Level reached: {state['level']}")
        draw_text_2d(px + 26, py + panel_h - 172, f"Time played: {mins}m {secs}s")
        draw_text_2d(px + 26, py + 56, "R = Restart,  Q = Quit,  ESC = Resume", GLUT_BITMAP_HELVETICA_12)

        # Restore
        glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_BLEND); glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)

    def soft_play(sound_relpath):
        if not playsound: return
        threading.Thread(target=lambda: _safe_play(sound_relpath), daemon=True).start()

    def _safe_play(path):
        try: playsound(path)
        except Exception: pass

    # ---- ZOMBIE: spawn an ally from a killed enemy
    def spawn_ally_from_enemy(enemy, reason=""):
        # Guard against double-spawn
        if enemy.get('zombified'): 
            return
        etype = enemy.get('type', 'stickyman')
        base = BASE_SPEED.get(etype, 0.08)
        ally = {
            'pos': [enemy['pos'][0], max(-1.0, enemy['pos'][1]), enemy['pos'][2]],
            'type': etype,
            'speed': max(0.02, base * 0.5),   # 2x slower, never zero
            'active': True,
        }
        state['allies'].append(ally)
        enemy['zombified'] = True
        print(f"[ALLY] Spawned {etype} at {ally['pos']} ({reason})")
        # subtle audio cue (reusing death)
        soft_play('assets/bgm/enemy die_bgm.mp3')

    def reset_game():
        """Restart a fresh run but keep current view mode and gesture toggle."""
        view_mode_keep = state['view_mode']
        gesture_keep = state['gesture_aim_enabled']
        state.clear()
        state.update({
            'audience_data': generate_audience(),
            'cheer_time': 0.0,
            'camera_distance': 35.0,
            'camera_angle': 0.0,
            'camera_height': 24.0,
            'camera_move_speed': 3.0,
            'show_aiming_line': True,
            'aiming_point': [0.0, 0.0, 0.0],
            'CANNON_MIN_Z': -12.0, 'CANNON_MAX_Z': 12.0,
            'CANNON_MIN_ANGLE': 0.0, 'CANNON_MAX_ANGLE': 90.0,
            'cannon_z': 0.0, 'cannon_angle': 45.0,
            'gravity': -0.02, 'bullets': [], 'bullet_speed': 1.2,
            'PLAYER_LIFE': 20, 'player_life': 20,
            'enemies': [], 'level': 1, 'level_spawn_time': None,
            'level_second_spawned': False, 'level_complete': False,
            'score': 0,
            'laser_active': False, 'laser_start_time': 0.0, 'laser_cooldown_end': 0.0,
            'laser_duration': 5.0, 'laser_cooldown': 30.0,
            'cheat_active': False, 'cheat_start_time': 0.0, 'cheat_cooldown_end': 0.0,
            'cheat_shots': 0, 'cheat_max_shots': 3, 'cheat_cooldown': 20.0,
            'cheat_last_shot_time': 0.0, 'cheat_shot_delay': 1.0,
            'spawned_count': 0, 'max_enemies': 5, 'spawn_delays': [],
            'view_mode': view_mode_keep,

            'game_state': 'playing', 'enemies_killed': 0, 'shots_fired': 0,
            'start_time': glutGet(GLUT_ELAPSED_TIME) / 1000.0, 'end_time': 0.0, 'end_title': None,

            'gesture_aim_enabled': gesture_keep,
            'allies': [],
        })

    # -------------------------
    # Display
    # -------------------------
    def display():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Camera
        if state['view_mode'] == 'third':
            cam_x = state['camera_distance'] * math.sin(math.radians(state['camera_angle']))
            cam_z = state['camera_distance'] * math.cos(math.radians(state['camera_angle']))
            gluLookAt(cam_x, state['camera_height'], cam_z, 0, 6, 0, 0, 1, 0)
        else:
            cannon_x = -20.0; cannon_y = -1.3; cannon_z_pos = state['cannon_z']
            angle_rad = math.radians(state['cannon_angle'])
            look_x = cannon_x + 10 * math.cos(angle_rad)
            look_y = cannon_y + 10 * math.sin(angle_rad)
            look_z = cannon_z_pos
            cam_x = cannon_x - 2.0; cam_y = cannon_y + 2.0; cam_z = cannon_z_pos
            gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 1, 0)

        # Arena + cannon
        draw_arena_floor()
        draw_gallery_structure()
        draw_audience(state['audience_data'], state['cheer_time'])
        draw_arena_lights()
        draw_roof_structure()
        draw_atmosphere_effects(state['cheer_time'])

        draw_complete_cannon(state['cannon_z'], state['cannon_angle'])
        calculate_aiming_point(state['cannon_z'], state['cannon_angle'], state['aiming_point'])
        draw_aiming_system(state['show_aiming_line'], state['cannon_z'], state['cannon_angle'], state['aiming_point'])

        # Laser beam (if active)
        if state['laser_active']:
            angle_rad = math.radians(state['cannon_angle'])
            tip_x = -20.0 + 2.5 * math.cos(angle_rad)
            tip_y = -1.3   + 2.5 * math.sin(angle_rad)
            tip_z = state['cannon_z']
            end_x = tip_x + 50.0 * math.cos(angle_rad)
            end_y = tip_y + 50.0 * math.sin(angle_rad)
            end_z = tip_z
            glDisable(GL_LIGHTING); glColor3f(1.0, 0.0, 0.0); glLineWidth(5.0)
            glBegin(GL_LINES)
            glVertex3f(tip_x, tip_y, tip_z); glVertex3f(end_x, end_y, end_z)
            glEnd()
            glLineWidth(1.0); glEnable(GL_LIGHTING)

        # Bullets
        draw_bullets(state['bullets'])

        # Enemies
        for enemy in state['enemies']:
            if not enemy.get('alive', True):
                continue
            glPushMatrix()
            glTranslatef(enemy['pos'][0], enemy['pos'][1], enemy['pos'][2])
            t_anim = glutGet(GLUT_ELAPSED_TIME) / 1000.0
            if enemy['type'] == 'stickyman':
                draw_stickman(t_anim)
            elif enemy['type'] == 'bug':
                draw_bug(t_anim)
            elif enemy['type'] == 'archer':
                draw_archer(t_anim)
                for arrow in enemy.get('arrows', []):
                    if arrow.get('alive', False):
                        glPushMatrix()
                        glTranslatef(arrow['x'] - enemy['pos'][0], 1.5, arrow['z'] - enemy['pos'][2])
                        glColor3f(0.7, 0.2, 0.2)
                        glutSolidSphere(0.12, 12, 12)
                        glPopMatrix()
            elif enemy['type'] == 'boss':
                draw_boss_demon_queen(t_anim)
                for proj in enemy.get('projectiles', []):
                    if proj.get('alive', False):
                        glPushMatrix()
                        glTranslatef(proj['x'] - enemy['pos'][0], 1.5, proj['z'] - enemy['pos'][2])
                        glColor3f(1, 0, 1); glutSolidSphere(0.15, 12, 12); glPopMatrix()
            glPopMatrix()

        # ALLIES (zombies)
        for ally in state['allies']:
            if not ally.get('active', True):
                continue
            glPushMatrix()
            glTranslatef(ally['pos'][0], ally['pos'][1], ally['pos'][2])
            t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
            # same model as type
            if ally['type'] == 'stickyman':
                draw_stickman(t)
            elif ally['type'] == 'bug':
                draw_bug(t)
            elif ally['type'] == 'archer':
                draw_archer(t)
            elif ally['type'] == 'boss':
                draw_boss_demon_queen(t)
            # green aura ring + overhead marker to make it obvious
            glDisable(GL_LIGHTING)
            glColor3f(0.2, 1.0, 0.2)
            glutWireSphere(0.9, 12, 12)
            glBegin(GL_LINES)
            glVertex3f(0, 1.6, 0); glVertex3f(0, 2.2, 0)
            glEnd()
            glEnable(GL_LIGHTING)
            glPopMatrix()

        # HUD
        glDisable(GL_LIGHTING)
        glWindowPos2f(10, 40)
        level_name = {1: 'Stickyman', 2: 'Bug', 3: 'Archer', 4: 'Boss'}
        now = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        laser_status = "Laser: Active" if state['laser_active'] else ("Laser: "+(f"{int(state['laser_cooldown_end']-now)}s" if now < state['laser_cooldown_end'] else "Ready"))
        if state['cheat_active']:
            cheat_status = f"Cheat: {state['cheat_shots']}/{state['cheat_max_shots']}"
        elif now < state['cheat_cooldown_end']:
            cheat_status = f"Cheat: {int(state['cheat_cooldown_end'] - now)}s"
        else:
            cheat_status = "Cheat: Ready"
        hud = f"Life: {state['player_life']}  |  Level {state['level']}: {level_name.get(state['level'], '')}  |  Score: {state['score']}  |  Allies: {len(state['allies'])}  |  {laser_status}  |  {cheat_status}  |  View: {state['view_mode'].capitalize()}"
        for c in hud: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
        glEnable(GL_LIGHTING)

        # SUMMARY OVERLAY
        if state['game_state'] != 'playing':
            draw_exit_overlay()

        glutSwapBuffers()

    # -------------------------
    # Idle (update loop)
    # -------------------------
    def idle():
        # Pause the world when summary is open
        if state['game_state'] != 'playing':
            glutPostRedisplay(); return

        state['cheer_time'] += 0.05

        # Gestures (if tracker ready)
        if getattr(tracker, "ready", False):
            actions = tracker.get_actions() or {}

            if actions.get('fire'):
                create_bullet(state['bullets'], state['cannon_z'], state['cannon_angle'], state['bullet_speed'])
                state['shots_fired'] += 1
                soft_play('assets/bgm/bomb_bgm.mp3')

            if actions.get('laser_toggle'):
                now = glutGet(GLUT_ELAPSED_TIME) / 1000.0
                if not state['laser_active'] and now >= state['laser_cooldown_end']:
                    state['laser_active'] = True
                    state['laser_start_time'] = now
                    state['laser_cooldown_end'] = now + state['laser_duration'] + state['laser_cooldown']
                    def laser_loop():
                        while state['laser_active']: soft_play('assets/bgm/laser_bgm.mp3')
                    threading.Thread(target=laser_loop, daemon=True).start()

            if actions.get('cheat_toggle'):
                now = glutGet(GLUT_ELAPSED_TIME) / 1000.0
                if not state['cheat_active'] and now >= state['cheat_cooldown_end']:
                    state['cheat_active'] = True
                    state['cheat_start_time'] = now
                    state['cheat_cooldown_end'] = now + state['cheat_cooldown']
                    state['cheat_shots'] = 0
                    state['cheat_last_shot_time'] = now - state['cheat_shot_delay']

            if actions.get('quit'):
                try: tracker.stop()
                except Exception: pass
                sys.exit(0)

            if actions.get('view_toggle'):
                state['view_mode'] = 'first' if state['view_mode'] == 'third' else 'third'

            # Continuous gesture controls with strong deadzones
            zoom_val = actions.get('zoom', 0.0)
            if zoom_val < 0:   state['camera_distance'] = max(20.0, state['camera_distance'] - 2.0)
            elif zoom_val > 0: state['camera_distance'] = min(150.0, state['camera_distance'] + 2.0)

            cz_delta = actions.get('cannon_z_delta', 0.0)
            if abs(cz_delta) > 0.05:
                nz = state['cannon_z'] + cz_delta * 0.01
                state['cannon_z'] = max(state['CANNON_MIN_Z'], min(state['CANNON_MAX_Z'], nz))

            ca_delta = actions.get('cannon_angle_delta', 0.0)
            if state['gesture_aim_enabled'] and abs(ca_delta) > 0.05:
                na = state['cannon_angle'] + ca_delta * 0.005
                state['cannon_angle'] = max(state['CANNON_MIN_ANGLE'], min(state['CANNON_MAX_ANGLE'], na))

            cam_ang_delta = actions.get('camera_angle_delta', 0.0)
            if abs(cam_ang_delta) > 0.05: state['camera_angle'] += cam_ang_delta * 0.0005
            cam_h_delta = actions.get('camera_height_delta', 0.0)
            if abs(cam_h_delta) > 0.05:   state['camera_height'] = max(5.0, state['camera_height'] + cam_h_delta * 0.001)

        # Physics
        update_bullets(state['bullets'])

        # -------------------------
        # Level logic
        # -------------------------
        now = glutGet(GLUT_ELAPSED_TIME) / 1000.0

        # Level 1: Stickyman
        if state['level'] == 1:
            if not state['level_spawn_time']:
                state['enemies'] = []
                state['spawn_delays'] = [0, 2] + [random.uniform(2, 5) for _ in range(3)]
                state['spawned_count'] = 0
                state['level_spawn_time'] = now
                state['level_complete'] = False

            while state['spawned_count'] < state['max_enemies'] and now - state['level_spawn_time'] >= state['spawn_delays'][state['spawned_count']]:
                z_pos = random.uniform(-10, 10)
                state['enemies'].append({'pos': [20.0, -1.0, z_pos], 'alive': True, 'type': 'stickyman', 'collided': False})
                state['spawned_count'] += 1

            for enemy in state['enemies']:
                if not enemy['alive']: continue
                dx = -20.0 - enemy['pos'][0]; dz = state['cannon_z'] - enemy['pos'][2]
                dist = (dx*dx + dz*dz) ** 0.5
                if dist > 1.0:
                    enemy['pos'][0] += 0.08 * dx / dist
                    enemy['pos'][2] += 0.08 * dz / dist
                    enemy['collided'] = False
                else:
                    if not enemy.get('collided', False):
                        state['player_life'] -= 2; enemy['collided'] = True

            # Transition 1 -> 2
            if all((not e['alive']) or e.get('collided', False) for e in state['enemies']) and state['spawned_count'] == state['max_enemies']:
                if not state['level_complete']:
                    state['level_complete'] = True; state['level'] += 1
                    state['level_complete'] = False; state['level_spawn_time'] = None
                    state['spawned_count'] = 0; state['enemies'] = []

        # Level 2: Bug
        elif state['level'] == 2:
            if not state['level_spawn_time']:
                state['enemies'] = []
                state['spawn_delays'] = [0, 2] + [random.uniform(2, 5) for _ in range(3)]
                state['spawned_count'] = 0
                state['level_spawn_time'] = now
                state['level_complete'] = False

            while state['spawned_count'] < state['max_enemies'] and now - state['level_spawn_time'] >= state['spawn_delays'][state['spawned_count']]:
                z_pos = random.uniform(-10, 10)
                state['enemies'].append({'pos': [20.0, 8.0, z_pos], 'alive': True, 'type': 'bug', 'collided': False})
                state['spawned_count'] += 1

            for enemy in state['enemies']:
                if not enemy['alive']: continue
                target_x, target_y, target_z = -20.0, -1.0, state['cannon_z']
                dx = target_x - enemy['pos'][0]; dy = target_y - enemy['pos'][1]; dz = target_z - enemy['pos'][2]
                dist = (dx*dx + dy*dy + dz*dz) ** 0.5
                if dist > 1.5:
                    enemy['pos'][0] += 0.13 * dx / dist
                    enemy['pos'][1] += 0.13 * dy / dist
                    enemy['pos'][2] += 0.13 * dz / dist
                    enemy['collided'] = False
                else:
                    if not enemy.get('collided', False):
                        state['player_life'] -= 2; enemy['collided'] = True

            # Transition 2 -> 3
            if all((not e['alive']) or e.get('collided', False) for e in state['enemies']) and state['spawned_count'] == state['max_enemies']:
                if not state['level_complete']:
                    state['level_complete'] = True; state['level'] += 1
                    state['level_complete'] = False; state['level_spawn_time'] = None
                    state['spawned_count'] = 0; state['enemies'] = []

        # Level 3: Archer
        elif state['level'] == 3:
            if not state['level_spawn_time']:
                state['enemies'] = []
                state['spawn_delays'] = [0, 2] + [random.uniform(2, 5) for _ in range(3)]
                state['spawned_count'] = 0
                state['level_spawn_time'] = now
                state['level_complete'] = False

            while state['spawned_count'] < state['max_enemies'] and now - state['level_spawn_time'] >= state['spawn_delays'][state['spawned_count']]:
                z_pos = random.uniform(-10, 10)
                state['enemies'].append({
                    'pos': [20.0, -1.0, z_pos], 'alive': True, 'type': 'archer',
                    'walk_timer': 0.0, 'shoot_timer': 0.0, 'walking': True,
                    'arrows': [], 'shots_fired': 0, 'collided': False
                })
                state['spawned_count'] += 1

            for enemy in state['enemies']:
                if not enemy['alive']: continue
                enemy['walk_timer'] += 0.016
                if enemy['walking']:
                    dx = -20.0 - enemy['pos'][0]; dz = state['cannon_z'] - enemy['pos'][2]
                    dist = (dx*dx + dz*dz) ** 0.5
                    if dist > 1.0:
                        enemy['pos'][0] += 0.06 * dx / dist
                        enemy['pos'][2] += 0.06 * dz / dist
                        enemy['collided'] = False
                        if enemy['walk_timer'] > 5.0 + (enemy['pos'][0] % 2.0):
                            enemy['walking'] = False; enemy['walk_timer'] = 0.0
                    else:
                        if not enemy.get('collided', False):
                            state['player_life'] -= 2; enemy['collided'] = True
                else:
                    enemy['shoot_timer'] += 0.016
                    if enemy['shoot_timer'] > 2.0:
                        dx = -20.0 - enemy['pos'][0]; dz = state['cannon_z'] - enemy['pos'][2]
                        dist = (dx*dx + dz*dz) ** 0.5
                        arrow = {'x': enemy['pos'][0], 'y': 1.5, 'z': enemy['pos'][2],
                                 'dx': dx / dist, 'dz': dz / dist, 'alive': True}
                        enemy['arrows'].append(arrow)
                        enemy['shoot_timer'] = 0.0; enemy['shots_fired'] += 1
                        if enemy['shots_fired'] >= 2:
                            enemy['walking'] = True; enemy['shots_fired'] = 0

            for enemy in state['enemies']:
                if enemy['type'] == 'archer':
                    for arrow in enemy['arrows']:
                        if not arrow.get('alive', False): continue
                        arrow['x'] += arrow['dx'] * 0.5
                        arrow['z'] += arrow['dz'] * 0.5
                        if abs(arrow['x'] - -20.0) < 1.0 and abs(arrow['z'] - state['cannon_z']) < 1.0:
                            state['player_life'] -= 1; arrow['alive'] = False

            # Transition 3 -> 4
            if all((not e['alive']) or e.get('collided', False) for e in state['enemies']) and state['spawned_count'] == state['max_enemies']:
                if not state['level_complete']:
                    state['level_complete'] = True; state['level'] += 1
                    state['level_complete'] = False; state['level_spawn_time'] = None
                    state['spawned_count'] = 0; state['enemies'] = []

        # Level 4: Boss
        elif state['level'] == 4:
            if not state['level_spawn_time']:
                state['enemies'] = [{'pos': [20.0, -1.0, 0.0], 'alive': True, 'type': 'boss', 'projectiles': [], 'collided': False}]
                state['level_spawn_time'] = now; state['level_complete'] = False

            for enemy in state['enemies']:
                if not enemy['alive']: continue
                dx = -20.0 - enemy['pos'][0]; dz = state['cannon_z'] - enemy['pos'][2]
                dist = (dx*dx + dz*dz) ** 0.5
                if dist > 1.0:
                    enemy['pos'][0] += 0.18 * dx / dist
                    enemy['pos'][2] += 0.18 * dz / dist
                    enemy['collided'] = False
                else:
                    if not enemy.get('collided', False):
                        state['player_life'] -= 5; enemy['collided'] = True

                if int(now * 2) % 2 == 0 and len(enemy['projectiles']) < 3:
                    for i in range(3):
                        angle = math.radians(-20 + i * 20)
                        dx_proj = math.sin(angle); dz_proj = math.cos(angle)
                        proj = {'x': enemy['pos'][0], 'y': 1.5, 'z': enemy['pos'][2],
                                'dx': dx_proj, 'dz': dz_proj, 'alive': True}
                        enemy['projectiles'].append(proj)

            for enemy in state['enemies']:
                if enemy['type'] == 'boss':
                    for proj in enemy['projectiles']:
                        if not proj.get('alive', False): continue
                        proj['x'] += proj['dx'] * 0.7; proj['z'] += proj['dz'] * 0.7
                        if abs(proj['x'] - -20.0) < 1.0 and abs(proj['z'] - state['cannon_z']) < 1.0:
                            state['player_life'] -= 2; proj['alive'] = False

            # Boss defeated => mark Level 4 complete (win)
            if all((not e['alive']) or e.get('collided', False) for e in state['enemies']):
                if not state['level_complete']:
                    state['level_complete'] = True

        # -------------------------
        # LASER: timeout & hits
        # -------------------------
        if state['laser_active'] and now - state['laser_start_time'] > state['laser_duration']:
            state['laser_active'] = False

        if state['laser_active']:
            angle_rad = math.radians(state['cannon_angle'])
            tip_x = -20.0 + 2.5 * math.cos(angle_rad); tip_y = -1.3 + 2.5 * math.sin(angle_rad)
            tip_z = state['cannon_z']
            dir_x = math.cos(angle_rad); dir_y = math.sin(angle_rad); dir_z = 0.0
            for enemy in state['enemies']:
                if not enemy.get('alive', True): continue
                ex, ey, ez = enemy['pos']
                vx = ex - tip_x; vy = ey - tip_y; vz = ez - tip_z
                proj = vx * dir_x + vy * dir_y + vz * dir_z
                if proj > 0:
                    perp_x = vx - proj * dir_x; perp_y = vy - proj * dir_y; perp_z = vz - proj * dir_z
                    dist_perp = math.sqrt(perp_x**2 + perp_y**2 + perp_z**2)
                    if dist_perp < 1.0 and proj < 30.0:
                        enemy['alive'] = False
                        state['score'] += 100; state['enemies_killed'] += 1
                        spawn_ally_from_enemy(enemy, "laser")

        # -------------------------
        # Bullet-enemy collision
        # -------------------------
        for enemy in state['enemies']:
            if not enemy.get('alive', True): continue
            for bullet in state['bullets']:
                if not bullet.get('alive', False): continue
                dx = bullet['x'] - enemy['pos'][0]
                dy = bullet['y'] - enemy['pos'][1]
                dz = bullet['z'] - enemy['pos'][2]
                if dx*dx + dy*dy + dz*dz < 1.2:
                    enemy['alive'] = False; bullet['alive'] = False
                    state['score'] += 100; state['enemies_killed'] += 1
                    spawn_ally_from_enemy(enemy, "bullet")

        # -------------------------
        # ALLY (zombie) AI: chase nearest living enemy
        # -------------------------
        for ally in state['allies']:
            if not ally.get('active', True): continue
            # nearest living enemy
            nearest = None; best_d2 = 1e9
            ax, ay, az = ally['pos']
            for e in state['enemies']:
                if not e.get('alive', True): continue
                ex, ey, ez = e['pos']
                d2 = (ex - ax) ** 2 + (ez - az) ** 2
                if d2 < best_d2:
                    best_d2 = d2; nearest = e
            if nearest is None: 
                continue
            ex, ey, ez = nearest['pos']
            dx = ex - ax; dz = ez - az
            dist = math.sqrt(dx*dx + dz*dz)
            if dist > 1.0:
                step = ally['speed']
                ally['pos'][0] += step * (dx / dist)
                ally['pos'][2] += step * (dz / dist)
                # gently move toward target's height but clamp to ground min
                ally['pos'][1] = max(-1.0, ally['pos'][1] + (ey - ay) * 0.05)
            else:
                # kill the enemy on contact -> player gains points
                nearest['alive'] = False
                state['score'] += 100; state['enemies_killed'] += 1
                soft_play('assets/bgm/enemy die_bgm.mp3')
                # NOTE: Only YOUR kills create allies (not chain infection).
                # If you want chain zombies, call: spawn_ally_from_enemy(nearest, "ally kill")

        # -------------------------
        # End conditions -> Summary screen (only after Level 4 complete)
        # -------------------------
        if state['player_life'] <= 0:
            soft_play('assets/bgm/player_die_bgm.mp3')
            state['game_state'] = 'summary'; state['end_time'] = now; state['end_title'] = "Game Over"
            glutPostRedisplay(); return

        if state['level'] == 4 and state['level_complete']:
            state['game_state'] = 'summary'; state['end_time'] = now; state['end_title'] = "You Win!"
            glutPostRedisplay(); return

        glutPostRedisplay()

    # -------------------------
    # Keyboard
    # -------------------------
    def keyboard(key, x, y):
        if key in (b'q', b'Q'):
            try: tracker.stop()
            except Exception: pass
            sys.exit(0)
        elif key == b'\x1b':
            if state['game_state'] == 'playing':
                state['game_state'] = 'summary'
                state['end_time'] = glutGet(GLUT_ELAPSED_TIME) / 1000.0
                state['end_title'] = "Session Summary"
            else:
                state['game_state'] = 'playing'; state['end_time'] = 0.0; state['end_title'] = None
        elif key in (b'r', b'R'):
            reset_game()
        elif key == b' ':
            create_bullet(state['bullets'], state['cannon_z'], state['cannon_angle'], state['bullet_speed'])
            state['shots_fired'] += 1; soft_play('assets/bgm/bomb_bgm.mp3')
        elif key in (b'l', b'L'):
            now = glutGet(GLUT_ELAPSED_TIME) / 1000.0
            if not state['laser_active'] and now >= state['laser_cooldown_end']:
                state['laser_active'] = True
                state['laser_start_time'] = now
                state['laser_cooldown_end'] = now + state['laser_duration'] + state['laser_cooldown']
                def laser_loop(): 
                    while state['laser_active']: soft_play('assets/bgm/laser_bgm.mp3')
                threading.Thread(target=laser_loop, daemon=True).start()
        elif key in (b'c', b'C'):
            now = glutGet(GLUT_ELAPSED_TIME) / 1000.0
            if not state['cheat_active'] and now >= state['cheat_cooldown_end']:
                state['cheat_active'] = True; state['cheat_start_time'] = now
                state['cheat_cooldown_end'] = now + state['cheat_cooldown']
                state['cheat_shots'] = 0; state['cheat_last_shot_time'] = now - state['cheat_shot_delay']
        elif key in (b'v', b'V'):
            state['view_mode'] = 'first' if state['view_mode'] == 'third' else 'third'
        elif key in (b'g', b'G'):
            state['gesture_aim_enabled'] = not state['gesture_aim_enabled']
            print(f"[Gesture Aim] {'ON' if state['gesture_aim_enabled'] else 'OFF'}")
        elif key == b'=':
            state['camera_distance'] = max(20.0, state['camera_distance'] - 2.0)
        elif key == b'-':
            state['camera_distance'] = min(150.0, state['camera_distance'] + 2.0)
        elif key == b'w':
            state['cannon_angle'] = tilt_cannon_down(state['cannon_angle'], state['CANNON_MAX_ANGLE'])
        elif key == b's':
            state['cannon_angle'] = tilt_cannon_up(state['cannon_angle'], state['CANNON_MIN_ANGLE'])
        elif key in (b'a', b'A'):
            state['cannon_z'] = move_cannon_down(state['cannon_z'], state['CANNON_MIN_Z'])
        elif key in (b'd', b'D'):
            state['cannon_z'] = move_cannon_up(state['cannon_z'], state['CANNON_MAX_Z'])
        glutPostRedisplay()

    # -------------------------
    # Special keys
    # -------------------------
    def special_keys(key, x, y):
        if key == GLUT_KEY_LEFT:
            state['camera_angle'] -= state['camera_move_speed']
        elif key == GLUT_KEY_RIGHT:
            state['camera_angle'] += state['camera_move_speed']
        elif key == GLUT_KEY_UP:
            state['camera_distance'] = max(20.0, state['camera_distance'] - 2.0)
            state['camera_height'] += state['camera_move_speed']
        elif key == GLUT_KEY_DOWN:
            state['camera_distance'] = min(150.0, state['camera_distance'] + 2.0)
            state['camera_height'] = max(5.0, state['camera_height'] - state['camera_move_speed'])
        glutPostRedisplay()

    # -------------------------
    # Reshape
    # -------------------------
    def reshape(width, height):
        if height == 0: height = 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(60, width / float(height), 1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)

    # -------------------------
    # GLUT init
    # -------------------------
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Arena Strike - 3D Arena with Cannon")

    glClearColor(0.15, 0.2, 0.25, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)

    # Start time for session
    state['start_time'] = glutGet(GLUT_ELAPSED_TIME) / 1000.0

    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutReshapeFunc(reshape)

    print("=== ARENA STRIKE - 3D Arena with Cannon & Bombs ===")
    print("- ESC to open/close Summary (R=Restart, Q=Quit)")
    print("- SPACE fire | L laser | C cheat | V view | G toggle gesture tilt (default OFF)")
    print("- Arrow keys rotate/zoom camera; WASD move/aim cannon")
    print("- ZOMBIE MODE: Your kills spawn green allies (2x slower) that fight for you.")
    glutMainLoop()


if __name__ == '__main__':
    main()