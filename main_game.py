"""
main_game.py

GLUT-based controller for the Arena_Strike assets.

This file implements the 4-level gameplay described by the user and uses drawing helpers in the
`asset/` directory. It is intentionally minimal and defensive so it will run even if some
asset draw functions have different names (it will render placeholders instead).

Run:
    python main_game.py

"""
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import time
import math

from asset import cannon, arena

# Try importing known enemy modules; fall back gracefully if missing
try:
    from asset import lvl1_stickyman
except Exception:
    lvl1_stickyman = None

try:
    from asset import lvl2_bug
except Exception:
    lvl2_bug = None

try:
    from asset import lvl3_archer
except Exception:
    lvl3_archer = None

try:
    from asset import lvl4_boss
except Exception:
    lvl4_boss = None


# Game constants
CANNON_Z = 0.0
ENEMY_START_Z = 18.0
SPAWN_DELAY = 3.0  # spawn second enemy after 3 seconds


class Enemy:
    def __init__(self, kind, spawn_x, speed=0.02, hp=1, damage=2):
        self.kind = kind  # string: 'lvl1', 'lvl2', 'lvl3', 'lvl4'
        self.x = spawn_x
        self.y = 0.0
        self.z = ENEMY_START_Z
        self.speed = speed
        self.hp = hp
        self.damage = damage
        self.alive = True
        self.spawn_time = time.time()
        self.local_timer = 0.0

    def update(self, dt):
        self.local_timer += dt
        # basic following behavior: approach cannon and adjust x to follow cannon
        target_x = cannon.cannon_x
        # Move horizontally towards cannon slowly (follow)
        dx = target_x - self.x
        self.x += dx * min(1.0, 0.5 * dt)  # smoothing factor

        # Move forward along z depending on kind
        if self.kind == 'lvl1':
            self.z -= self.speed * dt * 60.0
        elif self.kind == 'lvl2':
            self.z -= (self.speed * 1.1) * dt * 60.0
        elif self.kind == 'lvl3':
            # slow walking with stop-and-shoot behavior: walk for 2s then pause 3s
            cycle = self.local_timer % 5.0
            if cycle < 2.0:
                self.z -= (self.speed * 0.5) * dt * 60.0
            else:
                # when paused, archer shoots (the module handles visual arrows if present)
                if lvl3_archer and hasattr(lvl3_archer, 'shoot_arrow') and (int(self.local_timer) % 3 == 0):
                    try:
                        lvl3_archer.shoot_arrow()
                    except Exception:
                        pass
        elif self.kind == 'lvl4':
            # boss moves faster
            self.z -= (self.speed * 1.6) * dt * 60.0
            # boss shoots continuously if module supports it
            if lvl4_boss and hasattr(lvl4_boss, 'shoot'):
                try:
                    lvl4_boss.shoot()
                except Exception:
                    pass

        # bound check
        if self.z < -2.0:
            self.z = -2.0

    def draw(self, t):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        # call appropriate draw from asset modules if available
        try:
            if self.kind == 'lvl1' and lvl1_stickyman and hasattr(lvl1_stickyman, 'draw_stickman'):
                lvl1_stickyman.draw_stickman(t)
            elif self.kind == 'lvl2' and lvl2_bug and hasattr(lvl2_bug, 'draw_bug'):
                lvl2_bug.draw_bug(t)
            elif self.kind == 'lvl3' and lvl3_archer and hasattr(lvl3_archer, 'draw_archer'):
                lvl3_archer.draw_archer(t)
            elif self.kind == 'lvl4' and lvl4_boss and hasattr(lvl4_boss, 'draw_boss'):
                lvl4_boss.draw_boss(t)
            else:
                # placeholder
                glColor3f(1.0, 0.2, 0.2)
                glutSolidCube(1.0)
        except Exception:
            # drawing failed; show a cube placeholder
            glColor3f(1.0, 0.2, 0.2)
            glutSolidCube(1.0)
        glPopMatrix()

    def hit_by_shot(self):
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False


class Bullet:
    def __init__(self, x, z, speed=0.6):
        self.x = x
        self.z = z
        self.speed = speed
        self.alive = True

    def update(self, dt):
        self.z += self.speed * dt * 60.0
        if self.z > ENEMY_START_Z + 5:
            self.alive = False

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, 0.2, self.z)
        glColor3f(1.0, 1.0, 0.0)
        glutSolidSphere(0.08, 8, 8)
        glPopMatrix()


