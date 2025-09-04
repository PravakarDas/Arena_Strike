# --- GLOBALS NEEDED FOR GAME STATE ---
audience_data = []
cheer_time = 0.0
camera_distance = 35.0
camera_angle = 0.0
camera_height = 24.0
camera_move_speed = 3.0
show_aiming_line = True
aiming_point = [0.0, 0.0, 0.0]
CANNON_MIN_Z = -12.0
CANNON_MAX_Z = 12.0
CANNON_MIN_ANGLE = 0.0
CANNON_MAX_ANGLE = 90.0
bombs = []
bomb_speed = 0.8
gravity = -0.02
max_bombs = 10
zoom_speed = 2.0
# --- GLOBALS NEEDED FOR GAME STATE ---
audience_data = []
cheer_time = 0.0
camera_distance = 35.0
camera_angle = 0.0
camera_height = 24.0
camera_move_speed = 3.0
show_aiming_line = True
aiming_point = [0.0, 0.0, 0.0]
CANNON_MIN_Z = -12.0
CANNON_MAX_Z = 12.0
CANNON_MIN_ANGLE = 0.0
CANNON_MAX_ANGLE = 90.0
cannon_z = 0.0
cannon_angle = 45.0
bombs = []
bomb_speed = 0.8
gravity = -0.02
max_bombs = 10
zoom_speed = 2.0
# ...existing code...

# --- INIT FUNCTION (OpenGL and game setup) ---
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

import lvl1_stickyman as lvl1_stickyman
import lvl2_bug as lvl2_bug
import lvl3_archer as lvl3_archer
import lvl4_boss as lvl4_boss


# --- GAME/ENEMY STATE ---
PLAYER_LIFE = 20
player_life = PLAYER_LIFE


# Each enemy: {'pos': [x, y, z], 'alive': bool, 'type': str, ...}
enemies = []
level = 1
level_spawn_time = None
level_second_spawned = False
level_complete = False
score = 0

# --- BULLET STATE ---
bullets = []  # Each: {'x','y','z','vx','vy','vz','alive'}
bullet_speed = 1.2


from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import sys
import math
import random

# ...existing code...

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

# CANNON FUNCTIONS
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
    """Draw the complete cannon at current position on length side"""
    glPushMatrix()
    # Position cannon at length side of the arena (X = -20.0 for left side)
    glTranslatef(-20.0, -1.0, cannon_z)  # Move cannon up/down along length side
    glRotatef(90, 0, 1, 0)  # Rotate cannon to face into the arena
    
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
    
    # Calculate barrel tip position (cannon is at length side)
    barrel_length = 2.5
    cannon_world_x = -20.0  # Left side of arena
    cannon_world_y = -1.3  # Cannon base height
    cannon_world_z = cannon_z  # Along length side
    
    # Account for cannon rotation (90 degrees to face into arena)
    barrel_tip_x = cannon_world_x + barrel_length * math.cos(math.radians(cannon_angle))
    barrel_tip_y = cannon_world_y + barrel_length * math.sin(math.radians(cannon_angle))
    barrel_tip_z = cannon_world_z
    
    # Calculate aiming direction (into arena from left side)
    aiming_distance = 30.0
    aiming_direction_x = math.cos(math.radians(cannon_angle))  # Forward into arena
    aiming_direction_y = math.sin(math.radians(cannon_angle))
    aiming_direction_z = 0  # No side movement
    
    aiming_point[0] = barrel_tip_x + aiming_direction_x * aiming_distance
    aiming_point[1] = barrel_tip_y + aiming_direction_y * aiming_distance
    aiming_point[2] = barrel_tip_z + aiming_direction_z * aiming_distance

