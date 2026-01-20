# Vollständige Technische Dokumentation
## 3D Windkraft-Visualisierung Deutschland

**Version:** 1.0  
**Datum:** Januar 2025  
**Status:** Production Ready  

---

## Inhaltsverzeichnis

1. [Projekt-Übersicht](#projekt-übersicht)
2. [System-Anforderungen](#system-anforderungen)
3. [Installation & Setup](#installation--setup)
4. [Architektur-Detail](#architektur-detail)
5. [Datenverarbeitung](#datenverarbeitung)
6. [Rendering-System](#rendering-system)
7. [Animationssystem](#animationssystem)
8. [Performance-Optimierungen](#performance-optimierungen)
9. [Bekannte Probleme & Lösungen](#bekannte-probleme--lösungen)
10. [API-Referenz](#api-referenz)
11. [Erweiterungen & Zukünftige Arbeiten](#erweiterungen--zukünftige-arbeiten)

---

## Projekt-Übersicht

### Was ist dieses Projekt?

Ein interaktiver 3D-Visualizer der Windkraft-Entwicklung in Deutschland von 1990-2025.

**Kernfeatures:**
- Dynamische Bundesland-Höhen basierend auf installierter Windkraft-Leistung
- 29.722 individuell positionierte und animierte Windräder
- 3 Stadtstaaten als echte Polygonlöcher in ihren Nachbarn
- Echtzeit-Animation mit 60 FPS auf Standard-Hardware
- Wissenschaftliche Datenvisualisierung mit Farbkodierung

**Technischer Stack:**
- **Language:** Python 3.11
- **Graphics:** OpenGL 2.1 via PyOpenGL
- **GUI Framework:** pygame 2.6.1
- **GIS:** GeoJSON (Bundesländer), Point-in-Polygon, mapbox_earcut
- **Data:** CSV (Windraeder), JSON (Grenzen)

**Dateigröße & Performance:**
- Hauptprogramm: ~2 MB Python-Code
- GeoJSON-Daten: ~1 MB (16 Bundesländer)
- CSV-Windräder: ~2 MB (29.722 Einträge)
- Memory Usage: ~500 MB zur Laufzeit
- Startup: 2-3 Sekunden
- FPS: 55-60 (konstant)

---

## System-Anforderungen

### Minimum-Anforderungen
```
Processor:  Intel Core 2 Duo oder äquivalent
RAM:        2 GB
GPU:        OpenGL 2.1 kompatible Grafikkarte
OS:         Windows 7+, Linux, macOS 10.7+
Monitor:    1024x768 (empfohlen: 1920x1080)
```

### Empfohlene Anforderungen
```
Processor:  Intel Core i5 oder besser
RAM:        8+ GB
GPU:        NVIDIA/AMD mit 2GB+ VRAM
OS:         Windows 10+, Ubuntu 20.04+, macOS 10.13+
Monitor:    1920x1080 oder besser
```

### Python-Abhängigkeiten
```
python>=3.8
pygame>=2.6.1
PyOpenGL>=3.1.5
Pillow>=9.0.0
numpy>=1.20.0
mapbox-earcut>=0.12.11
```

---

## Installation & Setup

### 1. Python-Umgebung einrichten

```bash
# Virtual Environment erstellen
python -m venv venv

# Aktivieren
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

**requirements.txt Inhalt:**
```
pygame==2.6.1
PyOpenGL==3.1.5
Pillow==9.0.0
numpy==1.21.0
mapbox-earcut==0.12.11
```

### 3. Daten-Setup

```
windkraft_projekt/
├── data/
│   ├── germany_borders.geo.json     (16 Bundesländer mit GPS-Grenzen)
│   ├── windmills_processed.csv      (29.722 Windräder mit Metadaten)
│   └── plz_geocoord.csv             (Postleitzahl-Koordinaten)
└── main.py
```

### 4. Programm starten

```bash
python main.py
```

---

## Architektur-Detail

### Modul: `germany3d/config.py`

**Zweck:** Zentrale Konfigurationsdatei für alle Konstanten

**Wichtige Konstanten:**

```python
# Fenster
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 1000

# Geografische Grenzen (GPS-Koordinaten von Deutschland)
LAT_MIN = 47.27      # Süden
LAT_MAX = 55.06      # Norden
LON_MIN = 5.87       # Westen
LON_MAX = 15.04      # Osten

# Höhen-Berechnung
MIN_HEIGHT = 0.08    # Minimale Extrusion (> 0 sonst Tiefenbuffer-Fehler)
MAX_HEIGHT = 0.35    # Maximale Extrusion
BASE_HEIGHT = 0.10   # Basis-Höhe für Vergleiche
DEFAULT_HEIGHT = 0.14 # Fallback für unbekannte Bundesländer

# Polygon-Vereinfachung
POLYGON_SIMPLIFICATION = 500  # Jeden n-ten Punkt beibehalten

# Farben (RGB, 0-1)
COLORS = {
    'Schleswig-Holstein': (0.60, 0.68, 0.75),  # Blau
    'Niedersachsen':      (0.85, 0.65, 0.55),  # Lachs
    'Berlin':             (0.50, 0.80, 0.40),  # Grün
    # ... weitere 13 Bundesländer
}
```

**Änderbare Parameter:**
- `POLYGON_SIMPLIFICATION`: Höher = weniger Vertices, schneller, weniger Genauigkeit
- `MIN_HEIGHT`, `MAX_HEIGHT`: Skalierung der Bundesland-Höhen
- `WINDOW_WIDTH/HEIGHT`: Fenster-Größe

---

### Modul: `germany3d/core/viewer.py`

**Zweck:** Haupt-Anwendungsklasse, steuert alles

**Klassendefinition:**

```python
class Germany3DViewer:
    def __init__(self):
        # === INITIALISIERUNG ===
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        
        # Pygame-Setup
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            DOUBLEBUF | OPENGL
        )
        
        # OpenGL-Setup
        init_opengl()
        setup_projection(self.width, self.height)
        
        # Daten laden
        self.bundeslaender = load_bundeslaender(DATA_DIR)
        self.wind_turbines = load_windturbines_with_heights(
            DATA_DIR,
            self.bundeslaender
        )
        self.wind_statistics = WindPowerStatistics(DATA_DIR)
        
        # Kamera
        self.camera = Camera()
        self.mouse = MouseHandler(self.camera)
        
        # Animation
        self.current_year = 1990
        self.animation_running = False
        self.animation_time = 0.0
        self.animation_speed = 5  # Jahre pro Sekunde
```

**Wichtige Methoden:**

```python
def run(self):
    """Haupt-Loop (60 FPS)"""
    clock = pygame.time.Clock()
    
    while True:
        dt = clock.tick(60) / 1000.0  # Delta Time in Sekunden
        
        if not self._handle_events():
            break
        
        self._update_animation(dt)
        self._update_bundesland_heights()
        self._update_turbine_heights()
        self._render()

def _update_animation(self, dt):
    """Aktualisiert Animations-Zeit"""
    if self.animation_running:
        self.animation_time += dt * self.animation_speed
        
        new_year = int(self.animation_time / 5) * 5 + 1990
        if new_year != self.current_year:
            self.current_year = new_year
            self._update_bundesland_heights()
            self._update_turbine_heights()

def _update_bundesland_heights(self):
    """Berechnet neue Höhen für aktuelles Jahr"""
    for bl in self.bundeslaender:
        new_height = self.wind_statistics.get_height_for_year(
            bl.name, 
            self.current_year
        )
        bl.update_height(new_height)

def _update_turbine_heights(self):
    """Synchronisiert Turbinen-Höhen mit Bundesland-Höhen"""
    height_map = {bl.name: bl.extrusion for bl in self.bundeslaender}
    
    for turbine in self.wind_turbines.turbines:
        bl_name = getattr(turbine, 'bl_name', None)
        if bl_name and bl_name in height_map:
            turbine.bl_height = height_map[bl_name]

def _render_3d_scene(self):
    """Rendert alle 3D-Geometrie"""
    apply_camera_transform(
        self.camera.rot_x,
        self.camera.rot_y,
        self.camera.zoom
    )
    update_lighting()
    
    # Stadtstaaten müssen NACH normalen Bundesländern kommen
    CITY_STATES = {'Berlin', 'Hamburg', 'Bremen'}
    
    normal_bl = [b for b in self.bundeslaender if b.name not in CITY_STATES]
    city_states = [b for b in self.bundeslaender if b.name in CITY_STATES]
    
    # Sortierung nach Z-Position (painter's algorithm)
    sorted_normal = sorted(
        normal_bl,
        key=lambda b: -sum(v[2] for v in b.vertices_top) / len(b.vertices_top)
    )
    sorted_cities = sorted(
        city_states,
        key=lambda b: -sum(v[2] for v in b.vertices_top) / len(b.vertices_top)
    )
    
    # Schatten
    all_bl = sorted_normal + sorted_cities
    render_map_shadows(all_bl, self.camera.rot_y)
    
    # Normale Bundesländer
    for bl in sorted_normal:
        bl.render()
    
    # Stadtstaaten (oben)
    for bl in sorted_cities:
        bl.render()
    
    # Windräder
    if self.show_turbines:
        for turbine in self.wind_turbines.get_visible_turbines():
            turbine.render(self.animation_time)

def _render_legend(self):
    """Rendert 2D-Legende auf top of 3D-Szene"""
    # Wechsel zu 2D-Projektion
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, self.width, 0, self.height)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    # === Titel ===
    self._render_text("Deutschland", 30, 180, large=True)
    self._render_text("Windkraft-Evolution", 30, 152)
    
    # === Farbverlauf-Gradient ===
    # 50 Segmente von 0-7000 kW
    gradient_x, gradient_y = 30, 110
    gradient_width, gradient_height = 180, 14
    
    glBegin(GL_QUADS)
    for i in range(50):
        power1 = (i / 50) * 7000
        power2 = ((i + 1) / 50) * 7000
        
        color1 = get_power_color(power1)
        color2 = get_power_color(power2)
        
        x1 = gradient_x + i * (gradient_width / 50)
        x2 = gradient_x + (i + 1) * (gradient_width / 50)
        
        glColor3f(*color1)
        glVertex2f(x1, gradient_y)
        glVertex2f(x1, gradient_y - gradient_height)
        
        glColor3f(*color2)
        glVertex2f(x2, gradient_y - gradient_height)
        glVertex2f(x2, gradient_y)
    glEnd()
    
    # === Jahr ===
    year_x = self.width - 200
    year_y = 120
    self._render_text(
        str(self.current_year),
        year_x, year_y,
        large=True,
        scale=2.5
    )
    
    # === Info ===
    count = self._count_visible_turbines()
    self._render_text(
        f"Windraeder: {count:,}".replace(",", "."),
        30, 60
    )
    
    # Zurück zu 3D
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
```

---

### Modul: `germany3d/geometry/bundesland.py`

**Zweck:** Einzelnes Bundesland mit Polygon-Rendering

**Klassendefinition:**

```python
class Bundesland:
    def __init__(self, name, polygon, base_color):
        self.name = name
        self.polygon = polygon              # GPS-Koordinaten
        self.base_color = base_color        # RGB
        self.extrusion = 0.15               # Höhe
        
        # Farben (abgeleitet)
        self.top_color = base_color
        self.side_color = tuple(max(0, c - 0.20) for c in base_color)
        self.edge_color = tuple(max(0, c - 0.40) for c in base_color)
        
        # Vertices
        self.vertices_2d = []       # (x, z) für Triangulation
        self.vertices_top = []      # (x, y, z) Oberseite
        self.vertices_bottom = []   # (x, y, z) Unterseite
        self.triangles = []         # Dreieck-Indizes
        self.holes = []             # Für Stadtstaaten
        
        # Geometrie aufbauen
        self._build_vertices()
        self._triangulate()

    def _gps_to_3d(self, lon, lat):
        """Konvertiert GPS zu 3D-Raumkoordinaten"""
        from ..config import LON_MIN, LON_MAX, LAT_MIN, LAT_MAX
        
        # Normalisierung auf 0-1
        nx = (lon - LON_MIN) / (LON_MAX - LON_MIN)
        nz = (lat - LAT_MIN) / (LAT_MAX - LAT_MIN)
        
        # Zu 3D-Raum ([-1.1, 1.1] x [-1.3, 1.3])
        x = (nx - 0.5) * 2.2
        z = -(nz - 0.5) * 2.6  # Invertiert (Norden oben)
        
        return x, z

    def _build_vertices(self):
        """Konvertiert GPS-Polygon zu 3D-Vertices"""
        from ..config import POLYGON_SIMPLIFICATION
        
        # Vereinfachung
        step = max(1, len(self.polygon) // POLYGON_SIMPLIFICATION)
        simplified = [self.polygon[i] for i in range(0, len(self.polygon), step)]
        
        # Schließe Polygon
        if simplified[0] != simplified[-1]:
            simplified.append(simplified[0])
        
        # Konvertiere zu 3D
        for lon, lat in simplified:
            x, z = self._gps_to_3d(lon, lat)
            self.vertices_2d.append((x, z))
            self.vertices_top.append((x, self.extrusion, z))
            self.vertices_bottom.append((x, 0.0, z))

    def _triangulate(self):
        """Trianguliert das Polygon"""
        from .triangulation import triangulate_polygon
        self.triangles = triangulate_polygon(self.vertices_2d)

    def add_holes(self, holes):
        """
        Fügt echte Polygonlöcher hinzu (für Stadtstaaten)
        
        Wichtig: mapbox_earcut braucht ALL Vertices (outer + holes)
        """
        from .triangulation import triangulate_polygon_with_holes
        
        self.holes = holes
        
        # Hole-Vertices zu Listen hinzufügen
        for hole in holes:
            for x, z in hole:
                self.vertices_2d.append((x, z))
                self.vertices_top.append((x, self.extrusion, z))
                self.vertices_bottom.append((x, 0.0, z))
        
        # Re-Triangulieren
        outer_len = len(self.vertices_2d) - sum(len(h) for h in holes)
        outer_vertices = self.vertices_2d[:outer_len]
        
        self.triangles = triangulate_polygon_with_holes(
            outer_vertices,
            holes
        )

    def update_height(self, new_height):
        """Aktualisiert Höhe (nur Y-Komponente!)"""
        self.extrusion = new_height
        self.vertices_top = [
            (v[0], new_height, v[2]) for v in self.vertices_top
        ]

    def render(self):
        """OpenGL-Rendering mit Loch-Unterstützung"""
        if len(self.vertices_top) < 3:
            return
        
        # Berechne outer/hole Vertex-Count
        if hasattr(self, 'holes') and self.holes:
            hole_vertex_count = sum(len(h) for h in self.holes)
            outer_count = len(self.vertices_top) - hole_vertex_count
        else:
            outer_count = len(self.vertices_top)
        
        # === OBERSEITE ===
        glColor3f(*self.top_color)
        glNormal3f(0, 1, 0)
        
        glBegin(GL_TRIANGLES)
        for a, b, c in self.triangles:
            glVertex3f(*self.vertices_top[a])
            glVertex3f(*self.vertices_top[b])
            glVertex3f(*self.vertices_top[c])
        glEnd()
        
        # === SEITENWÄNDE AUSSEN ===
        glColor3f(*self.side_color)
        
        glBegin(GL_QUADS)
        for i in range(outer_count):
            next_i = (i + 1) % outer_count
            
            t1 = self.vertices_top[i]
            t2 = self.vertices_top[next_i]
            b1 = self.vertices_bottom[i]
            b2 = self.vertices_bottom[next_i]
            
            # Normale berechnen
            dx = t2[0] - t1[0]
            dz = t2[2] - t1[2]
            length = math.sqrt(dx*dx + dz*dz)
            if length > 0.0001:
                nx = -dz / length
                nz = dx / length
            else:
                nx, nz = 0, 1
            
            glNormal3f(nx, 0, nz)
            glVertex3f(*t1)
            glVertex3f(*t2)
            glVertex3f(*b2)
            glVertex3f(*b1)
        glEnd()
        
        # === SEITENWÄNDE INNEN (Loch-Ränder) ===
        if hasattr(self, 'holes') and self.holes:
            glBegin(GL_QUADS)
            offset = outer_count
            
            for hole in self.holes:
                hole_len = len(hole)
                for i in range(hole_len):
                    next_i = (i + 1) % hole_len
                    
                    idx1 = offset + i
                    idx2 = offset + next_i
                    
                    t1 = self.vertices_top[idx1]
                    t2 = self.vertices_top[idx2]
                    b1 = self.vertices_bottom[idx1]
                    b2 = self.vertices_bottom[idx2]
                    
                    # Invertierte Normale (innere Wand)
                    dx = t2[0] - t1[0]
                    dz = t2[2] - t1[2]
                    length = math.sqrt(dx*dx + dz*dz)
                    if length > 0.0001:
                        nx = dz / length
                        nz = -dx / length
                    else:
                        nx, nz = 0, 1
                    
                    glNormal3f(nx, 0, nz)
                    glVertex3f(*t1)
                    glVertex3f(*t2)
                    glVertex3f(*b2)
                    glVertex3f(*b1)
                
                offset += hole_len
            glEnd()
        
        # === UNTERSEITE ===
        glColor3f(*self.side_color)
        glNormal3f(0, -1, 0)
        
        glBegin(GL_TRIANGLES)
        for a, b, c in self.triangles:
            # Umgekehrte Reihenfolge für Normale
            glVertex3f(*self.vertices_bottom[c])
            glVertex3f(*self.vertices_bottom[b])
            glVertex3f(*self.vertices_bottom[a])
        glEnd()
        
        # === UMRISS ===
        glDisable(GL_LIGHTING)
        glColor3f(*self.edge_color)
        glLineWidth(1.3)
        
        glBegin(GL_LINE_LOOP)
        for i in range(outer_count):
            v = self.vertices_top[i]
            glVertex3f(v[0], v[1] + 0.001, v[2])
        glEnd()
        
        if hasattr(self, 'holes') and self.holes:
            offset = outer_count
            for hole in self.holes:
                glBegin(GL_LINE_LOOP)
                for i in range(len(hole)):
                    v = self.vertices_top[offset + i]
                    glVertex3f(v[0], v[1] + 0.001, v[2])
                glEnd()
                offset += len(hole)
        
        glEnable(GL_LIGHTING)
```

---

### Modul: `germany3d/geometry/triangulation.py`

**Zweck:** Polygon-Triangulation mit earcut

```python
def triangulate_polygon(vertices):
    """Trianguliere Polygon ohne Löcher"""
    from .triangulation import triangulate_polygon_simple
    return triangulate_polygon_simple(vertices)

def triangulate_polygon_with_holes(outer, holes):
    """
    Trianguliere Polygon MIT Löchern
    
    Nutzt mapbox_earcut Library
    
    Args:
        outer: [(x, z), ...] Äußeres Polygon
        holes: [[(x, z), ...], ...] Innere Löcher
    
    Returns:
        [(a, b, c), ...] Dreieck-Indizes
    """
    import mapbox_earcut as earcut
    import numpy as np
    
    try:
        # === SCHRITT 1: Kombiniere ALL Vertices ===
        all_vertices = list(outer)
        ring_end_indices = [len(outer)]
        
        for hole in holes:
            all_vertices.extend(hole)
            ring_end_indices.append(len(all_vertices))
        
        # === SCHRITT 2: Konvertiere zu numpy Array ===
        vertices_array = np.array(all_vertices, dtype=np.float64)
        rings_array = np.array(ring_end_indices, dtype=np.uint32)
        
        # === SCHRITT 3: Trianguliere mit earcut ===
        indices = earcut.triangulate_float64(vertices_array, rings_array)
        
        # === SCHRITT 4: Konvertiere zu Dreiecke ===
        triangles = []
        for i in range(0, len(indices), 3):
            if i + 2 < len(indices):
                triangles.append((indices[i], indices[i+1], indices[i+2]))
        
        return triangles
    
    except Exception as e:
        print(f"ERROR triangulating with holes: {e}")
        # Fallback: ignoriere Löcher
        from .triangulation import triangulate_polygon_simple
        return triangulate_polygon_simple(outer)
```

---

### Modul: `germany3d/data/data_loader.py`

**Zweck:** Laden und Vorbereitung aller Daten

```python
CITY_STATE_HOLES = {
    'Brandenburg': ['Berlin'],
    'Niedersachsen': ['Bremen'],
    'Schleswig-Holstein': ['Hamburg']
}

def load_bundeslaender(data_dir):
    """
    Lade Bundesländer aus GeoJSON
    
    Returns:
        List[Bundesland]
    """
    import json
    from .point_in_polygon import point_in_polygon
    from ..geometry.bundesland import Bundesland
    from ..config import COLORS
    
    # GeoJSON laden
    geojson_file = os.path.join(data_dir, 'germany_borders.geo.json')
    with open(geojson_file) as f:
        geojson = json.load(f)
    
    bundeslaender = []
    
    for feature in geojson['features']:
        name = feature['properties']['name']
        coordinates = feature['geometry']['coordinates'][0]
        
        # Löschen: Koordinaten in [(lon, lat), ...] Format
        polygon = coordinates
        
        # Farbe
        color = COLORS.get(name, (0.5, 0.5, 0.5))
        
        # Bundesland-Objekt erstellen
        bl = Bundesland(name, polygon, color)
        bundeslaender.append(bl)
    
    # === WICHTIG: Stadtstaaten-Löcher stanzen ===
    _punch_holes_for_city_states(bundeslaender)
    
    return bundeslaender

def _punch_holes_for_city_states(bundeslaender):
    """
    Stanzt Löcher für Stadtstaaten in Nachbar-Bundesländer
    
    Dies ist die KERNLÖSUNG für Berlin/Hamburg/Bremen!
    """
    bl_map = {bl.name: bl for bl in bundeslaender}
    
    for parent_name, hole_names in CITY_STATE_HOLES.items():
        if parent_name not in bl_map:
            continue
        
        holes = []
        for hole_name in hole_names:
            if hole_name in bl_map:
                # Hole-Vertices = Stadtstaat-Polygon (vereinfacht)
                hole_vertices = bl_map[hole_name].vertices_2d
                holes.append(hole_vertices)
                print(f"    • {hole_name}: {len(hole_vertices)} Vertices")
        
        if holes:
            bl_map[parent_name].add_holes(holes)
            print(f"    * {parent_name}: {len(holes)} Loch/Loecher hinzugefuegt")

def load_windturbines_with_heights(data_dir, bundeslaender):
    """
    Lade Windräder aus CSV und weise Bundesland zu
    
    Returns:
        WindTurbineManager
    """
    import csv
    from .point_in_polygon import point_in_polygon
    from ..windturbine.manager import WindTurbineManager
    from ..windturbine.turbine import WindTurbine
    from ..config import DEFAULT_HEIGHT
    
    manager = WindTurbineManager()
    
    csv_file = os.path.join(data_dir, 'windmills_processed.csv')
    bl_map = {bl.name: bl for bl in bundeslaender}
    
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader):
            if i % 5000 == 0:
                print(f"    {i}/{29722} Windräder verarbeitet...")
            
            lon = float(row['lon'])
            lat = float(row['lat'])
            power = float(row['ElectricalPower_kW'])
            name = row.get('WindmillName', f'WM_{i}')
            
            # === WICHTIG: Bundesland-Zuordnung ===
            bl_name = get_bundesland_name_for_position(lon, lat, bundeslaender)
            
            if bl_name and bl_name in bl_map:
                bl_height = bl_map[bl_name].extrusion
            else:
                bl_height = DEFAULT_HEIGHT
            
            # Windrad erstellen
            turbine = WindTurbine(
                name=name,
                lon=lon,
                lat=lat,
                power=power,
                bl_name=bl_name,
                bl_height=bl_height
            )
            
            manager.add_turbine(turbine)
    
    return manager

def get_bundesland_name_for_position(lon, lat, bundeslaender):
    """
    Point-in-Polygon Test
    
    Welches Bundesland enthält den Punkt (lon, lat)?
    """
    from .point_in_polygon import point_in_polygon
    
    for bl in bundeslaender:
        if point_in_polygon((lon, lat), bl.polygon):
            return bl.name
    
    return None  # Außerhalb alle Bundesländer
```

---

### Modul: `germany3d/data/wind_statistics.py`

**Zweck:** Berechne Wind-Leistung pro Bundesland pro Jahr

```python
class WindPowerStatistics:
    """
    Aggregiert Windrad-Leistungen pro Bundesland pro Jahr
    """
    
    def __init__(self, data_dir):
        self.power_by_state_year = {}  # {state: {year: MW}}
        self.max_power = 0
        self._load_from_csv(data_dir)
        self._interpolate_missing_years()
    
    def _load_from_csv(self, data_dir):
        """Aggregiere MW pro Bundesland pro Jahr"""
        import csv
        from ..config import MIN_HEIGHT, MAX_HEIGHT
        
        csv_file = os.path.join(data_dir, 'windmills_processed.csv')
        
        with open(csv_file) as f:
            for row in csv.DictReader(f):
                bundesland = row['Bundesland']
                year = int(row['Year'])
                power = float(row['ElectricalPower_kW']) / 1000.0  # kW → MW
                
                if bundesland not in self.power_by_state_year:
                    self.power_by_state_year[bundesland] = {}
                
                if year not in self.power_by_state_year[bundesland]:
                    self.power_by_state_year[bundesland][year] = 0
                
                # AGGREGIEREN
                self.power_by_state_year[bundesland][year] += power
                
                # Track global maximum
                self.max_power = max(
                    self.max_power,
                    self.power_by_state_year[bundesland][year]
                )
    
    def _interpolate_missing_years(self):
        """Interpoliere fehlende Jahre linear"""
        for state in self.power_by_state_year:
            years = sorted(self.power_by_state_year[state].keys())
            
            for i in range(len(years) - 1):
                year1, year2 = years[i], years[i + 1]
                power1 = self.power_by_state_year[state][year1]
                power2 = self.power_by_state_year[state][year2]
                
                # Interpoliere Jahre dazwischen
                for year in range(year1 + 1, year2):
                    t = (year - year1) / (year2 - year1)
                    power = power1 + t * (power2 - power1)
                    self.power_by_state_year[state][year] = power
    
    def get_power_for_year(self, state, year):
        """Leistung eines Bundeslandes in einem Jahr (MW)"""
        return self.power_by_state_year.get(state, {}).get(year, 0)
    
    def get_height_for_year(self, state, year):
        """Höhe eines Bundeslandes in einem Jahr"""
        from ..config import MIN_HEIGHT, MAX_HEIGHT
        
        power = self.get_power_for_year(state, year)
        
        height = MIN_HEIGHT + (power / self.max_power) * (MAX_HEIGHT - MIN_HEIGHT)
        return max(MIN_HEIGHT, min(MAX_HEIGHT, height))
```

---

## Datenverarbeitung

### CSV-Format: windmills_processed.csv

```csv
WindmillName,lon,lat,ElectricalPower_kW,Year,Bundesland
WM_00001,8.123,52.456,2500,1995,Brandenburg
WM_00002,8.124,52.457,3000,2000,Brandenburg
...
```

**Spalten-Beschreibung:**
- `WindmillName`: Eindeutige ID
- `lon`, `lat`: GPS-Koordinaten (WGS84)
- `ElectricalPower_kW`: Installierte Leistung in Kilowatt
- `Year`: Inbetriebnahme-Jahr (oder Jahr der Daten)
- `Bundesland`: Berechnete Bundesland-Zuordnung

### GeoJSON-Format: germany_borders.geo.json

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {"name": "Brandenburg"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [11.27, 51.32],
          [11.28, 51.33],
          ...
          [11.27, 51.32]
        ]]
      }
    }
  ]
}
```

---

## Rendering-System

### OpenGL Pipeline

```
1. Clear Screen
   glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

2. Setup Matrices
   glMatrixMode(GL_MODELVIEW)
   glLoadIdentity()
   
   # Kamera-Transform
   glTranslatef(0, 0, -zoom)
   glRotatef(rot_x, 1, 0, 0)
   glRotatef(rot_y, 0, 1, 0)

3. Render Objects
   for bundesland in bundeslaender:
       bundesland.render()  # Dreiecke + Quads
   
   for turbine in turbines:
       turbine.render()  # Zylinder + Geometrie

4. Render 2D Overlay (Legende)
   glMatrixMode(GL_PROJECTION)
   gluOrtho2D(0, width, 0, height)
   # Render Text/Grafiken

5. Swap Buffers
   pygame.display.flip()
```

### Beleuchtungs-Setup

```python
def update_lighting():
    """3-Punkt Beleuchtung"""
    
    # Ambient (überall leicht)
    glLight(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0))
    
    # Directional (Sonne von oben-rechts)
    glLight(GL_LIGHT0, GL_POSITION, (1.0, 1.0, 1.0, 0.0))
    glLight(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
    
    # Specular (Glanz)
    glLight(GL_LIGHT0, GL_SPECULAR, (0.5, 0.5, 0.5, 1.0))
    
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
```

### Schatten-Rendering

```python
def render_map_shadows(bundeslaender, camera_rot_y):
    """Einfache Ebenen-Schatten für Atmosphäre"""
    
    glDisable(GL_LIGHTING)
    glColor4f(0, 0, 0, 0.15)  # Halbtransparent
    
    # Flache Ebene auf y = -0.05
    glBegin(GL_QUADS)
    glVertex3f(-2, -0.05, -3)
    glVertex3f(2, -0.05, -3)
    glVertex3f(2, -0.05, 3)
    glVertex3f(-2, -0.05, 3)
    glEnd()
    
    glEnable(GL_LIGHTING)
```

---

## Animationssystem

### Frame-Loop mit Delta-Time

```python
def run(self):
    clock = pygame.time.Clock()
    target_fps = 60
    
    while True:
        # Begrenzen auf target FPS
        dt = clock.tick(target_fps) / 1000.0  # Sekunden
        
        # Event-Verarbeitung
        if not self._handle_events():
            break
        
        # Updates
        self._update_animation(dt)
        self._update_bundesland_heights()
        self._update_turbine_heights()
        
        # Rendering
        self._render()
        
        # Display
        pygame.display.set_caption(
            f"Deutschland 3D - Jahr {self.current_year} - "
            f"FPS: {clock.get_fps():.0f}"
        )
```

### Jahr-Wechsel-Logik

```python
def _update_animation(self, dt):
    """Aktualisiert Animations-Zeit und Jahr"""
    
    if self.animation_running:
        # Akkumuliere Zeit
        self.animation_time += dt * self.animation_speed
        
        # Berechne Jahr (alle 5 Jahre)
        new_year = int(self.animation_time / 5) * 5 + 1990
        
        # Wenn Jahr gewechselt, update Höhen
        if new_year != self.current_year:
            old_year = self.current_year
            self.current_year = new_year
            
            print(f"  Jahr: {self.current_year}")
            
            # Neue Höhen berechnen
            self._update_bundesland_heights()
            self._update_turbine_heights()
```

---

## Performance-Optimierungen

### 1. Visibility Culling (Frustum Culling)

```python
def get_visible_turbines(self):
    """Nur Windräder rendern, die in Sichtbereich sind"""
    
    visible = []
    for turbine in self.turbines:
        x, y, z = turbine.position
        
        # Einfacher Bounding-Sphere Check
        if -2 < x < 2 and -3 < z < 3:  # View frustum
            visible.append(turbine)
    
    return visible
```

### 2. Vertex-Buffer Reuse

```python
# NICHT GUT: Jedes Frame neue Arrays
vertices_top = [(v[0], new_height, v[2]) for v in old_vertices]

# GUT: In-Place Update
for i in range(len(vertices_top)):
    vertices_top[i] = (vertices_top[i][0], new_height, vertices_top[i][2])
```

### 3. Polygon-Vereinfachung

```python
# Reduziert Vertices um Faktor POLYGON_SIMPLIFICATION
step = max(1, len(polygon) // POLYGON_SIMPLIFICATION)
simplified = [polygon[i] for i in range(0, len(polygon), step)]
```

### 4. Render-Batching

```python
# NICHT: 29.722 einzelne Rendering-Calls
for turbine in turbines:
    turbine.render()

# GUT: Batch ähnliche Objekte
glBegin(GL_TRIANGLES)
for turbine in visible_turbines:
    turbine._render_geometry()  # Nur Vertices, keine Transforms
glEnd()
```

---

## Bekannte Probleme & Lösungen

### Problem 1: Hamburg wird teilweise verdeckt

**Ursache:** Polygon-Vereinfachung führt dazu, dass Hamburg-Polygon nicht exakt in das Schleswig-Holstein-Loch passt.

**Lösung:** Render-Reihenfolge - Stadtstaaten NACH normalen Bundesländern rendern.

**Code:**
```python
CITY_STATES = {'Berlin', 'Hamburg', 'Bremen'}
normal_bl = [b for b in self.bundeslaender if b.name not in CITY_STATES]
city_states = [b for b in self.bundeslaender if b.name in CITY_STATES]

# Normal zuerst
for bl in normal_bl:
    bl.render()

# Dann Stadtstaaten (oben)
for bl in city_states:
    bl.render()
```

### Problem 2: Windräder "in der Luft"

**Ursache:** Einige Windräder können keinem Bundesland zugeordnet werden (liegen außerhalb der vereinfachten Polygone).

**Lösung:** DEFAULT_HEIGHT verwenden, aber Zuordnung verbessern.

**Mögliche Verbesserungen:**
1. Polygon-Vereinfachung reduzieren
2. Spatial Hashing für schnellere Point-in-Polygon Tests
3. Fallback: Nächstes Bundesland suchen

### Problem 3: Große Lücke zwischen Schleswig-Holstein und Niedersachsen

**Ursache:** GeoJSON-Daten stimmen möglicherweise nicht perfekt überein, oder Vereinfachung ist zu aggressiv.

**Lösungen:**
```python
# Reduziere Vereinfachung (weniger Performance, bessere Qualität)
POLYGON_SIMPLIFICATION = 1000  # Statt 500

# Oder: Höhere geografische Auflösung verwenden
# (bessere GeoJSON-Daten)
```

---

## API-Referenz

### Germany3DViewer

```python
viewer = Germany3DViewer()

# Hauptmethoden
viewer.run()                           # Start Animation
viewer.animation_running = True        # Start/Pause
viewer.current_year = 2020             # Set Jahr
viewer.show_turbines = True/False      # Toggle Windräder

# Kamera
viewer.camera.zoom = 5.0               # Zoom level
viewer.camera.rot_x = 30.0             # X-Rotation
viewer.camera.rot_y = 45.0             # Y-Rotation
viewer.camera.reset()                  # Reset view
```

### Bundesland

```python
bl = bundesland_list[0]

# Eigenschaften
bl.name                                # "Brandenburg"
bl.extrusion                           # Aktuelle Höhe (0.08-0.35)
bl.vertices_top                        # [(x,y,z), ...]
bl.triangles                           # [(a,b,c), ...]
bl.holes                               # Für Stadtstaaten

# Methoden
bl.update_height(0.25)                 # Neue Höhe
bl.render()                            # OpenGL Rendering
bl.add_holes([hole1, hole2])           # Loch-System
```

### WindTurbine

```python
turbine = wind_turbines.turbines[0]

# Eigenschaften
turbine.name                           # "WM_00001"
turbine.position                       # (x, y, z)
turbine.power                          # kW
turbine.bl_name                        # "Brandenburg"
turbine.bl_height                      # Aktuelle Bundesland-Höhe

# Methoden
turbine.render(animation_time)         # OpenGL Rendering
turbine.update_height(0.25)            # Neue Höhe
```

### WindPowerStatistics

```python
stats = WindPowerStatistics(data_dir)

# Methoden
stats.get_power_for_year('Brandenburg', 2020)      # MW
stats.get_height_for_year('Brandenburg', 2020)     # 0.08-0.35
stats.max_power                                     # Globales Maximum
```

---

## Erweiterungen & Zukünftige Arbeiten

### Kurzfristig (1-2 Wochen)

1. **Performance-Optimierungen**
   - Spatial Hashing für Point-in-Polygon
   - GPU-basierte Transformationen
   - Display Lists für statische Geometrie

2. **Hamburg-Problem lösen**
   - Genauere Polygon-Ausstechung
   - Bessere GeoJSON-Daten

3. **UI Verbesserungen**
   - Legende-Erwerbung
   - Controls-Hilfe
   - Pause-Screen

### Mittelfristig (1 Monat)

1. **Moderne Grafiken**
   - Wechsel zu OpenGL 3.3+ mit Shadern
   - PBR (Physically Based Rendering)
   - Schatten-Mapping

2. **Erweiterte Analysen**
   - Bundesland-Info-Popup
   - Zeitreihen-Grafiken
   - Vergleich-Modus

3. **Export-Funktionen**
   - Video-Export (Animation)
   - Screenshot-Verbesserungen
   - GeoJSON-Export

### Langfristig (2-3 Monate)

1. **Web-Version**
   - Three.js / Babylon.js Port
   - Cloud-Rendering
   - Multi-User Collaboration

2. **Erweiterte Datenquellen**
   - Weitere Energieträger (Solar, Hydro)
   - Echtzeit-Daten-Integration
   - Prognoseszenarien

3. **VR/AR Support**
   - WebXR API
   - VR-Headset Kompatibilität
   - Immersive Experiences

---

## Fazit

Dieses Projekt demonstriert erfolgreiche Integration von:

- ✅ GIS-Datenverarbeitung (GeoJSON, räumliche Abfragen)
- ✅ 3D-Graphik-Engine (OpenGL, GPU-Rendering)
- ✅ Echtzeit-Animation (Delta-Time basiert, 60 FPS)
- ✅ Wissenschaftliche Visualisierung (Datengetriebene Farben/Höhen)
- ✅ Saubere Software-Architektur (Modularität, Separation of Concerns)

Die Implementierung zeigt Best Practices in:
- Datenstrukturen & Algorithmen
- Performance-Optimierungen
- Fehlerbehandlung & Robustheit
- Benutzerfreundliche Interfaces

