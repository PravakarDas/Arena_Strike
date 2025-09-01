from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
import random

# Global variables
camera_angle = 0.0
audience_data = []
num_audience = 150
cheer_time = 0.0
camera_distance = 35.0  # Changed: Auto zoom to show arena fully (was 60.0)
zoom_speed = 2.0
camera_height = 24.0  # New: Controllable camera height
camera_move_speed = 3.0  # New: Speed for camera movement

def init():
    glClearColor(0.15, 0.2, 0.25, 1.0)  # Natural sky blue-gray
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    # Set up lighting
    light_pos = [10.0, 15.0, 10.0, 1.0]
    light_ambient = [0.3, 0.3, 0.4, 1.0]
    light_diffuse = [0.8, 0.8, 0.9, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, 1.0, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)
    
    generate_audience()

def generate_audience():
    """Generate random positions and animations for audience members"""
    global audience_data
    
    # Gallery rows (3 levels) - positioned around football field
    for level in range(3):
        height = 9.0 + level * 6.0  # 3x bigger heights
        
        # Different radius for football field shape
        radius_x = 55.0 + level * 6.0  # Longer radius for length
        radius_y = 40.0 + level * 4.0  # Shorter radius for width
        
        # Number of audience members per level
        count_per_level = 60 - level * 10  # More audience for bigger field
        
        for i in range(count_per_level):
            angle = (i / count_per_level) * 360
            
            # Elliptical positioning for football field
            x = radius_x * math.cos(math.radians(angle))
            z = radius_y * math.sin(math.radians(angle))
            y = height
            
            # Random animation properties
            cheer_offset = random.uniform(0, 2 * math.pi)
            cheer_intensity = random.uniform(0.5, 1.5)
            
            audience_data.append({
                'x': x, 'y': y, 'z': z,
                'cheer_offset': cheer_offset,
                'cheer_intensity': cheer_intensity,
                'base_height': height
            })

def draw_sphere(radius):
    glutSolidSphere(radius, 12, 12)

def draw_cylinder(radius, height):
    quad = gluNewQuadric()
    gluCylinder(quad, radius, radius, height, 12, 12)
    gluDeleteQuadric(quad)

def draw_arena_floor():
    """Draw the main football field with running tracks - 3x bigger"""
    
    # Running Track - Outer layer (should be drawn first, underneath)
    glColor3f(0.8, 0.4, 0.2)  # Orange track color
    glPushMatrix()
    glTranslatef(0, -1.5, 0)  # Same level as main field
    glScalef(55.0, 0.6, 35.0)  # Larger oval for outer track
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Running Track - Middle layer
    glColor3f(0.7, 0.35, 0.18)  # Slightly darker orange
    glPushMatrix()
    glTranslatef(0, -1.45, 0)  # Slightly above outer track
    glScalef(50.0, 0.6, 32.0)  # Medium oval
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Running Track - Inner layer
    glColor3f(0.6, 0.3, 0.15)  # Even darker orange
    glPushMatrix()
    glTranslatef(0, -1.4, 0)  # Slightly above middle track
    glScalef(45.0, 0.6, 29.0)  # Smaller oval, but still larger than field
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Main football field (rectangular, not square) - on top of tracks
    glColor3f(0.1, 0.7, 0.1)  # Green grass color
    glPushMatrix()
    glTranslatef(0, -1.35, 0)  # Slightly above inner track
    glScalef(40.0, 0.6, 25.0)  # Football field dimensions (longer than wide)
    glutSolidCube(1.0)
    glPopMatrix()
        
    # Track lane dividers (white lines on track)
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)
    
def draw_gallery_structure():
    """Draw the gallery seating structure around football field - 3x bigger"""
    glColor3f(0.6, 0.55, 0.5)  # Natural stone color
    
    # Gallery levels - 3x bigger, elliptical for football field
    for level in range(3):
        height = 7.5 + level * 6.0  # 3x bigger heights
        inner_radius_x = 50.0 + level * 6.0  # Longer radius for length
        inner_radius_y = 35.0 + level * 4.0  # Shorter radius for width
        depth = 4.5  # Platform depth
        
        # Create elliptical gallery platform
        glPushMatrix()
        glTranslatef(0, height, 0)
        
        # Draw platform segments in elliptical pattern
        for angle in range(0, 360, 12):  # More segments for smoother ellipse
            rad = math.radians(angle)
            
            # Calculate elliptical position
            base_x = inner_radius_x * math.cos(rad)
            base_z = inner_radius_y * math.sin(rad)
            
            glPushMatrix()
            glTranslatef(base_x, 0, base_z)
            glRotatef(angle, 0, 1, 0)
            glScalef(depth, 0.9, 6.0)  # 3x bigger scale
            glutSolidCube(1.0)
            glPopMatrix()
        
        # Support pillars - 3x bigger, elliptical placement
        if level > 0:
            glColor3f(0.5, 0.45, 0.4)
            for angle in range(0, 360, 24):  # Support pillars
                rad = math.radians(angle)
                pillar_x = (inner_radius_x - 2) * math.cos(rad)
                pillar_z = (inner_radius_y - 2) * math.sin(rad)
                
                glPushMatrix()
                glTranslatef(pillar_x, -3.0, pillar_z)
                glScalef(1.2, 6.0, 1.2)  # 3x bigger scale
                glutSolidCube(1.0)
                glPopMatrix()
        
        glPopMatrix()
        glColor3f(0.6, 0.55, 0.5)  # Reset color