def draw_aiming_system():
    """Draw the aiming line with dotted pattern"""
    if not show_aiming_line:
        return
    
    glDisable(GL_LIGHTING)
    
    # Calculate barrel tip position
    barrel_length = 2.5
    cannon_world_x = -20.0
    cannon_world_y = -1.3
    cannon_world_z = cannon_z
    
    barrel_tip_x = cannon_world_x + barrel_length * math.cos(math.radians(cannon_angle))
    barrel_tip_y = cannon_world_y + barrel_length * math.sin(math.radians(cannon_angle))
    barrel_tip_z = cannon_world_z
    
    # Draw dotted aiming line
    glColor3f(1.0, 0.0, 0.0)  # Red aiming line
    glLineWidth(3.0)
    
    # Create dotted line by drawing segments
    num_segments = 50
    for i in range(0, num_segments, 2):  # Skip every other segment for dots
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
    
    # Draw aiming point crosshair
    glPushMatrix()
    glTranslatef(aiming_point[0], aiming_point[1], aiming_point[2])
    
    # Pulsing crosshair
    pulse = 1.0 + 0.5 * math.sin(glutGet(GLUT_ELAPSED_TIME) * 0.005)
    size = 0.5 * pulse
    
    glColor3f(1.0, 1.0, 0.0)  # Yellow crosshair
    glLineWidth(4.0)
    glBegin(GL_LINES)
    # Horizontal line
    glVertex3f(-size, 0, 0)
    glVertex3f(size, 0, 0)
    # Vertical line
    glVertex3f(0, -size, 0)
    glVertex3f(0, size, 0)
    # Depth line
    glVertex3f(0, 0, -size)
    glVertex3f(0, 0, size)
    glEnd()
    
    # Center dot
    glColor3f(1.0, 0.0, 0.0)
    glPointSize(10.0)
    glBegin(GL_POINTS)
    glVertex3f(0, 0, 0)
    glEnd()
    
    glPopMatrix()
    
    glEnable(GL_LIGHTING)

def move_cannon_up():
    """Move cannon up along length side with boundary checking"""
    global cannon_z
    new_z = cannon_z + 1.0
    if new_z <= CANNON_MAX_Z:
        cannon_z = new_z
        if show_aiming_line:
            calculate_aiming_point()
        print(f"Cannon moved up to Z: {cannon_z:.1f}")

def move_cannon_down():
    """Move cannon down along length side with boundary checking"""
    global cannon_z
    new_z = cannon_z - 1.0
    if new_z >= CANNON_MIN_Z:
        cannon_z = new_z
        if show_aiming_line:
            calculate_aiming_point()
        print(f"Cannon moved down to Z: {cannon_z:.1f}")


# Fix: Up means aim/model up, Down means aim/model down
def tilt_cannon_up():
    """Tilt cannon barrel up with angle limits (aim/model both up)"""
    global cannon_angle
    new_angle = cannon_angle - 5.0
    if new_angle >= CANNON_MIN_ANGLE:
        cannon_angle = new_angle
        if show_aiming_line:
            calculate_aiming_point()
        print(f"Cannon tilted up to angle: {cannon_angle:.1f}°")

def tilt_cannon_down():
    """Tilt cannon barrel down with angle limits (aim/model both down)"""
    global cannon_angle
    new_angle = cannon_angle + 5.0
    if new_angle <= CANNON_MAX_ANGLE:
        cannon_angle = new_angle
        if show_aiming_line:
            calculate_aiming_point()
        print(f"Cannon tilted down to angle: {cannon_angle:.1f}°")


# Aiming is always on now, so this is a no-op
def toggle_aiming():
    pass

# BOMB FUNCTIONS
def create_bomb():
    """Create a new bomb and add it to the bombs list"""
    global bombs
    
    if len(bombs) >= max_bombs:
        print("Maximum bombs reached! Wait for some to explode.")
        return
    
    # Calculate initial bomb position (barrel tip)
    barrel_length = 2.5
    cannon_world_x = -20.0
    cannon_world_y = -1.3
    cannon_world_z = cannon_z
    
    initial_x = cannon_world_x + barrel_length * math.cos(math.radians(cannon_angle))
    initial_y = cannon_world_y + barrel_length * math.sin(math.radians(cannon_angle))
    initial_z = cannon_world_z
    
    # Calculate initial velocity based on cannon angle
    velocity_x = bomb_speed * math.cos(math.radians(cannon_angle))
    velocity_y = bomb_speed * math.sin(math.radians(cannon_angle))
    velocity_z = 0.0
    
    # Create bomb object
    bomb = {
        'x': initial_x,
        'y': initial_y,
        'z': initial_z,
        'vel_x': velocity_x,
        'vel_y': velocity_y,
        'vel_z': velocity_z,
        'life_time': 0,
        'max_life': 300,  # Bomb disappears after 5 seconds at 60fps
        'exploded': False
    }
    
    bombs.append(bomb)
    print(f"BOMB FIRED! Bombs active: {len(bombs)}")

