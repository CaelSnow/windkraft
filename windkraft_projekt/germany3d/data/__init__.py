"""
Data Package - Daten laden
==========================

Enthaelt:
- data_loader: Funktionen zum Laden von GeoJSON und CSV
- point_in_polygon: Geometrische Hilfsfunktionen
- wind_statistics: Windkraft-Statistik pro Bundesland
"""

from .data_loader import (
    load_bundeslaender, 
    load_windturbines,
    load_windturbines_with_heights,
    get_height_for_position,
    get_bundesland_name_for_position
)
from .point_in_polygon import point_in_polygon, find_bundesland_for_point
from .wind_statistics import WindPowerStatistics

__all__ = [
    'load_bundeslaender', 
    'load_windturbines',
    'load_windturbines_with_heights',
    'get_height_for_position',
    'get_bundesland_name_for_position',
    'point_in_polygon',
    'find_bundesland_for_point',
    'WindPowerStatistics'
]
