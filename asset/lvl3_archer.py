from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
import random

run_time = 0.0
arrows = []  # List to store flying arrows
shoot_timer = 0.0
SHOOT_INTERVAL = 2.0  # Shoot every 2 seconds

class Arrow:
    def __init__(self, x, y, z, direction_x, direction_y, direction_z, speed=0.1):
        self.x = x
        self.y = y
        self.z = z
        self.dir_x = direction_x
        self.dir_y = direction_y
        self.dir_z = direction_z
        self.speed = speed
        self.lifetime = 0.0
        self.max_lifetime = 10.0  # Arrow disappears after 10 seconds
    
    def update(self, dt):
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed
        self.z += self.dir_z * self.speed
        self.lifetime += dt
        return self.lifetime < self.max_lifetime

def init():
    glClearColor(0.1, 0.15, 0.2, 1)  # Dark blue-gray background
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 1.0, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)

def draw_sphere(radius):
    glutSolidSphere(radius, 16, 16)

def draw_cylinder(radius, height):
    quad = gluNewQuadric()
    gluCylinder(quad, radius, radius, height, 16, 16)

def draw_cone(base_radius, height):
    glutSolidCone(base_radius, height, 16, 16)

def draw_face():
    """Draw archer face with focused expression"""
    # Eyes - more focused/determined look
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(0.07 * side, 0.05, 0.22)
        glColor3f(0, 0, 0)
        draw_sphere(0.025)
        
        # Eye pupils - looking forward with concentration
        glTranslatef(0, 0, 0.015)
        glColor3f(0.2, 0.4, 0.6)  # Blue eyes
        draw_sphere(0.015)
        glPopMatrix()

    # Determined brows
    glColor3f(0.15, 0.1, 0.05)
    glBegin(GL_TRIANGLES)
    glVertex3f(-0.09, 0.12, 0.21)
    glVertex3f(-0.02, 0.08, 0.21)
    glVertex3f(-0.09, 0.08, 0.21)
    glVertex3f(0.09, 0.12, 0.21)
    glVertex3f(0.02, 0.08, 0.21)
    glVertex3f(0.09, 0.08, 0.21)
    glEnd()

    # Mouth - slight grin
    glPushMatrix()
    glTranslatef(0, -0.08, 0.2)
    glColor3f(0.4, 0.2, 0.1)
    glScalef(0.08, 0.03, 0.01)
    glutSolidCube(1.0)
    glPopMatrix()

def draw_horn(side):
    """Draw curved horns - more elegant archer horns"""
    glPushMatrix()
    glColor3f(0.8, 0.7, 0.5)  # Ivory/bone color
    glTranslatef(0.12 * side, 0.18, 0.05)
    glRotatef(-30 * side, 0, 0, 1)
    glRotatef(-60, 1, 0, 0)

    # Horn with elegant curve
    for i in range(4):
        glPushMatrix()
        glTranslatef(0, 0, i * 0.12)
        glRotatef(15 * i, 1, 0, 0)  # Gradual curve
        draw_cylinder(0.025 - i * 0.003, 0.12)
        glPopMatrix()
        glTranslatef(0, 0, 0.12)
        glRotatef(15, 1, 0, 0)
    
    # Horn tip
    glColor3f(0.9, 0.8, 0.6)
    draw_cone(0.015, 0.08)
    glPopMatrix()