def update_bombs():
    """Update all bomb positions and handle physics"""
    global bombs
    
    bombs_to_remove = []
    
    for i, bomb in enumerate(bombs):
        if bomb['exploded']:
            continue
        
        # Update position
        bomb['x'] += bomb['vel_x']
        bomb['y'] += bomb['vel_y']
        bomb['z'] += bomb['vel_z']
        
        # Apply gravity
        bomb['vel_y'] += gravity
        
        # Check collision with ground
        if bomb['y'] <= -1.0:
            bomb['exploded'] = True
            print(f"BOMB EXPLODED at ({bomb['x']:.1f}, {bomb['y']:.1f}, {bomb['z']:.1f})")
        
        # Check arena boundaries
        if (bomb['x'] > 25.0 or bomb['x'] < -25.0 or 
            bomb['z'] > 15.0 or bomb['z'] < -15.0):
            bomb['exploded'] = True
            print("Bomb flew out of arena!")
        
        # Update lifetime
        bomb['life_time'] += 1
        if bomb['life_time'] >= bomb['max_life']:
            bombs_to_remove.append(i)
    
    # Remove expired bombs
    for i in reversed(bombs_to_remove):
        bombs.pop(i)

def draw_bomb(bomb):
    """Draw a single bomb"""
    glPushMatrix()
    glTranslatef(bomb['x'], bomb['y'], bomb['z'])
    
    if bomb['exploded']:
        # Draw explosion effect
        glColor3f(1.0, 0.5, 0.0)  # Orange explosion
        explosion_size = min(2.0, (bomb['life_time'] - 240) * 0.1)  # Grow over time
        draw_sphere(explosion_size)
        
        # Add some particles
        glColor3f(1.0, 1.0, 0.0)  # Yellow particles
        for j in range(8):
            angle = j * 45
            offset_x = explosion_size * 0.5 * math.cos(math.radians(angle))
            offset_z = explosion_size * 0.5 * math.sin(math.radians(angle))
            glPushMatrix()
            glTranslatef(offset_x, 0, offset_z)
            draw_sphere(0.1)
            glPopMatrix()
    else:
        # Draw flying bomb
        glColor3f(0.2, 0.2, 0.2)  # Dark gray bomb
        draw_sphere(0.15)
        
        # Add a fuse spark
        glColor3f(1.0, 0.8, 0.0)  # Yellow spark
        spark_offset = 0.2 + 0.1 * math.sin(bomb['life_time'] * 0.5)
        glPushMatrix()
        glTranslatef(0, spark_offset, 0)
        draw_sphere(0.05)
        glPopMatrix()
    
    glPopMatrix()

def draw_all_bombs():
    """Draw all active bombs"""
    glDisable(GL_LIGHTING)
    for bomb in bombs:
        draw_bomb(bomb)
    glEnable(GL_LIGHTING)

