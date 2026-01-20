"""
Geometrie-Rendering für Windrad-Komponenten
============================================

Enthält Funktionen zum Rendern der einzelnen Teile:
- Turm (konischer Zylinder)
- Gondel (horizontaler Zylinder)
- Nabe (Kegel/Spinner)
- Rotorblätter (aerodynamisches Profil)

Vorlesungskonzepte:
- Triangle Mesh
- Vertex-Normalen für Gouraud/Phong Shading
- Hierarchische Transformation

PERFORMANCE: Display Lists für statische Geometrie
"""

import math
from OpenGL.GL import *
from .colors import COLOR_TOWER, COLOR_NACELLE, COLOR_HUB, COLOR_BLADE
from .materials import set_tower_material, set_nacelle_material, set_hub_material, set_blade_material


# =============================================================================
# DISPLAY LIST CACHE
# =============================================================================
_TOWER_LIST = None
_NACELLE_LIST = None
_HUB_LIST = None


def _compile_tower_list():
    """Kompiliert Turm-Geometrie in Display List."""
    global _TOWER_LIST
    _TOWER_LIST = glGenLists(1)
    glNewList(_TOWER_LIST, GL_COMPILE)
    _render_tower_geometry()
    glEndList()


def _compile_nacelle_list():
    """Kompiliert Gondel-Geometrie in Display List."""
    global _NACELLE_LIST
    _NACELLE_LIST = glGenLists(1)
    glNewList(_NACELLE_LIST, GL_COMPILE)
    _render_nacelle_geometry()
    glEndList()


def _compile_hub_list():
    """Kompiliert Naben-Geometrie in Display List."""
    global _HUB_LIST
    _HUB_LIST = glGenLists(1)
    glNewList(_HUB_LIST, GL_COMPILE)
    _render_hub_geometry()
    glEndList()


# =============================================================================
# TURM
# =============================================================================
def _render_tower_geometry(segments: int = 24):
    """Interne Turm-Geometrie (normalisiert)."""
    # Mantel des Kegels
    glBegin(GL_QUAD_STRIP)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Normale für Gouraud/Phong Shading
        slope = (1.0 - 0.583) / 1.0  # (base - top) / height
        normal_len = math.sqrt(1 + slope * slope)
        nx = cos_a / normal_len
        ny = slope / normal_len
        nz = sin_a / normal_len
        glNormal3f(nx, ny, nz)
        
        # Oberer Punkt (normalisiert)
        glVertex3f(0.583 * cos_a, 1.0, 0.583 * sin_a)
        # Unterer Punkt
        glVertex3f(cos_a, 0, sin_a)
    glEnd()
    
    # Untere Kappe
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0, -1, 0)
    glVertex3f(0, 0, 0)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        glVertex3f(math.cos(angle), 0, math.sin(angle))
    glEnd()


def render_tower(base_radius: float = 0.06, top_radius: float = 0.035, 
                 height: float = 1.0, segments: int = 24):
    """
    Rendert einen konischen Turm.
    
    Vorlesung: Gouraud Shading auf gekrümmter Oberfläche
    
    Args:
        base_radius: Radius unten
        top_radius: Radius oben
        height: Höhe des Turms
        segments: Anzahl Segmente (mehr = glatter)
    """
    global _TOWER_LIST
    
    glColor3f(*COLOR_TOWER)
    set_tower_material()
    
    # PERFORMANCE: Display List verwenden
    if _TOWER_LIST is None:
        _compile_tower_list()
    
    glPushMatrix()
    glScalef(base_radius, height, base_radius)
    glCallList(_TOWER_LIST)
    glPopMatrix()


# =============================================================================
# GONDEL
# =============================================================================
def _render_nacelle_geometry(segments: int = 16):
    """Interne Gondel-Geometrie (normalisiert)."""
    # Zylinder-Mantel
    glBegin(GL_QUAD_STRIP)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        glNormal3f(cos_a, sin_a, 0)
        glVertex3f(cos_a, sin_a, 1.0)
        glVertex3f(cos_a, sin_a, 0)
    glEnd()
    
    # Vordere Kappe
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0, 0, 1)
    glVertex3f(0, 0, 1.0)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        glVertex3f(math.cos(angle), math.sin(angle), 1.0)
    glEnd()
    
    # Hintere Kappe
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0, 0, -1)
    glVertex3f(0, 0, 0)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        glVertex3f(math.cos(angle), math.sin(angle), 0)
    glEnd()


def render_nacelle(radius: float = 0.04, length: float = 0.18, segments: int = 16):
    """
    Rendert die Gondel (Maschinenhaus).
    
    Args:
        radius: Radius der Gondel
        length: Länge der Gondel
        segments: Anzahl Segmente
    """
    global _NACELLE_LIST
    
    glColor3f(*COLOR_NACELLE)
    set_nacelle_material()
    
    # PERFORMANCE: Display List verwenden
    if _NACELLE_LIST is None:
        _compile_nacelle_list()
    
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    glRotatef(90, 0, 0, 1)
    glTranslatef(0, 0, -0.12)
    glScalef(radius, radius, length)
    glCallList(_NACELLE_LIST)
    glPopMatrix()


# =============================================================================
# NABE (HUB)
# =============================================================================
def _render_hub_geometry(segments: int = 16):
    """Interne Naben-Geometrie (normalisiert)."""
    # Kegel (Spinner)
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0, 0, 1)
    glVertex3f(0, 0, 1.0)  # Spitze
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        glNormal3f(cos_a * 0.7, sin_a * 0.7, 0.7)
        glVertex3f(cos_a, sin_a, 0)
    glEnd()
    
    # Basis-Ring
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0, 0, -1)
    glVertex3f(0, 0, 0)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        glVertex3f(math.cos(angle), math.sin(angle), 0)
    glEnd()


