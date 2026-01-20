"""
Germany 3D - 3D-Visualisierung deutscher Bundesländer
======================================================

Ein modulares OpenGL-basiertes 3D-Rendering-System für
Deutschlands 16 Bundesländer mit Windkraftanlagen.

Packages:
    - core/: Kamera, Viewer (Hauptklassen)
    - rendering/: OpenGL-Utils, Schatten
    - geometry/: Bundesland, Triangulation
    - data/: Daten laden (GeoJSON, CSV)
    - windturbine/: Windrad-Komponenten

Verwendung:
    from germany3d import Germany3DViewer
    viewer = Germany3DViewer()
    viewer.run()
"""

from .config import *
from .geometry import Bundesland
from .core import Germany3DViewer
from .windturbine import WindTurbine, WindTurbineManager

__version__ = "2.0.0"
__author__ = "CGIV Project"

__all__ = [
    'Germany3DViewer',
    'Bundesland',
    'WindTurbine',
    'WindTurbineManager',
]
