# arena_strike_landing.py
# Fixed Game Landing Page with proper text rendering and full arena
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
import time

# Import the existing modules
try:
    from arena_model import *
    from GoldBox import draw_ring, ring_data, generate_ring_data
except ImportError:
    print("Error: Make sure arena_model.py and GoldBox.py are in the same directory!")
    sys.exit(1)

# Game states
MENU = 0
SETTINGS = 1
PLAYING = 2
current_state = MENU

# Animation variables
arena_rotation = 0
logo_blink_time = 0
menu_selection = 0
selection_time = 0
show_selection_box = False
cheer_time = 0

# Generate audience data
audience_data = generate_audience()

def init():
    glClearColor(0.05, 0.05, 0.15, 1.0)  # Dark blue background
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Dramatic lighting
    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 30.0, 20.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.4, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.2, 1.0])
    
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 1.333, 1.0, 300.0)
    glMatrixMode(GL_MODELVIEW)
    
    # Initialize golden ring data for selection effect
    generate_ring_data()

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

def draw_arena_complete():
    """Draw the complete arena with all components"""
    global cheer_time
    
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

def draw_blinking_logo():
    """Draw the Arena Strike logo with blinking effect"""
    blink_intensity = 0.7 + 0.3 * abs(math.sin(logo_blink_time * 4))
    
    # Golden blinking color
    glColor3f(1.0 * blink_intensity, 0.8 * blink_intensity, 0.2 * blink_intensity)
    
    # "ARENA STRIKE" text representation
    render_text_as_cubes("ARENA STRIKE", 0, 35, -5, 2.5)
    
    # Add glow effect
    glColor4f(1.0, 0.8, 0.0, 0.2 * blink_intensity)
    render_text_as_cubes("ARENA STRIKE", 0, 35, -4, 3.0)

def draw_selection_golden_effect():
    """Draw golden treasure box effect when option is selected"""
    if not show_selection_box or menu_selection == 0:
        return
    
    # Position based on selected menu option
    option_positions = [18, 10, 2]  # Y positions for Play, Settings, Quit
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

def draw_main_menu():
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

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    if current_state == MENU:
        # Main menu camera
        gluLookAt(0, 25, 60,   # Camera position
                  0, 15, 0,    # Look at point
                  0, 1, 0)     # Up vector
        
        # Draw rotating arena (dimmed for background)
        glColor4f(0.6, 0.6, 0.7, 0.8)
        draw_arena_complete()
        
        # Draw blinking logo
        draw_blinking_logo()
        
        # Draw menu options
        draw_main_menu()
        
        # Draw golden selection effect
        draw_selection_golden_effect()
        
    elif current_state == SETTINGS:
        gluLookAt(0, 20, 40, 0, 15, 0, 0, 1, 0)
        
        # Dimmed arena background
        glColor4f(0.4, 0.4, 0.5, 0.6)
        glPushMatrix()
        glRotatef(arena_rotation * 0.2, 0, 1, 0)
        draw_arena_complete()
        glPopMatrix()
        
        draw_settings_menu()
        
    elif current_state == PLAYING:
        # Game camera - closer to action
        gluLookAt(0, 15, 40, 0, 5, 0, 0, 1, 0)
        
        # Full brightness arena
        glColor3f(1.0, 1.0, 1.0)
        draw_arena_complete()
        
        # Game started message
        glDisable(GL_LIGHTING)
        glLineWidth(4.0)
        glColor3f(0.2, 1.0, 0.2)
        render_text_3d("GAME STARTED!", 0, 30, 0)
        glLineWidth(2.0)
        glColor3f(1.0, 1.0, 0.5)
        render_text_3d("Press ESC for menu", 0, 22, 0)
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
    
    glutSwapBuffers()

def update_animations():
    """Update all animation variables"""
    global arena_rotation, logo_blink_time, cheer_time, selection_time, show_selection_box
    
    current_time = glutGet(GLUT_ELAPSED_TIME) * 0.001
    
    # Arena rotation
    arena_rotation += 0.5
    arena_rotation %= 360
    
    # Logo blinking
    logo_blink_time = current_time
    
    # Audience cheering
    cheer_time = current_time
    
    # Selection box timing
    if menu_selection > 0:
        if current_time - selection_time < 0.5:
            show_selection_box = True
        else:
            show_selection_box = False
            execute_selection()

def execute_selection():
    """Execute the selected menu option"""
    global current_state, menu_selection
    
    if menu_selection == 1:  # Play
        current_state = PLAYING
        print("Game Started!")
    elif menu_selection == 2:  # Settings
        current_state = SETTINGS
        print("Entered Settings")
    elif menu_selection == 3:  # Quit
        print("Thanks for playing Arena Strike!")
        glutLeaveMainLoop()
    
    menu_selection = 0

def keyboard(key, x, y):
    """Handle keyboard input"""
    global menu_selection, selection_time, current_state
    
    if current_state == MENU:
        if key == b'1':
            menu_selection = 1
            selection_time = glutGet(GLUT_ELAPSED_TIME) * 0.001
            print("Selected: Play")
        elif key == b'2':
            menu_selection = 2
            selection_time = glutGet(GLUT_ELAPSED_TIME) * 0.001
            print("Selected: Settings")
        elif key == b'3':
            menu_selection = 3
            selection_time = glutGet(GLUT_ELAPSED_TIME) * 0.001
            print("Selected: Quit")
    
    elif current_state in [SETTINGS, PLAYING]:
        if key == b'\x1b':  # ESC key
            current_state = MENU
            print("Returned to main menu")

def idle():
    """Continuous animation updates"""
    update_animations()
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1024, 768)
    glutCreateWindow(b"Arena Strike - Epic Landing Page")
    
    init()
    
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)
    
    print("\n" + "="*50)
    print("      🏟️  ARENA STRIKE - EPIC BATTLES AWAIT  🏟️")
    print("="*50)
    print("📋 CONTROLS:")
    print("   [1] ➤ Play Game")
    print("   [2] ➤ Settings Menu") 
    print("   [3] ➤ Quit Game")
    print("   [ESC] ➤ Back to Menu")
    print("="*50)
    print("🎮 Ready for battle! Press 1, 2, or 3 to begin...")
    print("="*50 + "\n")
    
    glutMainLoop()

if __name__ == '__main__':
    main()