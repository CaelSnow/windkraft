"""
OpenGL Utilities - Initialisierung und Beleuchtung
===================================================

Hilffunktionen für OpenGL Fixed-Function Pipeline.

Vorlesungskonzepte:
- Phong Beleuchtungsmodell
- OpenGL Lighting States
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from ..config import BACKGROUND_COLOR


def init_opengl():
    """
    Initialisiert OpenGL mit Fixed-Function Pipeline.
    
    Aktiviert:
    - Depth Testing
    - Multisampling (Anti-Aliasing)
    - Smooth Shading
    - Zwei-Licht-Setup
    """
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glDepthFunc(GL_LEQUAL)
    
    # Hintergrundfarbe
    glClearColor(*BACKGROUND_COLOR)
    
    # Gouraud Shading
    glShadeModel(GL_SMOOTH)
    
    # Beleuchtung aktivieren
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)
    
    # Material-Tracking für Farben
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Globales Umgebungslicht
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.40, 0.40, 0.40, 1.0])
    glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
    
    # Standard-Material
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 8.0)


def setup_projection(width: int, height: int, fov: float = 32.0):
    """
    Setzt die Projektionsmatrix auf.
    
    Args:
        width, height: Fenstergröße
        fov: Field of View in Grad
    """
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fov, width / height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)


def update_lighting():
    """
    Aktualisiert die Lichtquellen.
    
    Zwei-Licht-Setup:
    - Hauptlicht von oben-vorne
    - Fülllicht von der Seite
    """
    # Hauptlicht - von oben-vorne
    glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 3.0, 2.0, 0.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.35, 0.35, 0.35, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.60, 0.60, 0.58, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.15, 0.15, 0.15, 1.0])
    
    # Fülllicht - von der anderen Seite
    glLightfv(GL_LIGHT1, GL_POSITION, [-1.5, 2.0, -1.0, 0.0])
    glLightfv(GL_LIGHT1, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.25, 0.25, 0.28, 1.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])


def apply_camera_transform(rot_x: float, rot_y: float, zoom: float):
    """
    Wendet die Kamera-Transformation an.
    
    Args:
        rot_x, rot_y: Rotation in Grad
        zoom: Abstand von der Szene
    """
    glLoadIdentity()
    glTranslatef(0, -0.1, -zoom)
    glRotatef(rot_x, 1, 0, 0)
    glRotatef(rot_y, 0, 1, 0)
