from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
import random

run_time = 0.0

def init():
    glClearColor(0.05, 0.15, 0.05, 1)  # Dark green background for forest feel
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 1.0, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)

def draw_sphere(radius):
    glutSolidSphere(radius, 16, 16)

def draw_cylinder(radius, height):
    quad = gluNewQuadric()
    gluCylinder(quad, radius, radius, height, 16, 16)

def draw_ellipsoid(rx, ry, rz):
    """Draw an ellipsoid by scaling a sphere"""
    glPushMatrix()
    glScalef(rx, ry, rz)
    draw_sphere(1.0)
    glPopMatrix()

def draw_face():
    """Draw bug face with compound eyes and mandibles"""
    # Large compound eyes
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(0.12 * side, 0.08, 0.18)
        glColor3f(0.1, 0.1, 0.1)  # Dark compound eyes
        draw_ellipsoid(0.08, 0.1, 0.08)
        
        # Eye shine
        glTranslatef(0.02 * side, 0.03, 0.05)
        glColor3f(0.3, 0.6, 0.3)  # Green shine
        draw_sphere(0.02)
        glPopMatrix()

    # Mandibles
    glColor3f(0.2, 0.1, 0.05)  # Brown mandibles
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(0.05 * side, -0.05, 0.2)
        glRotatef(20 * side, 0, 0, 1)
        glScalef(0.03, 0.08, 0.02)
        glutSolidCube(1.0)
        glPopMatrix()

def draw_feeler(side, t):
    """Draw antennae/feelers that move"""
    sway = math.sin(t * 2 + side) * 15
    glPushMatrix()
    glTranslatef(0.08 * side, 0.15, 0.1)
    glRotatef(sway, 1, 0, 0)
    glRotatef(10 * side, 0, 0, 1)
    
    # Feeler segments
    glColor3f(0.3, 0.2, 0.1)
    for i in range(4):
        glPushMatrix()
        glTranslatef(0, 0, 0.08 * i)
        glRotatef(sway * 0.3, 1, 0, 0)
        draw_cylinder(0.01, 0.08)
        
        # Feeler tip
        if i == 3:
            glTranslatef(0, 0, 0.08)
            glColor3f(0.4, 0.3, 0.1)
            draw_sphere(0.02)
        glPopMatrix()
    
    glPopMatrix()

def draw_wing(side, t):
    """Draw translucent flying wings"""
    wing_beat = math.sin(t * 8) * 45  # Fast wing beating
    glPushMatrix()
    glTranslatef(0.2 * side, 0.3, -0.1)
    glRotatef(wing_beat * side, 0, 0, 1)
    glRotatef(20, 1, 0, 0)  # Slight forward tilt
    
    # Wing membrane - translucent
    glColor4f(0.8, 0.9, 0.6, 0.6)  # Semi-transparent yellow-green
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Wing shape using quads
    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0)
    glVertex3f(0.4 * side, 0.2, 0)
    glVertex3f(0.5 * side, 0.6, 0)
    glVertex3f(0.1 * side, 0.4, 0)
    glEnd()
    
    # Wing veins
    glDisable(GL_BLEND)
    glColor3f(0.2, 0.3, 0.1)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0.4 * side, 0.2, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0.5 * side, 0.6, 0)
    glVertex3f(0.1 * side, 0.2, 0)
    glVertex3f(0.3 * side, 0.4, 0)
    glEnd()
    
    glPopMatrix()

