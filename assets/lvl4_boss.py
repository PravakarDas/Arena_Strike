from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
import random

run_time = 0.0
projectiles = []  # For ranged attacks
ATTACK_CYCLE = 8.0  # Full attack cycle duration

class Projectile:
    def __init__(self, x, y, z, direction_x, direction_y, direction_z, speed=0.12):
        self.x = x
        self.y = y
        self.z = z
        self.dir_x = direction_x
        self.dir_y = direction_y
        self.dir_z = direction_z
        self.speed = speed
        self.lifetime = 0.0
        self.max_lifetime = 8.0
        self.color = [random.uniform(0.8, 1.0), random.uniform(0.1, 0.3), random.uniform(0.7, 1.0)]  # Purple/magenta
    
    def update(self, dt):
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed
        self.z += self.dir_z * self.speed
        self.lifetime += dt
        return self.lifetime < self.max_lifetime

def init():
    glClearColor(0.05, 0.0, 0.1, 1)  # Dark purple background
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 1.0, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)

def draw_sphere(radius):
    glutSolidSphere(radius, 20, 20)

def draw_cylinder(radius, height):
    quad = gluNewQuadric()
    gluCylinder(quad, radius, radius, height, 20, 20)

def draw_cone(base_radius, height):
    glutSolidCone(base_radius, height, 20, 20)

def draw_ellipsoid(rx, ry, rz):
    """Draw an ellipsoid by scaling a sphere"""
    glPushMatrix()
    glScalef(rx, ry, rz)
    draw_sphere(1.0)
    glPopMatrix()

def draw_seductive_face(t):
    """Draw attractive demon face with glowing features"""
    # Glowing eyes with hypnotic effect
    eye_glow = 0.8 + 0.3 * math.sin(t * 3)
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(0.08 * side, 0.06, 0.28)
        
        # Eye socket glow
        glColor4f(1.0, 0.2, 0.8, 0.6)  # Bright magenta glow
        draw_sphere(0.06)
        
        # Eye pupil
        glColor3f(eye_glow, 0.1, eye_glow)  # Pulsing purple
        draw_sphere(0.035)
        
        # Eye highlight
        glTranslatef(0.01 * side, 0.01, 0.02)
        glColor3f(1.0, 0.8, 1.0)
        draw_sphere(0.012)
        glPopMatrix()

    # Seductive lips
    glPushMatrix()
    glTranslatef(0, -0.08, 0.25)
    glColor3f(0.8, 0.1, 0.4)  # Deep red lips
    glScalef(0.12, 0.04, 0.02)
    draw_ellipsoid(1.0, 1.0, 1.0)
    
    # Lip highlight
    glTranslatef(0, 0.3, 0.5)
    glColor3f(1.0, 0.4, 0.6)
    glScalef(0.8, 0.5, 0.5)
    draw_ellipsoid(1.0, 1.0, 1.0)
    glPopMatrix()

    # Facial markings/tattoos
    glColor3f(0.9, 0.3, 0.7)
    glLineWidth(3.0)
    glBegin(GL_LINES)
    # Cheek markings
    for side in [-1, 1]:
        glVertex3f(0.12 * side, 0.02, 0.24)
        glVertex3f(0.18 * side, -0.05, 0.22)
        glVertex3f(0.15 * side, 0.08, 0.23)
        glVertex3f(0.20 * side, 0.03, 0.21)
    glEnd()

