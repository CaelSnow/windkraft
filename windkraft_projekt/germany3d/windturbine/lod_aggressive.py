"""
Aggressive LOD-Konfiguration für Windkraft-Projekt
===================================================

Erweiterte Level-of-Detail Konfiguration mit aggressiverer Polygon-Reduktion
für bessere Performance bei großen Turbinen-Zahlen.

Wissenschaftliche Referenz:
- Luebke et al. (2002): "Level of Detail for 3D Graphics" (Elsevier)
- Hoppe (1996): "Progressive Meshes" (SIGGRAPH)

Standard LOD (alt):
    LOD0: 100% @ dist=0.0
    LOD1:  50% @ dist=0.3
    LOD2:  10% @ dist=0.8
    
Aggressiv LOD (neu):
    LOD0: 100% @ dist=0.0   (Nahbereich: volle Details)
    LOD1:  60% @ dist=0.2   (früher beginnen)
    LOD2:  25% @ dist=0.4   (mittlere Distanz)
    LOD3:   8% @ dist=0.6   (große Distanz)
    LOD4:   2% @ dist=0.9   (Punkte/Billboard)

Erwartete Einsparung: ~60-75% Polygone vs ~40% bei Standard-LOD
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class AggressiveLODLevel:
    """
    Definiert ein aggressives LOD-Level mit mehr Abstufungen.
    
    Zusätzliche Features:
    - segment_reduction: Weniger Segmente für zylindrische Formen
    - blade_count: Reduzierte Rotorblatt-Anzahl (3→1 bei LOD4)
    - skip_features: Liste von Features die übersprungen werden
    """
    name: str
    polygon_ratio: float
    distance_threshold: float
    segment_count: int = 8        # Turm/Nacelle Segmente (Standard: 8)
    blade_count: int = 3          # Rotorblatt-Anzahl (Standard: 3)
    skip_nacelle: bool = False    # Gondel überspringen?
    skip_blades: bool = False     # Rotorblätter überspringen?
    use_billboard: bool = False   # Billboard statt Geometrie?
    
    def __post_init__(self):
        # Validierung
        assert 0.0 <= self.polygon_ratio <= 1.0, "polygon_ratio muss zwischen 0 und 1 sein"
        assert self.distance_threshold >= 0.0, "distance_threshold muss >= 0 sein"
        assert self.segment_count >= 3, "Minimum 3 Segmente für Zylinder"
        assert 0 <= self.blade_count <= 3, "blade_count muss zwischen 0 und 3 sein"


class AggressiveLODManager:
    """
    Verwaltet aggressive Level-of-Detail Konfiguration.
    
    Bietet mehr LOD-Level mit stärkerer Polygon-Reduktion als Standard.
    """
    
    # Aggressive LOD-Konfiguration (5 Level statt 3)
    AGGRESSIVE_LODS = [
        AggressiveLODLevel("LOD0", polygon_ratio=1.00, distance_threshold=0.00,
                          segment_count=8, blade_count=3),
        AggressiveLODLevel("LOD1", polygon_ratio=0.60, distance_threshold=0.15,
                          segment_count=6, blade_count=3),
        AggressiveLODLevel("LOD2", polygon_ratio=0.25, distance_threshold=0.35,
                          segment_count=4, blade_count=3),
        AggressiveLODLevel("LOD3", polygon_ratio=0.08, distance_threshold=0.55,
                          segment_count=4, blade_count=1, skip_nacelle=True),
        AggressiveLODLevel("LOD4", polygon_ratio=0.02, distance_threshold=0.85,
                          segment_count=3, blade_count=0, skip_nacelle=True, 
                          skip_blades=True, use_billboard=True),
    ]
    
    # Standard-LOD zum Vergleich (aus lod.py)
    STANDARD_LODS = [
        AggressiveLODLevel("LOD0", polygon_ratio=1.00, distance_threshold=0.0),
        AggressiveLODLevel("LOD1", polygon_ratio=0.50, distance_threshold=0.3),
        AggressiveLODLevel("LOD2", polygon_ratio=0.10, distance_threshold=0.8),
    ]
    
    # Extreme LOD für sehr viele Turbinen (>30k)
    EXTREME_LODS = [
        AggressiveLODLevel("LOD0", polygon_ratio=1.00, distance_threshold=0.00,
                          segment_count=6, blade_count=3),
        AggressiveLODLevel("LOD1", polygon_ratio=0.40, distance_threshold=0.10,
                          segment_count=4, blade_count=2),
        AggressiveLODLevel("LOD2", polygon_ratio=0.15, distance_threshold=0.25,
                          segment_count=4, blade_count=1, skip_nacelle=True),
        AggressiveLODLevel("LOD3", polygon_ratio=0.05, distance_threshold=0.45,
                          segment_count=3, blade_count=0, skip_nacelle=True,
                          skip_blades=True),
        AggressiveLODLevel("LOD4", polygon_ratio=0.01, distance_threshold=0.70,
                          segment_count=3, blade_count=0, skip_nacelle=True,
                          skip_blades=True, use_billboard=True),
    ]
    
    def __init__(self, mode: str = "aggressive"):
        """
        Args:
            mode: "standard", "aggressive" oder "extreme"
        """
        self.mode = mode
        
        if mode == "standard":
            self.lod_levels = self.STANDARD_LODS
        elif mode == "extreme":
            self.lod_levels = self.EXTREME_LODS
        else:
            self.lod_levels = self.AGGRESSIVE_LODS
        
        # Sortiere nach distance_threshold
        self.lod_levels.sort(key=lambda x: x.distance_threshold)
        
        # Pre-compute Schwellenwerte für Binary Search
        self._thresholds = [lod.distance_threshold for lod in self.lod_levels]
    
    def get_lod_for_distance(self, distance: float) -> AggressiveLODLevel:
        """
        Wählt optimales LOD für gegebene Distanz.
        
        Verwendet Binary Search für O(log n) statt O(n).
        
        Args:
            distance: Normalisierte Distanz zur Kamera (0.0 - 1.0)
            
        Returns:
            Das passende LOD-Level
        """
        # Binary Search für passendes LOD
        import bisect
        idx = bisect.bisect_right(self._thresholds, distance) - 1
        idx = max(0, idx)
        return self.lod_levels[idx]
    
    def get_lod_for_distance_squared(self, distance_sq: float, 
                                     max_distance_sq: float = 1.0) -> AggressiveLODLevel:
        """
        Wählt LOD basierend auf quadrierter Distanz (schneller, keine sqrt).
        
        Args:
            distance_sq: Quadrierte Distanz zur Kamera
            max_distance_sq: Maximale Distanz² für Normalisierung
        
        Returns:
            Das passende LOD-Level
        """
        # Normalisiere mit quadriertem Threshold
        normalized = min(1.0, math.sqrt(distance_sq / max_distance_sq))
        return self.get_lod_for_distance(normalized)
    
    def calculate_polygon_savings(self, distances: List[float]) -> dict:
        """
        Berechnet erwartete Polygon-Einsparung für eine Distanz-Verteilung.
        
        Args:
            distances: Liste von Turbinen-Distanzen zur Kamera
            
        Returns:
            Dictionary mit Statistiken
        """
        total_base = len(distances) * 100  # Angenommene 100% pro Turbine
        total_with_lod = 0
        lod_counts = {}
        
        for dist in distances:
            lod = self.get_lod_for_distance(dist)
            total_with_lod += 100 * lod.polygon_ratio
            lod_counts[lod.name] = lod_counts.get(lod.name, 0) + 1
        
        return {
            'base_polygons': total_base,
            'lod_polygons': total_with_lod,
            'savings_percent': (1 - total_with_lod / total_base) * 100,
            'lod_distribution': lod_counts,
            'mode': self.mode
        }
    
    def get_config_summary(self) -> str:
        """Gibt lesbare Zusammenfassung der LOD-Konfiguration."""
        lines = [f"LOD-Konfiguration ({self.mode}):", "-" * 40]
        
        for lod in self.lod_levels:
            features = []
            if lod.skip_nacelle:
                features.append("no-nacelle")
            if lod.skip_blades:
                features.append("no-blades")
            if lod.use_billboard:
                features.append("billboard")
            
            feat_str = f" [{', '.join(features)}]" if features else ""
            lines.append(
                f"  {lod.name}: {lod.polygon_ratio*100:5.1f}% @ dist={lod.distance_threshold:.2f}"
                f" (seg={lod.segment_count}, blades={lod.blade_count}){feat_str}"
            )
        
        return "\n".join(lines)


def get_aggressive_lod_config(turbine_count: int) -> AggressiveLODManager:
    """
    Wählt automatisch die beste LOD-Konfiguration basierend auf Turbinen-Anzahl.
    
    Args:
        turbine_count: Anzahl der Turbinen in der Szene
        
    Returns:
        Passender LODManager
    """
    if turbine_count > 25000:
        return AggressiveLODManager("extreme")
    elif turbine_count > 10000:
        return AggressiveLODManager("aggressive")
    else:
        return AggressiveLODManager("standard")


# =============================================================================
# HYBRID LOD: Kombiniert Distanz + Bildschirmgröße
# =============================================================================

class HybridLODSelector:
    """
    Wählt LOD basierend auf kombinierter Metrik:
    - Distanz zur Kamera
    - Projizierte Bildschirmgröße (wichtiger bei verschiedenen Turbinengrößen)
    
    Referenz: Funkhouser & Séquin (1993): "Adaptive Display Algorithm"
    """
    
    def __init__(self, screen_height: int = 1080, fov: float = 45.0):
        """
        Args:
            screen_height: Bildschirmhöhe in Pixeln
            fov: Field-of-View in Grad
        """
        self.screen_height = screen_height
        self.fov_rad = math.radians(fov)
        
        # Pre-compute Konstante für Screen-Size-Berechnung
        # screen_size = object_size * screen_height / (2 * distance * tan(fov/2))
        self._screen_factor = screen_height / (2 * math.tan(self.fov_rad / 2))
    
    def get_screen_size(self, object_height: float, distance: float) -> float:
        """
        Berechnet projizierte Bildschirmgröße eines Objekts.
        
        Args:
            object_height: Reale Objekthöhe
            distance: Distanz zur Kamera
            
        Returns:
            Projizierte Höhe in Pixeln
        """
        if distance < 0.001:
            return float('inf')
        return object_height * self._screen_factor / distance
    
    def select_lod(self, object_height: float, distance: float,
                   lod_manager: AggressiveLODManager) -> AggressiveLODLevel:
        """
        Wählt LOD basierend auf Bildschirmgröße.
        
        Turbine, die auf dem Bildschirm klein erscheint → höheres LOD.
        """
        screen_size = self.get_screen_size(object_height, distance)
        
        # Pixel-Schwellenwerte für LOD-Auswahl
        # <10px: Billboard, <25px: LOD3, <50px: LOD2, <100px: LOD1, sonst LOD0
        if screen_size < 10:
            target_lod = 4
        elif screen_size < 25:
            target_lod = 3
        elif screen_size < 50:
            target_lod = 2
        elif screen_size < 100:
            target_lod = 1
        else:
            target_lod = 0
        
        # Verwende min(target_lod, available_lods)
        target_lod = min(target_lod, len(lod_manager.lod_levels) - 1)
        return lod_manager.lod_levels[target_lod]


# =============================================================================
# BENCHMARK: Vergleich Standard vs Aggressive LOD
# =============================================================================

def compare_lod_modes(num_turbines: int = 29722):
    """Vergleicht verschiedene LOD-Modi."""
    import random
    import time
    
    print("\n" + "=" * 70)
    print(f"LOD-Modus Vergleich ({num_turbines} Turbinen)")
    print("=" * 70)
    
    # Generiere zufällige Distanzen (0.0 - 1.0)
    random.seed(42)
    distances = [random.uniform(0.0, 1.0) for _ in range(num_turbines)]
    
    modes = ["standard", "aggressive", "extreme"]
    
    print(f"\n{'Mode':<12} | {'Polygone':>10} | {'Einsparung':>10} | {'LOD-Verteilung'}")
    print("-" * 70)
    
    for mode in modes:
        manager = AggressiveLODManager(mode)
        stats = manager.calculate_polygon_savings(distances)
        
        dist_str = ", ".join(f"{k}:{v}" for k, v in sorted(stats['lod_distribution'].items()))
        
        print(f"{mode:<12} | {stats['lod_polygons']:>10.0f} | {stats['savings_percent']:>9.1f}% | {dist_str}")
    
    print("\n" + "-" * 70)
    print("Konfigurationen im Detail:\n")
    
    for mode in modes:
        manager = AggressiveLODManager(mode)
        print(manager.get_config_summary())
        print()


if __name__ == "__main__":
    compare_lod_modes()
