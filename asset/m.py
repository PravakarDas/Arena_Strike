from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
import random

# Import enemy models (assuming they're in the same directory)
try:
    import lvl1_stickyman
    import lvl2_bug
    import lvl3_archer
    import lvl4_boss
except ImportError as e:
    print(f"Error importing model files: {e}")
    print("Make sure all model files are in the same directory!")
    sys.exit(1)

# Game constants
ARENA_SIZE = 40.0
CANNON_SPEED = 0.4
ENEMY_SPAWN_DISTANCE = 35.0
COLLISION_DISTANCE = 2.5

# Global variables
camera_angle = 0.0
audience_data = []
num_audience = 150
cheer_time = 0.0
camera_distance = 35.0
zoom_speed = 2.0
camera_height = 24.0
camera_move_speed = 3.0

class GameState:
    def __init__(self):
        self.level = 1
        self.max_level = 4
        self.cannon_life = 20
        self.max_life = 20
        self.score = 0
        self.game_over = False
        self.level_complete = False
        self.game_won = False
        
        # Timing
        self.game_time = 0.0
        self.level_start_time = 0.0
        self.last_spawn_time = 0.0
        
        # Cannon position
        self.cannon_x = 0.0
        self.cannon_z = 0.0
        
        # Enemies
        self.enemies = []
        self.enemies_spawned_this_level = 0
        self.enemies_killed_this_level = 0
        
        # Level requirements
        self.enemies_per_level = {1: 2, 2: 2, 3: 2, 4: 1}
        
        # Input
        self.keys = set()
        
    def reset_level(self):
        """Reset for new level"""
        self.enemies.clear()
        self.enemies_spawned_this_level = 0
        self.enemies_killed_this_level = 0
        self.level_start_time = self.game_time
        self.last_spawn_time = self.game_time
        self.level_complete = False
        print(f"\n=== LEVEL {self.level} STARTED ===")
        self.print_level_info()
    
    def print_level_info(self):
        """Print level-specific information"""
        level_info = {
            1: "STICKMAN SOLDIERS - They walk towards you!",
            2: "FLYING BUGS - They fly fast towards you!",
            3: "ARCHERS - They walk slowly and shoot arrows!",
            4: "DEMON QUEEN BOSS - Fast flying with continuous attacks!"
        }
        print(f"Enemies: {level_info.get(self.level, 'Unknown')}")
        print(f"Enemies to defeat: {self.enemies_per_level[self.level]}")
        print(f"Life remaining: {self.cannon_life}/{self.max_life}")

