import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from assets.arena_model import *

def render_text_as_cubes(text, x, y, z, scale=1.0):
    """Render text as colored cubes representing letters"""
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(scale, scale, scale)
    
    # Each character is represented as a small cube
    char_width = 1.5
    for i, char in enumerate(text):
        if char == ' ':
            continue
        glPushMatrix()
        glTranslatef(i * char_width - len(text) * char_width * 0.5, 0, 0)
        glScalef(1.0, 1.5, 0.3)
        glutSolidCube(1.0)
        glPopMatrix()
    glPopMatrix()

def draw_blinking_logo(logo_blink_time):
    """Draw the Arena Strike logo with blinking effect"""
    blink_intensity = 0.7 + 0.3 * abs(math.sin(logo_blink_time * 4))
    
    # Golden blinking color
    glColor3f(1.0 * blink_intensity, 0.8 * blink_intensity, 0.2 * blink_intensity)
    
    # "ARENA STRIKE" text representation
    render_text_as_cubes("ARENA STRIKE", 0, 35, -5, 2.5)
    
    # Add glow effect
    glColor4f(1.0, 0.8, 0.0, 0.2 * blink_intensity)
    render_text_as_cubes("ARENA STRIKE", 0, 35, -4, 3.0)

def draw_selection_golden_effect(show_selection_box, menu_selection, option_positions):
    """Draw golden treasure box effect when option is selected"""
    if not show_selection_box or menu_selection == 0:
        return
    
    # Position based on selected menu option
    box_y = option_positions[menu_selection - 1]
    
    current_time = glutGet(GLUT_ELAPSED_TIME) * 0.001
    
    # Draw spinning golden rings around selection
    glColor3f(1.0, 0.84, 0.0)  # Gold color
    
    for i in range(20):
        angle = (i / 20.0) * 360 + current_time * 150
        radius = 8 + math.sin(current_time * 3 + i) * 1
        rad = math.radians(angle)
        
        ring_x = radius * math.cos(rad)
        ring_z = -10 + radius * math.sin(rad) * 0.3
        ring_y = box_y + math.sin(current_time * 4 + i) * 2
        
        glPushMatrix()
        glTranslatef(ring_x, ring_y, ring_z)
        glRotatef(current_time * 200 + i * 18, 0, 1, 0)
        glutSolidTorus(0.3, 0.8, 8, 16)
        glPopMatrix()

def draw_main_menu(menu_selection):
    """Draw the main menu with properly positioned options"""
    menu_items = [
        ("Play [1]", 18),
        ("Settings [2]", 10), 
        ("Quit [3]", 2)
    ]
    
    for i, (text, y_pos) in enumerate(menu_items):
        # Highlight selected option
        if menu_selection == i + 1:
            glColor3f(1.0, 0.8, 0.2)  # Golden highlight
        else:
            glColor3f(0.9, 0.9, 1.0)  # White text
        
        render_text_as_cubes(text, 0, y_pos, -8, 1.8)

def draw_settings_menu():
    """Draw settings menu"""
    glColor3f(1.0, 1.0, 0.8)
    render_text_as_cubes("SETTINGS", 0, 25, -5, 2.0)
    
    settings_options = [
        "Sound: ON",
        "Graphics: HIGH",
        "Difficulty: MEDIUM", 
        "Press ESC to return"
    ]
    
    glColor3f(0.8, 0.8, 0.9)
    for i, option in enumerate(settings_options):
        render_text_as_cubes(option, 0, 15 - i * 5, -6, 1.2)

def draw_arena_complete(arena_rotation, audience_data, cheer_time):
    """Draw the complete arena with all components"""
    glPushMatrix()
    glRotatef(arena_rotation, 0, 1, 0)
    
    # Draw arena floor
    draw_arena_floor()
    
    # Draw gallery structure
    draw_gallery_structure()
    
    # Draw audience with cheering animation
    draw_audience(audience_data, cheer_time)
    
    # Draw arena lights
    draw_arena_lights()
    
    # Draw roof structure
    draw_roof_structure()
    
    # Draw atmosphere effects
    draw_atmosphere_effects(cheer_time)
    
    glPopMatrix()

def update_animations(arena_rotation, logo_blink_time, cheer_time, selection_time, show_selection_box, menu_selection):
    """Update all animation variables"""
    current_time = glutGet(GLUT_ELAPSED_TIME) * 0.001
    
    # Arena rotation
    arena_rotation[0] += 0.5
    arena_rotation[0] %= 360
    
    # Logo blinking
    logo_blink_time[0] = current_time
    
    # Audience cheering
    cheer_time[0] = current_time
    
    # Selection box timing
    if menu_selection[0] > 0:
        if current_time - selection_time[0] < 0.5:
            show_selection_box[0] = True
        else:
            show_selection_box[0] = False
            # Note: execute_selection should be called elsewhere