def display():
    global cheer_time, camera_distance, camera_height
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Camera position with arrow key control
    cam_x = camera_distance * math.sin(math.radians(camera_angle))
    cam_z = camera_distance * math.cos(math.radians(camera_angle))
    
    gluLookAt(cam_x, camera_height, cam_z,  # Eye position
              0, 6, 0,                      # Look at center of arena
              0, 1, 0)                      # Up vector
    
    # Draw all arena components
    draw_arena_floor()
    draw_gallery_structure()
    draw_audience()
    draw_arena_lights()
    draw_roof_structure()
    draw_atmosphere_effects()
    
    # Draw cannon at length side
    draw_complete_cannon()
    draw_aiming_system()
    
    # Draw bombs
    draw_all_bombs()


    # Draw bullets
    glDisable(GL_LIGHTING)
    glColor3f(1, 1, 0.2)
    for bullet in bullets:
        if bullet['alive']:
            glPushMatrix()
            glTranslatef(bullet['x'], bullet['y'], bullet['z'])
            draw_sphere(0.18)
            glPopMatrix()
    glEnable(GL_LIGHTING)

    # Draw all enemies by type
    for enemy in enemies:
        if not enemy['alive']:
            continue
        glPushMatrix()
        glTranslatef(enemy['pos'][0], 0, enemy['pos'][2])
        if enemy['type'] == 'stickyman':
            lvl1_stickyman.draw_stickman(0)
        elif enemy['type'] == 'bug':
            lvl2_bug.draw_bug(0)
        elif enemy['type'] == 'archer':
            lvl3_archer.draw_archer(0)
            # Draw archer arrows
            for arrow in enemy.get('arrows', []):
                if arrow['alive']:
                    glPushMatrix()
                    glTranslatef(arrow['x']-enemy['pos'][0], 1.5, arrow['z']-enemy['pos'][2])
                    glColor3f(0.7, 0.2, 0.2)
                    draw_sphere(0.12)
                    glPopMatrix()
        elif enemy['type'] == 'boss':
            lvl4_boss.draw_boss_demon_queen(0)
            # Draw boss projectiles
            for proj in enemy.get('projectiles', []):
                if proj['alive']:
                    glPushMatrix()
                    glTranslatef(proj['x']-enemy['pos'][0], 1.5, proj['z']-enemy['pos'][2])
                    glColor3f(1, 0, 1)
                    draw_sphere(0.15)
                    glPopMatrix()
        glPopMatrix()

    # HUD: player life, level, and score
    glDisable(GL_LIGHTING)
    glWindowPos2f(10, 40)
    level_name = {1: 'Stickyman', 2: 'Bug', 3: 'Archer', 4: 'Boss'}
    s = f"Life: {player_life}  |  Level {level}: {level_name.get(level, '')}  |  Score: {score}"
    # Ensure GLUT_BITMAP_HELVETICA_18 is defined
    try:
        font = GLUT_BITMAP_HELVETICA_18
    except NameError:
        from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18 as font
    for c in s:
        glutBitmapCharacter(font, ord(c))
    glEnable(GL_LIGHTING)

    glutSwapBuffers()