class Enemy:
    def __init__(self, enemy_type, x, z, target_x, target_z):
        self.type = enemy_type
        self.x = x
        self.y = 0.0
        self.z = z
        self.target_x = target_x
        self.target_z = target_z
        self.health = 1
        self.alive = True
        self.animation_time = 0.0
        
        # Type-specific properties
        if enemy_type == 1:  # Stickman
            self.speed = 0.08
            self.damage = 2
            self.flying = False
        elif enemy_type == 2:  # Bug
            self.speed = 0.12
            self.damage = 2
            self.flying = True
            self.y = 2.0  # Flying height
        elif enemy_type == 3:  # Archer
            self.speed = 0.04
            self.damage = 2
            self.flying = False
            self.last_shot_time = 0.0
            self.walking = True
            self.walk_pause_time = 0.0
        elif enemy_type == 4:  # Boss
            self.speed = 0.10
            self.damage = 5
            self.flying = True
            self.y = 3.0
            self.health = 3  # Boss has more health
    
    def update(self, dt, cannon_x, cannon_z, game_time):
        """Update enemy position and behavior"""
        if not self.alive:
            return
        
        self.animation_time += dt
        
        # Update target position to cannon's current position
        self.target_x = cannon_x
        self.target_z = cannon_z
        
        # Calculate direction to cannon
        dx = self.target_x - self.x
        dz = self.target_z - self.z
        distance = math.sqrt(dx*dx + dz*dz)
        
        if distance > 0.1:  # Avoid division by zero
            # Normalize direction
            dx /= distance
            dz /= distance
            
            # Type-specific behavior
            if self.type == 3:  # Archer special behavior
                self.update_archer_behavior(dx, dz, dt, game_time)
            else:
                # Move towards cannon
                self.x += dx * self.speed
                self.z += dz * self.speed
        
        # Keep enemies within arena bounds (football field size)
        max_pos = 18  # Within the green field area
        self.x = max(-max_pos, min(max_pos, self.x))
        self.z = max(-12, min(12, self.z))  # Football field is narrower
    
    def update_archer_behavior(self, dx, dz, dt, game_time):
        """Special behavior for archer: walk 2 seconds, pause 3 seconds to shoot"""
        if self.walking:
            # Walk towards cannon
            self.x += dx * self.speed
            self.z += dz * self.speed
            
            # Check if walked for 2 seconds
            if self.animation_time - self.walk_pause_time >= 2.0:
                self.walking = False
                self.walk_pause_time = self.animation_time
                self.last_shot_time = game_time
        else:
            # Paused for shooting - don't move
            # Check if paused for 3 seconds
            if self.animation_time - self.walk_pause_time >= 3.0:
                self.walking = True
                self.walk_pause_time = self.animation_time
    
    def get_distance_to_cannon(self, cannon_x, cannon_z):
        """Get distance to cannon for collision detection"""
        dx = self.x - cannon_x
        dz = self.z - cannon_z
        return math.sqrt(dx*dx + dz*dz)
    
    def render(self):
        """Render the enemy using appropriate model"""
        if not self.alive:
            return
        
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        # Face towards cannon (optional rotation)
        if hasattr(self, 'target_x') and hasattr(self, 'target_z'):
            dx = self.target_x - self.x
            dz = self.target_z - self.z
            if abs(dx) > 0.01 or abs(dz) > 0.01:
                angle = math.degrees(math.atan2(dx, dz))
                glRotatef(angle, 0, 1, 0)
        
        # Render based on type
        try:
            if self.type == 1:
                lvl1_stickyman.draw_stickman(self.animation_time)
            elif self.type == 2:
                lvl2_bug.draw_bug(self.animation_time)
            elif self.type == 3:
                lvl3_archer.draw_archer(self.animation_time)
            elif self.type == 4:
                lvl4_boss.draw_boss_demon_queen(self.animation_time)
        except Exception as e:
            # Fallback: draw a simple colored cube if model fails
            glColor3f(1.0, 0.0, 0.0)
            glutSolidCube(2.0)
        
        glPopMatrix()

# Global game state
game_state = GameState()

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
    
    # Start first level
    game_state.reset_level()

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

def draw_cannon():
    """Draw the player's cannon"""
    glPushMatrix()
    glTranslatef(game_state.cannon_x, 0, game_state.cannon_z)
    
    # Cannon base
    glColor3f(0.2, 0.4, 0.2)  # Dark green military color
    glutSolidCylinder(1.2, 0.8, 16, 16)
    
    # Cannon barrel
    glPushMatrix()
    glTranslatef(0, 0.8, 0)
    glRotatef(-30, 1, 0, 0)
    glColor3f(0.3, 0.5, 0.3)  # Lighter green
    glutSolidCylinder(0.4, 3.0, 16, 16)
    
    # Barrel tip
    glTranslatef(0, 0, 3.0)
    glColor3f(0.1, 0.2, 0.1)
    glutSolidCone(0.4, 0.3, 16, 16)
    glPopMatrix()
    
    glPopMatrix()

def update_game(dt):
    """Main game update logic"""
    if game_state.game_over or game_state.game_won:
        return
    
    game_state.game_time += dt
    
    # Handle cannon movement
    update_cannon_movement(dt)
    
    # Spawn enemies
    spawn_enemies()
    
    # Update enemies
    for enemy in game_state.enemies[:]:  # Copy list to avoid modification during iteration
        enemy.update(dt, game_state.cannon_x, game_state.cannon_z, game_state.game_time)
        
        # Check collision with cannon
        if enemy.get_distance_to_cannon(game_state.cannon_x, game_state.cannon_z) < COLLISION_DISTANCE:
            handle_enemy_collision(enemy)
    
    # Check level completion
    check_level_completion()
    
    # Print game status periodically
    if int(game_state.game_time) != int(game_state.game_time - dt):
        print_game_status()

