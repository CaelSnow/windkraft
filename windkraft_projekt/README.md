# Germany 3D Windkraft-Visualisierung

Interaktive 3D-Visualisierung der deutschen Windkraftanlagen mit fortgeschrittenen Performance-Optimierungen.

## Features

- **3D Deutschland-Karte**: Alle 16 Bundesländer als extrudierte Blöcke
- **29.722 Windturbinen**: Echte Daten aus dem MaStR-Register
- **Zeitanimation**: Entwicklung von 1990 bis 2025
- **Hardware-Erkennung**: Automatische Optimierung für GPU/CPU
- **Performance-Optimierungen**: Quadtree, LOD, Frustum Culling, Instancing

## Performance-Optimierungen

### 1. Quadtree (Spatial Indexing)
- 2D-Spatial-Index für schnelles Culling
- O(log n) statt O(n) für Sichtbarkeitsabfragen
- Referenz: Finkel & Bentley (1974)

### 2. Level-of-Detail (LOD)
- Standard: 3 LOD-Level (~40% Polygon-Reduktion)
- Aggressiv: 5 LOD-Level (~70% Polygon-Reduktion)
- Extrem: Billboard bei großer Distanz (~85% Reduktion)

### 3. View-Frustum Culling
- Nur sichtbare Turbinen werden gerendert
- Extrahiert aus ModelView-Projection-Matrix
- Referenz: Gribb & Hartmann (2001)

### 4. GPU-Instanced Rendering (wenn verfügbar)
- Gruppiert Turbinen nach LOD-Level
- Reduziert Draw-Calls von N auf ~5
- Referenz: Carucci (2005)

## Hardware-Erkennung

Das Projekt erkennt automatisch die verfügbare Hardware:

| Tier | GPU | Max Turbinen | LOD-Modus | Schatten |
|------|-----|--------------|-----------|----------|
| HIGH | NVIDIA RTX, AMD RX 6000+ | 50.000 | Standard | Ja |
| MEDIUM | GTX 1000+, RX 500+ | 30.000 | Aggressiv | Ja |
| LOW | Ältere GPUs | 20.000 | Aggressiv | Nein |
| MINIMAL | Integriert/CPU | 10.000 | Extrem | Nein |

## Projektstruktur

```
windkraft_projekt/
├── main.py                      # Einstiegspunkt
├── benchmark_scientific_final.py # Wissenschaftlicher Benchmark
├── germany3d/                   # Hauptpaket
│   ├── __init__.py
│   ├── config.py               # Konfiguration
│   ├── hardware.py             # Hardware-Erkennung (NEU)
│   ├── core/
│   │   ├── viewer.py           # Haupt-Viewer
│   │   └── camera.py           # Kamera-Steuerung
│   ├── data/
│   │   └── data_loader.py      # Daten-Import
│   ├── rendering/              # OpenGL-Rendering
│   └── windturbine/
│       ├── manager.py          # Turbinen-Manager
│       ├── quadtree.py         # Spatial Index
│       ├── lod.py              # Level-of-Detail
│       ├── lod_aggressive.py   # Aggressive LOD
│       ├── frustum_culling.py  # Frustum Culling
│       ├── instanced_rendering.py # GPU Instancing
│       └── optimized_manager.py   # Integrierter Manager
├── data/                        # Eingabedaten
│   ├── germany_borders.geo.json
│   └── windmills_processed.csv
├── results/                     # Benchmark-Ergebnisse
└── wissenschaftliche_arbeit/    # LaTeX-Dokumentation
```

## Installation

```bash
pip install pygame PyOpenGL Pillow numpy
```

## Verwendung

### Viewer starten
```bash
cd windkraft_projekt
python main.py
```

### Benchmark ausführen
```bash
python benchmark_scientific_final.py
```

## Steuerung

| Taste | Aktion |
|-------|--------|
| Maus ziehen | Ansicht rotieren |
| Scrollen | Zoom |
| SPACE | Animation Start/Pause |
| ← / → | Jahr +/- 5 |
| W | Windräder ein/aus |
| A | Blatt-Animation |
| R | Ansicht zurücksetzen |
| S | Screenshot speichern |
| ESC | Beenden |

## Benchmark-Ergebnisse

Typische Performance mit 29.722 Turbinen:

| Optimierung | Zeit (ms) | Polygon-Reduktion |
|-------------|-----------|-------------------|
| Baseline (keine) | ~50 ms | 0% |
| Quadtree | ~5 ms | 70% (Culling) |
| LOD Aggressiv | ~3 ms | 75% |
| Frustum Culling | ~2 ms | 80% |
| Kombiniert | ~1 ms | 88% |

## Literatur

1. Finkel & Bentley (1974): "Quad Trees: A Data Structure for Retrieval on Composite Keys"
2. Gribb & Hartmann (2001): "Fast Extraction of Viewing Frustum Planes"
3. Luebke (2002): "Level of Detail for 3D Graphics"
4. Carucci (2005): "Inside Geometry Instancing"
5. Wihlidal (2021): "Optimizing the Graphics Pipeline with Compute" (GDC)

## Lizenz

Bildungsprojekt für CGIV-Kurs (Computergrafik und Interaktive Visualisierung)