def idle():
    global cheer_time
    cheer_time += 0.05  # Keep audience movement
    update_bombs()  # Update bomb physics


    # --- LEVEL LOGIC ---
    global enemies, level_spawn_time, level_second_spawned, level_complete, player_life, level, score
    now = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    # Level 1: Stickyman
    if level == 1:
        if not level_spawn_time:
            enemies = [{'pos': [20.0, -1.0, 0.0], 'alive': True, 'type': 'stickyman', 'collided': False}]
            level_spawn_time = now
            level_second_spawned = False
            level_complete = False
        elif not level_second_spawned and now - level_spawn_time > 3.0:
            enemies.append({'pos': [20.0, -1.0, 6.0], 'alive': True, 'type': 'stickyman', 'collided': False})
            level_second_spawned = True
        # Move stickymen
        for enemy in enemies:
            if not enemy['alive']:
                continue
            dx = -20.0 - enemy['pos'][0]
            dz = cannon_z - enemy['pos'][2]
            dist = math.sqrt(dx*dx + dz*dz)
            if dist > 1.0:
                enemy['pos'][0] += 0.08 * dx / dist
                enemy['pos'][2] += 0.08 * dz / dist
                enemy['collided'] = False
            else:
                if not enemy.get('collided', False):
                    player_life -= 2
                    enemy['collided'] = True
                    print("Stickyman reached the cannon! Player life:", player_life)
        # Level complete check
        if all(not e['alive'] or e.get('collided', False) for e in enemies) and level_second_spawned:
            if not level_complete:
                level_complete = True
                print("Level 1 Complete!")
                level += 1
                level_spawn_time = None
                level_second_spawned = False
                enemies = []
    # Level 2: Bug
    elif level == 2:
        if not level_spawn_time:
            enemies = [{'pos': [20.0, -1.0, 0.0], 'alive': True, 'type': 'bug', 'collided': False}]
            level_spawn_time = now
            level_second_spawned = False
            level_complete = False
        elif not level_second_spawned and now - level_spawn_time > 3.0:
            enemies.append({'pos': [20.0, -1.0, 6.0], 'alive': True, 'type': 'bug', 'collided': False})
            level_second_spawned = True
        # Move bugs
        for enemy in enemies:
            if not enemy['alive']:
                continue
            dx = -20.0 - enemy['pos'][0]
            dz = cannon_z - enemy['pos'][2]
            dist = math.sqrt(dx*dx + dz*dz)
            if dist > 1.0:
                enemy['pos'][0] += 0.13 * dx / dist
                enemy['pos'][2] += 0.13 * dz / dist
                enemy['collided'] = False
            else:
                if not enemy.get('collided', False):
                    player_life -= 2
                    enemy['collided'] = True
                    print("Bug reached the cannon! Player life:", player_life)
        # Level complete check
        if all(not e['alive'] or e.get('collided', False) for e in enemies) and level_second_spawned:
            if not level_complete:
                level_complete = True
                print("Level 2 Complete!")
                level += 1
                level_spawn_time = None
                level_second_spawned = False
                enemies = []
    # Level 3: Archer
    elif level == 3:
        if not level_spawn_time:
            enemies = [{'pos': [20.0, -1.0, 0.0], 'alive': True, 'type': 'archer', 'walk_timer': 0.0, 'shoot_timer': 0.0, 'walking': True, 'arrows': [], 'collided': False}]
            level_spawn_time = now
            level_second_spawned = False
            level_complete = False
        elif not level_second_spawned and now - level_spawn_time > 3.0:
            enemies.append({'pos': [20.0, -1.0, 6.0], 'alive': True, 'type': 'archer', 'walk_timer': 0.0, 'shoot_timer': 0.0, 'walking': True, 'arrows': [], 'collided': False})
            level_second_spawned = True
        # Move archers and handle shooting
        for enemy in enemies:
            if not enemy['alive']:
                continue
            # Walk 2s, stop 3s, shoot
            enemy['walk_timer'] += 0.016
            if enemy['walking']:
                if enemy['walk_timer'] < 2.0:
                    dx = -20.0 - enemy['pos'][0]
                    dz = cannon_z - enemy['pos'][2]
                    dist = math.sqrt(dx*dx + dz*dz)
                    if dist > 1.0:
                        enemy['pos'][0] += 0.06 * dx / dist
                        enemy['pos'][2] += 0.06 * dz / dist
                        enemy['collided'] = False
                    else:
                        if not enemy.get('collided', False):
                            player_life -= 2
                            enemy['collided'] = True
                            print("Archer reached the cannon! Player life:", player_life)
                else:
                    enemy['walking'] = False
                    enemy['walk_timer'] = 0.0
            else:
                enemy['shoot_timer'] += 0.016
                if enemy['shoot_timer'] > 3.0:
                    # Shoot arrow at cannon
                    dx = -20.0 - enemy['pos'][0]
                    dz = cannon_z - enemy['pos'][2]
                    dist = math.sqrt(dx*dx + dz*dz)
                    arrow = {'x': enemy['pos'][0], 'y': 1.5, 'z': enemy['pos'][2], 'dx': dx/dist, 'dz': dz/dist, 'alive': True}
                    enemy['arrows'].append(arrow)
                    enemy['shoot_timer'] = 0.0
                    enemy['walking'] = True
        # Update archer arrows
        for enemy in enemies:
            if enemy['type'] == 'archer':
                for arrow in enemy['arrows']:
                    if not arrow['alive']:
                        continue
                    arrow['x'] += arrow['dx'] * 0.5
                    arrow['z'] += arrow['dz'] * 0.5
                    # Check if hit cannon
                    if abs(arrow['x'] - -20.0) < 1.0 and abs(arrow['z'] - cannon_z) < 1.0:
                        player_life -= 1
                        arrow['alive'] = False
                        print("Archer arrow hit the cannon! Player life:", player_life)
        # Level complete check
        if all(not e['alive'] or e.get('collided', False) for e in enemies) and level_second_spawned:
            if not level_complete:
                level_complete = True
                print("Level 3 Complete!")
                level += 1
                level_spawn_time = None
                level_second_spawned = False
                enemies = []
    # Level 4: Boss
    elif level == 4:
        if not level_spawn_time:
            enemies = [{'pos': [20.0, -1.0, 0.0], 'alive': True, 'type': 'boss', 'projectiles': [], 'collided': False}]
            level_spawn_time = now
            level_complete = False
        # Move boss
        for enemy in enemies:
            if not enemy['alive']:
                continue
            dx = -20.0 - enemy['pos'][0]
            dz = cannon_z - enemy['pos'][2]
            dist = math.sqrt(dx*dx + dz*dz)
            if dist > 1.0:
                enemy['pos'][0] += 0.18 * dx / dist
                enemy['pos'][2] += 0.18 * dz / dist
                enemy['collided'] = False
            else:
                if not enemy.get('collided', False):
                    player_life -= 5
                    enemy['collided'] = True
                    print("Boss reached the cannon! Player life:", player_life)
            # Boss shoots projectiles every 1s
            if int(now*2) % 2 == 0 and len(enemy['projectiles']) < 3:
                for i in range(3):
                    angle = math.radians(-20 + i*20)
                    dx_proj = math.sin(angle)
                    dz_proj = math.cos(angle)
                    proj = {'x': enemy['pos'][0], 'y': 1.5, 'z': enemy['pos'][2], 'dx': dx_proj, 'dz': dz_proj, 'alive': True}
                    enemy['projectiles'].append(proj)
        # Update boss projectiles
        for enemy in enemies:
            if enemy['type'] == 'boss':
                for proj in enemy['projectiles']:
                    if not proj['alive']:
                        continue
                    proj['x'] += proj['dx'] * 0.7
                    proj['z'] += proj['dz'] * 0.7
                    if abs(proj['x'] - -20.0) < 1.0 and abs(proj['z'] - cannon_z) < 1.0:
                        player_life -= 2
                        proj['alive'] = False
                        print("Boss projectile hit the cannon! Player life:", player_life)
        # Level complete check
        if all(not e['alive'] or e.get('collided', False) for e in enemies):
            if not level_complete:
                level_complete = True
                print("Level 4 Complete! YOU WIN!")
                # Optionally, end game or restart
    # --- BULLET UPDATE ---
    for bullet in bullets:
        if not bullet['alive']:
            continue
        bullet['x'] += bullet['vx']
        bullet['y'] += bullet['vy']
        bullet['z'] += bullet['vz']
        # Out of arena bounds
        if bullet['x'] < -25 or bullet['x'] > 25 or bullet['z'] < -15 or bullet['z'] > 15 or bullet['y'] < -2 or bullet['y'] > 30:
            bullet['alive'] = False
    # --- BULLET-ENEMY COLLISION ---
    for enemy in enemies:
        if not enemy['alive']:
            continue
        for bullet in bullets:
            if not bullet['alive']:
                continue
            dx = bullet['x'] - enemy['pos'][0]
            dz = bullet['z'] - enemy['pos'][2]
            dy = bullet['y'] - 0.0
            if dx*dx + dy*dy + dz*dz < 1.2:  # Hit radius
                enemy['alive'] = False
                bullet['alive'] = False
                score += 100
                print(f"{enemy['type'].capitalize()} killed by bullet! Score: {score}")
    # --- GAME OVER CHECK ---
    if player_life <= 0:
        print("\n==================== GAME OVER ====================")
        print(f"Final Score: {score}")
        print(f"Level Reached: {level}")
        print("Better luck next time!")
        sys.exit(0)
    # --- GAME WIN CHECK ---
    if level == 4 and level_complete:
        print("\n==================== YOU WIN! ====================")
        print(f"Final Score: {score}")
        print(f"All levels completed!")
        sys.exit(0)

    glutPostRedisplay()


