"""
Windkraft-Statistik pro Bundesland
==================================

Berechnet die installierte Windkraft-Leistung (MW) pro Bundesland und Jahr.
Die Hoehe der Bundeslaender wird basierend auf dieser Leistung angepasst.

Vorlesungskonzept: Datenvisualisierung - Mapping von Daten auf visuelle Attribute
"""

from ..data.point_in_polygon import point_in_polygon


# Minimale und maximale Hoehe fuer Bundeslaender
MIN_HEIGHT = 0.08    # Mindesthoehe (auch ohne Windkraft)
MAX_HEIGHT = 0.35    # Maximalhoehe (bei hoechster Leistung)
BASE_HEIGHT = 0.10   # Basishoehe ohne Windkraft


class WindPowerStatistics:
    """
    Berechnet und speichert Windkraft-Statistiken pro Bundesland.
    """
    
    def __init__(self):
        # Leistung pro Bundesland und Jahr: {bundesland: {jahr: leistung_mw}}
        self.power_by_state_year = {}
        # Maximale Leistung (fuer Normalisierung)
        self.max_power = 0
        # Bundesland-Namen zu Objekten Mapping
        self.bundesland_map = {}
    
    def calculate_from_turbines(self, turbines: list, bundeslaender: list):
        """
        Berechnet die Windkraft-Leistung pro Bundesland und Jahr
        basierend auf den Turbinen-Daten.
        
        Args:
            turbines: Liste von WindTurbine-Objekten mit year, power_kw, x, z
            bundeslaender: Liste von Bundesland-Objekten
        """
        # Bundesland-Map erstellen
        self.bundesland_map = {bl.name: bl for bl in bundeslaender}
        
        # Initialisiere Datenstruktur
        for bl in bundeslaender:
            self.power_by_state_year[bl.name] = {}
        
        # Zaehle Leistung pro Bundesland
        turbine_to_state = {}
        
        print("    Berechne Windkraft-Statistik pro Bundesland...")
        
        for i, turbine in enumerate(turbines):
            # Finde Bundesland fuer diese Turbine
            state_name = None
            for bl in bundeslaender:
                if point_in_polygon(turbine.x, turbine.z, bl.vertices_top):
                    state_name = bl.name
                    break
            
            if state_name:
                turbine_to_state[id(turbine)] = state_name
                year = getattr(turbine, 'year', 2000)
                power_kw = getattr(turbine, 'power_kw', 3000)
                
                # Addiere zur kumulativen Leistung
                if year not in self.power_by_state_year[state_name]:
                    self.power_by_state_year[state_name][year] = 0
                self.power_by_state_year[state_name][year] += power_kw / 1000  # kW -> MW
            
            if (i + 1) % 5000 == 0:
                print(f"      {i + 1}/{len(turbines)} Turbinen zugeordnet...")
        
        # Kumulative Summen berechnen (Leistung addiert sich ueber die Jahre)
        self._calculate_cumulative()
        
        # Maximum finden
        for state_data in self.power_by_state_year.values():
            for power in state_data.values():
                if power > self.max_power:
                    self.max_power = power
        
        print(f"    Statistik berechnet. Max Leistung: {self.max_power:.0f} MW")
        self._print_summary()
    
    def _calculate_cumulative(self):
        """Berechnet kumulative Leistung (Anlagen bleiben ja stehen)."""
        for state_name in self.power_by_state_year:
            years = sorted(self.power_by_state_year[state_name].keys())
            cumulative = 0
            cumulative_data = {}
            
            for year in years:
                cumulative += self.power_by_state_year[state_name][year]
                cumulative_data[year] = cumulative
            
            self.power_by_state_year[state_name] = cumulative_data
    
    def _print_summary(self):
        """Gibt eine Zusammenfassung aus."""
        print("\n    Top 5 Bundeslaender (aktuell):")
        
        # Finde hoechstes Jahr pro Bundesland
        latest = {}
        for state, years in self.power_by_state_year.items():
            if years:
                max_year = max(years.keys())
                latest[state] = years[max_year]
        
        # Sortieren
        sorted_states = sorted(latest.items(), key=lambda x: -x[1])[:5]
        for state, power in sorted_states:
            print(f"      {state}: {power:.0f} MW")
    
    def get_power_for_year(self, state_name: str, year: int) -> float:
        """
        Gibt die installierte Leistung fuer ein Bundesland in einem Jahr zurueck.
        
        Args:
            state_name: Name des Bundeslandes
            year: Jahr
            
        Returns:
            Installierte Leistung in MW
        """
        if state_name not in self.power_by_state_year:
            return 0
        
        state_data = self.power_by_state_year[state_name]
        if not state_data:
            return 0
        
        # Finde naechstes Jahr <= year
        available_years = sorted(state_data.keys())
        power = 0
        for y in available_years:
            if y <= year:
                power = state_data[y]
            else:
                break
        
        return power
    
    def get_height_for_year(self, state_name: str, year: int) -> float:
        """
        Berechnet die Hoehe eines Bundeslandes basierend auf der Windkraft-Leistung.
        
        Mapping: 0 MW -> MIN_HEIGHT, max_power MW -> MAX_HEIGHT
        
        Args:
            state_name: Name des Bundeslandes
            year: Jahr
            
        Returns:
            Hoehe fuer das Bundesland
        """
        power = self.get_power_for_year(state_name, year)
        
        if self.max_power <= 0:
            return BASE_HEIGHT
        
        # Normalisieren auf 0-1
        normalized = power / self.max_power
        
        # Auf Hoehen-Bereich mappen
        height = MIN_HEIGHT + normalized * (MAX_HEIGHT - MIN_HEIGHT)
        
        return height
    
    def update_bundesland_heights(self, bundeslaender: list, year: int):
        """
        Aktualisiert die Hoehen aller Bundeslaender fuer ein bestimmtes Jahr.
        
        Jedes Bundesland bekommt seine eigene Hoehe basierend auf seiner Windkraft.
        
        Args:
            bundeslaender: Liste von Bundesland-Objekten
            year: Aktuelles Jahr
        """
        for bl in bundeslaender:
            new_height = self.get_height_for_year(bl.name, year)
            if abs(bl.extrusion - new_height) > 0.001:
                bl.update_height(new_height)