def draw_leg(side, position, t):
    """Draw insect legs - 3 per side, each with 3 segments"""
    # position: 0=front, 1=middle, 2=back
    leg_swing = math.sin(t * 3 + position + side) * 25
    leg_lift = math.sin(t * 6 + position * 2) * 10
    
    glPushMatrix()
    
    # Position legs along the body
    y_offset = 0.1 - position * 0.15  # front higher, back lower
    z_offset = position * 0.3 - 0.3   # spread along body length
    
    glTranslatef(0.18 * side, y_offset, z_offset)
    glRotatef(leg_swing * side, 1, 0, 0)  # Forward/back swing
    glRotatef(leg_lift, 0, 0, 1)          # Up/down movement
    glRotatef(30 * side + position * 10, 0, 1, 0)  # Spread angle
    
    # Leg colors - darker for joints
    glColor3f(0.2, 0.15, 0.1)
    
    # Femur (thigh)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.02, 0.15)
    glTranslatef(0, 0, 0.15)
    draw_sphere(0.025)  # Joint
    glPopMatrix()
    
    # Tibia (shin)
    glTranslatef(0, -0.15, 0)
    glRotatef(-leg_swing * 0.3, 1, 0, 0)
    glColor3f(0.25, 0.2, 0.1)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.018, 0.12)
    glTranslatef(0, 0, 0.12)
    draw_sphere(0.02)  # Joint
    glPopMatrix()
    
    # Tarsus (foot)
    glTranslatef(0, -0.12, 0)
    glRotatef(-leg_swing * 0.2, 1, 0, 0)
    glColor3f(0.3, 0.25, 0.15)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.015, 0.08)
    # Foot tip
    glTranslatef(0, 0, 0.08)
    glColor3f(0.4, 0.3, 0.2)
    draw_sphere(0.018)
    glPopMatrix()
    
    glPopMatrix()

def draw_bug(t):
    """Draw complete bug similar to stickman structure"""
    
    # Main body (thorax + abdomen)
    glPushMatrix()
    
    # Thorax (chest area)
    glColor3f(0.4, 0.3, 0.2)  # Brown thorax
    glPushMatrix()
    glTranslatef(0, 0.2, 0)
    draw_ellipsoid(0.15, 0.12, 0.25)
    glPopMatrix()
    
    # Abdomen (back part)
    glColor3f(0.3, 0.4, 0.2)  # Green-brown abdomen
    glPushMatrix()
    glTranslatef(0, 0, -0.4)
    draw_ellipsoid(0.12, 0.1, 0.3)
    
    # Abdomen stripes
    glColor3f(0.2, 0.3, 0.1)
    for i in range(3):
        glPushMatrix()
        glTranslatef(0, 0.05, -0.2 + i * 0.15)
        glScalef(1.1, 0.3, 0.05)
        glutSolidCube(0.2)
        glPopMatrix()
    glPopMatrix()
    
    # Head
    glPushMatrix()
    glColor3f(0.5, 0.4, 0.3)  # Lighter brown head
    glTranslatef(0, 0.3, 0.3)
    draw_ellipsoid(0.12, 0.15, 0.12)
    draw_face()
    
    # Feelers/Antennae
    draw_feeler(1, t)   # Right feeler
    draw_feeler(-1, t)  # Left feeler
    glPopMatrix()
    
    # Wings
    draw_wing(1, t)   # Right wing
    draw_wing(-1, t)  # Left wing
    
    # All 6 legs (3 per side)
    for position in range(3):  # front, middle, back
        draw_leg(1, position, t)   # Right side legs
        draw_leg(-1, position, t)  # Left side legs
    
    glPopMatrix()

def display():
    global run_time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Camera orbits around the bug
    cam_angle = run_time * 0.5
    gluLookAt(4 * math.sin(cam_angle), 2.5, 4 * math.cos(cam_angle),
              0, 0, 0,
              0, 1, 0)
    
    # Add some floating motion to the bug
    hover = math.sin(run_time * 0.8) * 0.3
    glTranslatef(0, hover, 0)
    
    draw_bug(run_time)
    glutSwapBuffers()

def idle():
    global run_time
    run_time += 0.02
    glutPostRedisplay()

def keyboard(key, x, y):
    """Handle keyboard input"""
    if key == b'q' or key == b'Q':
        sys.exit()
    elif key == b' ':
        global run_time
        run_time = 0.0  # Reset animation

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Flying Bug - 6 Legs & 2 Feelers - Press SPACE to reset, Q to quit")
    init()
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    
    print("Controls:")
    print("SPACE - Reset animation")
    print("Q - Quit")
    print("Watch the bug fly with beating wings, moving feelers, and walking legs!")
    
    glutMainLoop()

if __name__ == '__main__':
    main()