from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
import random
import time

# Display boundaries
BOUNDARY_X = 8.0
BOUNDARY_Y = 4.0
BOUNDARY_Z = 6.0

# Game variables
movement_speed = 0.02
goal_speed = 0.01

# Soldier spawning control
soldier_count = 10     # how many soldiers total
spawn_time = 60       # in how many seconds all soldiers spawn
spawn_interval = spawn_time / soldier_count
last_spawn_time = 0.0
soldiers = []         # list of soldier dicts


# Goal movement
goal_x = 0.0
goal_y = 0.0
goal_z = 0.0
goal_vx = 0.02
goal_vy = 0.015
goal_vz = 0.017

# Runtime
run_time = 0.0
spawn_timer = 0.0

# Camera control
camera_angle_x = 30   # vertical tilt
camera_angle_y = 45   # horizontal rotation
camera_distance = 18


def init():
    glClearColor(0.05, 0.05, 0.15, 1)  # Dark blue background
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Lighting
    light_pos = [5.0, 10.0, 5.0, 1.0]
    light_ambient = [0.2, 0.2, 0.2, 1.0]
    light_diffuse = [0.8, 0.8, 0.8, 1.0]

    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 1.0, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)

    spawn_goal()
    # Spawn goal once, no more respawns
    global goal_x, goal_y, goal_z
    goal_x = random.uniform(-BOUNDARY_X + 1, BOUNDARY_X - 1)
    goal_y = random.uniform(-BOUNDARY_Y + 1, BOUNDARY_Y - 1)
    goal_z = random.uniform(-BOUNDARY_Z + 1, BOUNDARY_Z - 1)


def spawn_soldier():
    """Spawn a soldier with dropping animation"""
    soldier = {
        "x": random.uniform(-BOUNDARY_X + 1, BOUNDARY_X - 1),
        "y": BOUNDARY_Y + 2,
        "z": random.uniform(-BOUNDARY_Z + 1, BOUNDARY_Z - 1),
        "is_dropping": True,
        "drop_velocity": 0.0
    }
    soldiers.append(soldier)


def spawn_goal():
    global goal_x, goal_y, goal_z
    goal_x = random.uniform(-BOUNDARY_X + 1, BOUNDARY_X - 1)
    goal_y = random.uniform(-BOUNDARY_Y + 1, BOUNDARY_Y - 1)
    goal_z = random.uniform(-BOUNDARY_Z + 1, BOUNDARY_Z - 1)


def move_goal():
    """Move the goal continuously, bouncing inside the box"""
    global goal_x, goal_y, goal_z, goal_vx, goal_vy, goal_vz

    goal_x += goal_vx
    goal_y += goal_vy
    goal_z += goal_vz

    # Bounce off walls
    if goal_x <= -BOUNDARY_X + 1 or goal_x >= BOUNDARY_X - 1:
        goal_vx *= -1
    if goal_y <= -BOUNDARY_Y + 1 or goal_y >= BOUNDARY_Y - 1:
        goal_vy *= -1
    if goal_z <= -BOUNDARY_Z + 1 or goal_z >= BOUNDARY_Z - 1:
        goal_vz *= -1


def move_soldier(soldier):
    ground_level = -BOUNDARY_Y + 1.5

    if soldier["is_dropping"]:
        soldier["drop_velocity"] += -0.003
        soldier["y"] += soldier["drop_velocity"]
        if soldier["y"] <= ground_level:
            soldier["y"] = ground_level
            soldier["is_dropping"] = False
            soldier["drop_velocity"] = 0.0
    else:
        dx = goal_x - soldier["x"]
        dy = goal_y - soldier["y"]
        dz = goal_z - soldier["z"]
        distance = math.sqrt(dx * dx + dy * dy + dz * dz)
        if distance < 0.5:
            spawn_goal()
            return
        if distance > 0:
            soldier["x"] += (dx / distance) * movement_speed
            soldier["y"] += (dy / distance) * movement_speed
            soldier["z"] += (dz / distance) * movement_speed
        soldier["x"] = max(-BOUNDARY_X + 1, min(BOUNDARY_X - 1, soldier["x"]))
        soldier["y"] = max(-BOUNDARY_Y + 1, min(BOUNDARY_Y - 1, soldier["y"]))
        soldier["z"] = max(-BOUNDARY_Z + 1, min(BOUNDARY_Z - 1, soldier["z"]))


# ----- Drawing helpers -----
def draw_sphere(radius):
    glutSolidSphere(radius, 16, 16)


def draw_cylinder(radius, height):
    quad = gluNewQuadric()
    gluCylinder(quad, radius, radius, height, 16, 16)


