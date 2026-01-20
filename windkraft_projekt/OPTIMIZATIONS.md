# Performance-Optimierungen
## Windkraft-Visualisierung Deutschland

**Version:** 2.0 (Hardware-adaptiv)  
**Letzte Aktualisierung:** Januar 2025

---

## Übersicht

Dieses Projekt implementiert **5 wissenschaftlich fundierte Optimierungen** für das Rendering von 29.722+ Windturbinen in Echtzeit.

| Optimierung | Verfahren | Reduktion | Referenz |
|-------------|-----------|-----------|----------|
| Quadtree | Spatial Indexing (2D) | 70% Culling | Finkel & Bentley (1974) |
| LOD Aggressiv | 5 Detail-Level | 75% Polygone | Luebke (2002) |
| Frustum Culling | 3D View-Frustum | 80% Objekte | Gribb & Hartmann (2001) |
| Instanced Rendering | GPU Batching | 95% Draw-Calls | Carucci (2005) |
| Temporal Coherence | Frame-Kohärenz | 60-70% Tests | Wihlidal (2021) |

---

## 1. Quadtree (Spatial Indexing)

**Datei:** `germany3d/windturbine/quadtree.py`

### Konzept
Ein **2D-Quadtree** (nicht Octree, da Turbinen nur in X-Z-Ebene verteilt sind) für schnelles räumliches Culling.

### Komplexität
- **Aufbau:** O(n log n)
- **Query:** O(log n + k), wobei k = Anzahl Ergebnisse
- **Speicher:** O(n)

### Implementierung
```python
class QuadtreeNode:
    def __init__(self, bounds: BoundingBox, max_objects=100, max_depth=10):
        self.bounds = bounds
        self.turbines = []
        self.nw = self.ne = self.sw = self.se = None  # 4 Kinder (nicht 8!)

class QuadtreeManager:
    def get_visible(self, view_bounds: BoundingBox) -> List[WindTurbine]:
        """Gibt nur Turbinen im sichtbaren Bereich zurück."""
```

### Benchmark-Ergebnis
```
Lineare Suche: 5.2 ms (29722 Tests)
Quadtree:      0.4 ms (durchschn. 2100 Tests)
Speedup:       13x
```

---

## 2. Level-of-Detail (LOD)

**Dateien:**
- `germany3d/windturbine/lod.py` - Standard (3 Level)
- `germany3d/windturbine/lod_aggressive.py` - Aggressiv (5 Level)

### Standard LOD (3 Level)
| Level | Distanz | Polygon-Ratio | Beschreibung |
|-------|---------|---------------|--------------|
| LOD0 | < 0.5 | 100% | Volles Detail |
| LOD1 | 0.5-2.0 | 50% | Reduziert |
| LOD2 | > 2.0 | 10% | Minimal |

### Aggressive LOD (5 Level)
| Level | Distanz | Polygon-Ratio | Beschreibung |
|-------|---------|---------------|--------------|
| LOD0 | < 0.3 | 100% | Volles Detail |
| LOD1 | 0.3-0.8 | 60% | Leicht reduziert |
| LOD2 | 0.8-1.5 | 30% | Stark reduziert |
| LOD3 | 1.5-3.0 | 10% | Minimal |
| LOD4 | > 3.0 | 2% | Billboard |

### Benchmark-Ergebnis
```
Ohne LOD:        4.458.300 Polygone
Standard LOD:    2.674.980 Polygone (-40%)
Aggressiv LOD:   1.114.575 Polygone (-75%)
```

---

## 3. View-Frustum Culling

**Datei:** `germany3d/windturbine/frustum_culling.py`

### Konzept
Extrahiert die 6 Frustum-Ebenen aus der ModelView-Projection-Matrix und testet jede Turbine.

### Implementierung
```python
class ViewFrustum:
    def extract_from_opengl(self):
        """Extrahiert 6 Ebenen aus GL_MODELVIEW * GL_PROJECTION."""
        mv = glGetDoublev(GL_MODELVIEW_MATRIX)
        proj = glGetDoublev(GL_PROJECTION_MATRIX)
        clip = np.dot(proj.T, mv.T).T
        
        # 6 Frustum-Ebenen (left, right, bottom, top, near, far)
        self.planes = [
            clip[3] + clip[0],  # Left
            clip[3] - clip[0],  # Right
            # ... usw.
        ]

class FrustumCuller:
    def is_visible(self, x, y, z, radius=0.01) -> bool:
        """Prüft ob Punkt/Kugel im Frustum liegt."""
```

### Benchmark-Ergebnis
```
Ohne Culling:    29722 Turbinen getestet/gerendert
Mit Culling:     ~6000-12000 Turbinen (je nach Kamerawinkel)
Reduktion:       60-80%
```

---

## 4. GPU Instanced Rendering

**Datei:** `germany3d/windturbine/instanced_rendering.py`