def draw_bow(draw_angle, t):
    """Draw the archer's bow with string"""
    glPushMatrix()
    
    # Bow position and rotation - point bow forward (positive Z)
    glRotatef(90, 0, 1, 0)  # Point bow forward
    glRotatef(draw_angle, 0, 0, 1)  # Drawing motion
    
    # Bow limbs (upper and lower)
    glColor3f(0.4, 0.25, 0.1)  # Dark wood
    
    # Upper limb
    glPushMatrix()
    glTranslatef(0, 0.4, 0)
    glRotatef(-10, 0, 0, 1)
    draw_cylinder(0.02, 0.4)
    glTranslatef(0, 0.4, 0)
    glColor3f(0.6, 0.4, 0.2)
    draw_cone(0.02, 0.05)
    glPopMatrix()
    
    # Lower limb
    glPushMatrix()
    glTranslatef(0, -0.4, 0)
    glRotatef(10, 0, 0, 1)
    draw_cylinder(0.02, 0.4)
    glTranslatef(0, -0.4, 0)
    glColor3f(0.6, 0.4, 0.2)
    draw_cone(0.02, 0.05)
    glPopMatrix()
    
    # Bow handle/grip
    glColor3f(0.3, 0.2, 0.1)
    draw_cylinder(0.025, 0.2)
    
    # Bow string
    glColor3f(0.9, 0.9, 0.8)
    glLineWidth(3.0)
    glBegin(GL_LINES)
    
    # String curve based on draw angle
    string_pull = draw_angle * 0.01
    glVertex3f(0, 0.8, 0)
    glVertex3f(-string_pull, 0, 0)
    glVertex3f(-string_pull, 0, 0)
    glVertex3f(0, -0.8, 0)
    glEnd()
    
    glPopMatrix()

def draw_quiver():
    """Draw quiver on the back"""
    glPushMatrix()
    glTranslatef(-0.2, 0.8, -0.3)  # Back position
    glRotatef(-15, 1, 0, 0)  # Slight angle
    
    # Quiver body
    glColor3f(0.3, 0.2, 0.1)  # Dark leather
    draw_cylinder(0.08, 0.6)
    
    # Quiver bottom
    glColor3f(0.25, 0.15, 0.08)
    draw_cone(0.08, 0.1)
    
    # Arrow fletching visible at top
    glTranslatef(0, 0, 0.6)
    for i in range(3):
        glPushMatrix()
        glRotatef(120 * i, 0, 0, 1)
        glTranslatef(0.05, 0, 0)
        glColor3f(0.8, 0.2, 0.2)  # Red fletching
        glScalef(0.02, 0.08, 0.02)
        glutSolidCube(1.0)
        glPopMatrix()
    
    glPopMatrix()

def draw_arrow_in_hand(draw_progress):
    """Draw arrow being drawn in bow"""
    if draw_progress < 0.5:  # Only draw arrow when pulling back
        return
        
    glPushMatrix()
    glRotatef(90, 0, 1, 0)  # Point arrow forward
    
    # Arrow shaft
    pull_distance = (draw_progress - 0.5) * 2.0 * 0.3  # Max pull distance
    glTranslatef(pull_distance, 0, 0)  # Pull back along X axis
    
    glColor3f(0.6, 0.4, 0.2)  # Wood shaft
    draw_cylinder(0.008, 0.8)
    
    # Arrow head
    glTranslatef(0, 0, 0.8)
    glColor3f(0.7, 0.7, 0.8)  # Metal point
    draw_cone(0.015, 0.06)
    
    # Arrow fletching
    glTranslatef(0, 0, -0.8)
    for i in range(3):
        glPushMatrix()
        glRotatef(120 * i, 0, 0, 1)
        glTranslatef(0.01, 0, 0)
        glColor3f(0.2, 0.8, 0.2)  # Green fletching
        glScalef(0.015, 0.05, 0.015)
        glutSolidCube(1.0)
        glPopMatrix()
    
    glPopMatrix()

def shoot_arrow():
    """Create a new arrow"""
    global arrows
    
    # Arrow starting position (from bow) - in front of archer
    start_x, start_y, start_z = 0, 1.5, 0.8
    
    # Random target direction (mostly forward with some variation)
    angle = random.uniform(-30, 30)  # degrees
    elevation = random.uniform(-15, 15)  # degrees
    
    # Shoot forward (positive Z direction)
    dir_x = math.sin(math.radians(angle)) * math.cos(math.radians(elevation))
    dir_y = math.sin(math.radians(elevation))
    dir_z = math.cos(math.radians(angle)) * math.cos(math.radians(elevation))
    
    arrow = Arrow(start_x, start_y, start_z, dir_x, dir_y, dir_z, 0.15)
    arrows.append(arrow)

