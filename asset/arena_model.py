# arena_model.py
# Handles arena floor, gallery, lights, roof, and atmosphere rendering
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random

def draw_arena_floor():
    glColor3f(0.8, 0.4, 0.2)
    glPushMatrix()
    glTranslatef(0, -1.5, 0)
    glScalef(55.0, 0.6, 35.0)
    glutSolidCube(1.0)
    glPopMatrix()
    glColor3f(0.7, 0.35, 0.18)
    glPushMatrix()
    glTranslatef(0, -1.45, 0)
    glScalef(50.0, 0.6, 32.0)
    glutSolidCube(1.0)
    glPopMatrix()
    glColor3f(0.6, 0.3, 0.15)
    glPushMatrix()
    glTranslatef(0, -1.4, 0)
    glScalef(45.0, 0.6, 29.0)
    glutSolidCube(1.0)
    glPopMatrix()
    glColor3f(0.1, 0.7, 0.1)
    glPushMatrix()
    glTranslatef(0, -1.35, 0)
    glScalef(40.0, 0.6, 25.0)
    glutSolidCube(1.0)
    glPopMatrix()

def draw_gallery_structure():
    glColor3f(0.6, 0.55, 0.5)
    for level in range(3):
        height = 7.5 + level * 6.0
        inner_radius_x = 50.0 + level * 6.0
        inner_radius_y = 35.0 + level * 4.0
        depth = 4.5
        glPushMatrix()
        glTranslatef(0, height, 0)
        for angle in range(0, 360, 12):
            rad = math.radians(angle)
            base_x = inner_radius_x * math.cos(rad)
            base_z = inner_radius_y * math.sin(rad)
            glPushMatrix()
            glTranslatef(base_x, 0, base_z)
            glRotatef(angle, 0, 1, 0)
            glScalef(depth, 0.9, 6.0)
            glutSolidCube(1.0)
            glPopMatrix()
        if level > 0:
            glColor3f(0.5, 0.45, 0.4)
            for angle in range(0, 360, 24):
                rad = math.radians(angle)
                pillar_x = (inner_radius_x - 2) * math.cos(rad)
                pillar_z = (inner_radius_y - 2) * math.sin(rad)
                glPushMatrix()
                glTranslatef(pillar_x, -3.0, pillar_z)
                glScalef(1.2, 6.0, 1.2)
                glutSolidCube(1.0)
                glPopMatrix()
        glPopMatrix()
        glColor3f(0.6, 0.55, 0.5)

def draw_stick_figure(x, y, z, cheer_animation):
    glPushMatrix()
    glTranslatef(x, y, z)
    angle_to_center = math.degrees(math.atan2(-x, -z))
    glRotatef(angle_to_center, 0, 1, 0)
    glColor3f(0.7, 0.6, 0.5)
    glPushMatrix()
    glTranslatef(0, 5.4 + cheer_animation * 0.3, 0)
    glutSolidSphere(0.45, 12, 12)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 3.6, 0)
    glScalef(0.3, 2.4, 0.3)
    glutSolidCube(1.0)
    glPopMatrix()
    arm_angle = 45 + cheer_animation * 30
    glPushMatrix()
    glTranslatef(-0.6, 4.5, 0)
    glRotatef(arm_angle, 0, 0, 1)
    glScalef(0.18, 1.2, 0.18)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.6, 4.5, 0)
    glRotatef(-arm_angle, 0, 0, 1)
    glScalef(0.18, 1.2, 0.18)
    glutSolidCube(1.0)
    glPopMatrix()
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(0.3 * side, 1.2, 0)
        glScalef(0.24, 2.4, 0.24)
        glutSolidCube(1.0)
        glPopMatrix()
    glPopMatrix()

def draw_audience(audience_data, cheer_time):
    for person in audience_data:
        cheer_animation = math.sin(cheer_time + person['cheer_offset']) * person['cheer_intensity']
        draw_stick_figure(
            person['x'],
            person['y'] + cheer_animation * 0.05,
            person['z'],
            cheer_animation
        )

def draw_arena_lights():
    glColor3f(0.9, 0.9, 0.7)
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        light_x = 65.0 * math.cos(rad)
        light_z = 50.0 * math.sin(rad)
        glPushMatrix()
        glTranslatef(light_x, 24.0, light_z)
        glColor3f(0.3, 0.3, 0.3)
        glScalef(0.6, 12.0, 0.6)
        glutSolidCube(1.0)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(light_x, 28.5, light_z)
        glColor3f(0.9, 0.9, 0.7)
        glutSolidSphere(0.9, 12, 12)
        glPopMatrix()

def draw_roof_structure():
    glColor3f(0.4, 0.4, 0.45)
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        beam_x = 70.0 * math.cos(rad)
        beam_z = 55.0 * math.sin(rad)
        glPushMatrix()
        glTranslatef(beam_x, 30.0, beam_z)
        glRotatef(45, 0, 0, 1)
        glScalef(0.9, 60.0, 0.9)
        glutSolidCube(1.0)
        glPopMatrix()
    glColor3f(0.2, 0.25, 0.3)
    for i in range(12):
        angle = i * 30
        rad = math.radians(angle)
        panel_x = 35.0 * math.cos(rad)
        panel_z = 25.0 * math.sin(rad)
        glPushMatrix()
        glTranslatef(panel_x, 36.0, panel_z)
        glRotatef(angle, 0, 1, 0)
        glRotatef(-15, 1, 0, 0)
        glScalef(12.0, 0.3, 30.0)
        glutSolidCube(1.0)
        glPopMatrix()

def draw_atmosphere_effects(cheer_time):
    glColor4f(0.9, 0.9, 0.7, 0.3)
    glDisable(GL_LIGHTING)
    for i in range(20):
        x = random.uniform(-18, 18)
        y = 24 + random.uniform(0, 12)
        z = random.uniform(-18, 18)
        glPushMatrix()
        glTranslatef(x, y + math.sin(cheer_time * 2 + i) * 1.5, z)
        glutSolidSphere(0.15, 12, 12)
        glPopMatrix()
    glEnable(GL_LIGHTING)

def generate_audience():
    audience_data = []
    for level in range(3):
        height = 9.0 + level * 6.0
        radius_x = 55.0 + level * 6.0
        radius_y = 40.0 + level * 4.0
        count_per_level = 60 - level * 10
        for i in range(count_per_level):
            angle = (i / count_per_level) * 360
            x = radius_x * math.cos(math.radians(angle))
            z = radius_y * math.sin(math.radians(angle))
            y = height
            cheer_offset = random.uniform(0, 2 * math.pi)
            cheer_intensity = random.uniform(0.5, 1.5)
            audience_data.append({
                'x': x, 'y': y, 'z': z,
                'cheer_offset': cheer_offset,
                'cheer_intensity': cheer_intensity,
                'base_height': height
            })
    return audience_data
