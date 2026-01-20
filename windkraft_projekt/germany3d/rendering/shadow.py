"""
Shadow Rendering
================

Dynamische Schatten für die Bundesländer basierend auf Kamerarotation.

Vorlesungskonzepte:
- Schattenfühler (Shadow projection)
- Soft Shadows durch mehrere Schichten
"""

import math
from OpenGL.GL import *


def render_map_shadows(bundeslaender: list, rot_y: float):
    """
    Rendert dynamische Schatten für alle Bundesländer.
    
    Die Schatten bewegen sich basierend auf der Kamera-Rotation
    und bestehen aus mehreren Schichten für einen weichen Effekt.
    
    Args:
        bundeslaender: Liste von Bundesland-Objekten
        rot_y: Aktuelle Y-Rotation der Kamera
    """
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Schatten-Offset basierend auf Lichtrichtung
    light_angle = math.radians(rot_y + 45)
    base_offset_x = 0.08 * math.cos(light_angle)
    base_offset_z = 0.06 * math.sin(light_angle)
    
    # Mehrere Schichten für weichen Schatten
    for layer in range(3):
        alpha = 0.12 - layer * 0.03
        scale = 0.96 - layer * 0.01
        
        glColor4f(0.0, 0.0, 0.0, alpha)
        
        for bl in bundeslaender:
            # Schatten-Offset proportional zur Höhe des Blocks
            height_factor = bl.extrusion / 0.15  # Normalisiert auf kleinste Höhe
            offset_x = base_offset_x * height_factor * (1 + layer * 0.3)
            offset_z = base_offset_z * height_factor * (1 + layer * 0.3)
            
            _render_bundesland_shadow(
                bl, scale, offset_x, offset_z, layer, height_factor
            )
    
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)


def _render_bundesland_shadow(bl, scale: float, offset_x: float, 
                               offset_z: float, layer: int, height_factor: float):
    """
    Rendert den Schatten eines einzelnen Bundeslandes.
    
    Args:
        bl: Bundesland-Objekt
        scale: Skalierungsfaktor (kleiner = weiter vom Zentrum)
        offset_x, offset_z: Schatten-Versatz
        layer: Schicht-Index für Y-Position
        height_factor: Höhenfaktor für Schatten-Anpassung
    """
    if len(bl.vertices_top) < 3:
        return
    
    # Zentrum berechnen
    cx = sum(v[0] for v in bl.vertices_top) / len(bl.vertices_top)
    cz = sum(v[2] for v in bl.vertices_top) / len(bl.vertices_top)
    
    # Schatten knapp über dem Boden (y=-0.005)
    # Leicht höher als Bodenplane um Z-Fighting zu vermeiden
    y_pos = -0.004 + layer * 0.0001
    
    # Schatten auf dem Boden
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(cx + offset_x, y_pos, cz + offset_z)
    
    for v in bl.vertices_top:
        sx = cx + (v[0] - cx) * scale + offset_x
        sz = cz + (v[2] - cz) * scale + offset_z
        glVertex3f(sx, y_pos, sz)
    
    # Fan schließen
    v = bl.vertices_top[0]
    sx = cx + (v[0] - cx) * scale + offset_x
    sz = cz + (v[2] - cz) * scale + offset_z
    glVertex3f(sx, y_pos, sz)
    glEnd()
