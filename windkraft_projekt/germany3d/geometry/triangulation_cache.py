"""
Triangulation Cache
===================

Cached berechnete Triangulationen für schnelleres Laden.
Speichert Hash des Polygons + berechnete Dreiecke.
"""

import os
import json
import hashlib
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path


def hash_polygon(vertices: List[Tuple[float, float]]) -> str:
    """
    Berechnet einen Hash für ein Polygon.
    
    Args:
        vertices: Liste von (x, z) Koordinaten
        
    Returns:
        SHA256-Hash als Hex-String
    """
    # Konvertiere zu String mit Rundung für Stabilität
    data = "|".join(f"{x:.6f},{z:.6f}" for x, z in vertices)
    return hashlib.sha256(data.encode()).hexdigest()[:16]


class TriangulationCache:
    """
    Cache für berechnete Triangulationen.
    
    Speichert pro Bundesland: {hash: triangles}
    Datei: germany3d/data/tri_cache.json
    """
    
    _instance: Optional['TriangulationCache'] = None
    _cache: Dict[str, Dict[str, Any]] = {}
    _cache_file: Path = None
    _modified: bool = False
    
    def __new__(cls) -> 'TriangulationCache':
        """Singleton-Pattern für globalen Cache."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_cache()
        return cls._instance
    
    def _init_cache(self):
        """Initialisiert den Cache beim ersten Zugriff."""
        # Cache-Datei im data-Ordner (NICHT als *cache* im Namen!)
        base_dir = Path(__file__).parent.parent / "data"
        self._cache_file = base_dir / "tri_data.json"
        
        # Lade existierenden Cache
        if self._cache_file.exists():
            try:
                with open(self._cache_file, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
            except Exception as e:
                print(f"[WARN] Cache-Laden fehlgeschlagen: {e}")
                self._cache = {}
        else:
            self._cache = {}
    
    def get(self, name: str, poly_hash: str) -> Optional[List[Tuple[int, int, int]]]:
        """
        Holt Triangulation aus dem Cache.
        
        Args:
            name: Bundesland-Name
            poly_hash: Hash des Polygons
            
        Returns:
            Liste von Dreiecken (a, b, c) oder None
        """
        if name in self._cache:
            entry = self._cache[name]
            if entry.get('hash') == poly_hash:
                # Konvertiere Listen zurück zu Tupeln
                return [tuple(t) for t in entry.get('triangles', [])]
        return None
    
    def set(self, name: str, poly_hash: str, triangles: List[Tuple[int, int, int]]):
        """
        Speichert Triangulation im Cache.
        
        Args:
            name: Bundesland-Name
            poly_hash: Hash des Polygons
            triangles: Liste von Dreiecken (a, b, c)
        """
        self._cache[name] = {
            'hash': poly_hash,
            'triangles': [list(t) for t in triangles]
        }
        self._modified = True
    
    def save(self):
        """Speichert Cache auf Festplatte."""
        if not self._modified:
            return
            
        try:
            # Erstelle Verzeichnis falls nötig
            self._cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Verwende builtins.open für Sicherheit bei __del__
            import builtins
            with builtins.open(self._cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, indent=2)
            
            self._modified = False
        except Exception as e:
            # Ignoriere Fehler beim Beenden (builtins nicht verfügbar)
            pass
    
    def clear(self):
        """Löscht den Cache."""
        self._cache = {}
        self._modified = True
        
        if self._cache_file and self._cache_file.exists():
            try:
                self._cache_file.unlink()
            except Exception:
                pass
    
    def __del__(self):
        """Speichert Cache beim Beenden."""
        try:
            if hasattr(self, '_modified') and self._modified:
                self.save()
        except Exception:
            # Ignoriere alle Fehler beim Beenden
            pass