def draw_stick_figure(x, y, z, cheer_animation):
    """Draw a stick figure audience member - scaled for bigger arena"""
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Face the center
    angle_to_center = math.degrees(math.atan2(-x, -z))
    glRotatef(angle_to_center, 0, 1, 0)
    
    # Body color
    glColor3f(0.7, 0.6, 0.5)
    
    # Head - slightly bigger for the larger arena
    glPushMatrix()
    glTranslatef(0, 5.4 + cheer_animation * 0.3, 0)  # 3x scale
    draw_sphere(0.45)  # 3x bigger
    glPopMatrix()
    
    # Body - 3x bigger
    glPushMatrix()
    glTranslatef(0, 3.6, 0)
    glScalef(0.3, 2.4, 0.3)  # 3x bigger
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Arms (animated for cheering) - 3x bigger
    arm_angle = 45 + cheer_animation * 30
    
    # Left arm
    glPushMatrix()
    glTranslatef(-0.6, 4.5, 0)  # 3x positioning
    glRotatef(arm_angle, 0, 0, 1)
    glScalef(0.18, 1.2, 0.18)  # 3x bigger
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Right arm
    glPushMatrix()
    glTranslatef(0.6, 4.5, 0)  # 3x positioning
    glRotatef(-arm_angle, 0, 0, 1)
    glScalef(0.18, 1.2, 0.18)  # 3x bigger
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Legs - 3x bigger
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(0.3 * side, 1.2, 0)  # 3x positioning
        glScalef(0.24, 2.4, 0.24)  # 3x bigger
        glutSolidCube(1.0)
        glPopMatrix()
    
    glPopMatrix()

def draw_audience():
    """Draw all audience members with cheering animation"""
    global cheer_time
    
    for person in audience_data:
        cheer_animation = math.sin(cheer_time + person['cheer_offset']) * person['cheer_intensity']
        draw_stick_figure(
            person['x'], 
            person['y'] + cheer_animation * 0.05, 
            person['z'], 
            cheer_animation
        )

def draw_arena_lights():
    """Draw stadium-style lighting around football field - 3x bigger"""
    glColor3f(0.9, 0.9, 0.7)  # Warm light color
    
    # Light posts around the football field - elliptical placement
    for angle in range(0, 360, 30):  # More light posts
        rad = math.radians(angle)
        light_x = 65.0 * math.cos(rad)  # Elliptical positioning
        light_z = 50.0 * math.sin(rad)
        
        glPushMatrix()
        glTranslatef(light_x, 24.0, light_z)
        
        # Light post - 3x bigger
        glColor3f(0.3, 0.3, 0.3)
        glScalef(0.6, 12.0, 0.6)  # 3x bigger scale
        glutSolidCube(1.0)
        glPopMatrix()
        
        # Light fixture - 3x bigger
        glPushMatrix()
        glTranslatef(light_x, 28.5, light_z)
        glColor3f(0.9, 0.9, 0.7)
        draw_sphere(0.9)  # 3x bigger
        glPopMatrix()

def draw_roof_structure():
    """Draw modern roof/canopy structure over football field - 3x bigger"""
    glColor3f(0.4, 0.4, 0.45)  # Steel gray
    
    # Main support beams - elliptical pattern for football field
    for angle in range(0, 360, 60):  # Support beams
        rad = math.radians(angle)
        beam_x = 70.0 * math.cos(rad)
        beam_z = 55.0 * math.sin(rad)
        
        glPushMatrix()
        glTranslatef(beam_x, 30.0, beam_z)
        glRotatef(45, 0, 0, 1)
        glScalef(0.9, 60.0, 0.9)  # 3x bigger scale
        glutSolidCube(1.0)
        glPopMatrix()
    
    # Roof panels (translucent effect with darker color) - football field shape
    glColor3f(0.2, 0.25, 0.3)
    for i in range(12):  # More panels for coverage
        angle = i * 30
        rad = math.radians(angle)
        panel_x = 35.0 * math.cos(rad)
        panel_z = 25.0 * math.sin(rad)
        
        glPushMatrix()
        glTranslatef(panel_x, 36.0, panel_z)
        glRotatef(angle, 0, 1, 0)
        glRotatef(-15, 1, 0, 0)
        glScalef(12.0, 0.3, 30.0)  # Larger panels for football field
        glutSolidCube(1.0)
        glPopMatrix()

