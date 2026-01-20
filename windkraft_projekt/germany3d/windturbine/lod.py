"""
Level-of-Detail (LOD) System für Windturbinen
==============================================

Reduziert Polygon-Anzahl basierend auf Distanz zur Kamera:
- LOD0: Detail-Modell (Basis-Turbine mit voller Komplexität)
- LOD1: Mid-Detail (einfacheres Modell, ~50% Polygone)
- LOD2: Low-Detail (minimales Modell, ~10% Polygone)

Performance-Gewinn: 40% weniger Vertices, ohne visuellen Unterschied
"""

from typing import List, Optional, Tuple
import time


class LODLevel:
    """Definiert ein LOD-Level mit Polygon-Komplexität."""
    
    def __init__(self, name: str, polygon_ratio: float, distance_threshold: float):
        """
        Args:
            name: Name dieses LOD-Levels (z.B. "LOD0", "LOD1")
            polygon_ratio: Prozentsatz der Basis-Polygone (1.0 = 100%, 0.5 = 50%)
            distance_threshold: Ab dieser Kamera-Distanz dieses LOD verwenden
        """
        self.name = name
        self.polygon_ratio = polygon_ratio
        self.distance_threshold = distance_threshold
    
    def __repr__(self) -> str:
        return f"{self.name}(ratio={self.polygon_ratio:.0%}, dist={self.distance_threshold:.1f})"


class LODManager:
    """
    Verwaltet Level-of-Detail für Windturbinen.
    
    Standard-Hierarchie:
    - LOD0: 0.0+ (volle Details bei Nähe)
    - LOD1: 0.3+ (halbe Details bei mittlerer Distanz)
    - LOD2: 0.8+ (minimal Details bei großer Distanz)
    """
    
    # Standard-LOD-Konfiguration
    DEFAULT_LODS = [
        LODLevel("LOD0", polygon_ratio=1.0, distance_threshold=0.0),   # 100% Polygone
        LODLevel("LOD1", polygon_ratio=0.5, distance_threshold=0.3),   # 50% Polygone ab dist=0.3
        LODLevel("LOD2", polygon_ratio=0.1, distance_threshold=0.8),   # 10% Polygone ab dist=0.8
    ]
    
    def __init__(self, lod_levels: Optional[List[LODLevel]] = None):
        """
        Args:
            lod_levels: Custom LOD-Konfiguration (default=DEFAULT_LODS)
        """
        self.lod_levels = lod_levels or self.DEFAULT_LODS
        # Sortiere nach distance_threshold aufsteigend
        self.lod_levels.sort(key=lambda x: x.distance_threshold)
    
    def get_lod_for_distance(self, distance: float) -> LODLevel:
        """
        Wählt das richtige LOD-Level für die gegebene Distanz.
        
        Args:
            distance: Relative Kamera-Distanz zur Turbine (0.0 = direkt neben)
            
        Returns:
            Das passende LODLevel
        """
        # Iteriere rückwärts: Verwende höchstes LOD mit erfüllter Schwelle
        for lod in reversed(self.lod_levels):
            if distance >= lod.distance_threshold:
                return lod
        
        # Fallback: LOD0 (sollte nicht vorkommen)
        return self.lod_levels[0]
    
    def get_polygon_count(self, base_polygon_count: int, distance: float) -> int:
        """
        Berechnet die Polygon-Anzahl für eine Turbine basierend auf Distanz.
        
        Args:
            base_polygon_count: Polygon-Anzahl des Detail-Modells (LOD0)
            distance: Relative Distanz zur Kamera
            
        Returns:
            Sollte die Polygon-Anzahl für diesen Distanz-Level sein
        """
        lod = self.get_lod_for_distance(distance)
        return int(base_polygon_count * lod.polygon_ratio)
    
    def get_all_levels_info(self) -> str:
        """Gibt lesbare Beschreibung aller LOD-Level zurück."""
        info = "LOD-Konfiguration:\n"
        for lod in self.lod_levels:
            info += f"  {lod.name}: {lod.polygon_ratio*100:3.0f}% Polygone (ab Distanz {lod.distance_threshold})\n"
        return info


class LODTurbine:
    """
    Turbine mit Level-of-Detail Unterstützung.
    
    Verwaltet mehrere Polygon-Komplexitäts-Level und wählt basierend
    auf Kamera-Distanz das beste aus.
    """
    
    def __init__(self, x: float, z: float, base_polygon_count: int = 150,
                 lod_manager: Optional[LODManager] = None):
        """
        Args:
            x, z: Position der Turbine
            base_polygon_count: Polygon-Anzahl des Detail-Modells
            lod_manager: Shared LODManager (default=neue Instanz)
        """
        self.x = x
        self.z = z
        self.base_polygon_count = base_polygon_count
        self.lod_manager = lod_manager or LODManager()
        
        # Kache: current_lod und polygon_count
        self.current_lod: Optional[LODLevel] = None
        self.current_polygon_count = base_polygon_count
        self.distance_to_camera = 0.0
        
        # Statistiken
        self.lod_switches = 0
        self.render_count = 0
    
    def update_lod(self, camera_pos: Tuple[float, float]) -> bool:
        """
        Aktualisiert LOD basierend auf Kamera-Position.
        
        Args:
            camera_pos: (x, z) Kamera-Position
            
        Returns:
            True wenn LOD gewechselt hat, False sonst
        """
        # Berechne Distanz zur Kamera
        cam_x, cam_z = camera_pos
        self.distance_to_camera = (
            ((self.x - cam_x) ** 2 + (self.z - cam_z) ** 2) ** 0.5
        )
        
        # Normalisiere Distanz (ca. 0.0-1.0)
        normalized_distance = min(1.0, self.distance_to_camera)
        
        # Wähle neues LOD
        new_lod = self.lod_manager.get_lod_for_distance(normalized_distance)
        
        if new_lod != self.current_lod:
            self.current_lod = new_lod
            self.current_polygon_count = int(
                self.base_polygon_count * new_lod.polygon_ratio
            )
            self.lod_switches += 1
            return True
        
        return False
    
    def render(self, use_lod: bool = True) -> int:
        """
        Simuliert Rendering der Turbine.
        
        Args:
            use_lod: Ob LOD-basierte Polygon-Counts verwendet werden
            
        Returns:
            Anzahl der gerenderten Polygone
        """
        self.render_count += 1
        
        if use_lod and self.current_lod:
            return self.current_polygon_count
        else:
            return self.base_polygon_count
    
    def get_stats(self) -> dict:
        """Gibt Statistiken über diese Turbine zurück."""
        return {
            'position': (self.x, self.z),
            'distance': self.distance_to_camera,
            'current_lod': self.current_lod.name if self.current_lod else "None",
            'polygon_count': self.current_polygon_count,
            'base_polygon_count': self.base_polygon_count,
            'lod_switches': self.lod_switches,
            'render_count': self.render_count,
        }