### Konzept
Statt N einzelne `glDrawArrays`-Aufrufe, ein einziger `glDrawArraysInstanced` pro LOD-Level.

### Anforderungen
- OpenGL 3.1+ oder `GL_ARB_draw_instanced`
- Wird automatisch deaktiviert bei fehlender GPU-Unterstützung

### Implementierung
```python
class InstancedTurbineRenderer:
    def render_batch(self, turbines: List[BatchTurbineData]):
        """Rendert alle Turbinen eines LOD-Levels in einem Draw-Call."""
        # Positions-VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.position_vbo)
        positions = np.array([(t.x, t.y, t.z) for t in turbines])
        glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_DYNAMIC_DRAW)
        
        # Ein Draw-Call für alle
        glDrawArraysInstanced(GL_TRIANGLES, 0, vertex_count, len(turbines))
```

### Benchmark-Ergebnis
```
Ohne Instancing: 29722 Draw-Calls
Mit Instancing:  5 Draw-Calls (1 pro LOD-Level)
GPU-Zeit:        -60% auf NVIDIA, -40% auf AMD
```

---

## 5. Moderne Algorithmen (2020-2024)

**Datei:** `benchmark_scientific_final.py` (benchmark_modern_algorithms)

### 5.1 Temporal Coherence
Nutzt die Sichtbarkeit des vorherigen Frames:
- 70% der Objekte waren vorher sichtbar → überspringen
- Nur Rand-Objekte werden neu getestet

### 5.2 Clustered Rendering
Gruppiert nahe Turbinen in Cluster:
- Cluster-Level Test zuerst
- Nur bei Überschneidung: Einzeltests

### 5.3 Screen-Space LOD
LOD basierend auf projizierter Pixelgröße:
- >100px: LOD0
- 50-100px: LOD1
- 20-50px: LOD2
- 5-20px: LOD3
- <5px: Billboard

### 5.4 Hierarchical Early-Out
Überspringt komplett sichtbare/unsichtbare Baumknoten:
- Knoten komplett im Frustum → alle Kinder sichtbar
- Knoten komplett außerhalb → alle Kinder unsichtbar

---

## Hardware-Erkennung

**Datei:** `germany3d/hardware.py`

### Automatische Methodenwahl

```python
class HardwareCapabilities:
    @classmethod
    def detect(cls) -> 'HardwareCapabilities':
        """Erkennt GPU und wählt optimale Einstellungen."""
        
# Ergebnis basierend auf Hardware:
# - NVIDIA RTX → HIGH tier → alle Optimierungen
# - AMD RX 6000 → HIGH tier → alle Optimierungen
# - Intel Iris → MEDIUM tier → aggressives LOD
# - Integriert → MINIMAL tier → extremes LOD, kein Instancing
```

### Rendering Tiers

| Tier | Beispiel-GPUs | Max Turbinen | LOD | Schatten | Instancing |
|------|---------------|--------------|-----|----------|------------|
| HIGH | RTX 3080, RX 7900 | 50.000 | Standard | ✓ | ✓ |
| MEDIUM | GTX 1660, RX 580 | 30.000 | Aggressiv | ✓ | ✓ |
| LOW | GT 1030, RX 550 | 20.000 | Aggressiv | ✗ | ✗ |
| MINIMAL | Intel UHD | 10.000 | Extrem | ✗ | ✗ |

---

## Benchmark ausführen

```bash
cd windkraft_projekt
python benchmark_scientific_final.py
```

### Ausgabe
- `results/benchmark_YYYYMMDD_HHMMSS.json` - Komplette Ergebnisse
- `results/benchmark_YYYYMMDD_HHMMSS.csv` - Tabelle für Excel/LaTeX

### Kategorien
1. **Spatial Indexing:** Lineare Suche vs. Quadtree
2. **Frustum Culling:** 2D AABB vs. 3D Frustum
3. **Level-of-Detail:** Standard vs. Aggressiv vs. Extrem
4. **Pipeline:** Alle Optimierungen kombiniert
5. **Modern (2020-2024):** Temporal, Cluster, Screen-Space

---

## Literaturverzeichnis

1. **Finkel, R. A. & Bentley, J. L.** (1974): "Quad Trees: A Data Structure for Retrieval on Composite Keys"
2. **Gribb, G. & Hartmann, K.** (2001): "Fast Extraction of Viewing Frustum Planes from the World-View-Projection Matrix"
3. **Assarsson, U. & Möller, T.** (2000): "Optimized View Frustum Culling Algorithms for Bounding Boxes"
4. **Luebke, D.** (2002): "Level of Detail for 3D Graphics"
5. **Carucci, F.** (2005): "Inside Geometry Instancing" (GPU Gems 2)
6. **Wihlidal, G.** (2021): "Optimizing the Graphics Pipeline with Compute" (GDC 2021)
7. **Bittner, J. et al.** (2004): "Visibility Driven Rendering" (Wiley)
