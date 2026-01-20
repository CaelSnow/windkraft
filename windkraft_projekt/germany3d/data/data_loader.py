"""
Data Loader - Laedt GeoJSON und CSV Daten
=========================================

Funktionen zum Laden der Kartendaten und Windraeder.
Optimiert fuer Performance mit Bundesland-Zuordnung und Caching.
"""

import os
import csv
import json
import random
from ..config import DATA_DIR, HEIGHTS, DEFAULT_HEIGHT
from ..geometry import Bundesland, polygon_area
from .point_in_polygon import point_in_polygon
from ..caching import get_cache_manager


def load_bundeslaender(borders_path: str = None, use_cache: bool = True) -> list:
    """
    Laedt alle Bundeslaender aus der GeoJSON-Datei ODER aus Cache.
    
    Mit Cache: ~0.1s
    Ohne Cache: ~2s
    
    Args:
        borders_path: Pfad zur GeoJSON-Datei
        use_cache: Ob Cache genutzt werden soll
    """
    cache_manager = get_cache_manager()
    
    # Versuche aus Cache zu laden
    if use_cache and cache_manager.cache_exists():
        cached = cache_manager.load_bundeslaender()
        if cached:
            print(f"\n  ✓ Bundeslaender aus Cache geladen (schnell!)")
            cache_manager.hits += 1
            return cached
    
    # Cache nicht vorhanden oder deaktiviert → neu laden
    cache_manager.misses += 1
    
    if borders_path is None:
        borders_path = os.path.join(DATA_DIR, 'germany_borders.geo.json')
    
    if not os.path.exists(borders_path):
        print(f"\n  Datei nicht gefunden: {borders_path}")
        return []
    
    with open(borders_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    bundeslaender = []
    
    print("\n  Lade Bundeslaender:")
    
    for feature in data.get('features', []):
        bl = _process_feature(feature)
        if bl:
            bundeslaender.append(bl)
            print(f"    + {bl.name}")
    
    # Loch-System fuer Berlin und Bremen (Hamburg wird separat gerendert)
    _punch_holes_for_city_states(bundeslaender)
    
    print(f"\n  {len(bundeslaender)} Bundeslaender geladen")
    
    # Speichere im Cache für nächsten Start
    if use_cache:
        cache_manager.save_bundeslaender(bundeslaender)
    
    return bundeslaender


# Stadtstaaten und ihre umgebenden Bundeslaender
# ALLE drei Stadtstaaten bekommen echte Loecher
CITY_STATE_HOLES = {
    'Brandenburg': ['Berlin'],
    'Niedersachsen': ['Bremen'],
    'Schleswig-Holstein': ['Hamburg']  # NEU: Hamburg bekommt auch ein Loch
}


def _punch_holes_for_city_states(bundeslaender: list):
    """
    Stanzt Loecher fuer Stadtstaaten in die umgebenden Bundeslaender.
    
    Brandenburg bekommt ein Loch fuer Berlin.
    Niedersachsen bekommt ein Loch fuer Bremen.
    Schleswig-Holstein bekommt ein Loch fuer Hamburg.
    """
    # Erstelle Map fuer schnellen Zugriff
    bl_map = {bl.name: bl for bl in bundeslaender}
    
    for parent_name, hole_names in CITY_STATE_HOLES.items():
        if parent_name not in bl_map:
            continue
        
        parent_bl = bl_map[parent_name]
        holes = []
        
        for hole_name in hole_names:
            if hole_name in bl_map:
                hole_bl = bl_map[hole_name]
                # Hole-Vertices im 2D-Format (x, z)
                hole_2d = [(v[0], v[2]) for v in hole_bl.vertices_top]
                holes.append(hole_2d)
        
        if holes:
            # Re-trianguliere mit Loechern
            parent_bl.add_holes(holes)
            print(f"    * {parent_name}: {len(holes)} Loch/Loecher hinzugefuegt")


def _process_feature(feature: dict) -> Bundesland:
    """Verarbeitet ein einzelnes GeoJSON-Feature."""
    name = feature.get('properties', {}).get('name', 'Unknown')
    geometry = feature.get('geometry', {})
    geo_type = geometry.get('type', '')
    coords = geometry.get('coordinates', [])
    
    polygons = []
    if geo_type == 'Polygon':
        polygons = [coords[0]]
    elif geo_type == 'MultiPolygon':
        polygons = [poly[0] for poly in coords]
    
    if not polygons:
        return None
    
    largest = max(polygons, key=lambda p: polygon_area(p))
    height = HEIGHTS.get(name, DEFAULT_HEIGHT)
    bl = Bundesland(name, [(p[0], p[1]) for p in largest], extrusion=height)
    
    if bl.triangles:
        return bl
    return None


def _precompute_bboxes(bundeslaender: list):
    """Berechnet Bounding Boxes fuer schnelleren Point-in-Polygon Test."""
    for bl in bundeslaender:
        if bl.vertices_top:
            xs = [v[0] for v in bl.vertices_top]
            zs = [v[2] for v in bl.vertices_top]
            bl._bbox = (min(xs), max(xs), min(zs), max(zs))


def get_height_for_position(x: float, z: float, bundeslaender: list) -> float:
    """
    Ermittelt die Hoehe des Bundeslandes an Position (x, z).
    Optimiert mit Bounding-Box Check.
    WICHTIG: Prueft Stadtstaaten ZUERST (auch wenn sie Loecher sind).
    """
    # Stadtstaaten haben Prioritaet - IMMER zuerst pruefen!
    CITY_STATES = {'Berlin', 'Hamburg', 'Bremen'}
    
    # Erst Stadtstaaten pruefen (auch wenn sie Loecher in anderen Bundeslaendern sind)
    for bl in bundeslaender:
        if bl.name not in CITY_STATES:
            continue
        if hasattr(bl, '_bbox'):
            min_x, max_x, min_z, max_z = bl._bbox
            if x < min_x or x > max_x or z < min_z or z > max_z:
                continue
        if point_in_polygon(x, z, bl.vertices_top):
            # WICHTIG: Gib die Hoehe des Stadtstaats zurueck, nicht des umgebenden Bundeslandes!
            return bl.extrusion
    
    # Dann normale Bundeslaender
    for bl in bundeslaender:
        if bl.name in CITY_STATES:
            continue
        if hasattr(bl, '_bbox'):
            min_x, max_x, min_z, max_z = bl._bbox
            if x < min_x or x > max_x or z < min_z or z > max_z:
                continue
        if point_in_polygon(x, z, bl.vertices_top):
            return bl.extrusion
    return DEFAULT_HEIGHT


def get_bundesland_name_for_position(x: float, z: float, bundeslaender: list) -> str:
    """
    Ermittelt den Namen des Bundeslandes an Position (x, z).
    WICHTIG: Prueft Stadtstaaten ZUERST.
    
    Returns:
        Bundesland-Name oder None wenn außerhalb Deutschlands
    """
    # Stadtstaaten haben Prioritaet - sie werden zuerst geprueft
    CITY_STATES = {'Berlin', 'Hamburg', 'Bremen'}
    
    # Erst Stadtstaaten pruefen
    for bl in bundeslaender:
        if bl.name not in CITY_STATES:
            continue
        # Schneller Bounding-Box Check
        if hasattr(bl, '_bbox'):
            min_x, max_x, min_z, max_z = bl._bbox
            if x < min_x or x > max_x or z < min_z or z > max_z:
                continue
        if point_in_polygon(x, z, bl.vertices_top):
            return bl.name
    
    # Dann normale Bundeslaender pruefen
    for bl in bundeslaender:
        if bl.name in CITY_STATES:
            continue
        # Schneller Bounding-Box Check
        if hasattr(bl, '_bbox'):
            min_x, max_x, min_z, max_z = bl._bbox
            if x < min_x or x > max_x or z < min_z or z > max_z:
                continue
        if point_in_polygon(x, z, bl.vertices_top):
            return bl.name
    
    # KEIN FALLBACK mehr - Punkt liegt außerhalb Deutschlands
    return None


def _find_nearest_bundesland(x: float, z: float, bundeslaender: list) -> str:
    """
    Findet das naechste Bundesland fuer Punkte ausserhalb aller Polygone.
    Verwendet Distanz zum Polygon-Zentrum.
    """
    min_dist = float('inf')
    nearest = None
    
    for bl in bundeslaender:
        # Berechne Zentrum des Bundeslandes
        if bl.vertices_top:
            cx = sum(v[0] for v in bl.vertices_top) / len(bl.vertices_top)
            cz = sum(v[2] for v in bl.vertices_top) / len(bl.vertices_top)
            
            # Distanz zum Zentrum
            dist = (x - cx) ** 2 + (z - cz) ** 2
            
            if dist < min_dist:
                min_dist = dist
                nearest = bl.name
    
    return nearest if nearest else 'Unknown'


def load_windturbines_with_heights(csv_path: str, manager, bundeslaender: list,
                                    scale: float = 1.0, max_count: int = None,
                                    use_cache: bool = True):
    """
    Laedt ALLE Windraeder mit korrekter Bundesland-Hoehe ODER aus Cache.
    Die Windraeder werden nach Jahr sortiert gespeichert.
    
    Mit Cache: ~0.1s
    Ohne Cache: ~5s
    """
    cache_manager = get_cache_manager()
    
    # Versuche aus Cache zu laden
    if use_cache and cache_manager.cache_exists():
        cached = cache_manager.load_windmills()
        if cached:
            print(f"    ✓ Windraeder aus Cache geladen (schnell!)")
            cache_manager.hits += 1
            
            # Lade die gecachten Turbinen in den Manager
            for data in cached:
                base_height = 0.04 + (data['power'] / 10000) * 0.05
                height = base_height * scale
                rotor_radius = height * 0.4
                
                turbine = manager.add_turbine(
                    data['x'], data['z'], height, rotor_radius, data['power']
                )
                turbine.year = data['year']
                turbine.bl_height = data['bl_height']
                turbine.bl_name = data['bl_name']
            
            print(f"    {len(manager.turbines)} Windraeder aus Cache geladen")
            return
    
    # Cache nicht vorhanden oder deaktiviert → neu laden
    cache_manager.misses += 1
    
    if not os.path.exists(csv_path):
        print(f"    CSV nicht gefunden: {csv_path}")
        return
    
    turbine_data = []
    
    print("    Lese CSV-Daten...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                x = float(row['x'])
                z = float(row['z'])
                power = float(row.get('power_kw', 3000))
                year = int(row.get('year', 2000))
                
                turbine_data.append({
                    'x': x, 'z': z, 'power': power, 'year': year
                })
                
                if max_count and len(turbine_data) >= max_count:
                    break
                    
            except (ValueError, KeyError):
                continue
    
    print(f"    {len(turbine_data)} Eintraege gelesen, ermittle Bundesland-Hoehen...")
    
    # Bounding Boxes vorberechnen fuer schnelleren Lookup
    _precompute_bboxes(bundeslaender)
    
    # PERFORMANCE: Spatial Grid fuer schnelle Bundesland-Suche
    from .spatial_grid import SpatialGrid
    grid = SpatialGrid(bundeslaender, grid_size=100)
    
    # Statistik fuer Debugging
    stats = {
        'total': 0,
        'with_bundesland': 0,
        'fallback_nearest': 0,
        'by_bundesland': {}
    }
    
    # Bundesland-Hoehen und -Namen ermitteln (SCHNELL mit Grid)
    for i, data in enumerate(turbine_data):
        # Verwende Grid statt Point-in-Polygon (viel schneller!)
        data['bl_name'] = grid.get_bundesland_with_fallback(data['x'], data['z'])
        data['bl_height'] = get_height_for_position(data['x'], data['z'], bundeslaender)
        
        # Statistik
        stats['total'] += 1
        if data['bl_name'] and data['bl_name'] != 'Unknown':
            stats['with_bundesland'] += 1
            stats['by_bundesland'][data['bl_name']] = stats['by_bundesland'].get(data['bl_name'], 0) + 1
        
        if (i + 1) % 5000 == 0:
            print(f"      {i + 1}/{len(turbine_data)} verarbeitet...")
    
    # Nach Jahr sortieren
    turbine_data.sort(key=lambda t: t['year'])
    
    # Turbinen erstellen
    for data in turbine_data:
        base_height = 0.04 + (data['power'] / 10000) * 0.05
        height = base_height * scale
        rotor_radius = height * 0.4
        
        turbine = manager.add_turbine(
            data['x'], data['z'], height, rotor_radius, data['power']
        )
        turbine.year = data['year']
        turbine.bl_height = data['bl_height']
        turbine.bl_name = data['bl_name']  # NEU: Bundesland-Name speichern
    
    print(f"    {len(manager.turbines)} Windraeder geladen (mit Bundesland-Hoehen)")
    
    # Statistik ausgeben
    print(f"\n    Bundesland-Zuordnung:")
    print(f"      Gesamt: {stats['total']}")
    print(f"      Mit Bundesland: {stats['with_bundesland']} ({100*stats['with_bundesland']/stats['total']:.1f}%)")
    print(f"\n    Top 5 Bundeslaender:")
    sorted_bl = sorted(stats['by_bundesland'].items(), key=lambda x: -x[1])[:5]
    for name, count in sorted_bl:
        print(f"      {name}: {count}")
    
    # Speichere im Cache für nächsten Start
    if use_cache:
        cache_manager.save_windmills(turbine_data)



def load_windturbines(csv_path: str, manager, 
                      scale: float = 0.1,
                      max_count: int = None,
                      year_filter: int = None):
    """
    Legacy-Funktion - Laedt Windraeder ohne Bundesland-Hoehe.
    """
    if not os.path.exists(csv_path):
        print(f"    CSV nicht gefunden: {csv_path}")
        _add_demo_turbines(manager)
        return
    
    loaded = 0
    skipped_year = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if max_count and loaded >= max_count:
                break
            
            try:
                year = int(row.get('year', 0))
                if year_filter and year > 0 and year > year_filter:
                    skipped_year += 1
                    continue
                
                x = float(row['x'])
                z = float(row['z'])
                power = float(row.get('power_kw', 3000))
                
                base_height = 0.06 + (power / 10000) * 0.06
                height = base_height * scale
                rotor_radius = height * 0.4
                
                turbine = manager.add_turbine(x, z, height, rotor_radius, power)
                turbine.year = year
                loaded += 1
                
            except (ValueError, KeyError):
                continue
    
    print(f"    {loaded} Windraeder geladen")
    if year_filter:
        print(f"    (Jahr-Filter: <= {year_filter}, {skipped_year} uebersprungen)")


def _add_demo_turbines(manager, count: int = 50):
    """Fuegt Demo-Windraeder hinzu."""
    print("    Fuege Demo-Windraeder hinzu...")
    for _ in range(count):
        x = random.uniform(-1.0, 1.0)
        z = random.uniform(-1.2, 1.2)
        height = random.uniform(0.08, 0.15)
        power = random.uniform(500, 6000)
        manager.add_turbine(x, z, height, height * 0.5, power)
    print(f"    {count} Demo-Windraeder erstellt")
