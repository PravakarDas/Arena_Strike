from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
import random

# Cannon state variables
cannon_x = 0.0  # Horizontal position
cannon_angle = 45.0  # Vertical angle (0-90 degrees)
target_pos = [8.0, 2.0, 0.0]  # Fixed target position
show_aiming_line = False
aiming_point = [0.0, 0.0, 0.0]

# Screen boundaries
CANNON_MIN_X = -8.0
CANNON_MAX_X = 8.0
CANNON_MIN_ANGLE = 0.0
CANNON_MAX_ANGLE = 90.0

def init():
    glClearColor(0.3, 0.6, 0.9, 1.0)  # Sky blue background
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Setup lighting
    light_pos = [10.0, 10.0, 10.0, 1.0]
    light_ambient = [0.3, 0.3, 0.3, 1.0]
    light_diffuse = [0.8, 0.8, 0.8, 1.0]
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, 1.33, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

def draw_sphere(radius):
    glutSolidSphere(radius, 16, 16)

def draw_cylinder(radius, height):
    quad = gluNewQuadric()
    gluCylinder(quad, radius, radius, height, 16, 1)

def draw_cannon_base():
    """Draw the cannon base/chassis"""
    glColor3f(0.2, 0.2, 0.2)  # Dark gray metal
    
    # Main base platform
    glPushMatrix()
    glTranslatef(0, -0.8, 0)
    glScalef(1.5, 0.3, 1.0)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Wheels
    glColor3f(0.1, 0.1, 0.1)  # Black wheels
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(0.8 * side, -0.8, 0.6)
        glRotatef(90, 0, 1, 0)
        draw_cylinder(0.4, 0.2)
        
        # Wheel spokes
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

def draw_cannon_barrel():
    """Draw the tilting cannon barrel"""
    glPushMatrix()
    glRotatef(cannon_angle, 1, 0, 0)  # Tilt based on angle
    
    # Barrel
    glColor3f(0.15, 0.15, 0.2)  # Dark blue-gray metal
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.15, 2.5)
    
    # Barrel end cap
    glTranslatef(0, 0, 2.5)
    glColor3f(0.1, 0.1, 0.1)
    draw_cylinder(0.17, 0.1)
    glPopMatrix()
    
    # Cannon pivot/mount
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(0, 0, -0.3)
    draw_sphere(0.25)
    glPopMatrix()
    
    glPopMatrix()

def draw_complete_cannon():
    """Draw the complete cannon at current position"""
    glPushMatrix()
    glTranslatef(cannon_x, 0, 0)  # Move cannon left/right
    
    draw_cannon_base()
    
    # Barrel mount
    glPushMatrix()
    glTranslatef(0, -0.3, 0)
    draw_cannon_barrel()
    glPopMatrix()
    
    glPopMatrix()

def calculate_aiming_point():
    """Calculate where the aiming line should point based on cannon angle and position"""
    global aiming_point
    
    # Calculate barrel tip position
    barrel_length = 2.5
    barrel_tip_x = cannon_x
    barrel_tip_y = -0.3 + barrel_length * math.sin(math.radians(cannon_angle))
    barrel_tip_z = barrel_length * math.cos(math.radians(cannon_angle))
    
    # Project aiming line towards target
    # Calculate direction from barrel tip to target
    dx = target_pos[0] - barrel_tip_x
    dy = target_pos[1] - barrel_tip_y
    dz = target_pos[2] - barrel_tip_z
    
    # Normalize direction
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    if length > 0:
        dx /= length
        dy /= length
        dz /= length
    
    # Extend aiming line
    aiming_distance = 15.0
    aiming_point[0] = barrel_tip_x + dx * aiming_distance
    aiming_point[1] = barrel_tip_y + dy * aiming_distance
    aiming_point[2] = barrel_tip_z + dz * aiming_distance

