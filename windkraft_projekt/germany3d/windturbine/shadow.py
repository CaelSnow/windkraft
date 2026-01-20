"""
Schatten-Rendering für Windräder
================================

Vorlesung: Schattenfühler (Shadow Feelers)
- Projektion der Geometrie auf die Bodenebene
- Lichtrichtung bestimmt Schattenrichtung und -länge
"""

import math
from OpenGL.GL import *
from .colors import COLOR_SHADOW


def render_turbine_shadow(x: float, z: float, y_base: float, 
                          height: float, rotor_radius: float,
                          blade_angle: float, light_dir: tuple):
    """
    Rendert den Schatten einer Windturbine auf dem Boden.
    
    Args:
        x, z: Position der Turbine
        y_base: Y-Koordinate des Bodens
        height: Höhe der Turbine (skaliert)
        rotor_radius: Radius der Rotorblätter
        blade_angle: Aktueller Rotationswinkel der Blätter
        light_dir: Lichtrichtung als (x, y, z) Tupel
    """
    glPushMatrix()
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    
    # Schatten-Rendering Setup
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)  # Kein Tiefenschreiben für Schatten
    
    # Schattenfarbe setzen
    glColor4f(*COLOR_SHADOW)
    
    # Position knapp über dem Boden
    shadow_y = y_base + 0.001
    glTranslatef(x, shadow_y, z)
    
    # Berechne Schatten-Offset basierend auf Lichtrichtung
    lx, ly, lz = light_dir
    shadow_length = 1.5
    offset_x = -lx / ly * height * shadow_length
    offset_z = -lz / ly * height * shadow_length
    
    # Turm-Schatten rendern
    _render_tower_shadow(height, offset_x, offset_z)
    
    # Rotor-Schatten rendern
    _render_rotor_shadow(height, rotor_radius, blade_angle, offset_x, offset_z)
    
    # Cleanup
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    
    glPopAttrib()
    glPopMatrix()


def _render_tower_shadow(height: float, offset_x: float, offset_z: float):
    """Rendert den Turm-Schatten als Trapez."""
    tower_base = 0.06 * height
    tower_top = 0.035 * height
    
    glBegin(GL_QUADS)
    # Basis am Boden
    glVertex3f(-tower_base, 0, -tower_base)
    glVertex3f(tower_base, 0, -tower_base)
    # Spitze versetzt durch Licht
    glVertex3f(tower_top + offset_x, 0, -tower_top + offset_z)
    glVertex3f(-tower_top + offset_x, 0, -tower_top + offset_z)
    glEnd()


def _render_rotor_shadow(height: float, rotor_radius: float, 
                         blade_angle: float, offset_x: float, offset_z: float):
    """Rendert die Schatten der 3 Rotorblätter."""
    scaled_radius = rotor_radius * height * 0.8
    blade_width = 0.02 * height
    
    for blade_num in range(3):
        angle = math.radians(blade_angle + blade_num * 120.0)
        
        # Blatt-Endpunkt
        blade_end_x = offset_x + math.cos(angle) * scaled_radius * 0.3
        blade_end_z = offset_z + math.sin(angle) * scaled_radius
        
        # Blatt als Dreieck
        glBegin(GL_TRIANGLES)
        glVertex3f(offset_x - blade_width, 0, offset_z)
        glVertex3f(offset_x + blade_width, 0, offset_z)
        glVertex3f(blade_end_x, 0, blade_end_z)
        glEnd()
