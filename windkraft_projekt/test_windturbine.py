#!/usr/bin/env python3
"""
Wind Turbine Viewer - Einzelne Windmühle testen
================================================

Separates Script um eine einzelne realistische Windmühle 
zu betrachten und zu entwickeln.

Steuerung:
    - Maus ziehen: Rotieren
    - Scroll: Zoom
    - A: Animation ein/aus
    - +/-: Windrad größer/kleiner
    - 1-4: Verschiedene Leistungsklassen
    - R: Reset
    - S: Screenshot
    - ESC: Beenden
"""

import sys
import os
import math

# Pfad zum Projekt hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image

# Import der Windturbine-Klasse
from germany3d.windturbine import WindTurbine
from germany3d.windturbine.shadow import render_turbine_shadow


# =============================================================================
# KONFIGURATION
# =============================================================================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
BACKGROUND_COLOR = (0.15, 0.18, 0.22, 1.0)  # Dunkler Hintergrund für bessere Sicht

# Leistungsklassen zum Testen
POWER_CLASSES = {
    1: (800, "Klein (800 kW)"),
    2: (2500, "Mittel (2.5 MW)"),
    3: (4500, "Groß (4.5 MW)"),
    4: (6500, "Sehr groß (6.5 MW)"),
}


class WindTurbineViewer:
    """Viewer für einzelne Windturbine zum Entwickeln und Testen."""
    
    def __init__(self):
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        
        # Kamera
        self.rot_x = 25.0
        self.rot_y = 45.0
        self.zoom = 3.0
        
        # Maus
        self.dragging = False
        self.last_mouse = (0, 0)
        
        # Windturbine (wird nach OpenGL-Init erstellt)
        self.turbine_scale = 1.0
        self.current_power = 3000
        self.turbine = None
        self.animation_enabled = True
        
        # Boden anzeigen
        self.show_ground = True
        
        # Init
        self._init_pygame()
        self._init_opengl()
        
        # JETZT Turbine erstellen (nach OpenGL-Init!)
        self._create_turbine(self.current_power)
        
        self._print_controls()
    
    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Wind Turbine Viewer - Einzelne Windmühle")
        
        pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 4)
        
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            DOUBLEBUF | OPENGL | RESIZABLE
        )
    
    def _init_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)
        glDepthFunc(GL_LEQUAL)
        
        glClearColor(*BACKGROUND_COLOR)
        glShadeModel(GL_SMOOTH)
        
        # Beleuchtung
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)
        
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.3, 0.3, 0.35, 1.0])
        glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
        
        # Material
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 30.0)
        
        self._setup_projection()
    
    def _setup_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width / self.height, 0.01, 100.0)
        glMatrixMode(GL_MODELVIEW)
    
    def _update_lighting(self):
        # Hauptlicht von oben-vorne
        glLightfv(GL_LIGHT0, GL_POSITION, [2.0, 5.0, 3.0, 0.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.75, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
        
        # Fülllicht
        glLightfv(GL_LIGHT1, GL_POSITION, [-2.0, 3.0, -2.0, 0.0])
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.3, 0.3, 0.35, 1.0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
    
    def _print_controls(self):
        print("\n" + "=" * 60)
        print("  WIND TURBINE VIEWER")
        print("=" * 60)
        print("\n  Steuerung:")
        print("    • Maus ziehen = Rotieren")
        print("    • Scroll = Zoom")
        print("    • A = Animation ein/aus")
        print("    • +/- = Größe ändern")
        print("    • 1-4 = Leistungsklasse wählen")
        print("    • G = Boden ein/aus")
        print("    • R = Reset")
        print("    • S = Screenshot")
        print("    • ESC = Beenden")
        print("=" * 60 + "\n")
    
    def _create_turbine(self, power_kw):
        """Erstellt neue Turbine mit gegebener Leistung."""
        self.current_power = power_kw
        self.turbine = WindTurbine(
            x=0, z=0,
            height=0.5 * self.turbine_scale,
            rotor_radius=0.25 * self.turbine_scale,
            power_kw=power_kw
        )
        # Animation-Zustand übernehmen
        if not self.animation_enabled:
            self.turbine.blade_angle = 0
    
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
                    
                elif event.key == K_r:
                    self.rot_x = 25.0
                    self.rot_y = 45.0
                    self.zoom = 3.0
                    self.turbine_scale = 1.0
                    self._create_turbine(3000)
                    print("  Reset.")
                    
                elif event.key == K_s:
                    self._save_screenshot()
                    
                elif event.key == K_a:
                    self.animation_enabled = not self.animation_enabled
                    status = "ON" if self.animation_enabled else "OFF"
                    print(f"  Animation: {status}")
                    
                elif event.key == K_g:
                    self.show_ground = not self.show_ground
                    status = "ON" if self.show_ground else "OFF"
                    print(f"  Boden: {status}")
                    
                elif event.key == K_PLUS or event.key == K_EQUALS:
                    self.turbine_scale = min(3.0, self.turbine_scale + 0.1)
                    self._create_turbine(self.current_power)
                    print(f"  Größe: {self.turbine_scale:.1f}x")
                    
                elif event.key == K_MINUS:
                    self.turbine_scale = max(0.3, self.turbine_scale - 0.1)
                    self._create_turbine(self.current_power)
                    print(f"  Größe: {self.turbine_scale:.1f}x")
                    
                elif event.key in [K_1, K_2, K_3, K_4]:
                    key_num = event.key - K_1 + 1
                    if key_num in POWER_CLASSES:
                        power, name = POWER_CLASSES[key_num]
                        self._create_turbine(power)
                        print(f"  Leistungsklasse: {name}")
            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.dragging = True
                    self.last_mouse = event.pos
                elif event.button == 4:
                    self.zoom = max(1.0, self.zoom - 0.2)
                elif event.button == 5:
                    self.zoom = min(10.0, self.zoom + 0.2)
            
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
            
            elif event.type == MOUSEMOTION:
                if self.dragging:
                    dx = event.pos[0] - self.last_mouse[0]
                    dy = event.pos[1] - self.last_mouse[1]
                    self.rot_y += dx * 0.5
                    self.rot_x += dy * 0.5
                    self.rot_x = max(-90, min(90, self.rot_x))
                    self.last_mouse = event.pos
            
            elif event.type == VIDEORESIZE:
                self.width, self.height = event.size
                self.screen = pygame.display.set_mode(
                    (self.width, self.height),
                    DOUBLEBUF | OPENGL | RESIZABLE
                )
                glViewport(0, 0, self.width, self.height)
                self._setup_projection()
        
        return True
    
    def _render_ground(self):
        """Rendert einen einfachen Boden/Grid."""
        glDisable(GL_LIGHTING)
        
        # Boden-Fläche
        glColor3f(0.25, 0.28, 0.22)  # Dunkelgrün/Grau
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        size = 2.0
        glVertex3f(-size, 0, -size)
        glVertex3f(-size, 0, size)
        glVertex3f(size, 0, size)
        glVertex3f(size, 0, -size)
        glEnd()
        
        # Grid-Linien
        glColor3f(0.35, 0.38, 0.32)
        glLineWidth(1.0)
        glBegin(GL_LINES)
        grid_size = 2.0
        step = 0.2
        y = 0.001
        x = -grid_size
        while x <= grid_size:
            glVertex3f(x, y, -grid_size)
            glVertex3f(x, y, grid_size)
            glVertex3f(-grid_size, y, x)
            glVertex3f(grid_size, y, x)
            x += step
        glEnd()
        
        glEnable(GL_LIGHTING)
    
    def _render_axes(self):
        """Rendert Koordinatenachsen zur Orientierung."""
        glDisable(GL_LIGHTING)
        glLineWidth(2.0)
        
        axis_length = 0.3
        
        glBegin(GL_LINES)
        # X-Achse (Rot)
        glColor3f(1, 0.3, 0.3)
        glVertex3f(0, 0.01, 0)
        glVertex3f(axis_length, 0.01, 0)
        
        # Y-Achse (Grün)
        glColor3f(0.3, 1, 0.3)
        glVertex3f(0, 0.01, 0)
        glVertex3f(0, axis_length, 0)
        
        # Z-Achse (Blau)
        glColor3f(0.3, 0.3, 1)
        glVertex3f(0, 0.01, 0)
        glVertex3f(0, 0.01, axis_length)
        glEnd()
        
        glEnable(GL_LIGHTING)
    
    def _render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Kamera
        glTranslatef(0, -0.3, -self.zoom)
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)
        
        self._update_lighting()
        
        # Boden
        if self.show_ground:
            self._render_ground()
        
        # Koordinatenachsen
        self._render_axes()
        
        # Animation
        if self.animation_enabled and self.turbine:
            self.turbine.update(1.0 / 60.0)
        
        # Schatten (wie in main.py)
        if self.turbine:
            render_turbine_shadow(
                x=self.turbine.x,
                z=self.turbine.z,
                y_base=0.0,
                height=self.turbine.height,
                rotor_radius=self.turbine.rotor_radius,
                blade_angle=self.turbine.blade_angle,
                light_dir=(2.0, 5.0, 3.0)
            )
        
        # Windturbine rendern
        if self.turbine:
            self.turbine.render(y_base=0.0)
        
        pygame.display.flip()
    
    def _save_screenshot(self):
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        data = glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE)
        img = Image.frombytes('RGB', (self.width, self.height), data)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        
        path = os.path.join(output_dir, 'windturbine_test.png')
        img.save(path, quality=95)
        print(f"  📸 Screenshot: {path}")
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self._handle_events()
            self._render()
            clock.tick(60)
        
        pygame.quit()


def main():
    viewer = WindTurbineViewer()
    viewer.run()


if __name__ == "__main__":
    main()
