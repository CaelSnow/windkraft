"""
Camera - Kamera-Steuerung und Transformation
============================================

Verwaltet die interaktive Kamera mit Maus-Steuerung.

Features:
- Rotation mit Mausbewegung
- Zoom mit Scrollrad
- Reset-Funktion
"""

from dataclasses import dataclass
from ..config import (
    CAMERA_ROT_X, CAMERA_ROT_Y, CAMERA_ZOOM,
    CAMERA_MIN_ZOOM, CAMERA_MAX_ZOOM
)


@dataclass
class Camera:
    """
    Interaktive Kamera für 3D-Ansicht.
    
    Verwendet sphärische Koordinaten für die Rotation.
    """
    
    rot_x: float = CAMERA_ROT_X
    rot_y: float = CAMERA_ROT_Y
    zoom: float = CAMERA_ZOOM
    
    # Zoom-Grenzen
    min_zoom: float = CAMERA_MIN_ZOOM
    max_zoom: float = CAMERA_MAX_ZOOM
    
    # Rotation-Grenzen (X-Achse)
    min_rot_x: float = 10.0
    max_rot_x: float = 80.0
    
    def rotate(self, dx: float, dy: float, sensitivity: float = 0.3):
        """
        Rotiert die Kamera basierend auf Mausbewegung.
        
        Args:
            dx: Horizontale Mausbewegung (Pixel)
            dy: Vertikale Mausbewegung (Pixel)
            sensitivity: Empfindlichkeit
        """
        self.rot_y += dx * sensitivity
        self.rot_x += dy * sensitivity
        
        # X-Rotation begrenzen
        self.rot_x = max(self.min_rot_x, min(self.max_rot_x, self.rot_x))
    
    def zoom_in(self, amount: float = 0.1):
        """Zoom hinein (näher)."""
        self.zoom = max(self.min_zoom, self.zoom - amount)
    
    def zoom_out(self, amount: float = 0.1):
        """Zoom heraus (weiter weg)."""
        self.zoom = min(self.max_zoom, self.zoom + amount)
    
    def reset(self):
        """Setzt die Kamera auf Standardwerte zurück."""
        self.rot_x = CAMERA_ROT_X
        self.rot_y = CAMERA_ROT_Y
        self.zoom = CAMERA_ZOOM


class MouseHandler:
    """
    Verarbeitet Maus-Events für die Kamera-Steuerung.
    """
    
    def __init__(self, camera: Camera):
        self.camera = camera
        self.dragging = False
        self.last_pos = (0, 0)
    
    def start_drag(self, pos: tuple):
        """Startet das Ziehen."""
        self.dragging = True
        self.last_pos = pos
    
    def stop_drag(self):
        """Beendet das Ziehen."""
        self.dragging = False
    
    def update(self, pos: tuple):
        """
        Aktualisiert die Kamera basierend auf Mausposition.
        
        Args:
            pos: Aktuelle Mausposition (x, y)
        """
        if not self.dragging:
            return
        
        dx = pos[0] - self.last_pos[0]
        dy = pos[1] - self.last_pos[1]
        
        self.camera.rotate(dx, dy)
        self.last_pos = pos
    
    def scroll(self, direction: int):
        """
        Verarbeitet Scroll-Events.
        
        Args:
            direction: 4 = hoch (zoom in), 5 = runter (zoom out)
        """
        if direction == 4:
            self.camera.zoom_in()
        elif direction == 5:
            self.camera.zoom_out()
