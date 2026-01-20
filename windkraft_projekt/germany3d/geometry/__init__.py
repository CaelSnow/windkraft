"""
Geometry Package - Geometrie-Klassen
====================================

Enthält:
- triangulation: Polygon-Triangulierung (Ear-Clipping)
- bundesland: Bundesland-Klasse mit 3D-Rendering
"""

from .triangulation import triangulate_polygon, polygon_area
from .bundesland import Bundesland

__all__ = ['triangulate_polygon', 'polygon_area', 'Bundesland']
