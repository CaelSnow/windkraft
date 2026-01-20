"""
Configuration for Germany 3D Visualization
==========================================

All constants, colors, heights, and paths are defined here.
"""

import os

# =============================================================================
# PATHS
# =============================================================================
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')

# =============================================================================
# WINDOW SETTINGS
# =============================================================================
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 1000
WINDOW_TITLE = "Deutschland 3D"

# =============================================================================
# GEOGRAPHY - GPS Boundaries of Germany
# =============================================================================
LAT_MIN = 47.27
LAT_MAX = 55.06
LON_MIN = 5.87
LON_MAX = 15.04

# =============================================================================
# COLORS - Distinct and beautiful colors for each Bundesland
# =============================================================================
COLORS = {
    # Northern States
    # Schleswig-Holstein: Ein kühles, gräuliches Blau
    'Schleswig-Holstein':       (0.60, 0.68, 0.75),   
    # Mecklenburg-Vorpommern: Ähnlich wie SH, blau-grau
    'Mecklenburg-Vorpommern':   (0.55, 0.65, 0.75),   
    # Hamburg: Dunkel abgesetzt (geschätzt, da sehr klein)
    'Hamburg':                  (0.40, 0.45, 0.50),   
    # Bremen: Passt sich oft Niedersachsen an (Lachs-Ton)
    'Bremen':                   (0.80, 0.60, 0.55),   
    # Niedersachsen: Ein markantes Lachs-Rosa/Braun
    'Niedersachsen':            (0.85, 0.65, 0.55),   
    
    # Eastern States
    # Brandenburg: Ein helles Sandgelb/Beige
    'Brandenburg':              (0.92, 0.88, 0.70),   
    # Berlin: Sticht als grüner Punkt heraus
    'Berlin':                   (0.50, 0.80, 0.40),   
    # Sachsen-Anhalt: Ein blasses Grau-Grün
    'Sachsen-Anhalt':           (0.65, 0.70, 0.60),   
    # Sachsen: Ein rötliches Pink/Altrosa
    'Sachsen':                  (0.85, 0.60, 0.65),   
    # Thüringen: Ein kühles Blau-Lila-Grau
    'Thüringen':                (0.60, 0.65, 0.75),   
    
    # Western/Central States
    # Nordrhein-Westfalen: Ein blasses Gelb-Grün (Olivstich)
    'Nordrhein-Westfalen':      (0.75, 0.80, 0.60),   
    # Hessen: Ein warmes Hellbraun/Orange
    'Hessen':                   (0.80, 0.65, 0.50),   
    # Rheinland-Pfalz: Ein deutliches Salbeigrün
    'Rheinland-Pfalz':          (0.55, 0.75, 0.60),   
    # Saarland: Dunkleres Blau-Grau
    'Saarland':                 (0.45, 0.55, 0.65),   
    
    # Southern States
    # Baden-Württemberg: Ein kräftiges Senfgelb/Gold
    'Baden-Württemberg':        (0.90, 0.80, 0.50),   
    # Bayern: Ein sehr helles Mint/Pastell-Türkis
    'Bayern':                   (0.75, 0.90, 0.80),   
}

# =============================================================================
# EXTRUSION HEIGHTS - Larger states get more height for visual balance
# =============================================================================
HEIGHTS = {
    'Bayern':                   0.22,
    'Baden-Württemberg':        0.20,
    'Nordrhein-Westfalen':      0.19,
    'Niedersachsen':            0.18,
    'Hessen':                   0.18,
    'Sachsen':                  0.17,
    'Brandenburg':              0.17,
    'Rheinland-Pfalz':          0.17,
    'Schleswig-Holstein':       0.16,
    'Mecklenburg-Vorpommern':   0.16,
    'Thüringen':                0.17,
    'Sachsen-Anhalt':           0.17,
    'Berlin':                   0.19,
    'Hamburg':                  0.18,
    'Bremen':                   0.15,
    'Saarland':                 0.15,
}

# Default height for unknown states
DEFAULT_HEIGHT = 0.14

# =============================================================================
# CAMERA DEFAULTS
# =============================================================================
CAMERA_ROT_X = 45.0      # Viewing angle (degrees)
CAMERA_ROT_Y = 25.0      # Rotation (degrees)
CAMERA_ZOOM = 2.4        # Zoom level
CAMERA_MIN_ZOOM = 1.5
CAMERA_MAX_ZOOM = 5.0

# =============================================================================
# RENDERING
# =============================================================================
BACKGROUND_COLOR = (0.93, 0.92, 0.90, 1.0)  # Light gray
POLYGON_SIMPLIFICATION = 750  # Max vertices per polygon (hoeher = genauer, aber langsamer)
                               # 200 = schnell, aber ungenau bei kleinen Bundeslaendern
                               # 500 = guter Kompromiss fuer Hamburg-Loch
                               # 1000 = sehr genau

# =============================================================================
# PERFORMANCE - Windrad-Limits
# =============================================================================
MAX_WINDMILLS = None  # Maximale Anzahl Windraeder (None = alle ~30.000)
                       # Empfohlen: 5000 fuer fluessige Performance
                       # Hoeher = mehr Details, aber langsamer
