"""
Point-in-Polygon Test
=====================

Prueft ob ein Punkt innerhalb eines Polygons liegt.
Verwendet Ray-Casting Algorithmus.

Vorlesungskonzept: Computational Geometry
"""


def point_in_polygon(x: float, z: float, polygon_vertices: list) -> bool:
    """
    Prueft ob Punkt (x, z) im Polygon liegt.
    
    Ray-Casting Algorithmus: Zaehlt wie viele Kanten ein
    horizontaler Strahl nach rechts schneidet.
    Ungerade = innen, gerade = aussen.
    
    Args:
        x, z: Punkt-Koordinaten (3D x und z, nicht y)
        polygon_vertices: Liste von (x, y, z) Tupeln der Polygon-Ecken
        
    Returns:
        True wenn Punkt im Polygon liegt
    """
    n = len(polygon_vertices)
    if n < 3:
        return False
    
    inside = False
    
    # Extrahiere x und z aus den 3D-Vertices
    px = [v[0] for v in polygon_vertices]
    pz = [v[2] for v in polygon_vertices]
    
    j = n - 1
    for i in range(n):
        # Pruefe ob Kante den horizontalen Strahl schneidet
        if ((pz[i] > z) != (pz[j] > z)) and \
           (x < (px[j] - px[i]) * (z - pz[i]) / (pz[j] - pz[i]) + px[i]):
            inside = not inside
        j = i
    
    return inside


def find_bundesland_for_point(x: float, z: float, bundeslaender: list):
    """
    Findet das Bundesland fuer einen gegebenen Punkt.
    
    Args:
        x, z: Punkt-Koordinaten im 3D-Raum
        bundeslaender: Liste von Bundesland-Objekten
        
    Returns:
        Bundesland-Objekt oder None wenn nicht gefunden
    """
    for bl in bundeslaender:
        if point_in_polygon(x, z, bl.vertices_top):
            return bl
    return None