# Keyboard handler (top-level, not inside idle)
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
    # CANNON CONTROLS
    elif key == b'w':  # Move camera up
        camera_height += camera_move_speed
    elif key == b's':  # Move camera down
        camera_height = max(5.0, camera_height - camera_move_speed)
    elif key == b'j' or key == b'J':  # Move cannon down along length side
        move_cannon_down()
    elif key == b'k' or key == b'K':  # Move cannon up along length side
        move_cannon_up()
    elif key == b'o' or key == b'O':  # Tilt cannon up
        tilt_cannon_up()
    elif key == b'i' or key == b'I':  # Tilt cannon down
        tilt_cannon_down()
    elif key == b'a' or key == b'A':  # Camera left (same as left arrow)
        camera_angle -= camera_move_speed
    elif key == b'd' or key == b'D':  # Camera right (same as right arrow)
        camera_angle += camera_move_speed
    elif key == b'f' or key == b'F':  # FIRE bomb
        create_bomb()
    elif key == b'y' or key == b'Y':  # Shoot bullet
        # Bullet spawns at cannon barrel tip, flies forward (X direction)
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


def special_keys(key, x, y):
    """Handle special keys for camera movement and zoom control"""
    global camera_distance, camera_angle, camera_height, camera_move_speed
    if key == GLUT_KEY_LEFT:  # Rotate camera left (same as 'a')
        camera_angle -= camera_move_speed
    elif key == GLUT_KEY_RIGHT:  # Rotate camera right (same as 'd')
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
    glutCreateWindow(b"Arena Strike - 3D Arena with Cannon")
    
    init()
    
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutReshapeFunc(reshape)
    
    print("=== ARENA STRIKE - 3D Arena with Cannon & Bombs ===")
    print()
    print("🎮 CAMERA CONTROLS:")
    print("- ARROW KEYS: Rotate camera / Zoom in-out")
    print("- W/S keys: Move camera up/down")
    print("- +/- keys: Additional zoom")
    print("- SPACE: Manual camera rotation")
    print()
    print("🎯 CANNON CONTROLS:")
    print("- J key: Move cannon DOWN along length side")
    print("- K key: Move cannon UP along length side") 
    print("- O key: Tilt cannon barrel UP")
    print("- I key: Tilt cannon barrel DOWN")
    print("- C key: Toggle AIM (dotted line sight)")
    print("- F key: FIRE BOMB! 💣")
    print()
    print("📋 FEATURES:")
    print("✓ Cannon positioned at length side of arena")
    print("✓ Smooth up/down movement along arena length")
    print("✓ Up/down barrel tilting (0° to 90°)")
    print("✓ Dotted aiming line with crosshair target")
    print("✓ Bomb shooting with realistic physics")
    print("✓ Gravity and collision detection")
    print("✓ Explosion effects when bombs hit ground")
    print("✓ Animated audience in 3D gallery")
    print("✓ Dynamic lighting and atmosphere")
    print("✓ Football field arena layout")
    print()
    print("🎲 Instructions:")
    print("1. Use J/K to position the cannon along the length")
    print("2. Use O/I to aim the cannon up/down")
    print("3. Press C to see your aiming line")
    print("4. Press F to FIRE bombs!")
    print("5. The red dotted line shows where you're aiming")
    print("6. Yellow crosshair marks the target point")
    print("7. Watch bombs fly with realistic physics!")
    print()
    print("- Press 'q' or ESC to quit")
    
    glutMainLoop()

if __name__ == '__main__':
    main()