def draw_aiming_line():
    """Draw the aiming line when C key is pressed"""
    if not show_aiming_line:
        return
    
    # Calculate barrel tip position
    barrel_length = 2.5
    barrel_tip_x = cannon_x
    barrel_tip_y = -0.3 + barrel_length * math.sin(math.radians(cannon_angle))
    barrel_tip_z = barrel_length * math.cos(math.radians(cannon_angle))
    
    glDisable(GL_LIGHTING)
    
    # Main aiming line
    glColor3f(1.0, 0.0, 0.0)  # Red aiming line
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glVertex3f(barrel_tip_x, barrel_tip_y, barrel_tip_z)
    glVertex3f(aiming_point[0], aiming_point[1], aiming_point[2])
    glEnd()
    
    # Aiming point indicator
    glPushMatrix()
    glTranslatef(aiming_point[0], aiming_point[1], aiming_point[2])
    glColor3f(1.0, 1.0, 0.0)  # Yellow indicator
    draw_sphere(0.2)
    
    # Pulsing effect
    pulse = 1.0 + 0.3 * math.sin(glutGet(GLUT_ELAPSED_TIME) * 0.01)
    glColor3f(1.0, 0.5, 0.0)  # Orange outer glow
    draw_sphere(0.3 * pulse)
    glPopMatrix()
    
    # Distance markers along the line
    glColor3f(0.8, 0.8, 0.0)  # Yellow markers
    for i in range(1, 8):
        t = i / 8.0
        marker_x = barrel_tip_x + (aiming_point[0] - barrel_tip_x) * t
        marker_y = barrel_tip_y + (aiming_point[1] - barrel_tip_y) * t
        marker_z = barrel_tip_z + (aiming_point[2] - barrel_tip_z) * t
        
        glPushMatrix()
        glTranslatef(marker_x, marker_y, marker_z)
        draw_sphere(0.05)
        glPopMatrix()
    
    glEnable(GL_LIGHTING)

def draw_target():
    """Draw the target"""
    glPushMatrix()
    glTranslatef(target_pos[0], target_pos[1], target_pos[2])
    
    # Target post
    glColor3f(0.4, 0.2, 0.1)  # Brown wooden post
    glPushMatrix()
    glTranslatef(0, -1.5, 0)
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.05, 3.0)
    glPopMatrix()
    
    # Target board
    glColor3f(1.0, 1.0, 1.0)  # White background
    glPushMatrix()
    glScalef(0.8, 0.8, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Target rings
    colors = [[1.0, 0.0, 0.0], [1.0, 1.0, 1.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]]
    radii = [0.6, 0.45, 0.3, 0.15]
    
    for i, (color, radius) in enumerate(zip(colors, radii)):
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(0, 0, 0.06 + i * 0.01)
        glRotatef(90, 0, 1, 0)
        draw_cylinder(radius, 0.02)
        glPopMatrix()
    
    glPopMatrix()

def draw_ground():
    """Draw ground plane with grid pattern"""
    # Main ground
    glColor3f(0.2, 0.5, 0.2)  # Green grass
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-20, -2, -10)
    glVertex3f(20, -2, -10)
    glVertex3f(20, -2, 20)
    glVertex3f(-20, -2, 20)
    glEnd()
    
    # Grid lines for depth perception
    glDisable(GL_LIGHTING)
    glColor3f(0.3, 0.6, 0.3)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    for i in range(-20, 21, 2):
        glVertex3f(i, -1.98, -10)
        glVertex3f(i, -1.98, 20)
        glVertex3f(-20, -1.98, i)
        glVertex3f(20, -1.98, i)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_ui_info():
    """Draw UI information on screen"""
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    # Set up 2D projection for UI
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 800, 0, 600, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Display cannon status
    glColor3f(1.0, 1.0, 1.0)
    
    # Status text would go here if we had text rendering
    # For now, we'll use visual indicators
    
    # Cannon position indicator (horizontal bar)
    glColor3f(0.0, 1.0, 0.0)
    cannon_ui_x = 400 + (cannon_x / 16.0) * 300  # Scale to UI
    glBegin(GL_QUADS)
    glVertex2f(cannon_ui_x - 5, 550)
    glVertex2f(cannon_ui_x + 5, 550)
    glVertex2f(cannon_ui_x + 5, 570)
    glVertex2f(cannon_ui_x - 5, 570)
    glEnd()
    
    # Angle indicator (arc)
    glColor3f(1.0, 0.0, 0.0)
    angle_ui = (cannon_angle / 90.0) * 180  # Scale to UI
    glBegin(GL_LINES)
    for i in range(int(angle_ui)):
        angle_rad = math.radians(i)
        x1 = 50 + 30 * math.cos(angle_rad)
        y1 = 50 + 30 * math.sin(angle_rad)
        x2 = 50 + 35 * math.cos(angle_rad)
        y2 = 50 + 35 * math.sin(angle_rad)
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
    glEnd()
    
    # Restore 3D projection
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