def draw_demon_horn(side, t):
    """Draw elegant curved demon horns with magical aura"""
    horn_pulse = 0.9 + 0.2 * math.sin(t * 2 + side)
    
    glPushMatrix()
    glColor3f(0.3 * horn_pulse, 0.1, 0.3 * horn_pulse)  # Dark purple base
    glTranslatef(0.15 * side, 0.25, 0.1)
    glRotatef(-20 * side, 0, 0, 1)
    glRotatef(-50, 1, 0, 0)

    # Horn segments with magical glow
    for i in range(5):
        glPushMatrix()
        glow_intensity = horn_pulse * (1.0 - i * 0.15)
        glColor3f(0.4 * glow_intensity, 0.1, 0.4 * glow_intensity)
        
        glTranslatef(0, 0, i * 0.15)
        glRotatef(12 * i, 1, 0, 0)
        draw_cone(0.04 - i * 0.005, 0.15)
        
        # Magical aura rings
        if i % 2 == 0:
            glColor4f(1.0, 0.3, 0.8, 0.4)
            glTranslatef(0, 0, 0.075)
            glutSolidTorus(0.008, 0.05 - i * 0.005, 8, 12)
        glPopMatrix()
        
        glTranslatef(0, 0, 0.15)
        glRotatef(12, 1, 0, 0)
    
    # Horn tip crystal
    glColor3f(1.0, 0.5, 1.0)
    draw_cone(0.02, 0.08)
    glPopMatrix()

def draw_demon_wing(side, t, is_flying):
    """Draw large demon wings with membrane and magical effects"""
    if is_flying:
        wing_beat = math.sin(t * 6) * 35  # Fast flying
        wing_spread = 1.2
    else:
        wing_beat = math.sin(t * 2) * 15  # Slow intimidating flutter
        wing_spread = 0.8
    
    glPushMatrix()
    glTranslatef(0.3 * side, 0.8, -0.2)
    glRotatef(wing_beat * side, 0, 0, 1)
    glRotatef(25 * side, 0, 1, 0)  # Wing angle
    
    # Wing bone structure
    glColor3f(0.2, 0.1, 0.2)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.02, 0.4)
    glPopMatrix()
    
    # Wing membrane - translucent with gradient
    glEnable(GL_BLEND)
    
    # Main wing surface
    glColor4f(0.6, 0.1, 0.4, 0.7)  # Dark red membrane
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 0, 0)
    glVertex3f(0.8 * side * wing_spread, 0.6, 0)
    glVertex3f(0.4 * side * wing_spread, 1.2, 0)
    
    glVertex3f(0, 0, 0)
    glVertex3f(0.4 * side * wing_spread, 1.2, 0)
    glVertex3f(0.2 * side * wing_spread, 0.8, -0.3)
    
    glVertex3f(0, 0, 0)
    glVertex3f(0.6 * side * wing_spread, 0.3, -0.2)
    glVertex3f(0.8 * side * wing_spread, 0.6, 0)
    glEnd()
    
    # Wing veins with magical glow
    glDisable(GL_BLEND)
    glColor3f(0.9, 0.3, 0.7)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0.8 * side * wing_spread, 0.6, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0.4 * side * wing_spread, 1.2, 0)
    glVertex3f(0.2 * side * wing_spread, 0.4, 0)
    glVertex3f(0.6 * side * wing_spread, 0.9, 0)
    glEnd()
    
    glPopMatrix()

def draw_demonic_sword(t, attack_mode):
    """Draw flaming demonic sword with magical effects"""
    flame_intensity = 0.8 + 0.4 * math.sin(t * 8)
    
    glPushMatrix()
    if attack_mode == "sword":
        # Sword combat positioning
        glRotatef(-45, 1, 0, 0)
        glRotatef(math.sin(t * 4) * 20, 0, 1, 0)  # Slashing motion
    else:
        glRotatef(-90, 1, 0, 0)
    
    # Sword handle
    glColor3f(0.2, 0.1, 0.2)
    draw_cylinder(0.03, 0.25)
    
    # Guard
    glTranslatef(0, 0, 0.25)
    glColor3f(0.3, 0.1, 0.3)
    glPushMatrix()
    glRotatef(90, 0, 1, 0)
    draw_cylinder(0.02, 0.3)
    glPopMatrix()
    
    # Blade with fire effect
    glColor3f(0.8 * flame_intensity, 0.2, 0.4)
    draw_cylinder(0.04, 1.0)
    
    # Blade tip
    glTranslatef(0, 0, 1.0)
    draw_cone(0.04, 0.15)
    
    # Magical flame aura
    if attack_mode == "sword":
        glColor4f(1.0, 0.5, 0.2, 0.6)  # Orange flame
        glEnable(GL_BLEND)
        for i in range(3):
            glPushMatrix()
            glTranslatef(0, 0, -0.3 * i)
            glRotatef(t * 100 + i * 60, 0, 0, 1)
            glScalef(1.2 - i * 0.2, 1.2 - i * 0.2, 1.0)
            glutSolidTorus(0.02, 0.06, 8, 12)
            glPopMatrix()
        glDisable(GL_BLEND)
    
    glPopMatrix()

