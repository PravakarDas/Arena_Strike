# bullets.py
# Handles bullet creation, update, and drawing
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

def create_bullet(bullets, cannon_z, cannon_angle, bullet_speed):
    barrel_length = 2.5
    cannon_world_x = -20.0
    cannon_world_y = -1.3
    cannon_world_z = cannon_z
    tip_x = cannon_world_x + barrel_length * math.cos(math.radians(cannon_angle))
    tip_y = cannon_world_y + barrel_length * math.sin(math.radians(cannon_angle))
    tip_z = cannon_world_z
    vx = bullet_speed * math.cos(math.radians(cannon_angle))
    vy = bullet_speed * math.sin(math.radians(cannon_angle))
    vz = 0.0
    bullets.append({'x': tip_x, 'y': tip_y, 'z': tip_z, 'vx': vx, 'vy': vy, 'vz': vz, 'alive': True})
    print("Bullet fired!")

def update_bullets(bullets):
    for bullet in bullets:
        if not bullet['alive']:
            continue
        bullet['x'] += bullet['vx']
        bullet['y'] += bullet['vy']
        bullet['z'] += bullet['vz']
        if bullet['x'] < -25 or bullet['x'] > 25 or bullet['z'] < -15 or bullet['z'] > 15 or bullet['y'] < -2 or bullet['y'] > 30:
            bullet['alive'] = False

def draw_bullets(bullets):
    glDisable(GL_LIGHTING)
    glColor3f(1, 1, 0.2)
    for bullet in bullets:
        if bullet['alive']:
            glPushMatrix()
            glTranslatef(bullet['x'], bullet['y'], bullet['z'])
            glutSolidSphere(0.18, 12, 12)
            glPopMatrix()
    glEnable(GL_LIGHTING)
