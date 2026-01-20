"""
Optimierter WindTurbineManager mit allen 4 Performance-Optimierungen
=====================================================================

Integriert folgende Optimierungen:

1. FRUSTUM CULLING (3D View-Frustum)
   - Echtes 3D-Frustum statt AABB
   - Extrahiert aus ModelView-Projection-Matrix
   - Ref: Gribb & Hartmann (2001), Assarsson & Möller (2000)

2. AGGRESSIVE LOD
   - 5 LOD-Level statt 3
   - ~60-75% Polygon-Einsparung statt ~40%
   - Billboard bei großer Distanz
   - Ref: Luebke (2002) "LOD for 3D Graphics"

3. INSTANCED RENDERING
   - GPU-basiertes Batching
   - Gruppiert nach LOD-Level
   - Reduziert Draw-Calls von N auf ~5
   - Ref: Carucci (2005) "Inside Geometry Instancing"

4. VIEW-FRUSTUM AUS KAMERA-MATRIX
   - Präziseres Culling durch echte Projektion
   - Kamera-Rotation/Tilt wird berücksichtigt
   - Ref: Gribb & Hartmann (2001)

Verwendung:
    manager = OptimizedWindTurbineManager()
    manager.add_turbine(x, z, ...)
    manager.build_year_cache()
    
    # Im Render-Loop:
    manager.update_camera_from_opengl()  # Extrahiert Frustum
    manager.render_optimized(max_year=2020)
"""

import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass

# Lokale Imports
from .turbine import WindTurbine
from .shadow import render_turbine_shadow
from .quadtree import QuadtreeManager, BoundingBox
from .frustum_culling import ViewFrustum, FrustumCuller, VectorizedFrustumCuller
from .lod_aggressive import AggressiveLODManager, get_aggressive_lod_config
from .instanced_rendering import InstancedTurbineRenderer, BatchTurbineData

try:
    from OpenGL.GL import *
    HAS_OPENGL = True
except ImportError:
    HAS_OPENGL = False


@dataclass
class OptimizationStats:
    """Statistiken für Performance-Monitoring."""
    total_turbines: int = 0
    visible_turbines: int = 0
    culled_by_frustum: int = 0
    culled_by_quadtree: int = 0
    lod_distribution: dict = None
    polygon_count: int = 0
    polygon_savings_percent: float = 0.0
    draw_calls: int = 0
    frame_time_ms: float = 0.0
    
    def __post_init__(self):
        if self.lod_distribution is None:
            self.lod_distribution = {}