def draw_seductive_body(t, attack_mode):
    """Draw attractive feminine demon body"""
    # Hourglass torso
    glPushMatrix()
    glColor3f(0.8, 0.4, 0.6)  # Pink-tinted skin
    
    # Upper torso (chest)
    glPushMatrix()
    glTranslatef(0, 1.0, 0)
    draw_ellipsoid(0.18, 0.15, 0.12)
    glPopMatrix()
    
    # Waist (narrow)
    glPushMatrix()
    glTranslatef(0, 0.6, 0)
    draw_ellipsoid(0.12, 0.08, 0.10)
    glPopMatrix()
    
    # Hips (wider)
    glPushMatrix()
    glTranslatef(0, 0.2, 0)
    draw_ellipsoid(0.16, 0.12, 0.11)
    glPopMatrix()
    
    # Body markings/tattoos
    glColor3f(0.9, 0.2, 0.6)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    # Spine markings
    for i in range(4):
        y_pos = 1.1 - i * 0.25
        glVertex3f(0, y_pos, -0.12)
        glVertex3f(0, y_pos - 0.1, -0.11)
    glEnd()
    
    glPopMatrix()

def draw_demon_arm(side, t, attack_mode):
    """Draw demon arms with different combat stances"""
    swing = 0
    arm_position = 0
    
    if attack_mode == "sword":
        # Sword fighting stance
        swing = math.sin(t * 4) * 45 if side > 0 else math.sin(t * 2) * 20
        arm_position = -30 if side > 0 else 15
    elif attack_mode == "ranged":
        # Casting/shooting stance  
        swing = math.sin(t * 3) * 30
        arm_position = 45 if side > 0 else -20
    else:
        # Flying/idle stance
        swing = math.sin(t * 1.5 + side) * 25
        arm_position = 10 * side
    
    glPushMatrix()
    glTranslatef(0.22 * side, 1.3, 0)
    glRotatef(arm_position, 0, 0, 1)
    glRotatef(swing * side, 1, 0, 0)

    # Upper arm - toned and attractive
    glColor3f(0.75, 0.35, 0.55)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.06, 0.4)
    glTranslatef(0, 0, 0.4)
    draw_sphere(0.065)  # Shoulder joint
    glPopMatrix()

    # Forearm
    glTranslatef(0, -0.4, 0)
    elbow_bend = -30 if attack_mode == "sword" and side > 0 else -50
    glRotatef(elbow_bend, 1, 0, 0)
    glColor3f(0.7, 0.3, 0.5)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.055, 0.35)
    glPopMatrix()

    # Hand and weapon/magic
    glTranslatef(0, -0.35, 0)
    if side > 0:  # Right hand
        if attack_mode == "sword":
            draw_demonic_sword(t, attack_mode)
        elif attack_mode == "ranged":
            # Magic casting effect
            glColor4f(1.0, 0.3, 0.8, 0.8)
            glEnable(GL_BLEND)
            glPushMatrix()
            glRotatef(t * 180, 0, 1, 0)
            glutSolidTorus(0.03, 0.08, 8, 16)
            glPopMatrix()
            glDisable(GL_BLEND)
    else:  # Left hand
        if attack_mode == "ranged":
            # Secondary casting hand
            glColor4f(0.8, 0.3, 1.0, 0.6)
            glEnable(GL_BLEND)
            draw_sphere(0.05)
            glDisable(GL_BLEND)

    glPopMatrix()