class Game:
    def __init__(self):
        self.level = 1
        self.enemies = []
        self.bullets = []
        self.last_spawn = 0.0
        self.spawned_first = False
        self.last_time = time.time()
        self.run_time = 0.0
        self.score = 0
        self.life = 20
        self.show_aim = False

    def start_level(self):
        self.enemies.clear()
        self.bullets.clear()
        self.spawned_first = False
        self.last_spawn = time.time()
        print(f"Starting level {self.level}")

    def spawn_enemy_for_level(self, which):
        spawn_x = -cannon.CANNON_MAX_X if cannon.cannon_x > 0 else cannon.CANNON_MAX_X
        # spawn on opposite side of cannon
        spawn_x = -cannon.cannon_x if abs(cannon.cannon_x) > 0.1 else (cannon.CANNON_MAX_X)

        if which == 1:
            e = Enemy('lvl1', spawn_x, speed=0.03, hp=1, damage=2)
        elif which == 2:
            e = Enemy('lvl2', spawn_x, speed=0.035, hp=1, damage=2)
        elif which == 3:
            e = Enemy('lvl3', spawn_x, speed=0.018, hp=1, damage=2)
        else:
            e = Enemy('lvl4', spawn_x, speed=0.045, hp=3, damage=5)

        self.enemies.append(e)
        return e

    def update(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        self.run_time += dt

        # Handle level progression: spawn rules per the spec
        alive_enemies = [e for e in self.enemies if e.alive]

        if self.level <= 3:
            # levels 1-3 spawn two enemies sequentially
            if not self.spawned_first:
                # spawn first enemy of the level
                self.spawn_enemy_for_level(self.level)
                self.spawned_first = True
                self.last_spawn = now
            else:
                # spawn second after SPAWN_DELAY
                if now - self.last_spawn > SPAWN_DELAY and len(alive_enemies) < 2:
                    self.spawn_enemy_for_level(self.level)

            # If both were killed, advance
            if self.spawned_first and len([e for e in self.enemies if e.alive]) == 0 and len(self.enemies) >= 2:
                self.level += 1
                if self.level <= 4:
                    self.start_level()
        else:
            # level 4: spawn boss once
            if not self.spawned_first:
                self.spawn_enemy_for_level(4)
                self.spawned_first = True
            else:
                # if boss dead -> win (reset to level 1)
                if len([e for e in self.enemies if e.alive]) == 0:
                    print("All levels cleared! Final score:", self.score)
                    self.level = 1
                    self.start_level()

        # update enemies
        for e in self.enemies:
            if e.alive:
                e.update(dt)

                # collision with cannon: check z and x proximity
                if e.z <= 0.6 and abs(e.x - cannon.cannon_x) < 1.2:
                    # apply damage
                    self.life -= e.damage
                    print(f"Cannon hit by {e.kind}! Life now: {self.life}")
                    e.alive = False
                    if self.life <= 0:
                        print("Game Over. Final score:", self.score)
                        sys.exit(0)

        # update bullets
        for b in self.bullets:
            if b.alive:
                b.update(dt)

                # check collision with enemies
                for e in self.enemies:
                    if e.alive and abs(b.z - e.z) < 1.2 and abs(b.x - e.x) < 1.0:
                        e.hit_by_shot()
                        b.alive = False
                        if not e.alive:
                            self.score += 10
                            print(f"Enemy {e.kind} killed. Score: {self.score}")

        # remove dead bullets/enemies
        self.bullets = [b for b in self.bullets if b.alive]
        # enemies kept so we can inspect history, but skip dead for updates

    def draw(self):
        # basic scene setup
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(0, 8, 22, 0, 0, 0, 0, 1, 0)

        # draw arena background pieces if available
        try:
            arena.draw_arena_floor()
        except Exception:
            pass

        # draw cannon (module provides draw)
        try:
            cannon.draw_cannon()
        except Exception:
            pass

        # draw enemies
        for e in self.enemies:
            if e.alive:
                e.draw(self.run_time)

        # draw bullets
        for b in self.bullets:
            b.draw()

        glutSwapBuffers()

    def fire(self):
        # create a bullet at cannon position that travels forward (positive z)
        b = Bullet(cannon.cannon_x, 0.5, speed=0.9)
        self.bullets.append(b)


game = Game()


def init_gl():
    glClearColor(0.15, 0.4, 0.6, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, 1.33, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)


def display():
    game.draw()


def idle():
    game.update()
    glutPostRedisplay()


def keyboard(key, x, y):
    key = key.decode('utf-8') if isinstance(key, bytes) else key
    if key in ('q', '\x1b'):
        sys.exit(0)
    elif key.lower() == 'a':
        cannon.cannon_x = max(cannon.CANNON_MIN_X, cannon.cannon_x - 0.6)
    elif key.lower() == 'd':
        cannon.cannon_x = min(cannon.CANNON_MAX_X, cannon.cannon_x + 0.6)
    elif key.lower() == 'w':
        cannon.cannon_angle = min(cannon.CANNON_MAX_ANGLE, cannon.cannon_angle + 3.0)
    elif key.lower() == 's':
        cannon.cannon_angle = max(cannon.CANNON_MIN_ANGLE, cannon.cannon_angle - 3.0)
    elif key.lower() == 'f':
        game.fire()
    elif key.lower() == 'c':
        # toggle aiming display if module supports it
        cannon.show_aiming_line = not cannon.show_aiming_line


def reshape(w, h):
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, float(w)/float(h), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 700)
    glutCreateWindow(b"Arena Strike - Main")
    init_gl()

    game.start_level()

    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutReshapeFunc(reshape)

    print("Controls: A/D move, W/S tilt barrel, F fire, C toggle aim, Q quit")

    glutMainLoop()


if __name__ == '__main__':
    main()