def update_cannon_movement(dt):
    """Handle cannon movement with WASD keys"""
    move_x = 0
    move_z = 0
    
    if b'w' in game_state.keys or b'W' in game_state.keys:
        move_z -= 1
    if b's' in game_state.keys or b'S' in game_state.keys:
        move_z += 1
    if b'a' in game_state.keys or b'A' in game_state.keys:
        move_x -= 1
    if b'd' in game_state.keys or b'D' in game_state.keys:
        move_x += 1
    
    # Normalize diagonal movement
    if move_x != 0 and move_z != 0:
        move_x *= 0.707
        move_z *= 0.707
    
    # Apply movement
    game_state.cannon_x += move_x * CANNON_SPEED
    game_state.cannon_z += move_z * CANNON_SPEED
    
    # Keep cannon within football field bounds
    max_x = 18  # Football field width
    max_z = 10  # Football field length
    game_state.cannon_x = max(-max_x, min(max_x, game_state.cannon_x))
    game_state.cannon_z = max(-max_z, min(max_z, game_state.cannon_z))

def spawn_enemies():
    """Spawn enemies according to level rules"""
    current_time = game_state.game_time
    time_since_level_start = current_time - game_state.level_start_time
    time_since_last_spawn = current_time - game_state.last_spawn_time
    
    max_enemies = game_state.enemies_per_level[game_state.level]
    
    # Check if we should spawn an enemy
    should_spawn = False
    
    if game_state.enemies_spawned_this_level == 0:
        # Spawn first enemy immediately
        should_spawn = True
    elif (game_state.enemies_spawned_this_level < max_enemies and 
          time_since_last_spawn >= 3.0):  # 3 second delay between spawns
        should_spawn = True
    
    if should_spawn:
        spawn_enemy(game_state.level)
        game_state.enemies_spawned_this_level += 1
        game_state.last_spawn_time = current_time

def spawn_enemy(enemy_type):
    """Spawn a single enemy at the opposite side of the arena"""
    # Spawn on opposite side of arena from cannon
    cannon_distance_from_center = math.sqrt(game_state.cannon_x**2 + game_state.cannon_z**2)
    
    if cannon_distance_from_center > 1.0:
        # Spawn on opposite side from cannon
        spawn_x = -game_state.cannon_x * 1.8
        spawn_z = -game_state.cannon_z * 1.8
    else:
        # If cannon is near center, spawn randomly on edge
        angle = random.uniform(0, 2 * math.pi)
        spawn_x = 15 * math.cos(angle)
        spawn_z = 10 * math.sin(angle)
    
    # Ensure spawn position is within reasonable bounds but outside the field
    max_spawn_x = 20
    max_spawn_z = 15
    spawn_x = max(-max_spawn_x, min(max_spawn_x, spawn_x))
    spawn_z = max(-max_spawn_z, min(max_spawn_z, spawn_z))
    
    enemy = Enemy(enemy_type, spawn_x, spawn_z, game_state.cannon_x, game_state.cannon_z)
    game_state.enemies.append(enemy)
    
    print(f"Spawned level {enemy_type} enemy at ({spawn_x:.1f}, {spawn_z:.1f})")

def handle_enemy_collision(enemy):
    """Handle when enemy collides with cannon"""
    if enemy.alive:
        game_state.cannon_life -= enemy.damage
        enemy.alive = False
        
        print(f"COLLISION! Enemy dealt {enemy.damage} damage. Life: {game_state.cannon_life}/{game_state.max_life}")
        
        if game_state.cannon_life <= 0:
            game_state.game_over = True
            print("GAME OVER! Cannon destroyed!")
            return

def handle_enemy_death(enemy):
    """Handle when enemy is killed (for future projectile system)"""
    if enemy.alive:
        enemy.alive = False
        game_state.enemies_killed_this_level += 1
        game_state.score += 100 * game_state.level  # More points for higher levels
        print(f"Enemy killed! Score: {game_state.score}")