def draw_face():
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(0.07 * side, 0.05, 0.22)
        glColor3f(0, 0, 0)
        draw_sphere(0.03)
        glPopMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glBegin(GL_TRIANGLES)
    glVertex3f(-0.08, 0.12, 0.21)
    glVertex3f(-0.01, 0.09, 0.21)
    glVertex3f(-0.08, 0.09, 0.21)
    glVertex3f(0.08, 0.12, 0.21)
    glVertex3f(0.01, 0.09, 0.21)
    glVertex3f(0.08, 0.09, 0.21)
    glEnd()
    glPushMatrix()
    glTranslatef(0, -0.1, 0.2)
    glColor3f(0.3, 0, 0)
    glScalef(0.1, 0.05, 0.01)
    glutSolidCube(1.0)
    glPopMatrix()


def draw_horn(side):
    glPushMatrix()
    glColor3f(0.9, 0.9, 0.9)
    glTranslatef(0.15 * side, 0.2, 0)
    glRotatef(-45 * side, 0, 0, 1)
    glRotatef(-70, 1, 0, 0)
    for i in range(3):
        draw_cylinder(0.03, 0.15)
        glTranslatef(0, 0, 0.15)
        glRotatef(20, 1, 0, 0)
    glPopMatrix()


def draw_sword():
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.3, 0.15, 0)
    draw_cylinder(0.025, 0.2)
    glTranslatef(0, 0, 0.2)
    glColor3f(0.8, 0.8, 1.0)
    draw_cylinder(0.03, 0.8)
    glTranslatef(0, 0, 0.8)
    glutSolidCone(0.03, 0.2, 16, 16)
    glPopMatrix()


def draw_arm(side, t):
    swing = math.sin(t) * 30
    glPushMatrix()
    glTranslatef(0.25 * side, 1.1, 0)
    glRotatef(swing * side, 1, 0, 0)
    if side > 0:
        draw_sword()
    else:
        glColor3f(0.6, 0.6, 0.6)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        draw_cylinder(0.08, 0.6)
        glTranslatef(0, 0, 0.6)
        draw_sphere(0.08)
        glPopMatrix()
    glPopMatrix()


def draw_leg(side, t):
    swing = math.sin(t + math.pi) * 30
    glPushMatrix()
    glTranslatef(0.18 * side, -0.05, 0)
    glRotatef(swing * side, 1, 0, 0)
    glTranslatef(0, -0.7, 0)
    glRotatef(-swing * 0.5 * side, 1, 0, 0)
    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.09, 0.6)
    glPopMatrix()
    glPopMatrix()


def draw_soldier(soldier, t):
    rotation = 0
    if not soldier["is_dropping"]:
        dx = goal_x - soldier["x"]
        dz = goal_z - soldier["z"]
        if dx != 0 or dz != 0:
            rotation = math.degrees(math.atan2(dx, dz))

    glPushMatrix()
    glTranslatef(soldier["x"], soldier["y"], soldier["z"])
    if not soldier["is_dropping"]:
        glRotatef(rotation, 0, 1, 0)

    # Torso
    glPushMatrix()
    glColor3f(0.4, 0.4, 0.4)
    glRotatef(-90, 1, 0, 0)
    draw_cylinder(0.15, 1.2)
    glPopMatrix()

    # Head
    glPushMatrix()
    glColor3f(1.0, 0.8, 0.6)
    glTranslatef(0, 1.4, 0)
    draw_sphere(0.25)
    draw_face()
    draw_horn(1)
    draw_horn(-1)
    glPopMatrix()

    draw_arm(1, t)
    draw_arm(-1, t)
    draw_leg(1, t)
    draw_leg(-1, t)

    glPopMatrix()


def draw_goal():
    glPushMatrix()
    glTranslatef(goal_x, goal_y, goal_z)
    pulse = 0.8 + 0.3 * math.sin(run_time * 5)
    glScalef(pulse, pulse, pulse)
    glColor3f(1.0, 0.2, 0.2)
    draw_sphere(0.3)
    glColor3f(1.0, 0.5, 0.5)
    glutSolidTorus(0.05, 0.5, 8, 16)
    glPopMatrix()


