"""
Germany 3D Viewer - Mit Animation und Legende
=============================================

Interaktiver 3D-Viewer fuer die Deutschland-Windkraft-Visualisierung.
Zeigt die Entwicklung der Windkraft von 1990 bis 2025.

Features:
- Windraeder auf korrekter Bundesland-Hoehe
- Jahr-Animation (1990-2025, alle 5 Jahre)
- Legende mit Jahr und Farbskala
- Interaktive Kamera waehrend Animation

Steuerung:
    - Maus ziehen: Ansicht rotieren
    - Scroll: Zoom
    - SPACE: Animation Start/Pause
    - Links/Rechts: Jahr +/- 5
    - W: Windraeder ein/aus
    - A: Blatt-Animation ein/aus
    - R: Ansicht zuruecksetzen
    - S: Screenshot
    - ESC: Beenden
"""

import os
import time

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image

from ..config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    DATA_DIR, OUTPUT_DIR, MAX_WINDMILLS
)
from .camera import Camera, MouseHandler
from ..rendering import init_opengl, setup_projection, update_lighting, apply_camera_transform
from ..rendering import render_map_shadows
from ..data import load_bundeslaender, load_windturbines_with_heights, WindPowerStatistics
from ..windturbine import WindTurbineManager
from ..windturbine.colors import get_power_color
from ..hardware import get_capabilities, HardwareCapabilities


# =============================================================================
# KONFIGURATION
# =============================================================================
START_YEAR = 1990          # Startjahr der Animation
END_YEAR = 2025            # Endjahr der Animation
YEAR_STEP = 5              # Schrittweite (Jahre)
ANIMATION_SPEED = 1.5      # Sekunden pro Jahr-Schritt (REDUZIERT von 5.0)
SHADOW_THRESHOLD = 30000   # Schatten nur wenn weniger als 30000 Windraeder
# =============================================================================


