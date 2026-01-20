"""
Windturbine Package
===================

Optimiertes Package fuer Windrad-Visualisierung.

Module:
- turbine.py: WindTurbine Klasse mit Display Lists
- manager.py: WindTurbineManager fuer viele Windraeder
- colors.py: Farbdefinitionen nach Leistung
- quadtree.py: Quadtree für 2D Spatial Culling (x, z)
- lod.py: Level-of-Detail System
- cache_optimization.py: SoA/AoS Datenstrukturen

Performance-Optimierungen (NEU):
- frustum_culling.py: 3D View-Frustum Culling
- lod_aggressive.py: Aggressive LOD-Konfiguration (5 Level)
- instanced_rendering.py: GPU-basiertes Batch-Rendering
- optimized_manager.py: Integrierter optimierter Manager
"""

from .turbine import WindTurbine
from .manager import WindTurbineManager
from .colors import get_power_color, COLOR_TOWER, COLOR_HUB, COLOR_BLADE
from .quadtree import QuadtreeNode, QuadtreeManager, BoundingBox
from .lod import LODManager, LODLevel, LODTurbine

# Performance-Optimierungen
from .frustum_culling import ViewFrustum, FrustumCuller, VectorizedFrustumCuller
from .lod_aggressive import AggressiveLODManager, get_aggressive_lod_config
from .instanced_rendering import InstancedTurbineRenderer, BatchTurbineData
from .optimized_manager import OptimizedWindTurbineManager

__all__ = [
    # Core
    'WindTurbine', 
    'WindTurbineManager',
    'get_power_color',
    
    # Spatial (2D)
    'QuadtreeNode',
    'QuadtreeManager',
    'BoundingBox',
    
    # LOD
    'LODManager',
    'LODLevel',
    'LODTurbine',
    
    # Performance-Optimierungen (NEU)
    'ViewFrustum',
    'FrustumCuller',
    'VectorizedFrustumCuller',
    'AggressiveLODManager',
    'get_aggressive_lod_config',
    'InstancedTurbineRenderer',
    'BatchTurbineData',
    'OptimizedWindTurbineManager',
]
