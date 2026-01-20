"""
Spatial Grid - Schnelle Bundesland-Suche
=========================================

Vorberechnet ein 2D-Grid fuer O(1) Bundesland-Lookup.
Reduziert Point-in-Polygon Tests von O(n) auf O(1).
"""


class SpatialGrid:
    """
    2D-Grid fuer schnelle Bundesland-Zuordnung.
    
    Teilt Deutschland in ein Raster und speichert pro Zelle
    welches Bundesland dort ist.
    """
    
    def __init__(self, bundeslaender: list, grid_size: int = 100):
        """
        Args:
            bundeslaender: Liste von Bundesland-Objekten
            grid_size: Raster-Aufloesung (100x100 = 10.000 Zellen)
        """
        self.bundeslaender = bundeslaender
        self.grid_size = grid_size
        
        # Bounds (Deutschland)
        self.x_min, self.x_max = -1.1, 1.1
        self.z_min, self.z_max = -1.3, 1.3
        
        # Grid erstellen
        self.grid = {}
        self._build_grid()
    
    def _build_grid(self):
        """Baut das Grid auf."""
        from .point_in_polygon import point_in_polygon
        
        print(f"    Baue Spatial Grid ({self.grid_size}x{self.grid_size})...")
        
        dx = (self.x_max - self.x_min) / self.grid_size
        dz = (self.z_max - self.z_min) / self.grid_size
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x = self.x_min + (i + 0.5) * dx
                z = self.z_min + (j + 0.5) * dz
                
                # Finde Bundesland fuer diese Zelle
                bl_name = None
                
                # Stadtstaaten zuerst
                for bl in self.bundeslaender:
                    if bl.name in {'Berlin', 'Hamburg', 'Bremen'}:
                        if point_in_polygon(x, z, bl.vertices_top):
                            bl_name = bl.name
                            break
                
                # Dann normale Bundeslaender
                if not bl_name:
                    for bl in self.bundeslaender:
                        if bl.name not in {'Berlin', 'Hamburg', 'Bremen'}:
                            if point_in_polygon(x, z, bl.vertices_top):
                                bl_name = bl.name
                                break
                
                if bl_name:
                    self.grid[(i, j)] = bl_name
        
        print(f"      {len(self.grid)} Zellen mit Bundesland")
    
    def get_bundesland(self, x: float, z: float) -> str:
        """
        Schnelle Bundesland-Suche via Grid.
        
        Args:
            x, z: Position
            
        Returns:
            Bundesland-Name oder None
        """
        # Grid-Koordinaten berechnen
        i = int((x - self.x_min) / (self.x_max - self.x_min) * self.grid_size)
        j = int((z - self.z_min) / (self.z_max - self.z_min) * self.grid_size)
        
        # Bounds check
        if i < 0 or i >= self.grid_size or j < 0 or j >= self.grid_size:
            return None
        
        return self.grid.get((i, j))
    
    def get_bundesland_with_fallback(self, x: float, z: float) -> str:
        """
        Sucht Bundesland mit kleinem Fallback-Radius.
        
        Returns:
            Bundesland-Name oder None wenn außerhalb Deutschlands
        """
        bl_name = self.get_bundesland(x, z)
        
        if bl_name:
            return bl_name
        
        # Fallback: Suche NUR in direkten Nachbarzellen (1 Pixel Toleranz)
        # Dies erlaubt Windräder direkt an Grenzen, aber nicht weit außerhalb
        i = int((x - self.x_min) / (self.x_max - self.x_min) * self.grid_size)
        j = int((z - self.z_min) / (self.z_max - self.z_min) * self.grid_size)
        
        # Nur direkte Nachbarn (nicht diagonal)
        for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.grid_size and 0 <= nj < self.grid_size:
                bl_name = self.grid.get((ni, nj))
                if bl_name:
                    return bl_name
        
        # Außerhalb Deutschlands - None zurückgeben (wird nicht angezeigt)
        return None