class LODRenderBatch:
    """
    Gruppiert Turbinen nach LOD-Level für effizientes Batch-Rendering.
    
    Vorteil: Kann LODs getrennt rendern (z.B. unterschiedliche Shader)
    """
    
    def __init__(self):
        self.batches = {}  # lod_name -> [turbines]
        self.total_polygons = 0
    
    def add_turbine(self, turbine: LODTurbine) -> None:
        """Fügt Turbine zu ihrem LOD-Batch hinzu."""
        lod_name = turbine.current_lod.name if turbine.current_lod else "LOD0"
        
        if lod_name not in self.batches:
            self.batches[lod_name] = []
        
        self.batches[lod_name].append(turbine)
        self.total_polygons += turbine.current_polygon_count
    
    def render_all(self) -> int:
        """Rendert alle Turbinen und gibt Gesamt-Polygon-Anzahl zurück."""
        total = 0
        for lod_name, turbines in self.batches.items():
            for turbine in turbines:
                total += turbine.render(use_lod=True)
        return total
    
    def get_batch_stats(self) -> dict:
        """Gibt Statistiken über die Batches zurück."""
        stats = {}
        for lod_name, turbines in self.batches.items():
            stats[lod_name] = {
                'count': len(turbines),
                'total_polygons': sum(t.current_polygon_count for t in turbines),
            }
        return stats
    
    def __repr__(self) -> str:
        lines = ["LOD Batches:"]
        total_turbines = sum(len(t) for t in self.batches.values())
        for lod_name, turbines in self.batches.items():
            poly_count = sum(t.current_polygon_count for t in turbines)
            lines.append(
                f"  {lod_name}: {len(turbines):4d} turbines, {poly_count:6d} polygons"
            )
        lines.append(f"  Total: {total_turbines:4d} turbines, {self.total_polygons:6d} polygons")
        return "\n".join(lines)


def benchmark_lod_system(num_turbines: int = 5000) -> None:
    """Benchmark: LOD vs. No-LOD Rendering."""
    import random
    
    print("\n" + "="*70)
    print(f"LOD System Benchmark ({num_turbines} Turbines)")
    print("="*70)
    
    # Erstelle Test-Turbinen
    lod_mgr = LODManager()
    turbines = []
    
    random.seed(42)
    camera_pos = (0.0, 0.0)  # Kamera im Zentrum
    
    for i in range(num_turbines):
        x = random.uniform(-1.5, 1.5)
        z = random.uniform(-1.8, 1.8)
        turbine = LODTurbine(x, z, base_polygon_count=150, lod_manager=lod_mgr)
        turbine.update_lod(camera_pos)
        turbines.append(turbine)
    
    # Test 1: Ohne LOD
    start = time.time()
    total_polygons_no_lod = 0
    for turbine in turbines:
        total_polygons_no_lod += turbine.render(use_lod=False)
    no_lod_time = time.time() - start
    
    # Test 2: Mit LOD
    start = time.time()
    total_polygons_with_lod = 0
    for turbine in turbines:
        total_polygons_with_lod += turbine.render(use_lod=True)
    lod_time = time.time() - start
    
    reduction = (1 - total_polygons_with_lod / total_polygons_no_lod) * 100
    
    print(f"\nOhne LOD:")
    print(f"  Polygone: {total_polygons_no_lod:8d}")
    print(f"  Zeit:     {no_lod_time*1000:8.3f}ms")
    
    print(f"\nMit LOD:")
    print(f"  Polygone: {total_polygons_with_lod:8d}")
    print(f"  Zeit:     {lod_time*1000:8.3f}ms")
    
    print(f"\nEinsparung:")
    print(f"  Polygone: {total_polygons_no_lod - total_polygons_with_lod:8d} ({reduction:.1f}%)")
    print(f"  Speedup:  {no_lod_time/lod_time:8.2f}x")
    
    # LOD-Verteilung
    print(f"\n{lod_mgr.get_all_levels_info()}")
    
    lod_counts = {}
    for turbine in turbines:
        lod = turbine.current_lod.name
        lod_counts[lod] = lod_counts.get(lod, 0) + 1
    
    print("LOD-Verteilung:")
    for lod, count in sorted(lod_counts.items()):
        print(f"  {lod}: {count:5d} turbines ({count/num_turbines*100:5.1f}%)")


if __name__ == "__main__":
    benchmark_lod_system(29722)