class OptimizedWindTurbineManager:
    """
    Windturbinen-Manager mit allen 4 Performance-Optimierungen.
    
    Features:
    - 3D Frustum Culling (statt einfacher AABB)
    - Aggressive LOD (5 Level, 60-75% Einsparung)
    - Instanced Rendering (GPU-Batching)
    - View-Frustum aus Kamera-Matrix
    """
    
    def __init__(self, enable_all_optimizations: bool = True):
        """
        Args:
            enable_all_optimizations: Aktiviert alle 4 Optimierungen
        """
        # Turbinen-Speicher
        self.turbines: List[WindTurbine] = []
        
        # Jahr-Cache
        self._year_cache = {}
        self._cache_valid = False
        
        # ========================================
        # OPTIMIERUNG 1 & 4: 3D Frustum Culling
        # ========================================
        self.use_frustum_culling = enable_all_optimizations
        self.frustum = ViewFrustum()
        self.frustum_culler = FrustumCuller()
        self.vectorized_culler = VectorizedFrustumCuller()
        
        # Kamera-Parameter (für Frustum-Extraktion)
        self.camera_pos = (0.0, 0.0)
        self.camera_rot_x = 35.0
        self.camera_rot_y = 0.0
        self.camera_zoom = 1.0
        self.near_plane = 0.01
        self.far_plane = 10.0
        self.fov = 45.0
        self.aspect_ratio = 16.0 / 9.0
        
        # ========================================
        # OPTIMIERUNG 2: Aggressive LOD
        # ========================================
        self.use_aggressive_lod = enable_all_optimizations
        self.lod_manager = AggressiveLODManager("standard")  # Wird nach build_cache angepasst
        
        # ========================================
        # OPTIMIERUNG 3: Instanced Rendering
        # ========================================
        self.use_instanced_rendering = enable_all_optimizations
        self.instanced_renderer = InstancedTurbineRenderer()
        self.batch_data = BatchTurbineData()
        
        # ========================================
        # Legacy: Quadtree (2D Spatial Index)
        # ========================================
        self.use_quadtree = True
        self.quadtree = QuadtreeManager(BoundingBox(-1.6, 1.6, -1.9, 1.9))
        
        # Statistiken
        self.stats = OptimizationStats()
        self.animation_enabled = True
    
    # ========================================
    # TURBINE MANAGEMENT
    # ========================================
    
    def add_turbine(self, x: float, z: float, height: float = 0.08,
                    rotor_radius: float = 0.04, power_kw: float = 3000,
                    year: int = 2000) -> WindTurbine:
        """Fügt eine Windturbine hinzu."""
        turbine = WindTurbine(x, z, height, rotor_radius, power_kw)
        turbine.year = year
        turbine.blade_angle = (len(self.turbines) * 37) % 360
        turbine.current_lod_level = 0  # LOD0 default
        
        self.turbines.append(turbine)
        self._cache_valid = False
        return turbine
    
    def build_year_cache(self):
        """
        Baut alle Caches auf:
        - Jahr-Cache für schnelles Filtern
        - Quadtree für räumliche Abfragen
        - LOD-Manager (wählt Config basierend auf Turbinenanzahl)
        """
        # Jahr-Cache
        self._year_cache = {}
        for t in self.turbines:
            year = getattr(t, 'year', 2000)
            if year not in self._year_cache:
                self._year_cache[year] = []
            self._year_cache[year].append(t)
        
        # Quadtree
        if self.use_quadtree:
            self.quadtree.build(self.turbines)
        
        # Aggressive LOD: Wähle Config basierend auf Turbinenanzahl
        if self.use_aggressive_lod:
            self.lod_manager = get_aggressive_lod_config(len(self.turbines))
        
        # Batch-Daten initialisieren
        if self.use_instanced_rendering:
            self.batch_data = BatchTurbineData(max(50000, len(self.turbines)))
        
        self._cache_valid = True
    
    def get_turbines_until_year(self, max_year: int) -> List[WindTurbine]:
        """Gibt Turbinen bis zum Jahr zurück."""
        if not self._cache_valid:
            self.build_year_cache()
        
        result = []
        for year in sorted(self._year_cache.keys()):
            if year <= max_year:
                result.extend(self._year_cache[year])
        return result
    
    # ========================================
    # OPTIMIERUNG 1 & 4: FRUSTUM CULLING
    # ========================================
    
    def update_camera(self, rot_x: float, rot_y: float, zoom: float,
                      near: float = 0.01, far: float = 10.0,
                      fov: float = 45.0, aspect: float = 16/9):
        """
        Aktualisiert Kamera-Parameter und extrahiert View-Frustum.
        
        Args:
            rot_x, rot_y: Kamera-Rotation (Grad)
            zoom: Kamera-Zoom
            near, far: Clipping-Planes
            fov: Field-of-View (Grad)
            aspect: Seitenverhältnis
        """
        self.camera_rot_x = rot_x
        self.camera_rot_y = rot_y
        self.camera_zoom = zoom
        self.near_plane = near
        self.far_plane = far
        self.fov = fov
        self.aspect_ratio = aspect
        
        # Berechne Kamera-Position für LOD
        import math
        rad_x = math.radians(rot_x)
        rad_y = math.radians(rot_y)
        dist = zoom * 2.0  # Angenommene Distanz-Formel
        
        cam_x = dist * math.sin(rad_y) * math.cos(rad_x)
        cam_z = dist * math.cos(rad_y) * math.cos(rad_x)
        self.camera_pos = (cam_x, cam_z)
        
        # Extrahiere View-Frustum
        if self.use_frustum_culling:
            self.frustum.extract_from_camera(
                self.camera_pos[0], 0.5, self.camera_pos[1],  # eye
                0.0, 0.0, 0.0,  # look at origin
                fov, aspect, near, far
            )
    
    def update_camera_from_opengl(self):
        """
        Extrahiert View-Frustum direkt aus OpenGL-Matrizen.
        
        Dies ist die präziseste Methode, da sie die tatsächliche
        Projektion verwendet.
        """
        if not HAS_OPENGL or not self.use_frustum_culling:
            return
        
        # Hole ModelView und Projection Matrix
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        
        # Extrahiere Frustum-Planes
        self.frustum.extract_from_matrices(projection, modelview)
    
    def _frustum_cull_turbines(self, turbines: List[WindTurbine]) -> List[WindTurbine]:
        """
        Führt 3D Frustum Culling durch.
        
        Verwendet Sphere-Test für schnelle Approximation.
        
        Args:
            turbines: Kandidaten-Turbinen
            
        Returns:
            Turbinen im View-Frustum
        """
        if not self.use_frustum_culling:
            return turbines
        
        visible = []
        culled = 0
        
        for t in turbines:
            # Turbine als Sphere modellieren
            # Mittelpunkt bei halber Höhe, Radius = größter Ausdehnung
            center_y = getattr(t, 'bl_height', 0.18) + t.height / 2
            radius = max(t.height, t.rotor_radius) * 1.2  # Etwas Puffer
            
            if self.frustum.is_sphere_visible(t.x, center_y, t.z, radius):
                visible.append(t)
            else:
                culled += 1
        
        self.stats.culled_by_frustum = culled
        return visible
    
    def _frustum_cull_vectorized(self, turbines: List[WindTurbine]) -> np.ndarray:
        """
        Vektorisiertes Frustum Culling (schneller bei vielen Turbinen).
        
        Returns:
            Boolean-Maske der sichtbaren Turbinen
        """
        if not turbines:
            return np.array([], dtype=bool)
        
        # Extrahiere Positionen
        positions = np.array([[t.x, t.z] for t in turbines], dtype=np.float32)
        
        # Berechne Radii
        radii = np.array([max(t.height, t.rotor_radius) * 1.2 for t in turbines], 
                         dtype=np.float32)
        
        # Vektorisiertes Culling
        visible_mask = self.vectorized_culler.cull_spheres_batch(
            positions, radii, self.frustum.planes
        )
        
        return visible_mask
    
    # ========================================
    # OPTIMIERUNG 2: AGGRESSIVE LOD
    # ========================================
    
    def _update_lod_for_turbines(self, turbines: List[WindTurbine]):
        """
        Aktualisiert LOD-Level für alle Turbinen.
        
        Verwendet aggressive LOD-Konfiguration (5 Level).
        """
        if not self.use_aggressive_lod:
            return
        
        cam_x, cam_z = self.camera_pos
        lod_counts = {}
        
        for t in turbines:
            # Berechne normalisierte Distanz
            dx = t.x - cam_x
            dz = t.z - cam_z
            distance = (dx*dx + dz*dz) ** 0.5
            normalized_dist = min(1.0, distance / 2.0)  # 2.0 = max distance
            
            # Wähle LOD
            lod = self.lod_manager.get_lod_for_distance(normalized_dist)
            t.current_lod_level = int(lod.name[-1])  # "LOD0" → 0
            t.distance_to_camera = distance
            
            # Statistik
            lod_name = lod.name
            lod_counts[lod_name] = lod_counts.get(lod_name, 0) + 1
        
        self.stats.lod_distribution = lod_counts
    
    # ========================================
    # OPTIMIERUNG 3: INSTANCED RENDERING
    # ========================================
    
    def render_instanced(self, turbines: List[WindTurbine], y_base: float = 0.0):
        """
        Rendert Turbinen mit Instanced Rendering.
        
        Gruppiert nach LOD für effizientes Batch-Rendering.
        """
        if not self.use_instanced_rendering:
            # Fallback: Standard-Rendering
            for t in turbines:
                t.render(y_base=y_base)
            return
        
        # Aktualisiere Batch-Daten
        self.batch_data.update_from_turbines(turbines)
        
        # Rendere mit Instanced Renderer
        self.instanced_renderer.render_instances(turbines, y_base)
        
        self.stats.draw_calls = self.instanced_renderer.stats['draw_calls']
    
    # ========================================
    # HAUPTFUNKTIONEN
    # ========================================
    
    def render_optimized(self, max_year: int, y_base: float = 0.18,
                         shadow_threshold: int = 500):
        """
        Rendert alle Turbinen mit allen 4 Optimierungen.
        
        Pipeline:
        1. Jahr-Filter (Cache)
        2. Quadtree Pre-Filter (2D Bounding Box)
        3. Frustum Culling (3D View-Frustum)
        4. LOD Update (Aggressive LOD)
        5. Instanced Render (GPU-Batching)
        
        Args:
            max_year: Maximales Baujahr
            y_base: Terrain-Höhe
            shadow_threshold: Schatten nur bei weniger Turbinen
        """
        import time
        start_time = time.time()
        
        # 1. Jahr-Filter
        candidates = self.get_turbines_until_year(max_year)
        self.stats.total_turbines = len(candidates)
        
        # 2. Quadtree Pre-Filter (optional, bei großer Szene)
        if self.use_quadtree and len(candidates) > 1000:
            # AABB für aktuelle Kamera-Sicht
            visible_bb = self._get_visible_bounding_box()
            candidates = self.quadtree.get_visible(visible_bb)
            self.stats.culled_by_quadtree = self.stats.total_turbines - len(candidates)
        
        # 3. Frustum Culling (3D)
        visible = self._frustum_cull_turbines(candidates)
        self.stats.visible_turbines = len(visible)
        
        # 4. LOD Update
        self._update_lod_for_turbines(visible)
        
        # 5. Render
        if self.use_instanced_rendering:
            self.render_instanced(visible, y_base)
        else:
            # Standard-Render mit LOD-basierter Vereinfachung
            render_shadows = len(visible) <= shadow_threshold
            light_dir = (1.0, 3.0, 1.0)
            
            for t in visible:
                actual_y_base = getattr(t, 'bl_height', y_base)
                
                if render_shadows:
                    render_turbine_shadow(
                        t.x, t.z, actual_y_base,
                        t.height, t.rotor_radius,
                        t.blade_angle, light_dir
                    )
                
                t.render(y_base=actual_y_base)
        
        # Statistik
        self.stats.frame_time_ms = (time.time() - start_time) * 1000
    
    def _get_visible_bounding_box(self) -> BoundingBox:
        """Berechnet AABB für Quadtree-Pre-Filter."""
        # Basierend auf Kamera-Zoom
        scale = max(0.5, 2.0 / self.camera_zoom)
        return BoundingBox(
            self.camera_pos[0] - scale,
            self.camera_pos[0] + scale,
            self.camera_pos[1] - scale,
            self.camera_pos[1] + scale
        )
    
    def update(self, dt: float = 0.016):
        """Aktualisiert Animation."""
        if not self.animation_enabled:
            return
        
        for t in self.turbines:
            t.update(dt)
    
    def get_stats_summary(self) -> str:
        """Gibt lesbare Statistiken zurück."""
        s = self.stats
        lines = [
            "=" * 50,
            "Optimierungs-Statistiken",
            "=" * 50,
            f"Turbinen gesamt:     {s.total_turbines:6d}",
            f"Nach Quadtree:       {s.total_turbines - s.culled_by_quadtree:6d} ({s.culled_by_quadtree} culled)",
            f"Nach Frustum:        {s.visible_turbines:6d} ({s.culled_by_frustum} culled)",
            f"Draw Calls:          {s.draw_calls:6d}",
            f"Frame Zeit:          {s.frame_time_ms:6.2f}ms",
            "",
            "LOD-Verteilung:",
        ]
        
        for lod, count in sorted(s.lod_distribution.items()):
            pct = (count / s.visible_turbines * 100) if s.visible_turbines > 0 else 0
            lines.append(f"  {lod}: {count:5d} ({pct:.1f}%)")
        
        return "\n".join(lines)
    
    def __len__(self):
        return len(self.turbines)


