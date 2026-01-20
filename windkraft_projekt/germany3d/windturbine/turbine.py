"""
WindTurbine - Optimiert mit Display Lists
=========================================

Schnelle Windturbine fuer CPU-Rendering mit Display Lists.
Die Geometrie wird einmal kompiliert und dann sehr schnell wiederverwendet.

Vorlesungskonzept: Display Lists (OpenGL Optimierung)
"""

import math
from OpenGL.GL import *
from .colors import get_power_color, COLOR_HUB

# Globale Display Lists (werden einmal erstellt)
_tower_list = None
_nacelle_list = None
_hub_list = None
_blade_list = None
_initialized = False


def _create_display_lists():
    """Erstellt alle Display Lists einmalig."""
    global _tower_list, _nacelle_list, _hub_list, _blade_list, _initialized
    
    if _initialized:
        return
    
    # Prüfe ob OpenGL-Kontext vorhanden ist
    try:
        glGetIntegerv(GL_MAX_TEXTURE_SIZE)
    except:
        # Kein OpenGL-Kontext vorhanden - wird später aufgerufen (Lazy)
        return
    
    try:
        # Turm (vereinfacht: 8 Segmente statt 24)
        _tower_list = glGenLists(1)
        if _tower_list == 0:
            print("WARNUNG: glGenLists fehlgeschlagen - Display Lists deaktiviert")
            _initialized = True
            return
        
        glNewList(_tower_list, GL_COMPILE)
        _draw_simple_tower()
        glEndList()
        
        # Gondel
        _nacelle_list = glGenLists(1)
        glNewList(_nacelle_list, GL_COMPILE)
        _draw_simple_nacelle()
        glEndList()
        
        # Nabe
        _hub_list = glGenLists(1)
        glNewList(_hub_list, GL_COMPILE)
        _draw_simple_hub()
        glEndList()
        
        # Blatt (vereinfacht)
        _blade_list = glGenLists(1)
        glNewList(_blade_list, GL_COMPILE)
        _draw_simple_blade()
        glEndList()
        
        _initialized = True
    except Exception as e:
        print(f"FEHLER beim Erstellen von Display Lists: {e}")
        _initialized = True  # Marke als "versucht" um Endlos-Schleife zu vermeiden


def _draw_simple_tower():
    """Vereinfachter Turm - nur 8 Segmente."""
    segments = 8
    base_r = 0.06
    top_r = 0.035
    
    glMaterialfv(GL_FRONT, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 15.0)
    

    glBegin(GL_QUAD_STRIP)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        glNormal3f(cos_a, 0.1, sin_a)
        glVertex3f(top_r * cos_a, 1.0, top_r * sin_a)
        glVertex3f(base_r * cos_a, 0, base_r * sin_a)
    glEnd()


def _draw_simple_nacelle():
    """Gondel als Zylinder (Original-Form)."""
    segments = 12
    radius = 0.04
    length = 0.15
    
    glMaterialfv(GL_FRONT, GL_SPECULAR, [0.4, 0.4, 0.4, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 35.0)
    
    # Zylinder horizontal (rotiert)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    glRotatef(90, 0, 0, 1)
    glTranslatef(0, 0, -0.12)
    
    # Mantel
    glBegin(GL_QUAD_STRIP)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        glNormal3f(cos_a, sin_a, 0)
        glVertex3f(radius * cos_a, radius * sin_a, length)
        glVertex3f(radius * cos_a, radius * sin_a, 0)
    glEnd()
    
    # Vordere Kappe
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0, 0, 1)
    glVertex3f(0, 0, length)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        glVertex3f(radius * math.cos(angle), radius * math.sin(angle), length)
    glEnd()
    
    # Hintere Kappe
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0, 0, -1)
    glVertex3f(0, 0, 0)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        glVertex3f(radius * math.cos(angle), radius * math.sin(angle), 0)
    glEnd()
    
    glPopMatrix()