def draw_demon_leg(side, t, is_flying):
    """Draw shapely demon legs"""
    if is_flying:
        leg_motion = math.sin(t * 0.8 + side) * 15  # Floating motion
        knee_bend = -20
    else:
        leg_motion = math.sin(t * 2 + side) * 25  # Walking/combat stance
        knee_bend = -40
    
    glPushMatrix()
    glTranslatef(0.12 * side, 0.1, 0)
    glRotatef(leg_motion * side, 1, 0, 0)

    # Thigh - shapely and toned
    glColor3f(0.75, 0.35, 0.55)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_ellipsoid(0.08, 0.08, 0.35)  # More feminine shape
    glTranslatef(0, 0, 0.35)
    draw_sphere(0.08)  # Knee joint
    glPopMatrix()

    # Calf
    glTranslatef(0, -0.35, 0)
    glRotatef(knee_bend, 1, 0, 0)
    glColor3f(0.7, 0.3, 0.5)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_ellipsoid(0.06, 0.06, 0.3)
    glPopMatrix()

    # Foot - elegant
    glTranslatef(0, -0.3, 0)
    glColor3f(0.65, 0.25, 0.45)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_ellipsoid(0.05, 0.08, 0.12)
    glPopMatrix()

    glPopMatrix()

def shoot_projectile():
    """Create magical projectiles"""
    global projectiles
    
    # Multiple projectiles in spread pattern
    for i in range(3):
        # Starting position from hands
        start_x = random.uniform(-0.3, 0.3)
        start_y = 1.5
        start_z = 0.5
        
        # Random directions in forward cone
        angle = random.uniform(-45, 45) + (i - 1) * 20  # Spread pattern
        elevation = random.uniform(-20, 20)
        
        dir_x = math.sin(math.radians(angle)) * math.cos(math.radians(elevation))
        dir_y = math.sin(math.radians(elevation))
        dir_z = math.cos(math.radians(angle)) * math.cos(math.radians(elevation))
        
        projectile = Projectile(start_x, start_y, start_z, dir_x, dir_y, dir_z, 0.15)
        projectiles.append(projectile)

def draw_projectile(proj):
    """Draw magical projectile"""
    glPushMatrix()
    glTranslatef(proj.x, proj.y, proj.z)
    
    # Pulsing magical orb
    pulse = 0.8 + 0.4 * math.sin(run_time * 10 + proj.lifetime * 5)
    glScalef(pulse, pulse, pulse)
    
    glColor3f(proj.color[0], proj.color[1], proj.color[2])
    draw_sphere(0.08)
    
    # Trail effect
    glColor4f(proj.color[0], proj.color[1], proj.color[2], 0.4)
    glEnable(GL_BLEND)
    for i in range(3):
        glPushMatrix()
        trail_offset = (i + 1) * 0.1
        glTranslatef(-proj.dir_x * trail_offset, -proj.dir_y * trail_offset, -proj.dir_z * trail_offset)
        glScalef(0.8 - i * 0.2, 0.8 - i * 0.2, 0.8 - i * 0.2)
        draw_sphere(0.08)
        glPopMatrix()
    glDisable(GL_BLEND)
    
    glPopMatrix()

def get_current_attack_mode(t):
    """Determine current attack mode based on time"""
    cycle_time = t % ATTACK_CYCLE
    if cycle_time < 2.5:
        return "sword"      # Sword combat
    elif cycle_time < 5.0:
        return "ranged"     # Ranged attacks
    elif cycle_time < 7.0:
        return "flying"     # Flying around
    else:
        return "idle"       # Intimidating idle