def draw_boundaries():
    glColor3f(0.3, 0.3, 0.3)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    # Bottom
    glVertex3f(-BOUNDARY_X, -BOUNDARY_Y, -BOUNDARY_Z)
    glVertex3f(BOUNDARY_X, -BOUNDARY_Y, -BOUNDARY_Z)
    glVertex3f(BOUNDARY_X, -BOUNDARY_Y, -BOUNDARY_Z)
    glVertex3f(BOUNDARY_X, -BOUNDARY_Y, BOUNDARY_Z)
    glVertex3f(BOUNDARY_X, -BOUNDARY_Y, BOUNDARY_Z)
    glVertex3f(-BOUNDARY_X, -BOUNDARY_Y, BOUNDARY_Z)
    glVertex3f(-BOUNDARY_X, -BOUNDARY_Y, BOUNDARY_Z)
    glVertex3f(-BOUNDARY_X, -BOUNDARY_Y, -BOUNDARY_Z)
    # Top
    glVertex3f(-BOUNDARY_X, BOUNDARY_Y, -BOUNDARY_Z)
    glVertex3f(BOUNDARY_X, BOUNDARY_Y, -BOUNDARY_Z)
    glVertex3f(BOUNDARY_X, BOUNDARY_Y, -BOUNDARY_Z)
    glVertex3f(BOUNDARY_X, BOUNDARY_Y, BOUNDARY_Z)
    glVertex3f(BOUNDARY_X, BOUNDARY_Y, BOUNDARY_Z)
    glVertex3f(-BOUNDARY_X, BOUNDARY_Y, BOUNDARY_Z)
    glVertex3f(-BOUNDARY_X, BOUNDARY_Y, BOUNDARY_Z)
    glVertex3f(-BOUNDARY_X, BOUNDARY_Y, -BOUNDARY_Z)
    # Vertical
    glVertex3f(-BOUNDARY_X, -BOUNDARY_Y, -BOUNDARY_Z)
    glVertex3f(-BOUNDARY_X, BOUNDARY_Y, -BOUNDARY_Z)
    glVertex3f(BOUNDARY_X, -BOUNDARY_Y, -BOUNDARY_Z)
    glVertex3f(BOUNDARY_X, BOUNDARY_Y, -BOUNDARY_Z)
    glVertex3f(BOUNDARY_X, -BOUNDARY_Y, BOUNDARY_Z)
    glVertex3f(BOUNDARY_X, BOUNDARY_Y, BOUNDARY_Z)
    glVertex3f(-BOUNDARY_X, -BOUNDARY_Y, BOUNDARY_Z)
    glVertex3f(-BOUNDARY_X, BOUNDARY_Y, BOUNDARY_Z)
    glEnd()


def display():
    global run_time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Camera control
    lx = math.sin(math.radians(camera_angle_y)) * math.cos(math.radians(camera_angle_x))
    ly = math.sin(math.radians(camera_angle_x))
    lz = math.cos(math.radians(camera_angle_y)) * math.cos(math.radians(camera_angle_x))
    gluLookAt(camera_distance * lx, camera_distance * ly, camera_distance * lz,
              0, 0, 0,
              0, 1, 0)

    draw_boundaries()
    for s in soldiers:
        draw_soldier(s, run_time)
    draw_goal()

    glutSwapBuffers()


def idle():
    global run_time, spawn_timer, last_spawn_time
    run_time += 0.02
    spawn_timer += 0.02

    move_goal()
    for s in soldiers:
        move_soldier(s)

    # Gradual spawning
    if len(soldiers) < soldier_count and run_time - last_spawn_time >= spawn_interval:
        spawn_soldier()
        last_spawn_time = run_time

    glutPostRedisplay()


def keyboard(key, x, y):
    global movement_speed
    if key == b'r' or key == b'R':
        soldiers.clear()
        spawn_goal()
    elif key == b'q' or key == b'Q':
        sys.exit()
    elif key == b'+':
        movement_speed = min(0.1, movement_speed + 0.005)
    elif key == b'-':
        movement_speed = max(0.005, movement_speed - 0.005)


def special_keys(key, x, y):
    global camera_angle_x, camera_angle_y, camera_distance
    if key == GLUT_KEY_LEFT:
        camera_angle_y -= 5
    elif key == GLUT_KEY_RIGHT:
        camera_angle_y += 5
    elif key == GLUT_KEY_UP:
        camera_angle_x = min(80, camera_angle_x + 5)
    elif key == GLUT_KEY_DOWN:
        camera_angle_x = max(-80, camera_angle_x - 5)
    elif key == GLUT_KEY_PAGE_UP:      # zoom in
        camera_distance = max(5, camera_distance - 1)
    elif key == GLUT_KEY_PAGE_DOWN:    # zoom out
        camera_distance = min(50, camera_distance + 1)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutCreateWindow(b"Multiple Soldier Chase - Arrow keys to rotate view")
    init()
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    print("Controls:")
    print("R - Respawn goal and clear soldiers")
    print("+/- - Increase/decrease movement speed")
    print("Arrow keys - Rotate camera")
    print("Page Up / Page Down - Zoom in/out")
    print("Q - Quit")
    glutMainLoop()


if __name__ == '__main__':
    main()