def calculate_trajectory_point():
    """Calculate where the aiming line intersects based on cannon angle and position"""
    global aiming_point
    
    # Barrel length and position
    barrel_length = 2.0
    
    # Calculate barrel tip position
    barrel_tip_x = cannon_x
    barrel_tip_y = barrel_length * math.sin(math.radians(cannon_angle))
    barrel_tip_z = barrel_length * math.cos(math.radians(cannon_angle))
    
    # Calculate direction vector from barrel to target
    dx = target_pos[0] - barrel_tip_x
    dy = target_pos[1] - barrel_tip_y
    dz = target_pos[2] - barrel_tip_z
    
    # Normalize direction
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    if length > 0:
        dx /= length
        dy /= length
        dz /= length
    
    # Project aiming point along barrel direction
    aiming_distance = 10.0
    barrel_dir_x = 0  # Barrel points straight ahead in X
    barrel_dir_y = math.sin(math.radians(cannon_angle))
    barrel_dir_z = math.cos(math.radians(cannon_angle))
    
    aiming_point[0] = barrel_tip_x + barrel_dir_x * aiming_distance
    aiming_point[1] = barrel_tip_y + barrel_dir_y * aiming_distance
    aiming_point[2] = barrel_tip_z + barrel_dir_z * aiming_distance

def draw_cannon():
    """Draw the main cannon structure"""
    glPushMatrix()
    glTranslatef(cannon_x, 0, 0)  # Position cannon horizontally
    
    # Cannon base
    glColor3f(0.3, 0.3, 0.3)  # Gray base
    glPushMatrix()
    glTranslatef(0, -0.5, 0)
    glScalef(1.2, 0.4, 0.8)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Cannon mount/pivot
    glColor3f(0.25, 0.25, 0.25)
    glPushMatrix()
    glTranslatef(0, -0.1, 0)
    draw_sphere(0.3)
    glPopMatrix()
    
    # Cannon barrel (tilts with angle)
    glPushMatrix()
    glTranslatef(0, -0.1, 0)
    glRotatef(cannon_angle, 1, 0, 0)  # Tilt up/down
    
    # Main barrel
    glColor3f(0.2, 0.2, 0.3)  # Dark metal barrel
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.12, 2.0)
    
    # Barrel muzzle
    glTranslatef(0, 0, 2.0)
    glColor3f(0.1, 0.1, 0.1)
    draw_cylinder(0.14, 0.1)
    glPopMatrix()
    
    # Barrel reinforcement bands
    glColor3f(0.15, 0.15, 0.15)
    for i in range(4):
        glPushMatrix()
        glTranslatef(0, 0, 0.4 + i * 0.4)
        glRotatef(-90, 1, 0, 0)
        draw_cylinder(0.13, 0.05)
        glPopMatrix()
    
    glPopMatrix()
    glPopMatrix()

