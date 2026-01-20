#!/usr/bin/env python3
"""
Germany 3D - Main Entry Point
=============================

Interaktive 3D-Visualisierung der deutschen Windkraftlandschaft.

Usage:
    python main.py                         # Interaktiver Modus (Gouraud Shading)
    python main.py --shading phong         # Mit Phong Shading (GLSL)
    python main.py --record                # Video aufnehmen (versteckt)
    python main.py --record --show-preview # Video mit Vorschau-Fenster
    python main.py --help                  # Alle Optionen anzeigen

Shading-Optionen:
    --shading gouraud     Gouraud Shading (Standard, Fixed-Function Pipeline)
                          Beleuchtung pro Vertex, interpoliert
    --shading phong       Phong Shading (GLSL per-pixel)
                          Beleuchtung pro Pixel, bessere Qualität

Video-Optionen:
    --record              Video-Aufnahme aktivieren
    --show-preview        Zeigt Vorschau-Fenster während Aufnahme
    --fps N               Frames pro Sekunde (Standard: 30)
    --resolution RES      720p, 1080p, 1440p, 4k (Standard: 1080p)
    --output NAME         Ausgabe-Dateiname (ohne .mp4)
    --quality Q           low, medium, high, lossless (Standard: high)
    --speed S             Sekunden pro Jahr (Standard: 0.8)

Requirements:
    - pygame, PyOpenGL, Pillow, numpy
    - ffmpeg (für Video-Export, wird automatisch gefunden)

Controls (Interaktiver Modus):
    - Maus ziehen: Ansicht rotieren
    - Scroll: Zoom
    - SPACE: Animation Start/Pause
    - ←/→: Jahr +/- 5
    - W: Windräder ein/aus
    - A: Blatt-Animation
    - R: Ansicht zurücksetzen
    - S: Screenshot
    - ESC: Beenden
"""