def draw_flying_arrow(arrow):
    """Draw a flying arrow"""
    glPushMatrix()
    glTranslatef(arrow.x, arrow.y, arrow.z)
    
    # Rotate arrow to face direction of travel
    angle_y = math.degrees(math.atan2(arrow.dir_x, arrow.dir_z))
    angle_x = math.degrees(math.atan2(-arrow.dir_y, math.sqrt(arrow.dir_x**2 + arrow.dir_z**2)))
    
    glRotatef(angle_y, 0, 1, 0)
    glRotatef(angle_x, 1, 0, 0)
    
    # Arrow shaft
    glColor3f(0.6, 0.4, 0.2)
    draw_cylinder(0.008, 0.6)
    
    # Arrow head
    glPushMatrix()
    glTranslatef(0, 0, 0.6)
    glColor3f(0.7, 0.7, 0.8)
    draw_cone(0.015, 0.05)
    glPopMatrix()
    
    # Arrow fletching
    for i in range(3):
        glPushMatrix()
        glRotatef(120 * i, 0, 0, 1)
        glTranslatef(0.01, 0, -0.05)
        glColor3f(0.2, 0.8, 0.2)
        glScalef(0.015, 0.04, 0.015)
        glutSolidCube(1.0)
        glPopMatrix()
    
    glPopMatrix()

def draw_arm(side, t, is_drawing_bow):
    """Draw archer arms with bow drawing motion"""
    if side > 0:  # Right arm - holds bow
        glPushMatrix()
        glTranslatef(0.25 * side, 1.1, 0)
        glRotatef(90, 0, 1, 0)   # Point arm forward to hold bow
        glRotatef(10, 1, 0, 0)   # Slight upward angle
        
        # Upper arm
        glColor3f(0.6, 0.5, 0.4)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        draw_cylinder(0.08, 0.6)
        glTranslatef(0, 0, 0.6)
        draw_sphere(0.08)  # Elbow joint
        glPopMatrix()
        
        # Forearm extended holding bow
        glTranslatef(0, -0.6, 0)
        glRotatef(-20, 1, 0, 0)
        glColor3f(0.55, 0.45, 0.35)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        draw_cylinder(0.07, 0.5)
        glPopMatrix()
        
        # Draw bow in right hand
        glTranslatef(0, -0.4, 0)
        draw_angle = 0
        if is_drawing_bow:
            draw_angle = math.sin(t * 2) * 15
        draw_bow(draw_angle, t)
        
        glPopMatrix()
        
    else:  # Left arm - draws bowstring
        draw_cycle = t * 2
        draw_progress = (math.sin(draw_cycle) + 1) / 2  # 0 to 1
        
        glPushMatrix()
        glTranslatef(0.25 * side, 1.1, 0)
        
        # Drawing motion - pull back when drawing
        if draw_progress > 0.3:
            pull_back = (draw_progress - 0.3) * 0.5
            glRotatef(-pull_back * 60, 0, 1, 0)  # Pull arm back
            glTranslatef(0, 0, -pull_back * 0.3)
        
        glRotatef(20, 1, 0, 0)
        
        # Upper arm
        glColor3f(0.6, 0.5, 0.4)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        draw_cylinder(0.08, 0.6)
        glTranslatef(0, 0, 0.6)
        draw_sphere(0.08)
        glPopMatrix()
        
        # Forearm
        glTranslatef(0, -0.6, 0)
        elbow_angle = -40 if draw_progress > 0.3 else -70
        glRotatef(elbow_angle, 1, 0, 0)
        glColor3f(0.55, 0.45, 0.35)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        draw_cylinder(0.07, 0.5)
        glPopMatrix()
        
        # Draw arrow in drawing hand
        if draw_progress > 0.3:
            glTranslatef(0, -0.4, 0)
            draw_arrow_in_hand(draw_progress)
        
        glPopMatrix()

