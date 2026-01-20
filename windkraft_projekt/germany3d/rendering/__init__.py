"""
Rendering Package - OpenGL-Rendering
=====================================

Enthält:
- opengl_utils: OpenGL-Initialisierung und Beleuchtung
- shadow: Schatten-Rendering für Bundesländer
- shaders: GLSL Shader für Phong-Shading (optional)
"""

from .opengl_utils import (
    init_opengl, 
    setup_projection, 
    update_lighting, 
    apply_camera_transform
)
from .shadow import render_map_shadows

# Optional: Shader für Phong-Shading
try:
    from .shaders import (
        ShaderProgram,
        get_phong_shader,
        check_shader_support,
        PHONG_VERTEX_SHADER,
        PHONG_FRAGMENT_SHADER
    )
    SHADERS_AVAILABLE = True
except ImportError:
    SHADERS_AVAILABLE = False

__all__ = [
    'init_opengl', 
    'setup_projection', 
    'update_lighting', 
    'apply_camera_transform',
    'render_map_shadows',
    'SHADERS_AVAILABLE'
]