def check_level_completion():
    """Check if current level is complete"""
    if game_state.level_complete:
        return
    
    required_kills = game_state.enemies_per_level[game_state.level]
    
    # Check if all enemies for this level have been killed or collided
    alive_enemies = sum(1 for enemy in game_state.enemies if enemy.alive)
    total_spawned = game_state.enemies_spawned_this_level
    
    if (total_spawned >= required_kills and alive_enemies == 0):
        complete_level()

def complete_level():
    """Complete current level and advance to next"""
    game_state.level_complete = True
    game_state.score += 500 * game_state.level  # Bonus for completing level
    
    print(f"\n*** LEVEL {game_state.level} COMPLETE! ***")
    print(f"Score: {game_state.score}")
    
    if game_state.level >= game_state.max_level:
        game_state.game_won = True
        print("CONGRATULATIONS! YOU WON THE GAME!")
        print("🎉 The crowd goes wild! You are the Arena Champion! 🎉")
        return
    
    # Advance to next level
    game_state.level += 1
    game_state.reset_level()

def print_game_status():
    """Print current game status"""
    alive_enemies = sum(1 for enemy in game_state.enemies if enemy.alive)
    print(f"Level {game_state.level} | Life: {game_state.cannon_life}/{game_state.max_life} | "
          f"Score: {game_state.score} | Enemies: {alive_enemies} | "
          f"Killed: {game_state.enemies_killed_this_level}/{game_state.enemies_per_level[game_state.level]}")

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

def display():
    global cheer_time, camera_distance, camera_height
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Camera follows cannon with some offset for better view
    if not game_state.game_over and not game_state.game_won:
        # Dynamic camera that follows cannon
        cam_offset_x = 15.0
        cam_offset_z = 20.0
        cam_x = game_state.cannon_x + cam_offset_x
        cam_z = game_state.cannon_z + cam_offset_z
        cam_y = camera_height
        
        # Look at cannon
        gluLookAt(cam_x, cam_y, cam_z,
                 game_state.cannon_x, 2, game_state.cannon_z,
                 0, 1, 0)
    else:
        # Game over or won - show full arena view
        cam_x = camera_distance * math.sin(math.radians(camera_angle))
        cam_z = camera_distance * math.cos(math.radians(camera_angle))
        
        gluLookAt(cam_x, camera_height, cam_z,
                  0, 6, 0,
                  0, 1, 0)
    
    # Draw all arena components
    draw_arena_floor()
    draw_gallery_structure()
    draw_audience()
    draw_arena_lights()
    draw_roof_structure()
    
    # Add atmospheric effects
    draw_atmosphere_effects()
    
    # Draw game elements
    draw_cannon()
    
    # Draw enemies
    for enemy in game_state.enemies:
        enemy.render()
    
    # Draw game status on screen (simple text substitutes)
    draw_game_ui()
    
    glutSwapBuffers()