# =============================================================================
# BENCHMARK: Vergleich optimiert vs. nicht-optimiert
# =============================================================================

def benchmark_optimizations(num_turbines: int = 29722):
    """Benchmark der 4 Optimierungen."""
    import random
    import time
    
    print("\n" + "=" * 70)
    print(f"Optimierungs-Benchmark ({num_turbines} Turbinen)")
    print("=" * 70)
    
    # Manager ohne Optimierungen
    manager_none = OptimizedWindTurbineManager(enable_all_optimizations=False)
    
    # Manager mit allen Optimierungen
    manager_all = OptimizedWindTurbineManager(enable_all_optimizations=True)
    
    # Erstelle Turbinen
    random.seed(42)
    for i in range(num_turbines):
        x = random.uniform(-1.5, 1.5)
        z = random.uniform(-1.8, 1.8)
        year = random.randint(1990, 2023)
        power = random.uniform(2000, 8000)
        
        manager_none.add_turbine(x, z, year=year, power_kw=power)
        manager_all.add_turbine(x, z, year=year, power_kw=power)
    
    manager_none.build_year_cache()
    manager_all.build_year_cache()
    
    # Simuliere Kamera
    manager_all.update_camera(rot_x=35.0, rot_y=45.0, zoom=1.5)
    
    # Ohne Optimierungen: Zähle was gerendert würde
    start = time.time()
    visible_none = manager_none.get_turbines_until_year(2023)
    time_none = (time.time() - start) * 1000
    count_none = len(visible_none)
    
    # Mit Optimierungen
    start = time.time()
    candidates = manager_all.get_turbines_until_year(2023)
    visible_all = manager_all._frustum_cull_turbines(candidates)
    manager_all._update_lod_for_turbines(visible_all)
    time_all = (time.time() - start) * 1000
    count_all = len(visible_all)
    
    print(f"\nOhne Optimierungen:")
    print(f"  Zu rendern: {count_none:6d} Turbinen")
    print(f"  Zeit:       {time_none:6.2f}ms")
    
    print(f"\nMit allen Optimierungen:")
    print(f"  Zu rendern: {count_all:6d} Turbinen")
    print(f"  Zeit:       {time_all:6.2f}ms")
    print(f"  Reduktion:  {(1-count_all/count_none)*100:.1f}%")
    
    print(f"\n{manager_all.lod_manager.get_config_summary()}")
    
    print(f"\nLOD-Verteilung:")
    for lod, count in sorted(manager_all.stats.lod_distribution.items()):
        print(f"  {lod}: {count:5d}")


if __name__ == "__main__":
    benchmark_optimizations()
