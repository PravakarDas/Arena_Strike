from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
import random

# Ring data: list of (x, y, z, angle, rotation_speed)
ring_data = []
ring_count = 1000  # You can try 10_000 if your machine can handle it

angle = 0

def init():
    glClearColor(0.1, 0.1, 0.1, 1)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 1.0, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)

    generate_ring_data()

def generate_ring_data():
    """Randomly fill the box with ring positions and rotation speeds"""
    for _ in range(ring_count):
        x = random.uniform(-1.4, 1.4)
        y = random.uniform(-0.65, 0.65)
        z = random.uniform(-0.9, 0.9)
        angle = random.uniform(0, 360)
        speed = random.uniform(0.2, 2.0)
        ring_data.append([x, y, z, angle, speed])

def draw_box_wireframe():
    """Draws a hollow box using quads (6 sides)"""
    glColor3f(0.5, 0.25, 0.05)  # Brownish color
    x = 1.5
    y = 0.75
    z = 1.0

    # Bottom
    glBegin(GL_QUADS)
    glVertex3f(-x, -y, -z)
    glVertex3f(x, -y, -z)
    glVertex3f(x, -y, z)
    glVertex3f(-x, -y, z)
    glEnd()

    # Left
    glBegin(GL_QUADS)
    glVertex3f(-x, -y, -z)
    glVertex3f(-x, y, -z)
    glVertex3f(-x, y, z)
    glVertex3f(-x, -y, z)
    glEnd()

    # Right
    glBegin(GL_QUADS)
    glVertex3f(x, -y, -z)
    glVertex3f(x, y, -z)
    glVertex3f(x, y, z)
    glVertex3f(x, -y, z)
    glEnd()

    # Back
    glBegin(GL_QUADS)
    glVertex3f(-x, -y, -z)
    glVertex3f(-x, y, -z)
    glVertex3f(x, y, -z)
    glVertex3f(x, -y, -z)
    glEnd()

    # Front
    glBegin(GL_QUADS)
    glVertex3f(-x, -y, z)
    glVertex3f(-x, y, z)
    glVertex3f(x, y, z)
    glVertex3f(x, -y, z)
    glEnd()

def draw_lid():
    """Draws the open lid attached to the back"""
    glColor3f(0.4, 0.2, 0.05)
    glPushMatrix()
    glTranslatef(0, 0.75, -1.0)
    glRotatef(-60, 1, 0, 0)  # open backwards
    glTranslatef(0, 0, 1.0)
    glScalef(3.0, 0.1, 2.0)
    glutSolidCube(1.0)
    glPopMatrix()

def draw_ring(x, y, z, rotation_angle):
    """Draw a small golden spinning ring"""
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation_angle, 0, 1, 0)
    glColor3f(1.0, 0.84, 0.0)  # Gold color
    glutSolidTorus(0.025, 0.08, 8, 16)
    glPopMatrix()

def display():
    global angle
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(5 * math.sin(math.radians(angle)), 2.5, 5 * math.cos(math.radians(angle)),
              0, 0, 0,
              0, 1, 0)

    # Draw hollow box
    draw_box_wireframe()

    # Draw open lid
    draw_lid()

    # Draw spinning rings
    for i in range(ring_count):
        x, y, z, rot_angle, speed = ring_data[i]
        draw_ring(x, y, z, rot_angle)

    glutSwapBuffers()

def idle():
    global angle
    angle += 0.1
    if angle >= 360:
        angle -= 360

    # Update spin angles of rings
    for i in range(len(ring_data)):
        ring_data[i][3] += ring_data[i][4]  # Increase rotation angle by speed
        ring_data[i][3] %= 360

    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"3D Treasure Box Filled with Spinning Rings")
    init()
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == '__main__':
    main()