def draw_game_ui():
    """Draw simple UI elements in 3D space"""
    glDisable(GL_LIGHTING)
    
    # Health indicator - red spheres above cannon
    glPushMatrix()
    glTranslatef(game_state.cannon_x, 6, game_state.cannon_z)
    
    # Life indicator
    life_ratio = game_state.cannon_life / game_state.max_life
    glColor3f(1.0 - life_ratio, life_ratio, 0.0)  # Red to green based on health
    for i in range(int(game_state.cannon_life)):
        glPushMatrix()
        glTranslatef((i % 10) * 0.3 - 1.5, (i // 10) * 0.3, 0)
        draw_sphere(0.1)
        glPopMatrix()
    
    glPopMatrix()
    
    # Level indicator - floating text substitute with colored spheres
    glPushMatrix()
    glTranslatef(0, 25, 0)  # High above arena center
    
    # Level indicator spheres
    glColor3f(0.0, 0.8, 1.0)  # Cyan
    for i in range(game_state.level):
        glPushMatrix()
        glTranslatef(i * 2 - game_state.level, 0, 0)
        draw_sphere(0.5)
        glPopMatrix()
    
    # Game status indicators
    if game_state.game_won:
        # Victory celebration - golden spheres
        glColor3f(1.0, 0.8, 0.0)  # Gold
        for i in range(8):
            angle = i * 45
            x = 3 * math.cos(math.radians(angle))
            z = 3 * math.sin(math.radians(angle))
            glPushMatrix()
            glTranslatef(x, math.sin(cheer_time * 3 + i) * 2, z)
            draw_sphere(0.8)
            glPopMatrix()
    elif game_state.game_over:
        # Game over - red warning spheres
        glColor3f(1.0, 0.0, 0.0)  # Red
        for i in range(4):
            glPushMatrix()
            glTranslatef(0, math.sin(cheer_time * 5 + i) * 1, i * 2 - 3)
            draw_sphere(0.6)
            glPopMatrix()
    
    glPopMatrix()
    
    glEnable(GL_LIGHTING)

def idle():
    global cheer_time, camera_angle
    
    dt = 0.02
    cheer_time += 0.05  # Keep audience movement
    
    # Update game logic
    update_game(dt)
    
    # Slow camera rotation when game is over for dramatic effect
    if game_state.game_over or game_state.game_won:
        camera_angle += 0.3
        if camera_angle >= 360:
            camera_angle = 0
    
    glutPostRedisplay()

def keyboard(key, x, y):
    global camera_distance, camera_angle, camera_height
    
    # Add key to pressed keys set
    game_state.keys.add(key)
    
    if key == b'q' or key == b'\x1b':  # 'q' or ESC to quit
        print("Game quit by user")
        sys.exit(0)
    elif key == b' ':  # Space for manual enemy kill (cheat for testing)
        if game_state.enemies:
            enemy = next((e for e in game_state.enemies if e.alive), None)
            if enemy:
                handle_enemy_death(enemy)
                print("Cheat used: Enemy eliminated!")
    elif key == b'r' or key == b'R':  # Restart game
        global game_state
        game_state = GameState()
        game_state.reset_level()
        print("Game restarted!")
    elif key == b'=':  # '+' key for zoom in
        camera_distance = max(20.0, camera_distance - zoom_speed)
    elif key == b'-':  # '-' key for zoom out
        camera_distance = min(150.0, camera_distance + zoom_speed)

def keyboard_up(key, x, y):
    """Handle key release"""
    game_state.keys.discard(key)

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
    glutInitWindowSize(1200, 900)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Arena Defense Game - Football Stadium")
    
    init()
    
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_keys)
    glutReshapeFunc(reshape)
    
    print("=" * 70)
    print("          🏟️  ARENA DEFENSE GAME  🏟️")
    print("=" * 70)
    print("🎮 CONTROLS:")
    print("   WASD - Move your cannon around the football field")
    print("   SPACE - Kill nearest enemy (testing cheat)")
    print("   R - Restart game")
    print("   Arrow Keys - Manual camera control")
    print("   +/- - Zoom in/out")
    print("   Q/ESC - Quit game")
    print("")
    print("🎯 GAME RULES:")
    print("   - Survive 4 levels in this magnificent stadium!")
    print("   - Enemies spawn from opposite side and chase your cannon")
    print("   - Avoid collisions to preserve your 20 life points")
    print("   - The crowd is watching - don't disappoint them!")
    print("")
    print("⚔️  ENEMY DAMAGE:")
    print("   - Level 1-3 enemies: 2 damage each")
    print("   - Level 4 boss: 5 damage")
    print("")
    print("🏆 LEVELS:")
    print("   1. Stickman Soldiers (2 enemies, walking)")
    print("   2. Flying Bugs (2 enemies, flying)")
    print("   3. Archers (2 enemies, walk + pause to shoot)")
    print("   4. Demon Queen Boss (1 enemy, fast flying + attacks)")
    print("")
    print("🎪 ARENA FEATURES:")
    print("   - Cheering animated crowd")
    print("   - Stadium lights and atmosphere")
    print("   - Professional football field layout")
    print("   - Dynamic camera following your cannon")
    print("=" * 70)
    print("🚀 Game starting... Good luck, Champion!")
    print("=" * 70)
    
    glutMainLoop()

if __name__ == '__main__':
    main()