def draw_aiming_system():
    """Draw the aiming line and indicators when active"""
    if not show_aiming_line:
        return
    
    glDisable(GL_LIGHTING)
    
    # Calculate barrel tip position
    barrel_length = 2.0
    barrel_tip_x = cannon_x
    barrel_tip_y = -0.1 + barrel_length * math.sin(math.radians(cannon_angle))
    barrel_tip_z = barrel_length * math.cos(math.radians(cannon_angle))
    
    # Aiming line from barrel to aiming point
    glColor3f(1.0, 0.2, 0.2)  # Bright red
    glLineWidth(4.0)
    glBegin(GL_LINES)
    glVertex3f(barrel_tip_x, barrel_tip_y, barrel_tip_z)
    glVertex3f(aiming_point[0], aiming_point[1], aiming_point[2])
    glEnd()
    
    # Aiming point marker
    glPushMatrix()
    glTranslatef(aiming_point[0], aiming_point[1], aiming_point[2])
    
    # Pulsing crosshair
    pulse = 1.0 + 0.5 * math.sin(glutGet(GLUT_ELAPSED_TIME) * 0.005)
    size = 0.3 * pulse
    
    glColor3f(1.0, 1.0, 0.0)  # Yellow crosshair
    glLineWidth(3.0)
    glBegin(GL_LINES)
    # Horizontal line
    glVertex3f(-size, 0, 0)
    glVertex3f(size, 0, 0)
    # Vertical line
    glVertex3f(0, -size, 0)
    glVertex3f(0, size, 0)
    glEnd()
    
    # Center dot
    glColor3f(1.0, 0.0, 0.0)
    glPointSize(8.0)
    glBegin(GL_POINTS)
    glVertex3f(0, 0, 0)
    glEnd()
    
    glPopMatrix()
    
    # Line to actual target (dotted line)
    glColor3f(0.0, 1.0, 0.0)  # Green line to target
    glLineWidth(2.0)
    glEnable(GL_LINE_STIPPLE)
    glLineStipple(2, 0xAAAA)  # Dotted pattern
    glBegin(GL_LINES)
    glVertex3f(barrel_tip_x, barrel_tip_y, barrel_tip_z)
    glVertex3f(target_pos[0], target_pos[1], target_pos[2])
    glEnd()
    glDisable(GL_LINE_STIPPLE)
    
    glEnable(GL_LIGHTING)

def draw_trajectory_arc():
    """Draw predicted trajectory arc when aiming"""
    if not show_aiming_line:
        return
    
    glDisable(GL_LIGHTING)
    glColor3f(0.0, 0.8, 1.0)  # Cyan trajectory
    glLineWidth(2.0)
    
    # Calculate initial velocity components
    initial_speed = 15.0
    vx = 0  # No horizontal velocity component
    vy = initial_speed * math.sin(math.radians(cannon_angle))
    vz = initial_speed * math.cos(math.radians(cannon_angle))
    
    # Starting position
    start_x = cannon_x
    start_y = -0.1 + 2.0 * math.sin(math.radians(cannon_angle))
    start_z = 2.0 * math.cos(math.radians(cannon_angle))
    
    # Draw trajectory points
    glBegin(GL_LINE_STRIP)
    for t in range(0, 200):  # 2 seconds in 0.01s steps
        time = t * 0.01
        
        # Physics calculation
        x = start_x + vx * time
        y = start_y + vy * time - 0.5 * 9.8 * time * time  # gravity
        z = start_z + vz * time
        
        if y < -2:  # Stop when hits ground
            break
            
        glVertex3f(x, y, z)
    glEnd()
    
    glEnable(GL_LIGHTING)

def move_cannon_left():
    """Move cannon left with boundary checking"""
    global cannon_x
    new_x = cannon_x - 0.5
    if new_x >= CANNON_MIN_X:
        cannon_x = new_x
        if show_aiming_line:
            calculate_aiming_point()

def move_cannon_right():
    """Move cannon right with boundary checking"""
    global cannon_x
    new_x = cannon_x + 0.5
    if new_x <= CANNON_MAX_X:
        cannon_x = new_x
        if show_aiming_line:
            calculate_aiming_point()

def tilt_cannon_up():
    """Tilt cannon barrel up with angle limits"""
    global cannon_angle
    new_angle = cannon_angle + 5.0
    if new_angle <= CANNON_MAX_ANGLE:
        cannon_angle = new_angle
        if show_aiming_line:
            calculate_aiming_point()

def tilt_cannon_down():
    """Tilt cannon barrel down with angle limits"""
    global cannon_angle
    new_angle = cannon_angle - 5.0
    if new_angle >= CANNON_MIN_ANGLE:
        cannon_angle = new_angle
        if show_aiming_line:
            calculate_aiming_point()