def draw_boss_demon_queen(t):
    """Draw the complete boss demon queen"""
    attack_mode = get_current_attack_mode(t)
    is_flying = (attack_mode in ["flying", "ranged"])
    
    # Floating/hovering effect
    hover_height = 0
    if is_flying:
        hover_height = math.sin(t * 1.5) * 0.8 + 1.0
    else:
        hover_height = math.sin(t * 0.5) * 0.2
    
    glPushMatrix()
    glTranslatef(0, hover_height, 0)
    
    # Rotation for dramatic effect
    if attack_mode == "flying":
        glRotatef(math.sin(t * 0.8) * 20, 0, 1, 0)
    
    # Main body
    draw_seductive_body(t, attack_mode)
    
    # Head
    glPushMatrix()
    glColor3f(0.8, 0.4, 0.6)  # Matching skin tone
    glTranslatef(0, 1.8, 0)
    draw_ellipsoid(0.15, 0.18, 0.13)  # Slightly elongated head
    draw_seductive_face(t)
    
    # Horns
    draw_demon_horn(1, t)   # Right horn
    draw_demon_horn(-1, t)  # Left horn
    glPopMatrix()
    
    # Wings
    draw_demon_wing(1, t, is_flying)   # Right wing
    draw_demon_wing(-1, t, is_flying)  # Left wing
    
    # Arms with different combat modes
    draw_demon_arm(1, t, attack_mode)   # Right arm
    draw_demon_arm(-1, t, attack_mode)  # Left arm
    
    # Legs
    draw_demon_leg(1, t, is_flying)
    draw_demon_leg(-1, t, is_flying)
    
    glPopMatrix()

def display():
    global run_time, projectiles
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Dynamic camera that circles the boss
    cam_angle = run_time * 0.3
    cam_height = 3 + math.sin(run_time * 0.4) * 1
    gluLookAt(6 * math.sin(cam_angle), cam_height, 6 * math.cos(cam_angle),
              0, 2, 0,  # Look at boss center
              0, 1, 0)
    
    # Draw boss
    draw_boss_demon_queen(run_time)
    
    # Draw all projectiles
    for proj in projectiles:
        draw_projectile(proj)
    
    glutSwapBuffers()

def idle():
    global run_time, projectiles
    dt = 0.02
    run_time += dt
    
    # Auto-shoot during ranged attack phase
    attack_mode = get_current_attack_mode(run_time)
    if attack_mode == "ranged" and int(run_time * 3) != int((run_time - dt) * 3):
        shoot_projectile()
    
    # Update projectiles
    projectiles = [proj for proj in projectiles if proj.update(dt)]
    
    glutPostRedisplay()

def keyboard(key, x, y):
    """Handle keyboard input"""
    if key == b'q' or key == b'Q':
        sys.exit()
    elif key == b' ':
        shoot_projectile()  # Manual projectile attack
    elif key == b'r' or key == b'R':
        global projectiles
        projectiles = []  # Clear projectiles

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutCreateWindow(b"BOSS: Demon Queen - Triple Threat - SPACE for manual attack")
    init()
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    
    print("🔥 BOSS: DEMON QUEEN - TRIPLE THREAT 🔥")
    print("════════════════════════════════════════")
    print("ABILITIES:")
    print("⚔️  SWORD COMBAT - Flaming demonic blade slashing")
    print("🏹 RANGED ATTACKS - Magical projectile volleys")  
    print("🦋 FLIGHT CAPABILITY - Wings for aerial dominance")
    print("")
    print("CONTROLS:")
    print("SPACE - Manual magical attack")
    print("R - Clear all projectiles") 
    print("Q - Quit")
    print("")
    print("Watch the boss cycle through all three combat modes!")
    
    glutMainLoop()

if __name__ == '__main__':
    main()