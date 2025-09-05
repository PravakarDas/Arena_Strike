from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

def create_bomb(bombs, cannon_z, cannon_angle, bomb_speed, max_bombs, gravity):
    if len(bombs) >= max_bombs:
        print("Maximum bombs reached! Wait for some to explode.")
        return
    barrel_length = 2.5
    cannon_world_x = -20.0
    cannon_world_y = -1.3
    cannon_world_z = cannon_z
    initial_x = cannon_world_x + barrel_length * math.cos(math.radians(cannon_angle))
    initial_y = cannon_world_y + barrel_length * math.sin(math.radians(cannon_angle))
    initial_z = cannon_world_z
    velocity_x = bomb_speed * math.cos(math.radians(cannon_angle))
    velocity_y = bomb_speed * math.sin(math.radians(cannon_angle))
    velocity_z = 0.0
    bomb = {
        'x': initial_x,
        'y': initial_y,
        'z': initial_z,
        'vel_x': velocity_x,
        'vel_y': velocity_y,
        'vel_z': velocity_z,
        'life_time': 0,
        'max_life': 300,
        'exploded': False
    }
    bombs.append(bomb)
    print(f"BOMB FIRED! Bombs active: {len(bombs)}")

def update_bombs(bombs, gravity):
    bombs_to_remove = []
    for i, bomb in enumerate(bombs):
        if bomb['exploded']:
            continue
        bomb['x'] += bomb['vel_x']
        bomb['y'] += bomb['vel_y']
        bomb['z'] += bomb['vel_z']
        bomb['vel_y'] += gravity
        if bomb['y'] <= -1.0:
            bomb['exploded'] = True
            print(f"BOMB EXPLODED at ({bomb['x']:.1f}, {bomb['y']:.1f}, {bomb['z']:.1f})")
        if (bomb['x'] > 25.0 or bomb['x'] < -25.0 or bomb['z'] > 15.0 or bomb['z'] < -15.0):
            bomb['exploded'] = True
            print("Bomb flew out of arena!")
        bomb['life_time'] += 1
        if bomb['life_time'] >= bomb['max_life']:
            bombs_to_remove.append(i)
    for i in reversed(bombs_to_remove):
        bombs.pop(i)

def draw_bomb(bomb):
    glPushMatrix()
    glTranslatef(bomb['x'], bomb['y'], bomb['z'])
    if bomb['exploded']:
        glColor3f(1.0, 0.5, 0.0)
        explosion_size = min(2.0, (bomb['life_time'] - 240) * 0.1)
        glutSolidSphere(explosion_size, 12, 12)
        glColor3f(1.0, 1.0, 0.0)
        for j in range(8):
            angle = j * 45
            offset_x = explosion_size * 0.5 * math.cos(math.radians(angle))
            offset_z = explosion_size * 0.5 * math.sin(math.radians(angle))
            glPushMatrix()
            glTranslatef(offset_x, 0, offset_z)
            glutSolidSphere(0.1, 12, 12)
            glPopMatrix()
    else:
        glColor3f(0.2, 0.2, 0.2)
        glutSolidSphere(0.15, 12, 12)
        glColor3f(1.0, 0.8, 0.0)
        spark_offset = 0.2 + 0.1 * math.sin(bomb['life_time'] * 0.5)
        glPushMatrix()
        glTranslatef(0, spark_offset, 0)
        glutSolidSphere(0.05, 12, 12)
        glPopMatrix()
    glPopMatrix()

def draw_all_bombs(bombs):
    glDisable(GL_LIGHTING)
    for bomb in bombs:
        draw_bomb(bomb)
    glEnable(GL_LIGHTING)
