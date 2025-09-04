# cannon_model.py
# Handles cannon base, barrel, aiming, and movement
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

def draw_cannon_base():
    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(0, -0.8, 0)
    glScalef(1.5, 0.3, 1.0)
    glutSolidCube(1.0)
    glPopMatrix()
    glColor3f(0.1, 0.1, 0.1)
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(0.8 * side, -0.8, 0.6)
        glRotatef(90, 0, 1, 0)
        quad = gluNewQuadric()
        gluCylinder(quad, 0.4, 0.4, 0.2, 12, 12)
        gluDeleteQuadric(quad)
        glColor3f(0.3, 0.3, 0.3)
        for i in range(6):
            glPushMatrix()
            glRotatef(i * 60, 0, 0, 1)
            glTranslatef(0, 0.2, 0.1)
            glScalef(0.05, 0.3, 0.05)
            glutSolidCube(1.0)
            glPopMatrix()
        glColor3f(0.1, 0.1, 0.1)
        glPopMatrix()

def draw_cannon_barrel(cannon_angle):
    glPushMatrix()
    glRotatef(cannon_angle, 1, 0, 0)
    glColor3f(0.15, 0.15, 0.2)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    quad = gluNewQuadric()
    gluCylinder(quad, 0.15, 0.15, 2.5, 12, 12)
    glTranslatef(0, 0, 2.5)
    glColor3f(0.1, 0.1, 0.1)
    gluCylinder(quad, 0.17, 0.17, 0.1, 12, 12)
    gluDeleteQuadric(quad)
    glPopMatrix()
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(0, 0, -0.3)
    glutSolidSphere(0.25, 12, 12)
    glPopMatrix()
    glPopMatrix()

def draw_complete_cannon(cannon_z, cannon_angle):
    glPushMatrix()
    glTranslatef(-20.0, -1.0, cannon_z)
    glRotatef(90, 0, 1, 0)
    draw_cannon_base()
    glPushMatrix()
    glTranslatef(0, -0.3, 0)
    draw_cannon_barrel(cannon_angle)
    glPopMatrix()
    glPopMatrix()

def calculate_aiming_point(cannon_z, cannon_angle, aiming_point):
    barrel_length = 2.5
    cannon_world_x = -20.0
    cannon_world_y = -1.3
    cannon_world_z = cannon_z
    barrel_tip_x = cannon_world_x + barrel_length * math.cos(math.radians(cannon_angle))
    barrel_tip_y = cannon_world_y + barrel_length * math.sin(math.radians(cannon_angle))
    barrel_tip_z = cannon_world_z
    aiming_distance = 30.0
    aiming_direction_x = math.cos(math.radians(cannon_angle))
    aiming_direction_y = math.sin(math.radians(cannon_angle))
    aiming_direction_z = 0
    aiming_point[0] = barrel_tip_x + aiming_direction_x * aiming_distance
    aiming_point[1] = barrel_tip_y + aiming_direction_y * aiming_distance
    aiming_point[2] = barrel_tip_z + aiming_direction_z * aiming_distance

def draw_aiming_system(show_aiming_line, cannon_z, cannon_angle, aiming_point):
    if not show_aiming_line:
        return
    glDisable(GL_LIGHTING)
    barrel_length = 2.5
    cannon_world_x = -20.0
    cannon_world_y = -1.3
    cannon_world_z = cannon_z
    barrel_tip_x = cannon_world_x + barrel_length * math.cos(math.radians(cannon_angle))
    barrel_tip_y = cannon_world_y + barrel_length * math.sin(math.radians(cannon_angle))
    barrel_tip_z = cannon_world_z
    glColor3f(1.0, 0.0, 0.0)
    glLineWidth(3.0)
    num_segments = 50
    for i in range(0, num_segments, 2):
        t1 = i / float(num_segments)
        t2 = min((i + 1) / float(num_segments), 1.0)
        x1 = barrel_tip_x + (aiming_point[0] - barrel_tip_x) * t1
        y1 = barrel_tip_y + (aiming_point[1] - barrel_tip_y) * t1
        z1 = barrel_tip_z + (aiming_point[2] - barrel_tip_z) * t1
        x2 = barrel_tip_x + (aiming_point[0] - barrel_tip_x) * t2
        y2 = barrel_tip_y + (aiming_point[1] - barrel_tip_y) * t2
        z2 = barrel_tip_z + (aiming_point[2] - barrel_tip_z) * t2
        glBegin(GL_LINES)
        glVertex3f(x1, y1, z1)
        glVertex3f(x2, y2, z2)
        glEnd()
    glPushMatrix()
    glTranslatef(aiming_point[0], aiming_point[1], aiming_point[2])
    pulse = 1.0 + 0.5 * math.sin(glutGet(GLUT_ELAPSED_TIME) * 0.005)
    size = 0.5 * pulse
    glColor3f(1.0, 1.0, 0.0)
    glLineWidth(4.0)
    glBegin(GL_LINES)
    glVertex3f(-size, 0, 0)
    glVertex3f(size, 0, 0)
    glVertex3f(0, -size, 0)
    glVertex3f(0, size, 0)
    glVertex3f(0, 0, -size)
    glVertex3f(0, 0, size)
    glEnd()
    glColor3f(1.0, 0.0, 0.0)
    glPointSize(10.0)
    glBegin(GL_POINTS)
    glVertex3f(0, 0, 0)
    glEnd()
    glPopMatrix()
    glEnable(GL_LIGHTING)

def move_cannon_up(cannon_z, CANNON_MAX_Z):
    new_z = cannon_z + 1.0
    if new_z <= CANNON_MAX_Z:
        return new_z
    return cannon_z

def move_cannon_down(cannon_z, CANNON_MIN_Z):
    new_z = cannon_z - 1.0
    if new_z >= CANNON_MIN_Z:
        return new_z
    return cannon_z

def tilt_cannon_up(cannon_angle, CANNON_MIN_ANGLE):
    new_angle = cannon_angle - 5.0
    if new_angle >= CANNON_MIN_ANGLE:
        return new_angle
    return cannon_angle

def tilt_cannon_down(cannon_angle, CANNON_MAX_ANGLE):
    new_angle = cannon_angle + 5.0
    if new_angle <= CANNON_MAX_ANGLE:
        return new_angle
    return cannon_angle
