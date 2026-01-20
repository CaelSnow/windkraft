"""
Triangulation - Ear-Clipping Algorithmus
========================================

Wandelt beliebige Polygone (auch konkave) in Dreiecke um.
Dies ist wichtig für das OpenGL-Rendering, da nur Dreiecke
nativ unterstützt werden.

Vorlesungskonzepte:
- Polygon Triangulation
- Computational Geometry
"""

# Versuche mapbox_earcut zu importieren (fuer Loecher)
try:
    import mapbox_earcut as earcut
    HAS_EARCUT = True
except ImportError:
    HAS_EARCUT = False


def triangulate_polygon(vertices_2d: list) -> list:
    """
    Ear-clipping Triangulierung für beliebige Polygone.
    
    Funktioniert auch bei konkaven Polygonen. Der Algorithmus
    findet "Ohren" (konvexe Ecken ohne innere Punkte) und
    schneidet sie nacheinander ab.
    
    Args:
        vertices_2d: Liste von (x, z) Koordinaten
        
    Returns:
        Liste von Dreieck-Indizes [(a, b, c), ...]
    """
    pts = vertices_2d[:]
    n = len(pts)
    
    if n < 3:
        return []
    
    # Stelle sicher, dass Polygon gegen den Uhrzeigersinn ist
    area = _polygon_signed_area(pts)
    
    if area < 0:
        pts = pts[::-1]
    
    # Ear-clipping Algorithmus
    indices = list(range(n))
    triangles = []
    
    while len(indices) > 3:
        ear_found = False
        
        for i in range(len(indices)):
            prev_i = indices[(i - 1) % len(indices)]
            curr_i = indices[i]
            next_i = indices[(i + 1) % len(indices)]
            
            a, b, c = pts[prev_i], pts[curr_i], pts[next_i]
            
            # Prüfe ob konvex (CCW Windung)
            cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if cross <= 0:
                continue
            
            # Prüfe ob kein anderer Punkt im Dreieck liegt
            is_ear = True
            for j in indices:
                if j in (prev_i, curr_i, next_i):
                    continue
                if _point_in_triangle(pts[j], a, b, c):
                    is_ear = False
                    break
            
            if is_ear:
                triangles.append((prev_i, curr_i, next_i))
                indices.pop(i)
                ear_found = True
                break
        
        if not ear_found:
            # Fallback: Einfache Fan-Triangulierung
            for k in range(1, len(indices) - 1):
                triangles.append((indices[0], indices[k], indices[k + 1]))
            break
    
    if len(indices) == 3:
        triangles.append((indices[0], indices[1], indices[2]))
    
    return triangles


def _polygon_signed_area(pts: list) -> float:
    """
    Berechnet die vorzeichenbehaftete Fläche eines Polygons.
    
    Positiv = gegen Uhrzeigersinn
    Negativ = im Uhrzeigersinn
    """
    n = len(pts)
    area = sum(
        pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1]
        for i in range(n)
    )
    return area


def _point_in_triangle(p: tuple, a: tuple, b: tuple, c: tuple) -> bool:
    """
    Prüft ob Punkt p im Dreieck abc liegt.
    
    Verwendet das Sign-Test Verfahren.
    """
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    
    d1 = sign(p, a, b)
    d2 = sign(p, b, c)
    d3 = sign(p, c, a)
    
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    
    return not (has_neg and has_pos)


def polygon_area(polygon: list) -> float:
    """
    Berechnet die Fläche eines Polygons (Shoelace-Formel).
    
    Args:
        polygon: Liste von (x, y) Koordinaten
        
    Returns:
        Fläche (immer positiv)
    """
    n = len(polygon)
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += polygon[i][0] * polygon[j][1]
        area -= polygon[j][0] * polygon[i][1]
    return abs(area) / 2


def triangulate_polygon_with_holes(outer: list, holes: list) -> list:
    """
    Trianguliert ein Polygon MIT Loechern.
    
    Verwendet mapbox_earcut wenn verfuegbar, sonst Fallback.
    
    Args:
        outer: Aeusseres Polygon als [(x, z), ...]
        holes: Liste von Loch-Polygonen, jedes als [(x, z), ...]
        
    Returns:
        Liste von Dreieck-Indizes [(a, b, c), ...]
    """
    if HAS_EARCUT:
        return _triangulate_with_earcut(outer, holes)
    else:
        # Fallback: Ignoriere Loecher (nicht ideal, aber funktioniert)
        print("    WARNUNG: mapbox_earcut nicht installiert, Loecher werden ignoriert")
        print("    Installieren mit: pip install mapbox-earcut")
        return triangulate_polygon(outer)


def _triangulate_with_earcut(outer: list, holes: list) -> list:
    """
    Trianguliert mit mapbox_earcut Bibliothek.
    
    mapbox_earcut erwartet:
    - vertices: Nx2 Array aller Vertices (outer + alle holes)
    - ring_end_indices: Array mit Endindizes jedes Rings
      z.B. outer hat 100 vertices, hole1 hat 20, hole2 hat 15
      -> ring_end_indices = [100, 120, 135]
    """
    import numpy as np
    
    # Alle Vertices sammeln: erst outer, dann holes
    all_vertices = list(outer)
    ring_end_indices = [len(outer)]  # Endindex des aeusseren Rings
    
    for hole in holes:
        all_vertices.extend(hole)
        ring_end_indices.append(len(all_vertices))  # Endindex dieses Lochs
    
    # In 2D numpy array konvertieren (shape: N x 2)
    vertices_array = np.array(all_vertices, dtype=np.float64)
    
    # Ring end indices als uint32 array
    rings_array = np.array(ring_end_indices, dtype=np.uint32)
    
    # Triangulieren
    indices = earcut.triangulate_float64(vertices_array, rings_array)
    
    # In Tripel konvertieren
    triangles = []
    for i in range(0, len(indices), 3):
        triangles.append((int(indices[i]), int(indices[i+1]), int(indices[i+2])))
    
    return triangles