def toggle_aiming():
    """Toggle aiming line display and calculate aiming point"""
    global show_aiming_line
    show_aiming_line = not show_aiming_line
    if show_aiming_line:
        calculate_aiming_point()
        print(f"AIMING: Cannon at ({cannon_x:.1f}, angle: {cannon_angle:.1f}°)")
        print(f"Target at ({target_pos[0]:.1f}, {target_pos[1]:.1f}, {target_pos[2]:.1f})")
    else:
        print("Aiming OFF")

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Camera position - side view for better cannon control
    gluLookAt(0, 3, 15,  # Eye position
              0, 0, 0,   # Look at origin
              0, 1, 0)   # Up vector
    
    # Draw scene
    draw_ground()
    draw_complete_cannon()
    draw_target()
    draw_aiming_system()
    draw_trajectory_arc()
    draw_ui_info()
    
    glutSwapBuffers()

def idle():
    glutPostRedisplay()

def keyboard(key, x, y):
    """Handle keyboard input"""
    if key == b'q' or key == b'Q':
        sys.exit()
    elif key == b'c' or key == b'C':  # Toggle aiming
        toggle_aiming()
    elif key == b'r' or key == b'R':  # Reset cannon position and angle
        global cannon_x, cannon_angle, show_aiming_line
        cannon_x = 0.0
        cannon_angle = 45.0
        show_aiming_line = False
        print("Cannon reset to center position")
    elif key == b't' or key == b'T':  # Move target to random position
        global target_pos
        target_pos[0] = random.uniform(5.0, 15.0)
        target_pos[1] = random.uniform(0.5, 4.0)
        target_pos[2] = random.uniform(-3.0, 3.0)
        if show_aiming_line:
            calculate_aiming_point()
        print(f"Target moved to ({target_pos[0]:.1f}, {target_pos[1]:.1f}, {target_pos[2]:.1f})")

def special_keys(key, x, y):
    """Handle special arrow key controls"""
    if key == GLUT_KEY_LEFT:
        move_cannon_left()
        print(f"Cannon moved left to X: {cannon_x:.1f}")
    elif key == GLUT_KEY_RIGHT:
        move_cannon_right()
        print(f"Cannon moved right to X: {cannon_x:.1f}")
    elif key == GLUT_KEY_UP:
        tilt_cannon_up()
        print(f"Cannon tilted up to angle: {cannon_angle:.1f}°")
    elif key == GLUT_KEY_DOWN:
        tilt_cannon_down()
        print(f"Cannon tilted down to angle: {cannon_angle:.1f}°")

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 750)
    glutCreateWindow(b"Cannon Aiming System - Pure OpenGL")
    
    init()
    
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    
    print("=== CANNON AIMING SYSTEM ===")
    print("A precise cannon control simulation")
    print("")
    print("🎯 MAIN CONTROLS:")
    print("LEFT ARROW    - Move cannon left")
    print("RIGHT ARROW   - Move cannon right") 
    print("UP ARROW      - Tilt cannon head up (+5°)")
    print("DOWN ARROW    - Tilt cannon head down (-5°)")
    print("C             - Toggle aiming line/point")
    print("")
    print("🔧 ADDITIONAL CONTROLS:")
    print("T             - Move target to random position")
    print("R             - Reset cannon to center")
    print("Q             - Quit")
    print("")
    print("📊 FEATURES:")
    print("• Smooth cannon movement with boundaries")
    print("• Angle limits (0° to 90°)")
    print("• Dynamic aiming point calculation")
    print("• Trajectory preview when aiming")
    print("• Real-time status indicators")
    print("• Target distance and angle feedback")
    print("")
    print("🎮 Instructions:")
    print("1. Use arrow keys to position and aim the cannon")
    print("2. Press 'C' to see where you're aiming")
    print("3. The red line shows your aim direction")
    print("4. The cyan arc shows predicted trajectory")
    print("5. Try to aim at the target!")
    
    glutMainLoop()

if __name__ == '__main__':
    main()