class Germany3DViewer:
    """Interaktiver 3D-Viewer fuer Deutschland mit Windkraft-Animation."""
    
    def __init__(self, shading_mode: str = 'gouraud'):
        """
        Initialisiert den Viewer.
        
        Args:
            shading_mode: 'gouraud' (Fixed-Function) oder 'phong' (GLSL per-pixel)
        """
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.shading_mode = shading_mode
        
        # Pygame und OpenGL initialisieren ZUERST
        self._init_pygame()
        init_opengl()  # OpenGL-Kontext muss vor Hardware-Erkennung existieren!
        setup_projection(self.width, self.height)
        
        # Phong-Shader initialisieren wenn angefordert
        self.phong_shader = None
        self._init_shading()
        
        # Hardware-Erkennung (nutzt den existierenden OpenGL-Kontext)
        self.capabilities: HardwareCapabilities = get_capabilities()
        self.capabilities.print_summary()
        
        # Shading-Modus Info ausgeben
        if self.shading_mode == 'phong' and self.phong_shader:
            print(f"\n  🎨 Shading-Modus: PHONG (Per-Pixel GLSL)")
        else:
            print(f"\n  🎨 Shading-Modus: GOURAUD (Fixed-Function)")
            if self.shading_mode == 'phong':
                print(f"      ⚠ Phong nicht verfügbar, Fallback zu Gouraud")
        
        # Kamera
        self.camera = Camera()
        self.mouse = MouseHandler(self.camera)
        
        # Daten
        self.bundeslaender = []
        self.wind_turbines = WindTurbineManager()
        self.wind_statistics = WindPowerStatistics()
        self.show_turbines = True
        
        # Wende Hardware-Empfehlungen an
        self._apply_hardware_recommendations()
        
        # Animation - startet automatisch!
        self.current_year = START_YEAR
        self.animation_running = True
        self.last_year_change = 0
        
        # Daten laden
        self._load_data()
    
    def _init_pygame(self):
        """Initialisiert Pygame."""
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        pygame.font.init()
        
        # Font fuer Legende
        self.font = pygame.font.SysFont('Arial', 18)
        self.font_large = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_year = pygame.font.SysFont('Arial', 72, bold=True)  # Extra gross fuer Jahr
        
        # Anti-Aliasing
        pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 4)
        
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            DOUBLEBUF | OPENGL | RESIZABLE
        )
    
    def _init_shading(self):
        """
        Initialisiert den gewünschten Shading-Modus.
        
        Gouraud (Standard): OpenGL Fixed-Function Pipeline
            - Beleuchtung pro Vertex, dann interpoliert
            - Schneller, weniger genau bei wenigen Vertices
            
        Phong: GLSL Shader für per-Pixel Beleuchtung
            - Normalen werden interpoliert, Beleuchtung pro Pixel
            - Bessere Qualität, besonders bei spekularen Highlights
        """
        if self.shading_mode == 'phong':
            try:
                from ..rendering.shaders import check_shader_support, get_phong_shader
                
                if check_shader_support():
                    self.phong_shader = get_phong_shader()
                    if self.phong_shader:
                        # Shader erfolgreich initialisiert
                        return
                
                # Fallback zu Gouraud wenn Shader nicht verfügbar
                print("  ⚠ Phong-Shader nicht verfügbar, verwende Gouraud")
                self.shading_mode = 'gouraud'
                
            except ImportError as e:
                print(f"  ⚠ Shader-Module nicht verfügbar: {e}")
                self.shading_mode = 'gouraud'
    
    def _load_data(self):
        """Laedt alle Daten."""
        print("\n" + "=" * 60)
        print("  DEUTSCHLAND 3D - Windkraft Evolution")
        print("=" * 60)
        
        # Bundeslaender laden
        self.bundeslaender = load_bundeslaender()
        
        # Windraeder mit Bundesland-Hoehen laden
        print("\n  Lade Windraeder:")
        csv_path = os.path.join(DATA_DIR, 'windmills_processed.csv')
        load_windturbines_with_heights(
            csv_path, 
            self.wind_turbines, 
            self.bundeslaender,
            scale=1.0,
            max_count=MAX_WINDMILLS
        )
        
        # NEU: Windkraft-Statistik berechnen
        print("\n  Berechne Windkraft-Statistik:")
        self.wind_statistics.calculate_from_turbines(
            self.wind_turbines.turbines,
            self.bundeslaender
        )
        
        # NEU: Initiale Bundesland-Hoehen setzen
        self._update_bundesland_heights()
        
        self._print_controls()
    
    def _apply_hardware_recommendations(self):
        """
        Wendet Hardware-basierte Empfehlungen auf die Rendering-Einstellungen an.
        Alle Features sind aktiviert - LOD und Quadtree sorgen für Performance.
        """
        caps = self.capabilities
        
        # LOD-Modus setzen (aggressiv für bessere Performance)
        if caps.lod_mode == "extreme":
            self.wind_turbines.lod_manager = self._get_lod_manager("extreme")
        elif caps.lod_mode == "aggressive":
            self.wind_turbines.lod_manager = self._get_lod_manager("aggressive")
        
        # ALLE Optimierungen aktivieren
        self.wind_turbines.use_quadtree = True   # Spatial Culling
        self.wind_turbines.use_lod = True        # Level-of-Detail
        self.wind_turbines.use_shadows = True    # Schatten immer an
        
        print(f"\n  Hardware-Optimierungen angewendet:")
        print(f"    LOD-Modus: {caps.lod_mode}")
        print(f"    Quadtree: Ja")
        print(f"    Schatten: Ja")
        print(f"    Instancing: {'Ja' if caps.use_instanced_rendering else 'Nein'}")
    
    def _get_lod_manager(self, mode: str):
        """Gibt LOD-Manager für den gegebenen Modus zurück."""
        try:
            from ..windturbine.lod_aggressive import AggressiveLODManager
            return AggressiveLODManager(mode)
        except ImportError:
            return self.wind_turbines.lod_manager
    
    def _print_controls(self):
        """Gibt Steuerungshinweise aus."""
        print("\n  Steuerung:")
        print("    * Maus ziehen = Rotieren")
        print("    * Scroll = Zoom")
        print("    * SPACE = Animation Start/Pause")
        print("    * Links/Rechts = Jahr +/- 5")
        print("    * W = Windraeder ein/aus")
        print("    * A = Blatt-Animation ein/aus")
        print("    * R = Ansicht zuruecksetzen")
        print("    * S = Screenshot")
        print("    * ESC = Beenden")
        print("=" * 60 + "\n")
    
    def _update_bundesland_heights(self):
        """
        Aktualisiert die Bundesland-Hoehen basierend auf dem aktuellen Jahr.
        
        Die Hoehe repraesentiert die installierte Windkraft-Leistung (MW).
        Mehr Leistung = Hoeheres Bundesland.
        """
        # Debug: Zeige Hoehen vor Update
        # print(f"\n  Bundesland-Hoehen fuer Jahr {self.current_year}:")
        # for bl in self.bundeslaender:
        #     if bl.name in ['Berlin', 'Hamburg', 'Bremen', 'Brandenburg', 'Niedersachsen']:
        #         print(f"    {bl.name}: {bl.extrusion:.3f}")
        
        # Bundesland-Hoehen aktualisieren
        self.wind_statistics.update_bundesland_heights(
            self.bundeslaender,
            self.current_year
        )
        
        # Debug: Zeige Hoehen nach Update
        # for bl in self.bundeslaender:
        #     if bl.name in ['Berlin', 'Hamburg', 'Bremen', 'Brandenburg', 'Niedersachsen']:
        #         power = self.wind_statistics.get_power_for_year(bl.name, self.current_year)
        #         print(f"    {bl.name}: {bl.extrusion:.3f} ({power:.0f} MW)")
        
        # Turbinen auf neue Bundesland-Hoehen setzen
        self._update_turbine_heights()
    
    def _update_turbine_heights(self):
        """
        Aktualisiert die bl_height aller Turbinen entsprechend ihrer Bundeslaender.
        
        Wird aufgerufen wenn sich die Bundesland-Hoehen aendern.
        OPTIMIERT: Nutzt gespeicherten Bundesland-Namen statt Point-in-Polygon.
        """
        # Erstelle schnelles Mapping: Bundesland-Name -> Hoehe
        height_map = {bl.name: bl.extrusion for bl in self.bundeslaender}
        
        # Aktualisiere bl_height basierend auf gespeichertem bl_name
        for turbine in self.wind_turbines.turbines:
            bl_name = getattr(turbine, 'bl_name', None)
            if bl_name and bl_name in height_map:
                turbine.bl_height = height_map[bl_name]
    
    def _handle_events(self) -> bool:
        """Verarbeitet pygame Events."""
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
                self._handle_key(event.key)
            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse.start_drag(event.pos)
                elif event.button in (4, 5):
                    self.mouse.scroll(event.button)
            
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse.stop_drag()
            
            elif event.type == MOUSEMOTION:
                self.mouse.update(event.pos)
            
            elif event.type == VIDEORESIZE:
                self._handle_resize(event.size)
        
        return True
    
    def _handle_key(self, key):
        """Verarbeitet Tastendruck."""
        if key == K_r:
            self.camera.reset()
            print("  Ansicht zurueckgesetzt.")
        
        elif key == K_s:
            self._save_screenshot()
        
        elif key == K_w:
            self.show_turbines = not self.show_turbines
            status = "AN" if self.show_turbines else "AUS"
            print(f"  Windraeder: {status}")
        
        elif key == K_a:
            self.wind_turbines.animation_enabled = not self.wind_turbines.animation_enabled
            status = "AN" if self.wind_turbines.animation_enabled else "AUS"
            print(f"  Blatt-Animation: {status}")
        
        elif key == K_SPACE:
            self.animation_running = not self.animation_running
            status = "LAEUFT" if self.animation_running else "PAUSIERT"
            print(f"  Jahr-Animation: {status}")
        
        elif key == K_RIGHT:
            self._change_year(YEAR_STEP)
        
        elif key == K_LEFT:
            self._change_year(-YEAR_STEP)
    
    def _change_year(self, delta: int):
        """Aendert das aktuelle Jahr und aktualisiert Bundesland-Hoehen."""
        new_year = self.current_year + delta
        if START_YEAR <= new_year <= END_YEAR:
            self.current_year = new_year
            
            # NEU: Bundesland-Hoehen aktualisieren
            self._update_bundesland_heights()
            
            count = self._count_visible_turbines()
            print(f"  Jahr: {self.current_year} ({count} Windraeder)")
    
    def _count_visible_turbines(self) -> int:
        """Zaehlt sichtbare Windraeder fuer aktuelles Jahr - OPTIMIERT."""
        # Nutze den schnellen Cache des Managers
        return self.wind_turbines.count_until_year(self.current_year)
    
    def _handle_resize(self, size):
        """Verarbeitet Fenstergroessenaenderung."""
        self.width, self.height = size
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            DOUBLEBUF | OPENGL | RESIZABLE
        )
        glViewport(0, 0, self.width, self.height)
        setup_projection(self.width, self.height)
    
    def _update_animation(self):
        """Aktualisiert Jahr-Animation und Bundesland-Hoehen."""
        if not self.animation_running:
            return
        
        current_time = time.time()
        if current_time - self.last_year_change >= ANIMATION_SPEED:
            self.last_year_change = current_time
            
            new_year = self.current_year + YEAR_STEP
            if new_year > END_YEAR:
                new_year = START_YEAR  # Loop
            
            self.current_year = new_year
            
            # NEU: Bundesland-Hoehen aktualisieren
            self._update_bundesland_heights()
            
            count = self._count_visible_turbines()
            print(f"  Jahr: {self.current_year} ({count} Windraeder)")
    
    def _render(self):
        """Rendert die komplette Szene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 3D-Szene
        self._render_3d_scene()
        
        # 2D-Overlay (Legende) - nur wenn Windräder angezeigt werden
        if self.show_turbines :
            self._render_legend()
        
        pygame.display.flip()
    
    def _render_3d_scene(self):
        """Rendert die 3D-Szene."""
        # Kamera-Transformation
        apply_camera_transform(
            self.camera.rot_x,
            self.camera.rot_y,
            self.camera.zoom
        )
        
        # Beleuchtung
        update_lighting()
        
        # Stadtstaaten separat (muessen zuletzt gerendert werden)
        CITY_STATES = {'Berlin', 'Hamburg', 'Bremen'}
        
        # Normale Bundeslaender sortieren (hinten nach vorne)
        normal_bl = [b for b in self.bundeslaender if b.name not in CITY_STATES]
        city_states = [b for b in self.bundeslaender if b.name in CITY_STATES]
        
        sorted_normal = sorted(
            normal_bl,
            key=lambda b: -sum(v[2] for v in b.vertices_top) / len(b.vertices_top)
        )
        
        sorted_cities = sorted(
            city_states,
            key=lambda b: -sum(v[2] for v in b.vertices_top) / len(b.vertices_top)
        )
        
        # Schatten (alle Bundeslaender)
        all_bl = sorted_normal + sorted_cities
        render_map_shadows(all_bl, self.camera.rot_y)
        
        # Erst normale Bundeslaender rendern
        for bl in sorted_normal:
            bl.render()
        
        # Dann Stadtstaaten rendern (ueber den Loechern)
        for bl in sorted_cities:
            bl.render()
        
        # Windraeder (gefiltert nach Jahr) - OPTIMIERT mit Frustum Culling
        if self.show_turbines:
            # Nur sichtbare Turbinen updaten (Performance!)
            self.wind_turbines.update_visible_only(1.0 / 60.0, self.current_year)
            # PERFORMANCE: Frustum Culling + Jahr-Cache + SHADOW_THRESHOLD
            self.wind_turbines.render_until_year(
                self.current_year, 
                SHADOW_THRESHOLD#,
                #self.camera.zoom
            )
    
    def _render_turbines_by_year(self):
        """Legacy - wird nicht mehr verwendet."""
        pass
    
    def _render_legend(self):
        """Rendert moderne 2D-Legende im Stil wissenschaftlicher Visualisierungen."""
        # OpenGL auf 2D umschalten
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Legende Position (unten links)
        margin = 120
        legend_x = margin
        legend_y = 300  # Von unten
        
        # === TITEL: "Deutschland Windkraft" ===
        self._render_text("Deutschland", legend_x, legend_y, large=True, color=(0.3, 0.3, 0.3))
        self._render_text("Windkraft-Evolution", legend_x, legend_y - 28, color=(0.5, 0.5, 0.5))
        
        # === FARBSKALA mit Gradient ===
        gradient_x = legend_x
        gradient_y = legend_y - 70
        gradient_width = 180
        gradient_height = 14
        
        # Farbverlauf zeichnen (von grün nach rot)
        num_segments = 50
        segment_width = gradient_width / num_segments
        
        glBegin(GL_QUADS)
        for i in range(num_segments):
            # Interpoliere Leistung von 0 bis 7000 kW
            power1 = (i / num_segments) * 7000
            power2 = ((i + 1) / num_segments) * 7000
            
            color1 = get_power_color(power1)
            color2 = get_power_color(power2)
            
            x1 = gradient_x + i * segment_width
            x2 = gradient_x + (i + 1) * segment_width
            
            # Links
            glColor3f(*color1)
            glVertex2f(x1, gradient_y)
            glVertex2f(x1, gradient_y - gradient_height)
            
            # Rechts
            glColor3f(*color2)
            glVertex2f(x2, gradient_y - gradient_height)
            glVertex2f(x2, gradient_y)
        glEnd()
        
        # Rahmen um Gradient
        glColor4f(0.4, 0.4, 0.4, 1.0)
        glLineWidth(1.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(gradient_x, gradient_y)
        glVertex2f(gradient_x + gradient_width, gradient_y)
        glVertex2f(gradient_x + gradient_width, gradient_y - gradient_height)
        glVertex2f(gradient_x, gradient_y - gradient_height)
        glEnd()
        
        # Beschriftung: "Leistung [kW]" über dem Gradient
        self._render_text("Leistung", gradient_x, gradient_y + 18, color=(0.4, 0.4, 0.4))
        self._render_text("[kW]", gradient_x + 62, gradient_y + 18, color=(0.5, 0.5, 0.5))
        
        # Min/Max Werte unter dem Gradient
        self._render_text("0", gradient_x, gradient_y - gradient_height - 18, color=(0.4, 0.4, 0.4))
        self._render_text("7000", gradient_x + gradient_width - 30, gradient_y - gradient_height - 18, color=(0.4, 0.4, 0.4))
        
        # === JAHR gross rechts ===
        year_x = self.width - 300
        year_y = 150
        
        # Jahr mit grosser Schrift
        year_str = str(self.current_year)
        self._render_text(year_str, year_x, year_y, large=True, color=(0.35, 0.35, 0.35), scale=2.5)
        
        # === INFO: Windräder-Anzahl ===
        count = self._count_visible_turbines()
        info_y = legend_y - 120
        self._render_text(f"Windraeder: {count:,}".replace(",", "."), legend_x, info_y, color=(0.5, 0.5, 0.5))
        
        # === STEUERUNG unten ===
        if self.animation_running:
            status = "▶ Animation laeuft"
            status_color = (0.3, 0.6, 0.3)
        else:
            status = "◼ [SPACE] Start"
            status_color = (0.5, 0.5, 0.5)
        self._render_text(status, legend_x, info_y - 25, color=status_color)
        
        # Zurueck zu 3D
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glDisable(GL_BLEND)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def _render_text(self, text: str, x: float, y: float, 
                     large: bool = False, color: tuple = (0.1, 0.1, 0.1), scale: float = 1.0):
        """Rendert Text mit Pygame."""
        # Waehle Font basierend auf scale
        if scale > 2.0:
            font = self.font_year  # Extra gross (fuer Jahr)
        elif large:
            font = self.font_large
        else:
            font = self.font
        
        # Text rendern
        text_surface = font.render(text, True, 
                                   (int(color[0]*255), int(color[1]*255), int(color[2]*255)))
        text_data = pygame.image.tostring(text_surface, 'RGBA', True)
        
        # Als OpenGL Textur zeichnen
        glRasterPos2f(x, y)
        glDrawPixels(text_surface.get_width(), text_surface.get_height(),
                     GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
    def _save_screenshot(self):
        """Speichert einen Screenshot."""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        data = glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE)
        img = Image.frombytes('RGB', (self.width, self.height), data)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        
        filename = f'germany_3d_{self.current_year}.png'
        path = os.path.join(OUTPUT_DIR, filename)
        img.save(path, quality=95)
        print(f"  Screenshot gespeichert: {path}")
    
    def run(self):
        """Haupt-Schleife."""
        clock = pygame.time.Clock()
        running = True
        self.last_year_change = time.time()
        
        print(f"\n  Starte mit Jahr {self.current_year}...")
        print(f"  Druecke SPACE fuer Animation oder Links/Rechts fuer manuell.\n")
        
        while running:
            running = self._handle_events()
            self._update_animation()
            self._render()
            clock.tick(60)
        
        pygame.quit()
