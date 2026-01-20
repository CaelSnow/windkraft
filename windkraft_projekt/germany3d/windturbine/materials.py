"""
Material-Eigenschaften für Phong Shading
========================================

Vorlesung: Phongsches Reflexionsmodell
I = I_ambient + I_diffuse + I_specular
I = (I_a * k_a) + (I_e * k_d * cos θ) + (I_e * k_s * (cos α)^n)

Jedes Material hat:
- Specular Color: Farbe der Glanzlichter
- Shininess (n): Schärfe der Glanzlichter (1-128)
"""

from OpenGL.GL import *


def set_tower_material():
    """
    Material für Turm (Beton/Stahl).
    
    Wenig Glanz, matter Look.
    """
    glMaterialfv(GL_FRONT, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 15.0)


def set_nacelle_material():
    """
    Material für Gondel (lackiertes Metall).
    
    Mittlerer Glanz, glatte Oberfläche.
    """
    glMaterialfv(GL_FRONT, GL_SPECULAR, [0.4, 0.4, 0.4, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 40.0)


def set_hub_material():
    """
    Material für Nabe (Metall).
    
    Starker Glanz, polierte Oberfläche.
    """
    glMaterialfv(GL_FRONT, GL_SPECULAR, [0.6, 0.6, 0.6, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 60.0)


def set_blade_material():
    """
    Material für Rotorblätter (GFK/Composite).
    
    Leichter Glanz, glatte aber nicht spiegelnde Oberfläche.
    """
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.35, 0.35, 0.35, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 30.0)


def set_default_material():
    """
    Standard-Material für Windrad-Komponenten.
    """
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 25.0)
