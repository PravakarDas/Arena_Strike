from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math

run_time = 0.0

def init():
    glClearColor(0.05, 0.05, 0.05, 1)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 1.0, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)

def draw_sphere(radius):
    glutSolidSphere(radius, 16, 16)

def draw_cylinder(radius, height):
    quad = gluNewQuadric()
    gluCylinder(quad, radius, radius, height, 16, 16)

def draw_face():
    # Eyes
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(0.07 * side, 0.05, 0.22)
        glColor3f(0, 0, 0)
        draw_sphere(0.03)
        glPopMatrix()

    # Angry brows
    glColor3f(0.1, 0.1, 0.1)
    glBegin(GL_TRIANGLES)
    glVertex3f(-0.08, 0.12, 0.21)
    glVertex3f(-0.01, 0.09, 0.21)
    glVertex3f(-0.08, 0.09, 0.21)
    glVertex3f(0.08, 0.12, 0.21)
    glVertex3f(0.01, 0.09, 0.21)
    glVertex3f(0.08, 0.09, 0.21)
    glEnd()

    # Mouth
    glPushMatrix()
    glTranslatef(0, -0.1, 0.2)
    glColor3f(0.3, 0, 0)
    glScalef(0.1, 0.05, 0.01)
    glutSolidCube(1.0)
    glPopMatrix()

def draw_horn(side):
    glPushMatrix()
    glColor3f(0.9, 0.9, 0.9)
    glTranslatef(0.15 * side, 0.2, 0)
    glRotatef(-45 * side, 0, 0, 1)
    glRotatef(-70, 1, 0, 0)

    for i in range(3):
        draw_cylinder(0.03, 0.15)
        glTranslatef(0, 0, 0.15)
        glRotatef(20, 1, 0, 0)
    glPopMatrix()


    glPushMatrix()
    glColor3f(0.9, 0.9, 0.9)
    glTranslatef(0.15 * side, 0.2, 0)
    glRotatef(-45 * side, 0, 0, 1)
    glRotatef(-70, 1, 0, 0)

    for i in range(3):
        draw_cylinder(0.03, 0.15)
        glTranslatef(0, 0, 0.15)
        glRotatef(20, 1, 0, 0)
    glPopMatrix()

def draw_sword():
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.3, 0.15, 0)
    draw_cylinder(0.025, 0.2)
    glTranslatef(0, 0, 0.2)
    glColor3f(0.8, 0.8, 1.0)
    draw_cylinder(0.03, 0.8)
    glTranslatef(0, 0, 0.8)
    glutSolidCone(0.03, 0.2, 16, 16)
    glPopMatrix()

def draw_arm(side, t):
    swing = math.sin(t) * 30
    glPushMatrix()
    glTranslatef(0.25 * side, 1.1, 0)
    glRotatef(swing * side, 1, 0, 0)

    if side > 0:
        # Right arm: sword only (no arm parts)
        draw_sword()
    else:
        # Left arm: upper arm only (no forearm)
        glColor3f(0.6, 0.6, 0.6)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        draw_cylinder(0.08, 0.6)
        glTranslatef(0, 0, 0.6)
        draw_sphere(0.08)
        glPopMatrix()
        # Skipping forearm
        # glTranslatef(0, -0.6, 0)
        # glRotatef(-swing * 0.5 * side, 1, 0, 0)
        # glColor3f(0.5, 0.5, 0.5)
        # glPushMatrix()
        # glRotatef(-90, 1, 0, 0)
        # draw_cylinder(0.07, 0.5)
        # glPopMatrix()

    glPopMatrix()

def draw_leg(side, t):
    swing = math.sin(t + math.pi) * 30
    glPushMatrix()
    glTranslatef(0.18 * side, -0.05, 0)
    glRotatef(swing * side, 1, 0, 0)

    # Thigh
    # glColor3f(0.3, 0.3, 0.3)
    # glPushMatrix()
    # glRotatef(-90, 1, 0, 0)
    # draw_cylinder(0.1, 0.7)
    # glTranslatef(0, 0, 0.7)
    # draw_sphere(0.1)
    # glPopMatrix()

    # Knee & Shin
    glTranslatef(0, -0.7, 0)
    glRotatef(-swing * 0.5 * side, 1, 0, 0)
    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.09, 0.6)
    glPopMatrix()

    glPopMatrix()

def draw_stickman(t):
    # Torso
    glPushMatrix()
    glColor3f(0.4, 0.4, 0.4)
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.15, 1.2)
    glPopMatrix()

    # Head
    glPushMatrix()
    glColor3f(1.0, 0.8, 0.6)
    glTranslatef(0, 1.4, 0)
    draw_sphere(0.25)
    draw_face()
    draw_horn(1)   # Will be skipped
    draw_horn(-1)  # Left horn stays
    glPopMatrix()

    # Arms
    draw_arm(1, t)   # Right (sword only)
    draw_arm(-1, t)  # Left (upper arm only)

    # Legs
    draw_leg(1, t)
    draw_leg(-1, t)

def display():
    global run_time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(4, 2.5, 5, 0, 1, 0, 0, 1, 0)
    draw_stickman(run_time)
    glutSwapBuffers()

def idle():
    global run_time
    run_time += 0.01
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Running Stickman Soldier - Cleaned Up")
    init()
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == '__main__':
    main()
