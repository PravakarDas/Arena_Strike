# main_game.py
# Main entry point for Arena Strike game
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from asset.arena_model import *
from asset.cannon_model import *
from asset.bombs import *
from asset.bullets import *
from asset.lvl1_stickyman import *
from asset.lvl2_bug import *
from asset.lvl3_archer import *
from asset.lvl4_boss import *

def main():
    # --- GAME STATE ---
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
        'score': 0
    }

    def display():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        cam_x = state['camera_distance'] * math.sin(math.radians(state['camera_angle']))
        cam_z = state['camera_distance'] * math.cos(math.radians(state['camera_angle']))
        gluLookAt(cam_x, state['camera_height'], cam_z, 0, 6, 0, 0, 1, 0)
        draw_arena_floor()
        draw_gallery_structure()
        draw_audience(state['audience_data'], state['cheer_time'])
        draw_arena_lights()
        draw_roof_structure()
        draw_atmosphere_effects(state['cheer_time'])
        draw_complete_cannon(state['cannon_z'], state['cannon_angle'])
        calculate_aiming_point(state['cannon_z'], state['cannon_angle'], state['aiming_point'])
        draw_aiming_system(state['show_aiming_line'], state['cannon_z'], state['cannon_angle'], state['aiming_point'])
        draw_all_bombs(state['bombs'])
        draw_bullets(state['bullets'])
        # Draw all enemies by type
        for enemy in state['enemies']:
            if not enemy['alive']:
                continue
            glPushMatrix()
            glTranslatef(enemy['pos'][0], 0, enemy['pos'][2])
            if enemy['type'] == 'stickyman':
                draw_stickman(0)
            elif enemy['type'] == 'bug':
                draw_bug(0)
            elif enemy['type'] == 'archer':
                draw_archer(0)
                for arrow in enemy.get('arrows', []):
                    if arrow['alive']:
                        glPushMatrix()
                        glTranslatef(arrow['x']-enemy['pos'][0], 1.5, arrow['z']-enemy['pos'][2])
                        glColor3f(0.7, 0.2, 0.2)
                        glutSolidSphere(0.12, 12, 12)
                        glPopMatrix()
            elif enemy['type'] == 'boss':
                draw_boss_demon_queen(0)
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
        s = f"Life: {state['player_life']}  |  Level {state['level']}: {level_name.get(state['level'], '')}  |  Score: {state['score']}"
        from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
        for c in s:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
        glEnable(GL_LIGHTING)
        glutSwapBuffers()

    def idle():
        state['cheer_time'] += 0.05
        update_bombs(state['bombs'], state['gravity'])
        update_bullets(state['bullets'])
        # --- LEVEL LOGIC ---
        now = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        # Level 1: Stickyman
        if state['level'] == 1:
            if not state['level_spawn_time']:
                state['enemies'] = [{'pos': [20.0, -1.0, 0.0], 'alive': True, 'type': 'stickyman', 'collided': False}]
                state['level_spawn_time'] = now
                state['level_second_spawned'] = False
                state['level_complete'] = False
            elif not state['level_second_spawned'] and now - state['level_spawn_time'] > 3.0:
                state['enemies'].append({'pos': [20.0, -1.0, 6.0], 'alive': True, 'type': 'stickyman', 'collided': False})
                state['level_second_spawned'] = True
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
            if all(not e['alive'] or e.get('collided', False) for e in state['enemies']) and state['level_second_spawned']:
                if not state['level_complete']:
                    state['level_complete'] = True
                    state['level'] += 1
                    state['level_spawn_time'] = None
                    state['level_second_spawned'] = False
                    state['enemies'] = []
        elif state['level'] == 2:
            if not state['level_spawn_time']:
                state['enemies'] = [{'pos': [20.0, -1.0, 0.0], 'alive': True, 'type': 'bug', 'collided': False}]
                state['level_spawn_time'] = now
                state['level_second_spawned'] = False
                state['level_complete'] = False
            elif not state['level_second_spawned'] and now - state['level_spawn_time'] > 3.0:
                state['enemies'].append({'pos': [20.0, -1.0, 6.0], 'alive': True, 'type': 'bug', 'collided': False})
                state['level_second_spawned'] = True
            for enemy in state['enemies']:
                if not enemy['alive']:
                    continue
                dx = -20.0 - enemy['pos'][0]
                dz = state['cannon_z'] - enemy['pos'][2]
                dist = (dx*dx + dz*dz) ** 0.5
                if dist > 1.0:
                    enemy['pos'][0] += 0.13 * dx / dist
                    enemy['pos'][2] += 0.13 * dz / dist
                    enemy['collided'] = False
                else:
                    if not enemy.get('collided', False):
                        state['player_life'] -= 2
                        enemy['collided'] = True
            if all(not e['alive'] or e.get('collided', False) for e in state['enemies']) and state['level_second_spawned']:
                if not state['level_complete']:
                    state['level_complete'] = True
                    state['level'] += 1
                    state['level_spawn_time'] = None
                    state['level_second_spawned'] = False
                    state['enemies'] = []
        elif state['level'] == 3:
            if not state['level_spawn_time']:
                state['enemies'] = [{'pos': [20.0, -1.0, 0.0], 'alive': True, 'type': 'archer', 'walk_timer': 0.0, 'shoot_timer': 0.0, 'walking': True, 'arrows': [], 'collided': False}]
                state['level_spawn_time'] = now
                state['level_second_spawned'] = False
                state['level_complete'] = False
            elif not state['level_second_spawned'] and now - state['level_spawn_time'] > 3.0:
                state['enemies'].append({'pos': [20.0, -1.0, 6.0], 'alive': True, 'type': 'archer', 'walk_timer': 0.0, 'shoot_timer': 0.0, 'walking': True, 'arrows': [], 'collided': False})
                state['level_second_spawned'] = True
            for enemy in state['enemies']:
                if not enemy['alive']:
                    continue
                enemy['walk_timer'] += 0.016
                if enemy['walking']:
                    if enemy['walk_timer'] < 2.0:
                        dx = -20.0 - enemy['pos'][0]
                        dz = state['cannon_z'] - enemy['pos'][2]
                        dist = (dx*dx + dz*dz) ** 0.5
                        if dist > 1.0:
                            enemy['pos'][0] += 0.06 * dx / dist
                            enemy['pos'][2] += 0.06 * dz / dist
                            enemy['collided'] = False
                        else:
                            if not enemy.get('collided', False):
                                state['player_life'] -= 2
                                enemy['collided'] = True
                    else:
                        enemy['walking'] = False
                        enemy['walk_timer'] = 0.0
                else:
                    enemy['shoot_timer'] += 0.016
                    if enemy['shoot_timer'] > 3.0:
                        dx = -20.0 - enemy['pos'][0]
                        dz = state['cannon_z'] - enemy['pos'][2]
                        dist = (dx*dx + dz*dz) ** 0.5
                        arrow = {'x': enemy['pos'][0], 'y': 1.5, 'z': enemy['pos'][2], 'dx': dx/dist, 'dz': dz/dist, 'alive': True}
                        enemy['arrows'].append(arrow)
                        enemy['shoot_timer'] = 0.0
                        enemy['walking'] = True
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
            if all(not e['alive'] or e.get('collided', False) for e in state['enemies']) and state['level_second_spawned']:
                if not state['level_complete']:
                    state['level_complete'] = True
                    state['level'] += 1
                    state['level_spawn_time'] = None
                    state['level_second_spawned'] = False
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
        # --- BULLET-ENEMY COLLISION ---
        for enemy in state['enemies']:
            if not enemy['alive']:
                continue
            for bullet in state['bullets']:
                if not bullet['alive']:
                    continue
                dx = bullet['x'] - enemy['pos'][0]
                dz = bullet['z'] - enemy['pos'][2]
                dy = bullet['y'] - 0.0
                if dx*dx + dy*dy + dz*dz < 1.2:
                    enemy['alive'] = False
                    bullet['alive'] = False
                    state['score'] += 100
        # --- GAME OVER CHECK ---
        if state['player_life'] <= 0:
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
        if key == b'q' or key == b'\x1b':
            sys.exit(0)
        elif key == b' ':
            state['camera_angle'] += 45
        elif key == b'=':
            state['camera_distance'] = max(20.0, state['camera_distance'] - 2.0)
        elif key == b'-':
            state['camera_distance'] = min(150.0, state['camera_distance'] + 2.0)
        elif key == b'w':
            state['camera_height'] += state['camera_move_speed']
        elif key == b's':
            state['camera_height'] = max(5.0, state['camera_height'] - state['camera_move_speed'])
        elif key == b'j' or key == b'J':
            state['cannon_z'] = move_cannon_down(state['cannon_z'], state['CANNON_MIN_Z'])
        elif key == b'k' or key == b'K':
            state['cannon_z'] = move_cannon_up(state['cannon_z'], state['CANNON_MAX_Z'])
        elif key == b'o' or key == b'O':
            state['cannon_angle'] = tilt_cannon_up(state['cannon_angle'], state['CANNON_MIN_ANGLE'])
        elif key == b'i' or key == b'I':
            state['cannon_angle'] = tilt_cannon_down(state['cannon_angle'], state['CANNON_MAX_ANGLE'])
        elif key == b'a' or key == b'A':
            state['camera_angle'] -= state['camera_move_speed']
        elif key == b'd' or key == b'D':
            state['camera_angle'] += state['camera_move_speed']
        elif key == b'f' or key == b'F':
            create_bomb(state['bombs'], state['cannon_z'], state['cannon_angle'], state['bomb_speed'], state['max_bombs'], state['gravity'])
        elif key == b'y' or key == b'Y':
            create_bullet(state['bullets'], state['cannon_z'], state['cannon_angle'], state['bullet_speed'])

    def special_keys(key, x, y):
        if key == GLUT_KEY_LEFT:
            state['camera_angle'] -= state['camera_move_speed']
        elif key == GLUT_KEY_RIGHT:
            state['camera_angle'] += state['camera_move_speed']
        elif key == GLUT_KEY_UP:
            state['camera_distance'] = max(20.0, state['camera_distance'] - 2.0)
        elif key == GLUT_KEY_DOWN:
            state['camera_distance'] = min(150.0, state['camera_distance'] + 2.0)
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
    glutSpecialFunc(special_keys)
    glutReshapeFunc(reshape)
    print("=== ARENA STRIKE - 3D Arena with Cannon & Bombs ===")
    print("- Press 'q' or ESC to quit")
    glutMainLoop()

if __name__ == '__main__':
    main()
