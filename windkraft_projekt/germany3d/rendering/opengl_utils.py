"""
OpenGL Utilities - Initialisierung und Beleuchtung
===================================================

Hilffunktionen für OpenGL Fixed-Function Pipeline.

Vorlesungskonzepte:
- Phong Beleuchtungsmodell (Gouraud-Shading mit Fixed-Function)
- OpenGL Lighting States

SHADING-MODI:
1. Gouraud (Standard): 
   - Beleuchtung pro Vertex, dann interpoliert
   - Schneller, weniger genau bei großen Flächen
   - Verwendet OpenGL Fixed-Function Pipeline
   
2. Phong (GLSL):
   - Normalen werden interpoliert, Beleuchtung pro Pixel
   - Bessere Qualität für spekulare Highlights
   - Erfordert moderne OpenGL-Version
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from ..config import BACKGROUND_COLOR


def init_opengl(shading_mode: str = 'gouraud'):
    """
    Initialisiert OpenGL mit gewünschtem Shading-Modus.
    
    Args:
        shading_mode: 'gouraud' oder 'phong'
    
    Aktiviert:
    - Depth Testing
    - Multisampling (Anti-Aliasing)
    - Smooth Shading
    - Zwei-Licht-Setup mit Phong-Beleuchtungsmodell
    """
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glDepthFunc(GL_LEQUAL)
    
    # Hintergrundfarbe
    glClearColor(*BACKGROUND_COLOR)
    
    # Gouraud Shading (Smooth = interpolierte Vertex-Farben)
    # Bei Phong-Shading wird dies durch GLSL überschrieben
    glShadeModel(GL_SMOOTH)
    
    # Beleuchtung aktivieren (auch bei Gouraud wird Phong-Modell verwendet!)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)
    
    # Material-Tracking für Farben
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Globales Umgebungslicht (I_a aus der Vorlesung)
    # Erhöht für bessere Sichtbarkeit in Schattenregionen
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.35, 0.35, 0.35, 1.0])
    glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
    
    # Zwei-seitige Beleuchtung für korrekte Rückseiten
    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
    
    # Standard-Material mit Phong-Parametern
    # k_s (spekulare Reflexion) und n (Shininess)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.15, 0.15, 0.15, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 16.0)


def init_opengl_phong():
    """
    Initialisiert OpenGL für Phong-Shading (GLSL).
    
    Bei Phong-Shading werden die Lichtparameter an den Shader übergeben,
    nicht an die Fixed-Function Pipeline.
    """
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glDepthFunc(GL_LEQUAL)
    
    # Hintergrundfarbe
    glClearColor(*BACKGROUND_COLOR)
    
    # Für GLSL: Fixed-Function Lighting DEAKTIVIEREN
    glDisable(GL_LIGHTING)
    
    # VBO für Vertex-Daten benötigt
    print("  ℹ Phong-Shading aktiviert - GLSL Shader werden verwendet")


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
    Aktualisiert die Lichtquellen mit Phong-Beleuchtungsmodell.
    
    Implementiert die Phong-Formel aus der Vorlesung:
    I = I_a * k_a + Σ(I_d * k_d * max(0, N·L) + I_s * k_s * max(0, R·V)^n)
    
    Zwei-Licht-Setup:
    - LIGHT0: Hauptlicht (Sonne) - von oben-vorne
    - LIGHT1: Fülllicht - von der Seite für weichere Schatten
    
    Komponenten (OpenGL-Namen -> Vorlesungsnamen):
    - GL_AMBIENT  = I_a (Umgebungslicht)
    - GL_DIFFUSE  = I_d (Diffuse Reflexion, Lambert)  
    - GL_SPECULAR = I_s (Spiegelnde Reflexion, Phong)
    """
    # === HAUPTLICHT (LIGHT0) - Sonne von oben-vorne ===
    # Position: (1, 3, 2, 0) - 0 = Richtungslicht (unendlich weit)
    glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 3.0, 2.0, 0.0])
    
    # Ambiente Komponente (I_a): Basisbeleuchtung, unabhängig von Normale
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.30, 0.30, 0.30, 1.0])
    
    # Diffuse Komponente (I_d): Lambert'sche Reflexion, N·L abhängig
    # Leicht warmtonig für natürlicheres Sonnenlicht
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.65, 0.63, 0.60, 1.0])
    
    # Spiegelnde Komponente (I_s): Phong Highlight, (R·V)^n abhängig
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.20, 0.20, 0.20, 1.0])
    
    # === FÜLLLICHT (LIGHT1) - Weiche Gegenbeleuchtung ===
    # Position: (-1.5, 2, -1, 0) - von der anderen Seite
    glLightfv(GL_LIGHT1, GL_POSITION, [-1.5, 2.0, -1.0, 0.0])
    
    # Kein Ambiente für Fülllicht (würde sonst zu hell)
    glLightfv(GL_LIGHT1, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])
    
    # Diffuse: Leicht bläulich für kühlen Kontrast
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.22, 0.24, 0.28, 1.0])
    
    # Kaum Specular für Fülllicht
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.05, 0.05, 0.05, 1.0])


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
