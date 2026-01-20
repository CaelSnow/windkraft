"""
Video-Export System für cinematische Aufnahmen
==============================================

Speichert die Animation als Video-Datei mit:
- Automatischer Frame-Capture
- ffmpeg-Integration für Video-Encoding
- Cinematische Kamera-Bewegungen
- Kommandozeilen-Steuerung

Verwendung:
    python main.py --record                    # Standard Video (1080p, 30fps)
    python main.py --record --fps 60           # 60 FPS
    python main.py --record --resolution 4k    # 4K Video
    python main.py --record --output myvideo   # Custom Dateiname

Voraussetzung:
    ffmpeg muss im PATH installiert sein
"""

import os
import time
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Callable
from PIL import Image
from OpenGL.GL import *


@dataclass
class VideoConfig:
    """Konfiguration für Video-Export."""
    
    # Ausgabe
    output_name: str = "windkraft_animation"
    output_dir: str = "output/videos"
    
    # Video-Einstellungen - OPTIMIERT für schnelle Aufnahme
    fps: int = 24                # REDUZIERT von 30 (weniger Frames)
    width: int = 1920
    height: int = 1080
    codec: str = "libx264"
    quality: str = "medium"      # REDUZIERT für schnelleres Encoding
    
    # Animation - STARK BESCHLEUNIGT
    start_year: int = 1990
    end_year: int = 2025
    seconds_per_year: float = 0.25  # STARK REDUZIERT (war 0.8) - ~9 Sekunden Video
    
    # Kamera-Bewegung
    rotation_speed: float = 12.0  # Grad pro Jahr (etwas langsamer)
    initial_rotation_x: float = 45.0
    initial_rotation_y: float = 0.0
    zoom_level: float = 4.0       # ERHÖHT für komplette Ansicht
    
    def get_quality_params(self) -> list:
        """Gibt ffmpeg-Parameter für Qualitätsstufe zurück."""
        if self.quality == "lossless":
            return ["-crf", "0", "-preset", "fast"]
        elif self.quality == "high":
            return ["-crf", "20", "-preset", "fast"]  # Schneller als "slow"
        elif self.quality == "medium":
            return ["-crf", "23", "-preset", "veryfast"]  # Sehr schnell
        else:  # low
            return ["-crf", "28", "-preset", "ultrafast"]  # Maximal schnell
    
    @property
    def total_frames(self) -> int:
        """Berechnet Gesamtanzahl der Frames."""
        years = self.end_year - self.start_year
        return int(years * self.seconds_per_year * self.fps)
    
    @property
    def total_duration(self) -> float:
        """Berechnet Gesamtdauer in Sekunden."""
        years = self.end_year - self.start_year
        return years * self.seconds_per_year


def get_ffmpeg_path() -> str:
    """
    Findet den ffmpeg-Pfad.
    
    Prüft:
    1. imageio-ffmpeg (pip install imageio-ffmpeg)
    2. System PATH (ffmpeg direkt installiert)
    
    Returns:
        Pfad zu ffmpeg oder 'ffmpeg' für System-PATH
    """
    # Versuche imageio-ffmpeg zuerst
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    
    # Fallback: System PATH
    return "ffmpeg"


