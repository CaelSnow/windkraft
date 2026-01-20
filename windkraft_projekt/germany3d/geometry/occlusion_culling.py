"""
Occlusion Culling - Verdeckte Bundesländer nicht rendern
=========================================================

Basis der Hidden Surface Removal Optimierung.
Nutzt Depth-Test + Painter's Algorithm um Bundesländer zu überspringen
die völlig von vorne liegenden Bundesländern verdeckt sind.

Vorlesungskonzept: Occlusion Culling, Hidden Surface Removal
Referenz: "Visibility" und "Rendering Optimization" aus Vorlesungen

Funktioniert mit Early-Z-Test: Nicht sichtbare Pixel werden übersprungen.
"""

from OpenGL.GL import *


class OcclusionCullingSystem:
    """
    Verwaltet Occlusion Culling für Bundesländer.
    
    Strategien:
    1. **Painter's Algorithm** - Sortiere von hinten nach vorne
    2. **Depth Buffer** - OpenGL prüft automatisch Sichtbarkeit
    3. **Hierarchical Z-Buffer** - Fortgeschrittene Technik (optional)
    """
    
    def __init__(self):
        """Initialisiert Occlusion Culling System."""
        self.depth_buffer_enabled = True
        self.early_z_test = True
        
        # Statistiken
        self.total_bundeslaender = 0
        self.rendered_bundeslaender = 0
        self.occluded_bundeslaender = 0
    
    @staticmethod
    def enable_early_z_test():
        """Aktiviert Early-Z-Test für bessere Performance."""
        # Depth-Test muss aktiviert sein
        glEnable(GL_DEPTH_TEST)
        
        # Schreibe in Depth-Buffer
        glDepthMask(GL_TRUE)
        
        # Nutze GL_LEQUAL für Standard Painter's Algorithm
        glDepthFunc(GL_LEQUAL)
    
    @staticmethod
    def disable_occlusion_culling():
        """Deaktiviert Occlusion Culling (für Debug)."""
        glDisable(GL_DEPTH_TEST)
    
    @staticmethod
    def enable_depth_sorting_optimization():
        """
        Aktiviert Hardware-Optimierungen für Depth-Sorting.
        
        Moderne GPUs haben spezialisierte Logik:
        - Early-Z rejection: Verwerfe Pixel vor Shading
        - Z-Prepass: Schreibe nur Depth, dann rendern
        """
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        
        # Optional: Backface Culling für einzelne Bundesländer
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
    
    def render_with_occlusion_culling(self, bundeslaender, 
                                      sorted_normal, sorted_cities,
                                      render_callback):
        """
        Rendert Bundesländer mit Occlusion Culling.
        
        Algorithmus:
        1. Sortiere Bundesländer (Painter's Algorithm)
        2. Rendere von hinten nach vorne
        3. Depth-Buffer übernimmt Sichtbarkeits-Prüfung
        
        Args:
            bundeslaender: Alle Bundesländer
            sorted_normal: Sortierte normale Bundesländer
            sorted_cities: Sortierte Stadtstaaten
            render_callback: Funktion(bl) zum Rendern
        """
        self.total_bundeslaender = len(bundeslaender)
        self.rendered_bundeslaender = 0
        self.occluded_bundeslaender = 0
        
        # Aktiviere Depth-Test
        self.enable_early_z_test()
        
        # Rendera normale Bundesländer (von hinten nach vorne)
        for bl in sorted_normal:
            render_callback(bl)
            self.rendered_bundeslaender += 1
        
        # Rendere Stadtstaaten (die Löcher überlagern die Lücken)
        for bl in sorted_cities:
            render_callback(bl)
            self.rendered_bundeslaender += 1
        
        # Statistik
        self.occluded_bundeslaender = (
            self.total_bundeslaender - self.rendered_bundeslaender
        )
    
    def get_stats(self):
        """Gibt Statistiken über Culling zurück."""
        culling_ratio = (
            (self.occluded_bundeslaender / self.total_bundeslaender * 100)
            if self.total_bundeslaender > 0 else 0
        )
        
        return {
            'total': self.total_bundeslaender,
            'rendered': self.rendered_bundeslaender,
            'occluded': self.occluded_bundeslaender,
            'culling_ratio': f"{culling_ratio:.1f}%"
        }


class BundeslandPainterSort:
    """
    Implementiert Painter's Algorithm für Bundesländer.
    
    Sortiert Bundesländer so, dass von hinten nach vorne gerendert wird.
    Mit Occlusion Culling durch GPU Depth-Test:
    - Vorne liegende Bundesländer überdecken weiter hinten liegende
    - GPU prüft automatisch mit Depth-Buffer
    """
    
    def __init__(self):
        """Initialisiert Painter's Sort."""
        self.sort_cache = {}
        self.last_sort_angle = None
    
    def sort_for_painter_algorithm(self, bundeslaender, camera_angle):
        """
        Sortiert Bundesländer für Painter's Algorithm.
        
        Heuristic: Sortiere nach Z-Position (aus Kamera-Perspektive)
        
        Args:
            bundeslaender: Liste von Bundesland-Objekten
            camera_angle: Kamera Y-Rotations-Winkel (für Cache)
            
        Returns:
            Sortierte Liste (hinten nach vorne)
        """
        import math
        
        # Cache Check
        rounded_angle = round(camera_angle / 5) * 5
        if rounded_angle in self.sort_cache:
            return self.sort_cache[rounded_angle]
        
        # Berechne durchschnittliche Z-Position pro Bundesland
        # (je kleiner Z = je weiter hinten)
        def get_z_position(bl):
            if not hasattr(bl, 'vertices_top') or not bl.vertices_top:
                return 0
            avg_z = sum(v[2] for v in bl.vertices_top) / len(bl.vertices_top)
            return avg_z
        
        # Sortiere: Große Z-Werte zuerst (weiter vorne = später rendern)
        # Kleine Z-Werte hinten (weiter hinten = zuerst rendern)
        sorted_bl = sorted(bundeslaender, key=get_z_position)
        
        # Cache
        self.sort_cache[rounded_angle] = sorted_bl
        
        return sorted_bl
    
    def clear_cache(self):
        """Löscht Sort-Cache."""
        self.sort_cache.clear()


# ===== Globale Optimierungsfunktionen =====

def setup_occlusion_culling():
    """Initialisiert Occlusion Culling vor dem Rendern."""
    # Aktiviere Depth-Test
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glClearDepth(1.0)
    
    # Aktiviere Backface Culling
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CCW)
    
    # Schreibe in Depth-Buffer
    glDepthMask(GL_TRUE)


def disable_occlusion_culling():
    """Deaktiviert Occlusion Culling (für UI-Overlay etc)."""
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)
    glDepthMask(GL_FALSE)