import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def parse_arguments():
    """Parst Kommandozeilen-Argumente."""
    parser = argparse.ArgumentParser(
        description="Germany 3D - Windkraft-Visualisierung",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python main.py                          Interaktiver Modus
  python main.py --record                 Standard Video (1080p, 30fps)
  python main.py --record --fps 60        60 FPS Video
  python main.py --record --resolution 4k 4K Video
  python main.py --record --quality high  Hohe Qualität
  python main.py --record --speed 1.0     Schnellere Animation (1s/Jahr)
"""
    )
    
    # Video-Aufnahme
    parser.add_argument(
        '--record', '-r',
        action='store_true',
        help='Video-Aufnahme aktivieren (benötigt ffmpeg)'
    )
    
    parser.add_argument(
        '--fps',
        type=int,
        default=30,
        help='Frames pro Sekunde (Standard: 30)'
    )
    
    parser.add_argument(
        '--resolution',
        type=str,
        choices=['720p', '1080p', '1440p', '4k'],
        default='1080p',
        help='Video-Auflösung (Standard: 1080p)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='windkraft_animation',
        help='Ausgabe-Dateiname ohne Erweiterung'
    )
    
    parser.add_argument(
        '--quality', '-q',
        type=str,
        choices=['low', 'medium', 'high', 'lossless'],
        default='high',
        help='Video-Qualität (Standard: high)'
    )
    
    parser.add_argument(
        '--speed', '-s',
        type=float,
        default=2.0,
        help='Sekunden pro Jahr in der Animation (Standard: 2.0)'
    )
    
    # Shading-Modus
    parser.add_argument(
        '--shading',
        type=str,
        choices=['gouraud', 'phong'],
        default='gouraud',
        help='Shading-Modus: gouraud (Standard, Fixed-Function) oder phong (GLSL per-pixel)'
    )
    
    # Anzeige während Aufnahme
    parser.add_argument(
        '--show-preview',
        action='store_true',
        help='Zeigt das Fenster während der Video-Aufnahme an (Standard: versteckt)'
    )
    
    parser.add_argument(
        '--hidden',
        action='store_true',
        help='Versteckt das Fenster während der Aufnahme (schneller, Standard)'
    )
    
    return parser.parse_args()


def main():
    """Start the Germany 3D viewer."""
    args = parse_arguments()
    
    if args.record:
        # Video-Aufnahme Modus
        run_video_recording(args)
    else:
        # Interaktiver Modus
        from germany3d import Germany3DViewer
        viewer = Germany3DViewer(shading_mode=args.shading)
        viewer.run()


def run_video_recording(args):
    """Führt Video-Aufnahme durch."""
    print("\n" + "=" * 60)
    print("  🎬 GERMANY 3D - VIDEO RECORDING MODE")
    print("=" * 60)
    
    # Bestimme ob Preview angezeigt werden soll
    show_preview = args.show_preview if hasattr(args, 'show_preview') else False
    
    # Video-Konfiguration erstellen
    from germany3d.video_export import (
        VideoConfig, VideoRecorder, CinematicAnimator,
        create_video_config_from_args
    )
    
    config = create_video_config_from_args(args)
    recorder = VideoRecorder(config)
    animator = CinematicAnimator(config)
    
    # Prüfe ffmpeg
    if not recorder.check_ffmpeg():
        sys.exit(1)
    
    # Pygame und OpenGL initialisieren
    import pygame
    from pygame.locals import DOUBLEBUF, OPENGL, HIDDEN, SHOWN
    import os
    
    # Unterdrücke vm3dgl Warnungen (nicht kritisch)
    #os.environ['MESA_DEBUG'] = 'silent'
    #os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'  # Konsistent Software-Rendering
    
    # Für verstecktes Fenster: SDL Environment Variable setzen
    if not show_preview:
        os.environ['SDL_VIDEO_WINDOW_POS'] = '-10000,-10000'
        print("\n  📺 Vorschau: AUS (--show-preview für Vorschau)")
    else:
        print("\n  📺 Vorschau: AN")
    
    pygame.init()
    
    if show_preview:
        pygame.display.set_caption("Germany 3D - Recording... (ESC zum Abbrechen)")
    else:
        pygame.display.set_caption("Germany 3D - Recording (hidden)")
    
    # Fenster in Video-Auflösung erstellen
    screen = pygame.display.set_mode(
        (config.width, config.height),
        DOUBLEBUF | OPENGL
    )
    
    # Viewer initialisieren (ohne eigenen Event-Loop)
    from germany3d.core.viewer import Germany3DViewer
    from germany3d.rendering import init_opengl, setup_projection
    
    # OpenGL Setup
    init_opengl()
    setup_projection(config.width, config.height)
    
    # Daten laden
    from germany3d.config import DATA_DIR
    from germany3d.data import load_bundeslaender, load_windturbines_with_heights, WindPowerStatistics
    from germany3d.windturbine import WindTurbineManager
    import os
    
    print("\n  Lade Daten...")
    bundeslaender = load_bundeslaender()
    
    wind_turbines = WindTurbineManager()
    csv_path = os.path.join(DATA_DIR, 'windmills_processed.csv')
    load_windturbines_with_heights(csv_path, wind_turbines, bundeslaender)
    
    wind_statistics = WindPowerStatistics()
    wind_statistics.calculate_from_turbines(wind_turbines.turbines, bundeslaender)
    
    # Aufnahme starten
    if not recorder.start_recording():
        sys.exit(1)
    
    animator.reset()
    clock = pygame.time.Clock()
    
    # Import für Rendering
    from germany3d.rendering import apply_camera_transform, update_lighting, render_map_shadows
    from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT
    
    print("\n  🎥 Aufnahme läuft...")
    
    # Animations-Loop
    while not animator.is_finished():
        # Events verarbeiten (für Abbruch mit ESC)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("\n  ⚠️ Aufnahme abgebrochen!")
                recorder.is_recording = False
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("\n  ⚠️ Aufnahme abgebrochen!")
                    recorder.is_recording = False
                    pygame.quit()
                    sys.exit(0)
        
        # Kamera-Zustand für diesen Frame
        state = animator.advance_frame()
        
        # Bundesland-Höhen aktualisieren
        wind_statistics.update_bundesland_heights(bundeslaender, state['year'])
        
        # Turbinen-Höhen synchronisieren
        height_map = {bl.name: bl.extrusion for bl in bundeslaender}
        for turbine in wind_turbines.turbines:
            bl_name = getattr(turbine, 'bl_name', None)
            if bl_name and bl_name in height_map:
                turbine.bl_height = height_map[bl_name]
        
        # === RENDERING ===
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Kamera-Transformation
        apply_camera_transform(state['rot_x'], state['rot_y'], state['zoom'])
        update_lighting()
        
        # Stadtstaaten separat rendern
        CITY_STATES = {'Berlin', 'Hamburg', 'Bremen'}
        normal_bl = [b for b in bundeslaender if b.name not in CITY_STATES]
        city_states = [b for b in bundeslaender if b.name in CITY_STATES]
        
        # Sortieren (hinten nach vorne)
        sorted_normal = sorted(
            normal_bl,
            key=lambda b: -sum(v[2] for v in b.vertices_top) / len(b.vertices_top)
        )
        sorted_cities = sorted(
            city_states,
            key=lambda b: -sum(v[2] for v in b.vertices_top) / len(b.vertices_top)
        )
        
        # Schatten
        render_map_shadows(sorted_normal + sorted_cities, state['rot_y'])
        
        # Bundesländer rendern
        for bl in sorted_normal:
            bl.render()
        for bl in sorted_cities:
            bl.render()
        
        # Windräder rendern (bis zum aktuellen Jahr)
        wind_turbines.render_until_year(state['year'], shadow_threshold=30000)
        
        # Jahr-Anzeige rendern (2D Overlay)
        _render_year_overlay(config.width, config.height, state['year'], 
                            wind_turbines.count_until_year(state['year']))
        
        # WICHTIG: glFinish() um sicherzustellen dass alle GL-Befehle ausgeführt sind
        from OpenGL.GL import glFinish
        glFinish()
        
        # Frame aufnehmen (VOR flip, direkt aus dem Back-Buffer)
        recorder.capture_frame(config.width, config.height)
        
        # Display aktualisieren (bei Vorschau)
        if show_preview:
            pygame.display.flip()
        
        # FPS begrenzen (nur bei Vorschau wichtig)
        if show_preview:
            clock.tick(60)
    
    # Umgebungsvariable zurücksetzen
    if 'SDL_VIDEO_WINDOW_POS' in os.environ:
        del os.environ['SDL_VIDEO_WINDOW_POS']
    
    # Video generieren
    video_path = recorder.finish_recording()
    
    pygame.quit()
    
    if video_path:
        print(f"\n  🎉 Fertig! Video gespeichert: {video_path}")
    else:
        print("\n  ❌ Video-Generierung fehlgeschlagen")
        sys.exit(1)


def _render_year_overlay(width: int, height: int, year: int, turbine_count: int):
    """Rendert vollständige Legende als 2D-Overlay (wie im interaktiven Modus)."""
    from OpenGL.GL import (
        glMatrixMode, glPushMatrix, glPopMatrix, glLoadIdentity,
        glDisable, glEnable, glBlendFunc, glRasterPos2f, glDrawPixels,
        glBegin, glEnd, glVertex2f, glColor3f, glColor4f, glLineWidth,
        GL_PROJECTION, GL_MODELVIEW, GL_DEPTH_TEST, GL_LIGHTING,
        GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_RGBA, GL_UNSIGNED_BYTE,
        GL_QUADS, GL_LINE_LOOP
    )
    from OpenGL.GLU import gluOrtho2D
    from germany3d.windturbine.colors import get_power_color
    import pygame
    
    # Auf 2D umschalten
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Fonts
    font_large = pygame.font.SysFont('Arial', 72, bold=True)
    font_medium = pygame.font.SysFont('Arial', 28, bold=True)
    font_small = pygame.font.SysFont('Arial', 22)
    
    # === TITEL oben links ===
    title_y = height - 80
    _draw_text(font_medium, "Deutschland", 80, title_y, (80, 80, 80))
    _draw_text(font_small, "Windkraft-Evolution 1990-2025", 80, title_y - 35, (120, 120, 120))
    
    # === FARBSKALA mit Gradient (links unten) ===
    gradient_x = 80
    gradient_y = 280
    gradient_width = 200
    gradient_height = 16
    
    # Beschriftung über Gradient
    _draw_text(font_small, "Leistung [kW]", gradient_x, gradient_y + 25, (100, 100, 100))
    
    # Farbverlauf zeichnen (von grün nach rot)
    num_segments = 50
    segment_width = gradient_width / num_segments
    
    glBegin(GL_QUADS)
    for i in range(num_segments):
        power1 = (i / num_segments) * 7000
        power2 = ((i + 1) / num_segments) * 7000
        
        color1 = get_power_color(power1)
        color2 = get_power_color(power2)
        
        x1 = gradient_x + i * segment_width
        x2 = gradient_x + (i + 1) * segment_width
        
        glColor3f(*color1)
        glVertex2f(x1, gradient_y)
        glVertex2f(x1, gradient_y - gradient_height)
        
        glColor3f(*color2)
        glVertex2f(x2, gradient_y - gradient_height)
        glVertex2f(x2, gradient_y)
    glEnd()
    
    # Rahmen um Gradient
    glColor4f(0.4, 0.4, 0.4, 1.0)
    glLineWidth(1.5)
    glBegin(GL_LINE_LOOP)
    glVertex2f(gradient_x, gradient_y)
    glVertex2f(gradient_x + gradient_width, gradient_y)
    glVertex2f(gradient_x + gradient_width, gradient_y - gradient_height)
    glVertex2f(gradient_x, gradient_y - gradient_height)
    glEnd()
    
    # Min/Max Werte
    _draw_text(font_small, "0", gradient_x, gradient_y - gradient_height - 25, (100, 100, 100))
    _draw_text(font_small, "7000", gradient_x + gradient_width - 45, gradient_y - gradient_height - 25, (100, 100, 100))
    
    # === WINDRÄDER-ANZAHL (links unten) ===
    count_text = f"Windräder: {turbine_count:,}".replace(",", ".")
    _draw_text(font_small, count_text, gradient_x, gradient_y - 70, (100, 100, 100))
    
    # === JAHR gross rechts unten ===
    year_surface = font_large.render(str(year), True, (70, 70, 70))
    year_data = pygame.image.tostring(year_surface, 'RGBA', True)
    glRasterPos2f(width - 280, 120)
    glDrawPixels(year_surface.get_width(), year_surface.get_height(),
                 GL_RGBA, GL_UNSIGNED_BYTE, year_data)
    
    # Zurück zu 3D
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glDisable(GL_BLEND)
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()


def _draw_text(font, text: str, x: float, y: float, color: tuple):
    """Hilfsfunktion zum Zeichnen von Text."""
    from OpenGL.GL import glRasterPos2f, glDrawPixels, GL_RGBA, GL_UNSIGNED_BYTE
    import pygame
    
    surface = font.render(text, True, color)
    data = pygame.image.tostring(surface, 'RGBA', True)
    glRasterPos2f(x, y)
    glDrawPixels(surface.get_width(), surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data)


if __name__ == "__main__":
    main()
