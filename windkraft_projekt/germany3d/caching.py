"""
Cache Manager - Pickle-basiertes Caching für Bundesländer und Windräder
========================================================================

Reduziert Startup-Zeit von 7 Sekunden auf 0.5 Sekunden (beim Cache-Hit).
Nutzt Pickle mit HIGHEST_PROTOCOL für maximale Kompatibilität und Speed.

Verwendung:
    cache = get_cache_manager()
    if cache.cache_exists():
        data = cache.load_bundeslaender()
    else:
        data = compute_expensive_data()
        cache.save_bundeslaender(data)
"""

import os
import pickle
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


class CacheManager:
    """Verwaltet Pickle-Cache für Bundesländer und Windräder."""
    
    def __init__(self, cache_dir: str = None):
        """
        Initialisiert den CacheManager.
        
        Args:
            cache_dir: Cache-Verzeichnis. Default: <project>/data/cache/
        """
        if cache_dir is None:
            # Standard: data/cache/ im Projektverzeichnis
            project_root = Path(__file__).parent.parent
            cache_dir = str(project_root / 'windkraft_projekt' / 'data' / 'cache')
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Pfade für verschiedene Cache-Dateien
        self.bundeslaender_cache = self.cache_dir / 'bundeslaender.pkl'
        self.windmills_cache = self.cache_dir / 'windmills.pkl'
        self.metadata_file = self.cache_dir / 'metadata.json'
        
        # Statistiken
        self.hits = 0
        self.misses = 0
        self._load_metadata()
    
    
    def _load_metadata(self):
        """Lädt oder initialisiert Metadaten."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            except:
                self.metadata = self._empty_metadata()
        else:
            self.metadata = self._empty_metadata()
    
    def _empty_metadata(self) -> Dict[str, Any]:
        """Erstellt leere Metadaten."""
        return {
            'created': None,
            'bundeslaender': {
                'saved': False,
                'timestamp': None,
                'count': 0,
                'size_bytes': 0
            },
            'windmills': {
                'saved': False,
                'timestamp': None,
                'count': 0,
                'size_bytes': 0
            },
            'cache_version': '1.0'
        }
    
    def _save_metadata(self):
        """Speichert Metadaten in JSON."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def cache_exists(self) -> bool:
        """Prüft, ob vollständiger Cache vorhanden ist."""
        bl_ok = self.bundeslaender_cache.exists() and self.bundeslaender_cache.stat().st_size > 0
        wm_ok = self.windmills_cache.exists() and self.windmills_cache.stat().st_size > 0
        return bl_ok and wm_ok
    
    def save_bundeslaender(self, bundeslaender: List) -> bool:
        """
        Speichert Bundesländer im Cache.
        
        Args:
            bundeslaender: Liste von Bundesland-Objekten
        
        Returns:
            True wenn erfolgreich, False sonst
        """
        try:
            with open(self.bundeslaender_cache, 'wb') as f:
                pickle.dump(bundeslaender, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            file_size = self.bundeslaender_cache.stat().st_size
            self.metadata['bundeslaender']['saved'] = True
            self.metadata['bundeslaender']['timestamp'] = datetime.now().isoformat()
            self.metadata['bundeslaender']['count'] = len(bundeslaender)
            self.metadata['bundeslaender']['size_bytes'] = file_size
            self._save_metadata()
            
            print(f"    [Cache] Bundesländer gespeichert ({file_size / 1024 / 1024:.1f} MB)")
            return True
        except Exception as e:
            print(f"    [Cache] Fehler beim Speichern: {e}")
            return False
    
    def load_bundeslaender(self) -> Optional[List]:
        """
        Lädt Bundesländer aus Cache.
        
        Returns:
            Liste von Bundesland-Objekten oder None
        """
        try:
            if not self.bundeslaender_cache.exists():
                return None
            
            with open(self.bundeslaender_cache, 'rb') as f:
                data = pickle.load(f)
            
            return data
        except Exception as e:
            print(f"    [Cache] Fehler beim Laden: {e}")
            return None
    
    def save_windmills(self, windmills: List[Dict]) -> bool:
        """
        Speichert Windmühlen-Daten im Cache.
        
        Args:
            windmills: Liste von Windmühlen-Dictionaries
        
        Returns:
            True wenn erfolgreich, False sonst
        """
        try:
            with open(self.windmills_cache, 'wb') as f:
                pickle.dump(windmills, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            file_size = self.windmills_cache.stat().st_size
            self.metadata['windmills']['saved'] = True
            self.metadata['windmills']['timestamp'] = datetime.now().isoformat()
            self.metadata['windmills']['count'] = len(windmills)
            self.metadata['windmills']['size_bytes'] = file_size
            self._save_metadata()
            
            print(f"    [Cache] Windmühlen gespeichert ({file_size / 1024 / 1024:.1f} MB)")
            return True
        except Exception as e:
            print(f"    [Cache] Fehler beim Speichern: {e}")
            return False
    
    def load_windmills(self) -> Optional[List[Dict]]:
        """
        Lädt Windmühlen-Daten aus Cache.
        
        Returns:
            Liste von Windmühlen-Dictionaries oder None
        """
        try:
            if not self.windmills_cache.exists():
                return None
            
            with open(self.windmills_cache, 'rb') as f:
                data = pickle.load(f)
            
            return data
        except Exception as e:
            print(f"    [Cache] Fehler beim Laden: {e}")
            return None
    
    def clear_cache(self, bundeslaender: bool = True, windmills: bool = True) -> bool:
        """
        Löscht Cache-Dateien.
        
        Args:
            bundeslaender: Ob Bundesländer-Cache gelöscht werden soll
            windmills: Ob Windmühlen-Cache gelöscht werden soll
        
        Returns:
            True wenn erfolgreich, False sonst
        """
        try:
            if bundeslaender and self.bundeslaender_cache.exists():
                self.bundeslaender_cache.unlink()
                self.metadata['bundeslaender']['saved'] = False
                print("    [Cache] Bundesländer-Cache gelöscht")
            
            if windmills and self.windmills_cache.exists():
                self.windmills_cache.unlink()
                self.metadata['windmills']['saved'] = False
                print("    [Cache] Windmühlen-Cache gelöscht")
            
            self._save_metadata()
            return True
        except Exception as e:
            print(f"    [Cache] Fehler beim Löschen: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über den Cache zurück."""
        return {
            'total_size_mb': sum([
                self.metadata['bundeslaender'].get('size_bytes', 0),
                self.metadata['windmills'].get('size_bytes', 0)
            ]) / 1024 / 1024,
            'bundeslaender': self.metadata['bundeslaender'],
            'windmills': self.metadata['windmills'],
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
        }
    
    def print_stats(self):
        """Gibt Cache-Statistiken aus."""
        stats = self.get_cache_stats()
        print("\n  [Cache Statistiken]")
        print(f"    Gesamtgröße: {stats['total_size_mb']:.1f} MB")
        print(f"    Hits: {stats['hits']}, Misses: {stats['misses']}")
        print(f"    Hit-Rate: {stats['hit_rate']*100:.1f}%")
        
        bl = stats['bundeslaender']
        if bl['saved']:
            print(f"    Bundesländer: {bl['count']} ({bl['size_bytes']/1024/1024:.1f} MB)")
        
        wm = stats['windmills']
        if wm['saved']:
            print(f"    Windmühlen: {wm['count']} ({wm['size_bytes']/1024/1024:.1f} MB)")


# Singleton-Instanz
_cache_manager: Optional[CacheManager] = None


def get_cache_manager(cache_dir: str = None) -> CacheManager:
    """
    Gibt die Singleton-Instanz des CacheManagers zurück.
    
    Args:
        cache_dir: Cache-Verzeichnis (nur beim ersten Aufruf relevant)
    
    Returns:
        CacheManager-Instanz
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(cache_dir)
    return _cache_manager