def render_hub(radius: float = 0.03, length: float = 0.04, segments: int = 16):
    """
    Rendert die Nabe (Spinner) als Kegel.
    
    Args:
        radius: Radius der Naben-Basis
        length: Länge des Spinners
        segments: Anzahl Segmente
    """
    global _HUB_LIST
    
    glColor3f(*COLOR_HUB)
    set_hub_material()
    
    # PERFORMANCE: Display List verwenden
    if _HUB_LIST is None:
        _compile_hub_list()
    
    glPushMatrix()
    glScalef(radius, radius, length)
    glCallList(_HUB_LIST)
    glPopMatrix()


# =============================================================================
# ROTORBLATT
# =============================================================================
# Aerodynamisches Blatt-Profil
# (position entlang Blatt, Breite, Dicke, Twist-Winkel)
BLADE_PROFILE = [
    (0.00, 0.024, 0.010, 0),      # Wurzel (dick)
    (0.08, 0.026, 0.009, 3),
    (0.20, 0.024, 0.007, 7),
    (0.35, 0.020, 0.006, 11),
    (0.50, 0.016, 0.005, 14),
    (0.65, 0.012, 0.004, 16),
    (0.80, 0.008, 0.003, 18),
    (0.92, 0.004, 0.002, 19),
    (1.00, 0.001, 0.001, 20),     # Spitze
]


def render_blade(blade_length: float, power_color: tuple = None):
    """
    Rendert ein einzelnes Rotorblatt.
    
    Vorlesung: Triangle Mesh mit korrekten Normalen
    
    Args:
        blade_length: Länge des Blattes (= Rotor-Radius)
    """
    #glColor3f(*COLOR_BLADE)
    if power_color:
        glColor3f(*power_color)  # ← Farbe nach Leistung
    else:
        glColor3f(*COLOR_BLADE)  # Fallback: weiß
    
    set_blade_material()
    
    
    for i in range(len(BLADE_PROFILE) - 1):
        pos1, width1, thick1, twist1 = BLADE_PROFILE[i]
        pos2, width2, thick2, twist2 = BLADE_PROFILE[i + 1]
        
        y1 = pos1 * blade_length
        y2 = pos2 * blade_length
        tw1 = math.radians(twist1)
        tw2 = math.radians(twist2)
        
        _render_blade_section(y1, y2, width1, width2, thick1, thick2, tw1, tw2)
    
    # Blattspitze
    _render_blade_tip(blade_length)


def _render_blade_section(y1, y2, w1, w2, t1, t2, tw1, tw2):
    """Rendert ein Segment des Blattes."""
    # Normalen-Komponenten
    nx1 = math.sin(tw1) * 0.2
    nz1 = math.cos(tw1)
    nx2 = math.sin(tw2) * 0.2
    nz2 = math.cos(tw2)
    
    # Oberseite
    glBegin(GL_QUADS)
    glNormal3f(nx1, 0.15, nz1)
    glVertex3f(-w1 * math.cos(tw1), y1, t1)
    glNormal3f(nx1, 0.15, nz1)
    glVertex3f(w1 * math.cos(tw1), y1, t1 * 0.5)
    glNormal3f(nx2, 0.15, nz2)
    glVertex3f(w2 * math.cos(tw2), y2, t2 * 0.5)
    glNormal3f(nx2, 0.15, nz2)
    glVertex3f(-w2 * math.cos(tw2), y2, t2)
    glEnd()
    
    # Unterseite
    glBegin(GL_QUADS)
    glNormal3f(-nx1, -0.1, -nz1)
    glVertex3f(w1 * math.cos(tw1), y1, -t1 * 0.3)
    glVertex3f(-w1 * math.cos(tw1), y1, -t1 * 0.3)
    glVertex3f(-w2 * math.cos(tw2), y2, -t2 * 0.3)
    glVertex3f(w2 * math.cos(tw2), y2, -t2 * 0.3)
    glEnd()
    
    # Vorderkante
    glBegin(GL_QUADS)
    glNormal3f(-1, 0.1, 0)
    glVertex3f(-w1 * math.cos(tw1), y1, t1)
    glVertex3f(-w2 * math.cos(tw2), y2, t2)
    glVertex3f(-w2 * math.cos(tw2), y2, -t2 * 0.3)
    glVertex3f(-w1 * math.cos(tw1), y1, -t1 * 0.3)
    glEnd()
    
    # Hinterkante
    glBegin(GL_QUADS)
    glNormal3f(1, 0.1, 0)
    glVertex3f(w1 * math.cos(tw1), y1, t1 * 0.5)
    glVertex3f(w1 * math.cos(tw1), y1, -t1 * 0.3)
    glVertex3f(w2 * math.cos(tw2), y2, -t2 * 0.3)
    glVertex3f(w2 * math.cos(tw2), y2, t2 * 0.5)
    glEnd()


def _render_blade_tip(blade_length: float):
    """Rendert die Blattspitze."""
    pos_tip, w_tip, t_tip, tw_tip = BLADE_PROFILE[-1]
    pos_prev, w_prev, t_prev, tw_prev = BLADE_PROFILE[-2]
    
    y_tip = pos_tip * blade_length
    y_prev = pos_prev * blade_length
    tw_p = math.radians(tw_prev)
    
    glBegin(GL_TRIANGLES)
    glNormal3f(0, 1, 0)
    glVertex3f(0, y_tip, 0)
    glVertex3f(-w_prev * math.cos(tw_p), y_prev, t_prev)
    glVertex3f(w_prev * math.cos(tw_p), y_prev, t_prev * 0.5)
    glEnd()