def _draw_simple_hub():
    """Vereinfachte Nabe - Kegel mit 6 Segmenten."""
    segments = 6
    radius = 0.025
    length = 0.03
    
    glMaterialfv(GL_FRONT, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
    
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0, 0, 1)
    glVertex3f(0, 0, length)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        glVertex3f(radius * math.cos(angle), radius * math.sin(angle), 0)
    glEnd()


def _draw_simple_blade():
    """Vereinfachtes Blatt - nur 2 Triangles."""
    glMaterialfv(GL_FRONT, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 25.0)
    
    glBegin(GL_TRIANGLES)
    # Vorderseite
    glNormal3f(0, 0, 1)
    glVertex3f(-0.015, 0, 0)
    glVertex3f(0.015, 0, 0)
    glVertex3f(0, 0.5, 0)
    # Rueckseite
    glNormal3f(0, 0, -1)
    glVertex3f(0.015, 0, -0.002)
    glVertex3f(-0.015, 0, -0.002)
    glVertex3f(0, 0.5, -0.002)
    glEnd()


class WindTurbine:
    """
    Optimierte Windturbine mit Display Lists und LOD-Support.
    
    Die Geometrie wird einmal kompiliert und dann sehr schnell
    wiederverwendet - ideal fuer CPU-Rendering mit vielen Turbinen.
    
    Neu: LOD (Level-of-Detail) Unterstützung für bessere Performance.
    """
    
    def __init__(self, x: float, z: float, height: float = 0.08, 
                 rotor_radius: float = 0.04, power_kw: float = 3000):
        self.x = x
        self.z = z
        self.height = height
        self.rotor_radius = rotor_radius
        self.power_kw = power_kw
        
        # Jahr und Bundesland-Hoehe (werden vom Loader gesetzt)
        self.year = 2000
        self.bl_height = 0.18
        
        # Animation
        self.blade_angle = 0.0
        self.rotation_speed = 90.0
        
        # LOD (Level-of-Detail) Unterstützung
        self.current_lod_level = 0  # 0=LOD0 (full), 1=LOD1 (mid), 2=LOD2 (low)
        self.distance_to_camera = 0.0
        self.render_skip = False  # Falls zu weit weg
        
        # Display Lists werden Lazy geladen (beim ersten Render, nicht beim Init)
    
    @property
    def power_color(self) -> tuple:
        """Farbkodierung basierend auf Leistung."""
        return get_power_color(self.power_kw)
    
    def update(self, dt: float):
        """Aktualisiert Blatt-Rotation."""
        self.blade_angle += self.rotation_speed * dt
        if self.blade_angle >= 360.0:
            self.blade_angle -= 360.0
    
    def render(self, y_base: float = None, render_shadow: bool = False):
        """
        Schnelles Rendering mit Display Lists (Lazy-Loading).
        
        Args:
            y_base: Basis-Y-Koordinate (oder self.bl_height)
            render_shadow: Ignoriert (keine Schatten fuer Performance)
        """
        # PERFORMANCE: Lazy-Initialize Display Lists beim ersten Render
        global _initialized
        if not _initialized:
            _create_display_lists()
        
        if y_base is None:
            y_base = self.bl_height
            
        glPushMatrix()
        glTranslatef(self.x, y_base, self.z)
        glScalef(self.height, self.height, self.height)
        
        # Turm (hellgrau)
        glColor3f(0.85, 0.85, 0.82)
        if _tower_list:
            glCallList(_tower_list)
        
        # Gondel
        glTranslatef(0, 1.0, 0)
        glColor3f(0.9, 0.9, 0.88)
        if _nacelle_list:
            glCallList(_nacelle_list)
        
        # Nabe
        glTranslatef(0, 0, 0.06)
        glColor3f(*COLOR_HUB)
        if _hub_list:
            glCallList(_hub_list)
        
        # 3 Blaetter mit Farbe nach Leistung
        color = self.power_color
        glColor3f(*color)
        
        blade_scale = 0.8
        for i in range(3):
            glPushMatrix()
            glRotatef(self.blade_angle + i * 120.0, 0, 0, 1)
            glScalef(blade_scale, blade_scale, blade_scale)
            if _blade_list:
                glCallList(_blade_list)
            glPopMatrix()
        
        glPopMatrix()
