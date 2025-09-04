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
    tip_x = cannon_world_x + barrel_length * math.cos(math.radians(cannon_angle))
    tip_y = cannon_world_y + barrel_length * math.sin(math.radians(cannon_angle))
    tip_z = cannon_world_z

    # Simulate projectile trajectory with gravity
    gravity = -0.015
    bullet_speed = 1.2
    vx = bullet_speed * math.cos(math.radians(cannon_angle))
    vy = bullet_speed * math.sin(math.radians(cannon_angle))

    # Find the point where bullet would hit ground (y = -1.0) or max distance
    current_x = tip_x
    current_y = tip_y
    current_z = tip_z
    current_vy = vy

    # Simulate trajectory until bullet hits ground or goes too far
    max_iterations = 200
    for i in range(max_iterations):
        current_x += vx
        current_y += current_vy
        current_z += 0  # No z movement
        current_vy += gravity

        # Check if bullet would hit ground
        if current_y <= -1.0:
            # Interpolate to find exact ground hit point
            overshoot = current_y - (-1.0)
            prev_y = current_y - current_vy
            fraction = overshoot / (prev_y - current_y)
            hit_x = current_x - vx * fraction
            hit_z = current_z
            aiming_point[0] = hit_x
            aiming_point[1] = -1.0
            aiming_point[2] = hit_z
            return

        # Stop if bullet goes too far
        if current_x > 25 or abs(current_z - cannon_world_z) > 20:
            aiming_point[0] = current_x
            aiming_point[1] = current_y
            aiming_point[2] = current_z
            return

    # Fallback
    aiming_point[0] = tip_x + vx * 20
    aiming_point[1] = tip_y + vy * 20
    aiming_point[2] = tip_z

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

    # Draw projectile trajectory with gravity
    gravity = -0.015
    bullet_speed = 1.2
    vx = bullet_speed * math.cos(math.radians(cannon_angle))
    vy = bullet_speed * math.sin(math.radians(cannon_angle))

    glColor3f(1.0, 0.0, 0.0)
    glLineWidth(3.0)
    glBegin(GL_LINE_STRIP)

    current_x = barrel_tip_x
    current_y = barrel_tip_y
    current_z = barrel_tip_z
    current_vy = vy

    # Draw trajectory points
    glVertex3f(current_x, current_y, current_z)

    max_iterations = 50
    for i in range(max_iterations):
        current_x += vx * 0.5  # Smaller steps for smoother curve
        current_y += current_vy * 0.5
        current_z += 0
        current_vy += gravity * 0.5

        glVertex3f(current_x, current_y, current_z)

        # Stop if bullet hits ground or goes too far
        if current_y <= -1.0 or current_x > 25 or abs(current_z - cannon_world_z) > 20:
            break

    glEnd()

    # Draw crosshair at aiming point
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
    new_angle = cannon_angle - 1.0  # Reduced from 5.0 to 1.0 for finer control
    if new_angle >= CANNON_MIN_ANGLE:
        return new_angle
    return cannon_angle

def tilt_cannon_down(cannon_angle, CANNON_MAX_ANGLE):
    new_angle = cannon_angle + 1.0  # Reduced from 5.0 to 1.0 for finer control
    if new_angle <= CANNON_MAX_ANGLE:
        return new_angle
    return cannon_angle