def draw_leg(side, t):
    """Draw legs with slight movement"""
    sway = math.sin(t * 0.5 + side) * 5  # Gentle swaying
    glPushMatrix()
    glTranslatef(0.18 * side, -0.05, 0)
    glRotatef(sway * side, 1, 0, 0)

    # Thigh
    glColor3f(0.4, 0.35, 0.3)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.1, 0.7)
    glTranslatef(0, 0, 0.7)
    draw_sphere(0.1)  # Knee joint
    glPopMatrix()

    # Shin
    glTranslatef(0, -0.7, 0)
    glRotatef(-sway * 0.3 * side, 1, 0, 0)
    glColor3f(0.35, 0.3, 0.25)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.09, 0.6)
    glPopMatrix()

    glPopMatrix()

def draw_archer(t):
    """Draw complete archer stickman"""
    # Determine if currently drawing bow
    draw_cycle = t * 2
    is_drawing = (math.sin(draw_cycle) > -0.5)
    
    # Torso
    glPushMatrix()
    glColor3f(0.5, 0.4, 0.3)  # Leather armor color
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.15, 1.2)
    
    # Torso armor details
    glColor3f(0.4, 0.3, 0.2)
    for i in range(3):
        glPushMatrix()
        glTranslatef(0, 0, 0.3 + i * 0.3)
        glutSolidTorus(0.02, 0.16, 8, 16)
        glPopMatrix()
    glPopMatrix()

    # Head
    glPushMatrix()
    glColor3f(1.0, 0.8, 0.6)  # Skin color
    glTranslatef(0, 1.4, 0)
    draw_sphere(0.25)
    draw_face()
    
    # Draw both horns
    draw_horn(1)   # Right horn
    draw_horn(-1)  # Left horn
    glPopMatrix()

    # Arms with bow mechanics
    draw_arm(1, t, is_drawing)   # Right arm (bow holder)
    draw_arm(-1, t, is_drawing)  # Left arm (string puller)

    # Legs
    draw_leg(1, t)
    draw_leg(-1, t)
    
    # Quiver on back
    draw_quiver()

def display():
    global run_time, shoot_timer, arrows
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Camera position
    gluLookAt(4, 2.5, 5, 0, 1, 0, 0, 1, 0)
    
    # Draw archer
    draw_archer(run_time)
    
    # Draw all flying arrows
    for arrow in arrows:
        draw_flying_arrow(arrow)
    
    glutSwapBuffers()

def idle():
    global run_time, shoot_timer, arrows
    dt = 0.02
    run_time += dt
    shoot_timer += dt
    
    # Shoot arrows periodically
    if shoot_timer >= SHOOT_INTERVAL:
        shoot_arrow()
        shoot_timer = 0.0
    
    # Update arrows
    arrows = [arrow for arrow in arrows if arrow.update(dt)]
    
    glutPostRedisplay()

def keyboard(key, x, y):
    """Handle keyboard input"""
    if key == b'q' or key == b'Q':
        sys.exit()
    elif key == b' ':
        # Manual shoot
        shoot_arrow()
    elif key == b'r' or key == b'R':
        # Clear all arrows
        global arrows
        arrows = []

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Horned Archer - Continuous Shooting - SPACE to shoot, R to clear arrows")
    init()
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    
    print("Controls:")
    print("SPACE - Manual arrow shoot")
    print("R - Clear all arrows")
    print("Q - Quit")
    print("The archer automatically shoots arrows every 2 seconds!")
    
    glutMainLoop()

if __name__ == '__main__':
    main()