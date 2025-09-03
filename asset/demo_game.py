from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
import random
import time

# Import enemy models (assuming they're in the same directory)
try:
    import lvl1_stickyman
    import lvl2_bug
    import lvl3_archer
    import lvl4_boss
    import arena
except ImportError as e:
    print(f"Error importing model files: {e}")
    print("Make sure all model files are in the same directory!")
    sys.exit(1)

# Game constants
ARENA_SIZE = 40.0
CANNON_SPEED = 0.3
ENEMY_SPAWN_DISTANCE = 35.0
COLLISION_DISTANCE = 2.0

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
        
        # Keep enemies within arena bounds
        max_pos = ARENA_SIZE / 2 - 2
        self.x = max(-max_pos, min(max_pos, self.x))
        self.z = max(-max_pos, min(max_pos, self.z))
    
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
        if self.type == 1:
            lvl1_stickyman.draw_stickman(self.animation_time)
        elif self.type == 2:
            lvl2_bug.draw_bug(self.animation_time)
        elif self.type == 3:
            lvl3_archer.draw_archer(self.animation_time)
        elif self.type == 4:
            lvl4_boss.draw_boss_demon_queen(self.animation_time)
        
        glPopMatrix()

class Game:
    def __init__(self):
        self.state = GameState()
        self.keys = set()
        
    def init_opengl(self):
        """Initialize OpenGL settings"""
        glClearColor(0.1, 0.15, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        
        # Set up lighting
        light_pos = [10.0, 15.0, 10.0, 1.0]
        light_ambient = [0.4, 0.4, 0.5, 1.0]
        light_diffuse = [0.8, 0.8, 0.9, 1.0]
        
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        
        glMatrixMode(GL_PROJECTION)
        gluPerspective(60, 1.0, 1.0, 200.0)
        glMatrixMode(GL_MODELVIEW)
        
        # Start first level
        self.state.reset_level()
    
    def update(self, dt):
        """Main game update loop"""
        if self.state.game_over or self.state.game_won:
            return
        
        self.state.game_time += dt
        
        # Handle cannon movement
        self.update_cannon_movement(dt)
        
        # Spawn enemies
        self.spawn_enemies()
        
        # Update enemies
        for enemy in self.state.enemies[:]:  # Copy list to avoid modification during iteration
            enemy.update(dt, self.state.cannon_x, self.state.cannon_z, self.state.game_time)
            
            # Check collision with cannon
            if enemy.get_distance_to_cannon(self.state.cannon_x, self.state.cannon_z) < COLLISION_DISTANCE:
                self.handle_enemy_collision(enemy)
        
        # Check level completion
        self.check_level_completion()
        
        # Print game status periodically
        if int(self.state.game_time) != int(self.state.game_time - dt):
            self.print_game_status()
    
    def update_cannon_movement(self, dt):
        """Handle cannon movement with WASD keys"""
        move_x = 0
        move_z = 0
        
        if b'w' in self.keys or b'W' in self.keys:
            move_z -= 1
        if b's' in self.keys or b'S' in self.keys:
            move_z += 1
        if b'a' in self.keys or b'A' in self.keys:
            move_x -= 1
        if b'd' in self.keys or b'D' in self.keys:
            move_x += 1
        
        # Normalize diagonal movement
        if move_x != 0 and move_z != 0:
            move_x *= 0.707
            move_z *= 0.707
        
        # Apply movement
        self.state.cannon_x += move_x * CANNON_SPEED
        self.state.cannon_z += move_z * CANNON_SPEED
        
        # Keep cannon within arena bounds
        max_pos = ARENA_SIZE / 2 - 3
        self.state.cannon_x = max(-max_pos, min(max_pos, self.state.cannon_x))
        self.state.cannon_z = max(-max_pos, min(max_pos, self.state.cannon_z))
    
    def spawn_enemies(self):
        """Spawn enemies according to level rules"""
        current_time = self.state.game_time
        time_since_level_start = current_time - self.state.level_start_time
        time_since_last_spawn = current_time - self.state.last_spawn_time
        
        max_enemies = self.state.enemies_per_level[self.state.level]
        
        # Check if we should spawn an enemy
        should_spawn = False
        
        if self.state.enemies_spawned_this_level == 0:
            # Spawn first enemy immediately
            should_spawn = True
        elif (self.state.enemies_spawned_this_level < max_enemies and 
              time_since_last_spawn >= 3.0):  # 3 second delay between spawns
            should_spawn = True
        
        if should_spawn:
            self.spawn_enemy(self.state.level)
            self.state.enemies_spawned_this_level += 1
            self.state.last_spawn_time = current_time
    
    def spawn_enemy(self, enemy_type):
        """Spawn a single enemy at the opposite side of the arena"""
        # Spawn on opposite side of arena from cannon
        cannon_distance_from_center = math.sqrt(self.state.cannon_x**2 + self.state.cannon_z**2)
        
        if cannon_distance_from_center > 1.0:
            # Spawn on opposite side from cannon
            spawn_x = -self.state.cannon_x * 1.5
            spawn_z = -self.state.cannon_z * 1.5
        else:
            # If cannon is near center, spawn randomly on edge
            angle = random.uniform(0, 2 * math.pi)
            spawn_x = ENEMY_SPAWN_DISTANCE * math.cos(angle)
            spawn_z = ENEMY_SPAWN_DISTANCE * math.sin(angle)
        
        # Ensure spawn position is within reasonable bounds
        max_spawn = ARENA_SIZE / 2 - 2
        spawn_x = max(-max_spawn, min(max_spawn, spawn_x))
        spawn_z = max(-max_spawn, min(max_spawn, spawn_z))
        
        enemy = Enemy(enemy_type, spawn_x, spawn_z, self.state.cannon_x, self.state.cannon_z)
        self.state.enemies.append(enemy)
        
        print(f"Spawned level {enemy_type} enemy at ({spawn_x:.1f}, {spawn_z:.1f})")
    
    def handle_enemy_collision(self, enemy):
        """Handle when enemy collides with cannon"""
        if enemy.alive:
            self.state.cannon_life -= enemy.damage
            enemy.alive = False
            
            print(f"COLLISION! Enemy dealt {enemy.damage} damage. Life: {self.state.cannon_life}/{self.state.max_life}")
            
            if self.state.cannon_life <= 0:
                self.state.game_over = True
                print("GAME OVER! Cannon destroyed!")
                return
    
    def handle_enemy_death(self, enemy):
        """Handle when enemy is killed (for future projectile system)"""
        if enemy.alive:
            enemy.alive = False
            self.state.enemies_killed_this_level += 1
            self.state.score += 100 * self.state.level  # More points for higher levels
            print(f"Enemy killed! Score: {self.state.score}")
    
    def check_level_completion(self):
        """Check if current level is complete"""
        if self.state.level_complete:
            return
        
        required_kills = self.state.enemies_per_level[self.state.level]
        
        # Check if all enemies for this level have been killed or collided
        alive_enemies = sum(1 for enemy in self.state.enemies if enemy.alive)
        total_spawned = self.state.enemies_spawned_this_level
        
        if (total_spawned >= required_kills and alive_enemies == 0):
            self.complete_level()
    
    def complete_level(self):
        """Complete current level and advance to next"""
        self.state.level_complete = True
        self.state.score += 500 * self.state.level  # Bonus for completing level
        
        print(f"\n*** LEVEL {self.state.level} COMPLETE! ***")
        print(f"Score: {self.state.score}")
        
        if self.state.level >= self.state.max_level:
            self.state.game_won = True
            print("CONGRATULATIONS! YOU WON THE GAME!")
            return
        
        # Advance to next level
        self.state.level += 1
        self.state.reset_level()
    
    def draw_cannon(self):
        """Draw a simple cannon representation"""
        glPushMatrix()
        glTranslatef(self.state.cannon_x, 0, self.state.cannon_z)
        
        # Cannon base
        glColor3f(0.3, 0.3, 0.3)
        glutSolidCylinder(0.8, 0.5, 16, 16)
        
        # Cannon barrel
        glPushMatrix()
        glTranslatef(0, 0.5, 0)
        glRotatef(-45, 1, 0, 0)
        glColor3f(0.4, 0.4, 0.4)
        glutSolidCylinder(0.3, 2.0, 16, 16)
        glPopMatrix()
        
        glPopMatrix()
    
    def render(self):
        """Main render function"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Camera follows cannon
        camera_distance = 25.0
        camera_height = 15.0
        camera_x = self.state.cannon_x + camera_distance * 0.3
        camera_z = self.state.cannon_z + camera_distance * 0.8
        
        gluLookAt(camera_x, camera_height, camera_z,
                 self.state.cannon_x, 2, self.state.cannon_z,
                 0, 1, 0)
        
        # Draw arena (simplified version)
        self.draw_simple_arena()
        
        # Draw cannon
        self.draw_cannon()
        
        # Draw enemies
        for enemy in self.state.enemies:
            enemy.render()
        
        glutSwapBuffers()
    
    def draw_simple_arena(self):
        """Draw a simplified arena floor"""
        glPushMatrix()
        glTranslatef(0, -1, 0)
        glColor3f(0.2, 0.3, 0.2)  # Dark green
        glScalef(ARENA_SIZE, 0.2, ARENA_SIZE)
        glutSolidCube(1.0)
        glPopMatrix()
        
        # Arena walls
        glColor3f(0.4, 0.4, 0.4)
        wall_height = 3.0
        half_size = ARENA_SIZE / 2
        
        # Four walls
        for i in range(4):
            glPushMatrix()
            if i == 0:  # Front wall
                glTranslatef(0, wall_height/2, half_size)
                glScalef(ARENA_SIZE, wall_height, 1.0)
            elif i == 1:  # Back wall
                glTranslatef(0, wall_height/2, -half_size)
                glScalef(ARENA_SIZE, wall_height, 1.0)
            elif i == 2:  # Left wall
                glTranslatef(-half_size, wall_height/2, 0)
                glScalef(1.0, wall_height, ARENA_SIZE)
            else:  # Right wall
                glTranslatef(half_size, wall_height/2, 0)
                glScalef(1.0, wall_height, ARENA_SIZE)
            
            glutSolidCube(1.0)
            glPopMatrix()
    
    def print_game_status(self):
        """Print current game status"""
        alive_enemies = sum(1 for enemy in self.state.enemies if enemy.alive)
        print(f"Level {self.state.level} | Life: {self.state.cannon_life}/{self.state.max_life} | "
              f"Score: {self.state.score} | Enemies: {alive_enemies} | "
              f"Killed: {self.state.enemies_killed_this_level}/{self.state.enemies_per_level[self.state.level]}")
    
    def keyboard_down(self, key, x, y):
        """Handle key press"""
        self.keys.add(key)
        
        if key == b'q' or key == b'Q' or key == b'\x1b':  # Q or ESC
            print("Game quit by user")
            sys.exit(0)
        elif key == b' ':  # Space for manual enemy kill (cheat for testing)
            if self.state.enemies:
                enemy = next((e for e in self.state.enemies if e.alive), None)
                if enemy:
                    self.handle_enemy_death(enemy)
        elif key == b'r' or key == b'R':  # Restart game
            self.state = GameState()
            self.state.reset_level()
            print("Game restarted!")
    
    def keyboard_up(self, key, x, y):
        """Handle key release"""
        self.keys.discard(key)

# Global game instance
game = Game()

# GLUT callback functions
def display():
    game.render()

def idle():
    game.update(0.016)  # ~60 FPS
    glutPostRedisplay()

def keyboard(key, x, y):
    game.keyboard_down(key, x, y)

def keyboard_up(key, x, y):
    game.keyboard_up(key, x, y)

def reshape(width, height):
    if height == 0:
        height = 1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, width/height, 1.0, 200.0)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1200, 900)
    glutCreateWindow(b"Arena Defense Game")
    
    game.init_opengl()
    
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutReshapeFunc(reshape)
    
    print("=" * 60)
    print("          ARENA DEFENSE GAME")
    print("=" * 60)
    print("CONTROLS:")
    print("  WASD - Move cannon")
    print("  SPACE - Kill nearest enemy (cheat for testing)")
    print("  R - Restart game")
    print("  Q/ESC - Quit game")
    print("")
    print("GAME RULES:")
    print("  - Survive 4 levels of increasing difficulty")
    print("  - Enemies spawn from opposite side and chase your cannon")
    print("  - Avoid collisions to preserve your 20 life points")
    print("  - Level 1-3 enemies: 2 damage each")
    print("  - Level 4 boss: 5 damage")
    print("")
    print("LEVELS:")
    print("  1. Stickman Soldiers (2 enemies, walking)")
    print("  2. Flying Bugs (2 enemies, flying)")
    print("  3. Archers (2 enemies, walk + shoot arrows)")
    print("  4. Demon Queen Boss (1 enemy, fast flying + attacks)")
    print("=" * 60)
    
    glutMainLoop()

if __name__ == '__main__':
    main()