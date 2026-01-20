"""
Rendering Package - OpenGL-Rendering
=====================================

Enthält:
- opengl_utils: OpenGL-Initialisierung und Beleuchtung
- shadow: Schatten-Rendering für Bundesländer
"""

from .opengl_utils import (
    init_opengl, 
    setup_projection, 
    update_lighting, 
    apply_camera_transform
)
from .shadow import render_map_shadows

__all__ = [
    'init_opengl', 
    'setup_projection', 
    'update_lighting', 
    'apply_camera_transform',
    'render_map_shadows'
]