class VideoRecorder:
    """
    Nimmt OpenGL-Frames auf und exportiert sie als Video.
    
    Workflow:
    1. start_recording() - Initialisiert Aufnahme
    2. capture_frame() - Speichert aktuellen Frame (wird pro Frame aufgerufen)
    3. finish_recording() - Generiert Video mit ffmpeg
    """
    
    def __init__(self, config: VideoConfig = None):
        self.config = config or VideoConfig()
        self.frame_count = 0
        self.is_recording = False
        self.temp_dir = None
        self.start_time = None
        self.ffmpeg_path = get_ffmpeg_path()
        
    def check_ffmpeg(self) -> bool:
        """Prüft ob ffmpeg verfügbar ist."""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def start_recording(self) -> bool:
        """
        Startet die Video-Aufnahme.
        
        Returns:
            True wenn erfolgreich, False wenn ffmpeg fehlt
        """
        if not self.check_ffmpeg():
            print("\n" + "=" * 60)
            print("  FEHLER: ffmpeg nicht gefunden!")
            print("  ")
            print("  Installationsanleitung:")
            print("  Windows: winget install ffmpeg")
            print("           oder: choco install ffmpeg")
            print("  Linux:   sudo apt install ffmpeg")
            print("  macOS:   brew install ffmpeg")
            print("=" * 60 + "\n")
            return False
        
        # Temporäres Verzeichnis für Frames erstellen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_dir = Path(self.config.output_dir) / f"frames_{timestamp}"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.frame_count = 0
        self.is_recording = True
        self.start_time = time.time()
        
        print("\n" + "=" * 60)
        print("  🎬 VIDEO-AUFNAHME GESTARTET")
        print("=" * 60)
        print(f"  Auflösung: {self.config.width}x{self.config.height}")
        print(f"  FPS: {self.config.fps}")
        print(f"  Geschätzte Frames: {self.config.total_frames}")
        print(f"  Geschätzte Dauer: {self.config.total_duration:.1f} Sekunden")
        print(f"  Qualität: {self.config.quality}")
        print(f"  Temp-Ordner: {self.temp_dir}")
        print("=" * 60 + "\n")
        
        return True
    
    def capture_frame(self, width: int = None, height: int = None):
        """
        Speichert den aktuellen OpenGL-Frame als PNG.
        
        Args:
            width, height: Fenster-Größe (optional, nutzt config wenn nicht angegeben)
        """
        if not self.is_recording:
            return
        
        w = width or self.config.width
        h = height or self.config.height
        
        # OpenGL Framebuffer auslesen
        glReadBuffer(GL_FRONT)
        pixels = glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE)
        
        # In PIL Image konvertieren und vertikal spiegeln
        image = Image.frombytes('RGB', (w, h), pixels)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        
        # Optional: Auf Zielauflösung skalieren wenn nötig
        if (w, h) != (self.config.width, self.config.height):
            image = image.resize(
                (self.config.width, self.config.height),
                Image.Resampling.LANCZOS
            )
        
        # Als PNG speichern (mit fortlaufender Nummer)
        frame_path = self.temp_dir / f"frame_{self.frame_count:06d}.png"
        image.save(frame_path, "PNG")
        
        self.frame_count += 1
        
        # Fortschrittsanzeige (alle 30 Frames)
        if self.frame_count % 30 == 0:
            elapsed = time.time() - self.start_time
            fps_actual = self.frame_count / elapsed if elapsed > 0 else 0
            progress = (self.frame_count / self.config.total_frames) * 100
            print(f"  📹 Frame {self.frame_count}/{self.config.total_frames} "
                  f"({progress:.1f}%) - {fps_actual:.1f} fps capture")
    
    def finish_recording(self) -> Optional[str]:
        """
        Beendet die Aufnahme und generiert das Video.
        
        Returns:
            Pfad zum fertigen Video oder None bei Fehler
        """
        if not self.is_recording:
            return None
        
        self.is_recording = False
        elapsed = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("  🎞️  GENERIERE VIDEO...")
        print("=" * 60)
        print(f"  Aufgenommene Frames: {self.frame_count}")
        print(f"  Aufnahmedauer: {elapsed:.1f} Sekunden")
        
        # Output-Verzeichnis sicherstellen
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Zeitstempel für eindeutigen Dateinamen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"{self.config.output_name}_{timestamp}.mp4"
        
        # ffmpeg Befehl zusammenbauen
        input_pattern = str(self.temp_dir / "frame_%06d.png")
        
        cmd = [
            self.ffmpeg_path,  # Nutze erkannten ffmpeg-Pfad
            "-y",  # Überschreiben ohne Nachfrage
            "-framerate", str(self.config.fps),
            "-i", input_pattern,
            "-c:v", self.config.codec,
            *self.config.get_quality_params(),
            "-pix_fmt", "yuv420p",  # Kompatibilität
            "-movflags", "+faststart",  # Für Web-Streaming
            str(output_path)
        ]
        
        print(f"  Kommando: ffmpeg ...")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 Minuten Timeout (großzügig)
            )
            
            if result.returncode == 0:
                # Temporäre Frames löschen
                shutil.rmtree(self.temp_dir)
                
                # Dateigröße ermitteln
                file_size = output_path.stat().st_size / (1024 * 1024)  # MB
                
                print("\n  ✅ VIDEO ERFOLGREICH ERSTELLT!")
                print(f"  📁 Datei: {output_path}")
                print(f"  📊 Größe: {file_size:.1f} MB")
                print(f"  🎬 Dauer: {self.frame_count / self.config.fps:.1f} Sekunden")
                print("=" * 60 + "\n")
                
                return str(output_path)
            else:
                print(f"\n  ❌ ffmpeg Fehler:\n{result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("\n  ❌ ffmpeg Timeout - Video zu groß?")
            return None
        except Exception as e:
            print(f"\n  ❌ Fehler: {e}")
            return None


class CinematicAnimator:
    """
    Steuert die cinematische Kamera-Animation für Video-Aufnahmen.
    
    Bewegungsmuster:
    1. Start: Ansicht von oben auf ganz Deutschland
    2. Während Animation: Langsame Rotation um die Y-Achse
    3. Zeit läuft: 1990 → 2025, Windräder erscheinen
    """
    
    def __init__(self, config: VideoConfig = None):
        self.config = config or VideoConfig()
        self.current_frame = 0
        self.current_year = self.config.start_year
    
    def reset(self):
        """Setzt Animation zurück."""
        self.current_frame = 0
        self.current_year = self.config.start_year
    
    def get_camera_state(self, frame: int = None) -> dict:
        """
        Berechnet Kamera-Zustand für einen Frame.
        
        Args:
            frame: Frame-Nummer (optional, nutzt current_frame wenn nicht angegeben)
            
        Returns:
            dict mit rot_x, rot_y, zoom, year
        """
        if frame is None:
            frame = self.current_frame
        
        # Fortschritt berechnen (0.0 bis 1.0)
        total = self.config.total_frames
        progress = frame / total if total > 0 else 0
        
        # Jahr interpolieren
        year_range = self.config.end_year - self.config.start_year
        year = self.config.start_year + int(progress * year_range)
        
        # Rotation: Startet bei initial_rotation_y und dreht sich
        total_rotation = self.config.rotation_speed * year_range
        rot_y = self.config.initial_rotation_y + progress * total_rotation
        
        # X-Rotation bleibt konstant (Blickwinkel von oben)
        rot_x = self.config.initial_rotation_x
        
        # Zoom bleibt konstant für Gesamtansicht
        zoom = self.config.zoom_level
        
        return {
            'rot_x': rot_x,
            'rot_y': rot_y % 360,  # Auf 0-360 begrenzen
            'zoom': zoom,
            'year': year,
            'progress': progress
        }
    
    def advance_frame(self) -> dict:
        """
        Geht zum nächsten Frame und gibt Kamera-Zustand zurück.
        
        Returns:
            dict mit Kamera-Zustand
        """
        state = self.get_camera_state()
        self.current_frame += 1
        self.current_year = state['year']
        return state
    
    def is_finished(self) -> bool:
        """Prüft ob Animation beendet ist."""
        return self.current_frame >= self.config.total_frames


def create_video_config_from_args(args) -> VideoConfig:
    """
    Erstellt VideoConfig aus Kommandozeilen-Argumenten.
    
    Args:
        args: argparse Namespace mit --fps, --resolution, --output etc.
        
    Returns:
        VideoConfig Instanz
    """
    config = VideoConfig()
    
    if hasattr(args, 'fps') and args.fps:
        config.fps = args.fps
    
    if hasattr(args, 'resolution') and args.resolution:
        res = args.resolution.lower()
        if res == '720p':
            config.width, config.height = 1280, 720
        elif res == '1080p':
            config.width, config.height = 1920, 1080
        elif res == '1440p':
            config.width, config.height = 2560, 1440
        elif res == '4k':
            config.width, config.height = 3840, 2160
    
    if hasattr(args, 'output') and args.output:
        config.output_name = args.output
    
    if hasattr(args, 'quality') and args.quality:
        config.quality = args.quality
    
    if hasattr(args, 'speed') and args.speed:
        config.seconds_per_year = args.speed
    
    return config