def display():
    global cheer_time, camera_distance, camera_height  # Added camera_height
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Camera position with arrow key control
    cam_x = camera_distance * math.sin(math.radians(camera_angle))
    cam_z = camera_distance * math.cos(math.radians(camera_angle))
    
    gluLookAt(cam_x, camera_height, cam_z,  # Eye position (now uses controllable camera_height)
              0, 6, 0,                      # Look at center of arena (adjusted for bigger scale)
              0, 1, 0)                      # Up vector
    
    # Draw all components
    draw_arena_floor()
    draw_gallery_structure()
    draw_audience()
    draw_arena_lights()
    draw_roof_structure()
    
    # Add some atmospheric particles/effects
    draw_atmosphere_effects()
    
    glutSwapBuffers()

def draw_atmosphere_effects():
    """Add some floating particles for atmosphere - 3x bigger"""
    glColor4f(0.9, 0.9, 0.7, 0.3)  # Semi-transparent particles
    glDisable(GL_LIGHTING)
    
    for i in range(20):
        x = random.uniform(-18, 18)  # 3x bigger range
        y = 24 + random.uniform(0, 12)  # 3x bigger height
        z = random.uniform(-18, 18)  # 3x bigger range
        
        glPushMatrix()
        glTranslatef(x, y + math.sin(cheer_time * 2 + i) * 1.5, z)  # 3x bigger animation
        draw_sphere(0.15)  # 3x bigger particles
        glPopMatrix()
    
    glEnable(GL_LIGHTING)

def idle():
    global cheer_time  # Removed camera_angle update - no more spinning
    # camera_angle += 0.2  # REMOVED: Stop the spinning
    cheer_time += 0.05  # Keep audience movement
    
    # Removed camera angle reset logic since we're not spinning
    
    glutPostRedisplay()

def keyboard(key, x, y):
    global camera_distance, camera_angle, camera_height
    
    if key == b'q' or key == b'\x1b':  # 'q' or ESC to quit
        sys.exit(0)
    elif key == b' ':  # Space to manually rotate camera
        camera_angle += 45
    elif key == b'=':  # '+' key for zoom in
        camera_distance = max(20.0, camera_distance - zoom_speed)
    elif key == b'-':  # '-' key for zoom out
        camera_distance = min(150.0, camera_distance + zoom_speed)
    elif key == b'w':  # Move camera up
        camera_height += camera_move_speed
    elif key == b's':  # Move camera down
        camera_height = max(5.0, camera_height - camera_move_speed)

def special_keys(key, x, y):
    """Handle special keys for camera movement and zoom control"""
    global camera_distance, camera_angle, camera_height, camera_move_speed
    
    if key == GLUT_KEY_LEFT:  # Rotate camera left
        camera_angle -= camera_move_speed
    elif key == GLUT_KEY_RIGHT:  # Rotate camera right
        camera_angle += camera_move_speed
    elif key == GLUT_KEY_UP:  # Zoom in
        camera_distance = max(20.0, camera_distance - zoom_speed)
    elif key == GLUT_KEY_DOWN:  # Zoom out
        camera_distance = min(150.0, camera_distance + zoom_speed)
    
    glutPostRedisplay()

def reshape(width, height):
    if height == 0:
        height = 1
    
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, width/height, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Modern 3D Arena with Gallery Audience")
    
    init()
    
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)  # Add special keys handler
    glutReshapeFunc(reshape)
    
    print("Controls:")
    print("- Camera is now static and focused on football field")
    print("- Press SPACE for manual camera rotation")
    print("- Use ARROW KEYS for camera control:")
    print("  ← LEFT: Rotate camera left")
    print("  → RIGHT: Rotate camera right") 
    print("  ↑ UP: Zoom in")
    print("  ↓ DOWN: Zoom out")
    print("- Use W/S keys to move camera up/down")
    print("- Use +/- keys for additional zoom")
    print("- Press 'q' or ESC to quit")
    
    glutMainLoop()

if __name__ == '__main__':
    main()