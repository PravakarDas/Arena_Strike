import sys
import math
import random
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
from assets.menu_functions import *
import threading
from playsound import playsound
import time

def main():
    state = {
        'audience_data': generate_audience(),
        'cheer_time': 0.0,
        'camera_distance': 35.0,
        'camera_angle': 0.0,
        'camera_height': 24.0,
        'camera_move_speed': 3.0,
        'show_aiming_line': True,
        'aiming_point': [0.0, 0.0, 0.0],
        'CANNON_MIN_Z': -12.0,
        'CANNON_MAX_Z': 12.0,
        'CANNON_MIN_ANGLE': 0.0,
        'CANNON_MAX_ANGLE': 90.0,
        'cannon_z': 0.0,
        'cannon_angle': 45.0,
        'bombs': [],
        'bomb_speed': 0.8,
        'gravity': -0.02,
        'max_bombs': 10,
        'bullets': [],
        'bullet_speed': 1.2,
        'PLAYER_LIFE': 20,
        'player_life': 20,
        'enemies': [],
        'level': 1,
        'level_spawn_time': None,
        'level_second_spawned': False,
        'level_complete': False,
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
        'spawned_count': 0,
        'max_enemies': 5,
        'spawn_delays': [],
        'view_mode': 'third'
    }

    # Menu states
    MENU = 0
    SETTINGS = 1
    PLAYING = 2
    current_state = MENU

    # Animation variables
    arena_rotation = 0
    logo_blink_time = 0
    menu_selection = 0
    selection_time = 0
    show_selection_box = False
    cheer_time = 0

    # Generate audience data for menu
    audience_data = generate_audience()

    # Start BGM loop
    def play_bgm():
        while True:
            playsound('assets/bgm/bgm.mp3')

    bgm_thread = threading.Thread(target=play_bgm, daemon=True)
    bgm_thread.start()

    def render_text_as_cubes(text, x, y, z, scale=1.0):
        """Render text as colored cubes representing letters"""
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(scale, scale, scale)
        
        # Each character is represented as a small cube
        char_width = 1.5
        for i, char in enumerate(text):
            if char == ' ':
                continue
            glPushMatrix()
            glTranslatef(i * char_width - len(text) * char_width * 0.5, 0, 0)
            glScalef(1.0, 1.5, 0.3)
            glutSolidCube(1.0)
            glPopMatrix()
        glPopMatrix()

    def draw_arena_complete():
        """Draw the complete arena with all components"""
        nonlocal cheer_time
        
        glPushMatrix()
        glRotatef(arena_rotation, 0, 1, 0)
        
        # Draw arena floor
        draw_arena_floor()
        
        # Draw gallery structure
        draw_gallery_structure()
        
        # Draw audience with cheering animation
        draw_audience(audience_data, cheer_time)
        
        # Draw arena lights
        draw_arena_lights()
        
        # Draw roof structure
        draw_roof_structure()
        
        # Draw atmosphere effects
        draw_atmosphere_effects(cheer_time)
        
        glPopMatrix()

    def draw_blinking_logo():
        """Draw the Arena Strike logo with blinking effect"""
        blink_intensity = 0.7 + 0.3 * abs(math.sin(logo_blink_time * 4))
        
        # Golden blinking color
        glColor3f(1.0 * blink_intensity, 0.8 * blink_intensity, 0.2 * blink_intensity)
        
        # "ARENA STRIKE" text representation
        render_text_as_cubes("ARENA STRIKE", 0, 35, -5, 2.5)
        
        # Add glow effect
        glColor4f(1.0, 0.8, 0.0, 0.2 * blink_intensity)
        render_text_as_cubes("ARENA STRIKE", 0, 35, -4, 3.0)

    def draw_selection_golden_effect():
        """Draw golden treasure box effect when option is selected"""
        if not show_selection_box or menu_selection == 0:
            return
        
        # Position based on selected menu option
        option_positions = [18, 10, 2]  # Y positions for Play, Settings, Quit
        box_y = option_positions[menu_selection - 1]
        
        current_time = glutGet(GLUT_ELAPSED_TIME) * 0.001
        
        # Draw spinning golden rings around selection
        glColor3f(1.0, 0.84, 0.0)  # Gold color
        
        for i in range(20):
            angle = (i / 20.0) * 360 + current_time * 150
            radius = 8 + math.sin(current_time * 3 + i) * 1
            rad = math.radians(angle)
            
            ring_x = radius * math.cos(rad)
            ring_z = -10 + radius * math.sin(rad) * 0.3
            ring_y = box_y + math.sin(current_time * 4 + i) * 2
            
            glPushMatrix()
            glTranslatef(ring_x, ring_y, ring_z)
            glRotatef(current_time * 200 + i * 18, 0, 1, 0)
            glutSolidTorus(0.3, 0.8, 8, 16)
            glPopMatrix()

    def draw_main_menu():
        """Draw the main menu with properly positioned options"""
        menu_items = [
            ("Play [1]", 18),
            ("Settings [2]", 10), 
            ("Quit [3]", 2)
        ]
        
        for i, (text, y_pos) in enumerate(menu_items):
            # Highlight selected option
            if menu_selection == i + 1:
                glColor3f(1.0, 0.8, 0.2)  # Golden highlight
            else:
                glColor3f(0.9, 0.9, 1.0)  # White text
            
            render_text_as_cubes(text, 0, y_pos, -8, 1.8)

    def draw_settings_menu():
        """Draw settings menu"""
        glColor3f(1.0, 1.0, 0.8)
        render_text_as_cubes("SETTINGS", 0, 25, -5, 2.0)
        
        settings_options = [
            "Sound: ON",
            "Graphics: HIGH",
            "Difficulty: MEDIUM", 
            "Press ESC to return"
        ]
        
        glColor3f(0.8, 0.8, 0.9)
        for i, option in enumerate(settings_options):
            render_text_as_cubes(option, 0, 15 - i * 5, -6, 1.2)

    def update_animations():
        """Update all animation variables"""
        nonlocal arena_rotation, logo_blink_time, cheer_time, selection_time, show_selection_box
        
        current_time = glutGet(GLUT_ELAPSED_TIME) * 0.001
        
        # Arena rotation
        arena_rotation += 0.5
        arena_rotation %= 360
        
        # Logo blinking
        logo_blink_time = current_time
        
        # Audience cheering
        cheer_time = current_time
        
        # Selection box timing
        if menu_selection > 0:
            if current_time - selection_time < 0.5:
                show_selection_box = True
            else:
                show_selection_box = False
                execute_selection()

    def execute_selection():
        """Execute the selected menu option"""
        nonlocal current_state, menu_selection
        
        if menu_selection == 1:  # Play
            current_state = PLAYING
            print("Game Started!")
        elif menu_selection == 2:  # Settings
            current_state = SETTINGS
            print("Entered Settings")
        elif menu_selection == 3:  # Quit
            print("Thanks for playing Arena Strike!")
            glutLeaveMainLoop()
        
        menu_selection = 0

    def render_text_3d(text, x, y, z):
        glRasterPos3f(x, y, z)
        for c in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    def display():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        if current_state == MENU:
            # Main menu camera
            gluLookAt(0, 25, 60,   # Camera position
                      0, 15, 0,    # Look at point
                      0, 1, 0)     # Up vector
            
            # Draw rotating arena (dimmed for background)
            glColor4f(0.6, 0.6, 0.7, 0.8)
            draw_arena_complete()
            
            # Draw blinking logo
            draw_blinking_logo()
            
            # Draw menu options
            draw_main_menu()
            
            # Draw golden selection effect
            draw_selection_golden_effect()
            
        elif current_state == SETTINGS:
            gluLookAt(0, 20, 40, 0, 15, 0, 0, 1, 0)
            
            # Dimmed arena background
            glColor4f(0.4, 0.4, 0.5, 0.6)
            glPushMatrix()
            glRotatef(arena_rotation * 0.2, 0, 1, 0)
            draw_arena_complete()
            glPopMatrix()
            
            draw_settings_menu()
            
        elif current_state == PLAYING:
            if state['view_mode'] == 'third':
                cam_x = state['camera_distance'] * math.sin(math.radians(state['camera_angle']))
                cam_z = state['camera_distance'] * math.cos(math.radians(state['camera_angle']))
                gluLookAt(cam_x, state['camera_height'], cam_z, 0, 6, 0, 0, 1, 0)
            else:  # first
                cannon_x = -20.0
                cannon_y = -1.3
                cannon_z_pos = state['cannon_z']
                angle_rad = math.radians(state['cannon_angle'])
                look_x = cannon_x + 10 * math.cos(angle_rad)
                look_y = cannon_y + 10 * math.sin(angle_rad)
                look_z = cannon_z_pos
                # Position camera slightly back and up from cannon
                cam_x = cannon_x - 2.0
                cam_y = cannon_y + 2.0
                cam_z = cannon_z_pos
                gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 1, 0)
            draw_arena_floor()
            draw_gallery_structure()
            draw_audience(state['audience_data'], state['cheer_time'])
            draw_arena_lights()
            draw_roof_structure()
            draw_atmosphere_effects(state['cheer_time'])
            draw_complete_cannon(state['cannon_z'], state['cannon_angle'])
            calculate_aiming_point(state['cannon_z'], state['cannon_angle'], state['aiming_point'])
            draw_aiming_system(state['show_aiming_line'], state['cannon_z'], state['cannon_angle'], state['aiming_point'])
            # Draw laser if active
            if state['laser_active']:
                angle_rad = math.radians(state['cannon_angle'])
                tip_x = -20.0 + 2.5 * math.cos(angle_rad)
                tip_y = -1.3 + 2.5 * math.sin(angle_rad)
                tip_z = state['cannon_z']
                end_x = tip_x + 50.0 * math.cos(angle_rad)
                end_y = tip_y + 50.0 * math.sin(angle_rad)
                end_z = tip_z
                glDisable(GL_LIGHTING)
                glColor3f(1.0, 0.0, 0.0)  # Red laser
                glLineWidth(5.0)
                glBegin(GL_LINES)
                glVertex3f(tip_x, tip_y, tip_z)
                glVertex3f(end_x, end_y, end_z)
                glEnd()
                glLineWidth(1.0)
                glEnable(GL_LIGHTING)
            draw_all_bombs(state['bombs'])
            draw_bullets(state['bullets'])

            for enemy in state['enemies']:
                if not enemy['alive']:
                    continue
                glPushMatrix()
                glTranslatef(enemy['pos'][0], enemy['pos'][1], enemy['pos'][2])
                animation_time = glutGet(GLUT_ELAPSED_TIME) / 1000.0
                if enemy['type'] == 'stickyman':
                    draw_stickman(animation_time)
                elif enemy['type'] == 'bug':
                    draw_bug(animation_time)
                elif enemy['type'] == 'archer':
                    draw_archer(animation_time)
                    for arrow in enemy.get('arrows', []):
                        if arrow['alive']:
                            glPushMatrix()
                            glTranslatef(arrow['x']-enemy['pos'][0], 1.5, arrow['z']-enemy['pos'][2])
                            glColor3f(0.7, 0.2, 0.2)
                            glutSolidSphere(0.12, 12, 12)
                            glPopMatrix()
                elif enemy['type'] == 'boss':
                    draw_boss_demon_queen(animation_time)
                    for proj in enemy.get('projectiles', []):
                        if proj['alive']:
                            glPushMatrix()
                            glTranslatef(proj['x']-enemy['pos'][0], 1.5, proj['z']-enemy['pos'][2])
                            glColor3f(1, 0, 1)
                            glutSolidSphere(0.15, 12, 12)
                            glPopMatrix()
                glPopMatrix()
            # HUD: player life, level, and score
            glDisable(GL_LIGHTING)
            glWindowPos2f(10, 40)
            level_name = {1: 'Stickyman', 2: 'Bug', 3: 'Archer', 4: 'Boss'}
            now = glutGet(GLUT_ELAPSED_TIME) / 1000.0
            laser_status = "Laser: Ready"
            if state['laser_active']:
                laser_status = "Laser: Active"
            elif now < state['laser_cooldown_end']:
                remaining = int(state['laser_cooldown_end'] - now)
                laser_status = f"Laser: {remaining}s"
            cheat_status = "Cheat: Ready"
            if state['cheat_active']:
                cheat_status = f"Cheat: {state['cheat_shots']}/{state['cheat_max_shots']}"
            elif now < state['cheat_cooldown_end']:
                remaining = int(state['cheat_cooldown_end'] - now)
                cheat_status = f"Cheat: {remaining}s"
            s = f"Life: {state['player_life']}  |  Level {state['level']}: {level_name.get(state['level'], '')}  |  Score: {state['score']}  |  {laser_status}  |  {cheat_status}  |  View: {state['view_mode'].capitalize()}"
            from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
            for c in s:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
            glEnable(GL_LIGHTING)
        
        glutSwapBuffers()

    def idle():
        if current_state == MENU or current_state == SETTINGS:
            update_animations()
        elif current_state == PLAYING:
            state['cheer_time'] += 0.05
            update_bombs(state['bombs'], state['gravity'])
            update_bullets(state['bullets'])
        # --- LEVEL LOGIC ---
        now = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        # Level 1: Stickyman
        if state['level'] == 1:
            if not state['level_spawn_time']:
                state['enemies'] = []
                state['spawn_delays'] = [0, 2] + [random.uniform(2, 5) for _ in range(3)]
                state['spawned_count'] = 0
                state['level_spawn_time'] = now
                state['level_complete'] = False
            # Spawn enemies
            while state['spawned_count'] < state['max_enemies'] and now - state['level_spawn_time'] >= state['spawn_delays'][state['spawned_count']]:
                z_pos = random.uniform(-10, 10)
                state['enemies'].append({'pos': [20.0, -1.0, z_pos], 'alive': True, 'type': 'stickyman', 'collided': False})
                state['spawned_count'] += 1
            for enemy in state['enemies']:
                if not enemy['alive']:
                    continue
                dx = -20.0 - enemy['pos'][0]
                dz = state['cannon_z'] - enemy['pos'][2]
                dist = (dx*dx + dz*dz) ** 0.5
                if dist > 1.0:
                    enemy['pos'][0] += 0.08 * dx / dist
                    enemy['pos'][2] += 0.08 * dz / dist
                    enemy['collided'] = False
                else:
                    if not enemy.get('collided', False):
                        state['player_life'] -= 2
                        enemy['collided'] = True
            if all(not e['alive'] or e.get('collided', False) for e in state['enemies']) and state['spawned_count'] == state['max_enemies']:
                if not state['level_complete']:
                    state['level_complete'] = True
                    state['level'] += 1
                    state['level_spawn_time'] = None
                    state['spawned_count'] = 0
                    state['enemies'] = []
        elif state['level'] == 2:
            if not state['level_spawn_time']:
                state['enemies'] = []
                state['spawn_delays'] = [0, 2] + [random.uniform(2, 5) for _ in range(3)]
                state['spawned_count'] = 0
                state['level_spawn_time'] = now
                state['level_complete'] = False
            # Spawn enemies
            while state['spawned_count'] < state['max_enemies'] and now - state['level_spawn_time'] >= state['spawn_delays'][state['spawned_count']]:
                z_pos = random.uniform(-10, 10)
                state['enemies'].append({'pos': [20.0, 8.0, z_pos], 'alive': True, 'type': 'bug', 'collided': False})
                state['spawned_count'] += 1
            for enemy in state['enemies']:
                if not enemy['alive']:
                    continue
                # 3D movement towards cannon position [-20.0, -1.0, cannon_z]
                target_x = -20.0
                target_y = -1.0
                target_z = state['cannon_z']
                dx = target_x - enemy['pos'][0]
                dy = target_y - enemy['pos'][1]
                dz = target_z - enemy['pos'][2]
                dist = (dx*dx + dy*dy + dz*dz) ** 0.5
                if dist > 1.5:
                    enemy['pos'][0] += 0.13 * dx / dist
                    enemy['pos'][1] += 0.13 * dy / dist
                    enemy['pos'][2] += 0.13 * dz / dist
                    enemy['collided'] = False
                else:
                    if not enemy.get('collided', False):
                        state['player_life'] -= 2
                        enemy['collided'] = True
            if all(not e['alive'] or e.get('collided', False) for e in state['enemies']) and state['spawned_count'] == state['max_enemies']:
                if not state['level_complete']:
                    state['level_complete'] = True
                    state['level'] += 1
                    state['level_spawn_time'] = None
                    state['spawned_count'] = 0
                    state['enemies'] = []
        elif state['level'] == 3:
            if not state['level_spawn_time']:
                state['enemies'] = []
                state['spawn_delays'] = [0, 2] + [random.uniform(2, 5) for _ in range(3)]
                state['spawned_count'] = 0
                state['level_spawn_time'] = now
                state['level_complete'] = False
            # Spawn enemies
            while state['spawned_count'] < state['max_enemies'] and now - state['level_spawn_time'] >= state['spawn_delays'][state['spawned_count']]:
                z_pos = random.uniform(-10, 10)
                state['enemies'].append({'pos': [20.0, -1.0, z_pos], 'alive': True, 'type': 'archer', 'walk_timer': 0.0, 'shoot_timer': 0.0, 'walking': True, 'arrows': [], 'shots_fired': 0, 'collided': False})
                state['spawned_count'] += 1
            for enemy in state['enemies']:
                if not enemy['alive']:
                    continue
                enemy['walk_timer'] += 0.016
                if enemy['walking']:
                    dx = -20.0 - enemy['pos'][0]
                    dz = state['cannon_z'] - enemy['pos'][2]
                    dist = (dx*dx + dz*dz) ** 0.5
                    if dist > 1.0:
                        enemy['pos'][0] += 0.06 * dx / dist
                        enemy['pos'][2] += 0.06 * dz / dist
                        enemy['collided'] = False
                        # Switch to shooting after walking for 5-7 seconds (balanced)
                        if enemy['walk_timer'] > 5.0 + (enemy['pos'][0] % 2.0):
                            enemy['walking'] = False
                            enemy['walk_timer'] = 0.0
                    else:
                        if not enemy.get('collided', False):
                            state['player_life'] -= 2
                            enemy['collided'] = True
                else:
                    enemy['shoot_timer'] += 0.016
                    if enemy['shoot_timer'] > 2.0:  # Shoot every 2 seconds instead of 3
                        dx = -20.0 - enemy['pos'][0]
                        dz = state['cannon_z'] - enemy['pos'][2]
                        dist = (dx*dx + dz*dz) ** 0.5
                        arrow = {'x': enemy['pos'][0], 'y': 1.5, 'z': enemy['pos'][2], 'dx': dx/dist, 'dz': dz/dist, 'alive': True}
                        enemy['arrows'].append(arrow)
                        enemy['shoot_timer'] = 0.0
                        enemy['shots_fired'] += 1
                        if enemy['shots_fired'] >= 2:
                            enemy['walking'] = True
                            enemy['shots_fired'] = 0
            for enemy in state['enemies']:
                if enemy['type'] == 'archer':
                    for arrow in enemy['arrows']:
                        if not arrow['alive']:
                            continue
                        arrow['x'] += arrow['dx'] * 0.5
                        arrow['z'] += arrow['dz'] * 0.5
                        if abs(arrow['x'] - -20.0) < 1.0 and abs(arrow['z'] - state['cannon_z']) < 1.0:
                            state['player_life'] -= 1
                            arrow['alive'] = False
            if all(not e['alive'] or e.get('collided', False) for e in state['enemies']) and state['spawned_count'] == state['max_enemies']:
                if not state['level_complete']:
                    state['level_complete'] = True
                    state['level'] += 1
                    state['level_spawn_time'] = None
                    state['spawned_count'] = 0
                    state['enemies'] = []
        elif state['level'] == 4:
            if not state['level_spawn_time']:
                state['enemies'] = [{'pos': [20.0, -1.0, 0.0], 'alive': True, 'type': 'boss', 'projectiles': [], 'collided': False}]
                state['level_spawn_time'] = now
                state['level_complete'] = False
            for enemy in state['enemies']:
                if not enemy['alive']:
                    continue
                dx = -20.0 - enemy['pos'][0]
                dz = state['cannon_z'] - enemy['pos'][2]
                dist = (dx*dx + dz*dz) ** 0.5
                if dist > 1.0:
                    enemy['pos'][0] += 0.18 * dx / dist
                    enemy['pos'][2] += 0.18 * dz / dist
                    enemy['collided'] = False
                else:
                    if not enemy.get('collided', False):
                        state['player_life'] -= 5
                        enemy['collided'] = True
                if int(now*2) % 2 == 0 and len(enemy['projectiles']) < 3:
                    for i in range(3):
                        angle = math.radians(-20 + i*20)
                        dx_proj = math.sin(angle)
                        dz_proj = math.cos(angle)
                        proj = {'x': enemy['pos'][0], 'y': 1.5, 'z': enemy['pos'][2], 'dx': dx_proj, 'dz': dz_proj, 'alive': True}
                        enemy['projectiles'].append(proj)
            for enemy in state['enemies']:
                if enemy['type'] == 'boss':
                    for proj in enemy['projectiles']:
                        if not proj['alive']:
                            continue
                        proj['x'] += proj['dx'] * 0.7
                        proj['z'] += proj['dz'] * 0.7
                        if abs(proj['x'] - -20.0) < 1.0 and abs(proj['z'] - state['cannon_z']) < 1.0:
                            state['player_life'] -= 2
                            proj['alive'] = False
            if all(not e['alive'] or e.get('collided', False) for e in state['enemies']):
                if not state['level_complete']:
                    state['level_complete'] = True
                    # Game win
        # --- LASER LOGIC ---
        if state['laser_active'] and now - state['laser_start_time'] > state['laser_duration']:
            state['laser_active'] = False
        if state['laser_active']:
            # Calculate laser direction
            angle_rad = math.radians(state['cannon_angle'])
            tip_x = -20.0 + 2.5 * math.cos(angle_rad)
            tip_y = -1.3 + 2.5 * math.sin(angle_rad)
            tip_z = state['cannon_z']
            dir_x = math.cos(angle_rad)
            dir_y = math.sin(angle_rad)
            dir_z = 0.0
            # Kill enemies in laser path
            for enemy in state['enemies']:
                if not enemy['alive']:
                    continue
                ex, ey, ez = enemy['pos']
                # Vector from tip to enemy
                vx = ex - tip_x
                vy = ey - tip_y
                vz = ez - tip_z
                # Project onto direction
                proj = vx * dir_x + vy * dir_y + vz * dir_z
                if proj > 0:  # In front
                    # Perpendicular distance
                    perp_x = vx - proj * dir_x
                    perp_y = vy - proj * dir_y
                    perp_z = vz - proj * dir_z
                    dist_perp = math.sqrt(perp_x**2 + perp_y**2 + perp_z**2)
                    if dist_perp < 1.0 and proj < 30.0:  # Within 1 unit and 30 units range
                        enemy['alive'] = False
                        state['score'] += 100
                        playsound('assets/bgm/enemy die_bgm.mp3', block=False)
        # --- CHEAT MODE LOGIC ---
        if state['cheat_active'] and now - state['cheat_last_shot_time'] >= state['cheat_shot_delay']:
            # Find closest enemy
            closest = None
            min_dist = float('inf')
            for enemy in state['enemies']:
                if enemy['alive']:
                    dx = enemy['pos'][0] - (-20.0)
                    dz = enemy['pos'][2] - state['cannon_z']
                    dist = dx**2 + dz**2
                    if dist < min_dist:
                        min_dist = dist
                        closest = enemy
            if closest:
                # Aim at closest
                ex, ey, ez = closest['pos']
                # Set cannon_z to ez
                state['cannon_z'] = max(state['CANNON_MIN_Z'], min(state['CANNON_MAX_Z'], ez))
                # Compute angle
                dx = ex - (-20.0)
                dy = ey - (-1.3)
                angle = math.degrees(math.atan2(dy, dx))
                state['cannon_angle'] = max(state['CANNON_MIN_ANGLE'], min(state['CANNON_MAX_ANGLE'], angle))
                # Shoot
                create_bullet(state['bullets'], state['cannon_z'], state['cannon_angle'], state['bullet_speed'])
                state['cheat_last_shot_time'] = now
                state['cheat_shots'] += 1
                if state['cheat_shots'] >= state['cheat_max_shots']:
                    state['cheat_active'] = False
            else:
                state['cheat_active'] = False
        # --- BULLET-ENEMY COLLISION ---
        for enemy in state['enemies']:
            if not enemy['alive']:
                continue
            for bullet in state['bullets']:
                if not bullet['alive']:
                    continue
                dx = bullet['x'] - enemy['pos'][0]
                dz = bullet['z'] - enemy['pos'][2]
                dy = bullet['y'] - enemy['pos'][1]
                if dx*dx + dy*dy + dz*dz < 1.2:
                    enemy['alive'] = False
                    bullet['alive'] = False
                    state['score'] += 100
                    playsound('assets/bgm/enemy die_bgm.mp3', block=False)
        # --- GAME OVER CHECK ---
        if state['player_life'] <= 0:
            playsound('assets/bgm/player_die_bgm.mp3', block=False)
            print("\n==================== GAME OVER ====================")
            print(f"Final Score: {state['score']}")
            print(f"Level Reached: {state['level']}")
            print("Better luck next time!")
            sys.exit(0)
        # --- GAME WIN CHECK ---
        if state['level'] == 4 and state['level_complete']:
            print("\n==================== YOU WIN! ====================")
            print(f"Final Score: {state['score']}")
            print(f"All levels completed!")
            sys.exit(0)
        glutPostRedisplay()

    def keyboard(key, x, y):
        nonlocal current_state, menu_selection, selection_time
        if current_state == MENU:
            if key == b'1':
                menu_selection = 1
                selection_time = glutGet(GLUT_ELAPSED_TIME) * 0.001
                print("Selected: Play")
            elif key == b'2':
                menu_selection = 2
                selection_time = glutGet(GLUT_ELAPSED_TIME) * 0.001
                print("Selected: Settings")
            elif key == b'3':
                menu_selection = 3
                selection_time = glutGet(GLUT_ELAPSED_TIME) * 0.001
                print("Selected: Quit")
        elif current_state == SETTINGS:
            if key == b'\x1b':  # ESC key
                current_state = MENU
                print("Returned to main menu")
        elif current_state == PLAYING:
            if key == b'q' or key == b'\x1b':
                sys.exit(0)
            elif key == b' ':
                create_bullet(state['bullets'], state['cannon_z'], state['cannon_angle'], state['bullet_speed'])
                playsound('assets/bgm/bomb_bgm.mp3', block=False)
            elif key == b'l' or key == b'L':
                now = glutGet(GLUT_ELAPSED_TIME) / 1000.0
                if not state['laser_active'] and now >= state['laser_cooldown_end']:
                    state['laser_active'] = True
                    state['laser_start_time'] = now
                    state['laser_cooldown_end'] = now + state['laser_duration'] + state['laser_cooldown']
                    def laser_loop():
                        while state['laser_active']:
                            playsound('assets/bgm/laser_bgm.mp3')
                    threading.Thread(target=laser_loop, daemon=True).start()
            elif key == b'c' or key == b'C':
                now = glutGet(GLUT_ELAPSED_TIME) / 1000.0
                if not state['cheat_active'] and now >= state['cheat_cooldown_end']:
                    state['cheat_active'] = True
                    state['cheat_start_time'] = now
                    state['cheat_cooldown_end'] = now + state['cheat_cooldown']
                    state['cheat_shots'] = 0
                    state['cheat_last_shot_time'] = now - state['cheat_shot_delay']  # shoot immediately
            elif key == b'v' or key == b'V':
                state['view_mode'] = 'first' if state['view_mode'] == 'third' else 'third'
            elif key == b'=':
                state['camera_distance'] = max(20.0, state['camera_distance'] - 2.0)
            elif key == b'-':
                state['camera_distance'] = min(150.0, state['camera_distance'] + 2.0)
            elif key == b'w': #done
                state['cannon_angle'] = tilt_cannon_down(state['cannon_angle'], state['CANNON_MAX_ANGLE'])
            elif key == b's':
                state['cannon_angle'] = tilt_cannon_up(state['cannon_angle'], state['CANNON_MIN_ANGLE'])
            elif key == b'a' or key == b'A': #done
                state['cannon_z'] = move_cannon_down(state['cannon_z'], state['CANNON_MIN_Z']) 
            elif key == b'd' or key == b'D': #done
                state['cannon_z'] = move_cannon_up(state['cannon_z'], state['CANNON_MAX_Z'])

    def mouse(button, state_mouse, x, y):
        if button == GLUT_LEFT_BUTTON and state_mouse == GLUT_DOWN:
            create_bomb(state['bombs'], state['cannon_z'], state['cannon_angle'], state['bomb_speed'], state['max_bombs'], state['gravity'])
            playsound('assets/bgm/bomb_bgm.mp3', block=False)

    def special_keys(key, x, y):
        if key == GLUT_KEY_LEFT:
            state['camera_angle'] -= state['camera_move_speed']
            # state['camera_angle'] -= state['camera_move_speed']
        elif key == GLUT_KEY_RIGHT:
            state['camera_angle'] += state['camera_move_speed']
            # state['camera_angle'] += state['camera_move_speed']
        elif key == GLUT_KEY_UP:
            state['camera_distance'] = max(20.0, state['camera_distance'] - 2.0)
            state['camera_height'] += state['camera_move_speed']
        elif key == GLUT_KEY_DOWN:
            state['camera_distance'] = min(150.0, state['camera_distance'] + 2.0)
            state['camera_height'] = max(5.0, state['camera_height'] - state['camera_move_speed'])
        glutPostRedisplay()

    def reshape(width, height):
        if height == 0:
            height = 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, width/height, 1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)

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
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)
    glutSpecialFunc(special_keys)
    glutReshapeFunc(reshape)
    print("=== ARENA STRIKE - 3D Arena with Cannon & Bombs ===")
    print("- Press 'q' or ESC to quit")
    print("- Press SPACE to fire bullets")
    print("- Press L to activate laser (5s active, 30s cooldown)")
    print("- Press C to activate cheat mode (auto-aim & shoot 3 enemies, 20s cooldown)")
    print("- Press V to toggle view (third/first person)")
    glutMainLoop()

if __name__ == '__main__':
    main()
