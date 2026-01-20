#!/usr/bin/env python3
"""
Windmill Data Preprocessor
==========================

Liest windmills.csv und plz_geocoord.csv, kombiniert die Daten
und erstellt eine fertige CSV für die 3D-Visualisierung.

Ausgabe-Format:
    plz, x, z, power_kw, year

Wobei x, z die 3D-Koordinaten sind (bereits skaliert für unsere Visualisierung).
"""

import csv
import os
import sys
from datetime import datetime

# Pfade
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, 'data')

# Eingabe-Dateien
WINDMILLS_CSV = os.path.join(DATA_DIR, 'windmills.csv')
PLZ_GEOCOORD_CSV = os.path.join(DATA_DIR, 'plz_geocoord.csv')

# Ausgabe-Datei
OUTPUT_CSV = os.path.join(DATA_DIR, 'windmills_prepared.csv')

# Deutschland GPS-Grenzen (gleich wie in config.py)
LAT_MIN = 47.27
LAT_MAX = 55.06
LON_MIN = 5.87
LON_MAX = 15.04


def load_plz_coordinates():
    """Lädt PLZ → GPS Koordinaten aus plz_geocoord.csv."""
    plz_coords = {}
    
    print(f"  Lade PLZ-Koordinaten aus {os.path.basename(PLZ_GEOCOORD_CSV)}...")
    
    with open(PLZ_GEOCOORD_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Erste Spalte könnte leer sein oder PLZ enthalten
                plz = row.get('', '') or row.get('plz', '')
                if not plz:
                    # Versuche erste Spalte
                    plz = list(row.values())[0]
                
                plz = str(plz).strip().zfill(5)  # PLZ auf 5 Stellen
                lat = float(row.get('lat', 0))
                lng = float(row.get('lng', 0))
                
                if lat > 0 and lng > 0:
                    plz_coords[plz] = (lat, lng)
            except (ValueError, KeyError):
                continue
    
    print(f"    ✓ {len(plz_coords)} PLZ-Koordinaten geladen")
    return plz_coords


def gps_to_3d(lat, lon):
    """
    Konvertiert GPS-Koordinaten zu 3D-Koordinaten.
    
    Gleiche Formel wie in der Visualisierung verwendet.
    """
    # Normalisieren (0 bis 1)
    nx = (lon - LON_MIN) / (LON_MAX - LON_MIN)
    nz = (lat - LAT_MIN) / (LAT_MAX - LAT_MIN)
    
    # Zu 3D-Koordinaten skalieren
    x = (nx - 0.5) * 2.2
    z = -(nz - 0.5) * 2.6  # Negativ damit Norden oben ist
    
    return x, z


def parse_date(date_str):
    """Extrahiert das Jahr aus verschiedenen Datumsformaten."""
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    # Versuche verschiedene Formate
    formats = [
        '%m/%d/%Y',      # 10/23/2025
        '%d.%m.%Y',      # 23.10.2025
        '%Y-%m-%d',      # 2025-10-23
        '%d/%m/%Y',      # 23/10/2025
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.year
        except ValueError:
            continue
    
    # Versuche nur Jahr zu extrahieren
    try:
        # Falls nur Jahr angegeben (z.B. "2020")
        year = int(date_str[:4])
        if 1980 <= year <= 2030:
            return year
    except (ValueError, IndexError):
        pass
    
    return None


def process_windmills(plz_coords, year_filter=None):
    """
    Verarbeitet windmills.csv und erstellt die Ausgabe-Daten.
    
    Args:
        plz_coords: Dictionary PLZ → (lat, lng)
        year_filter: Optional - nur Windräder bis zu diesem Jahr
    
    Returns:
        Liste von Dictionaries mit den aufbereiteten Daten
    """
    windmills = []
    skipped_no_plz = 0
    skipped_no_coords = 0
    skipped_year = 0
    skipped_outside = 0
    
    print(f"  Verarbeite Windräder aus {os.path.basename(WINDMILLS_CSV)}...")
    
    with open(WINDMILLS_CSV, 'r', encoding='utf-8', errors='replace') as f:
        # Semikolon-getrennt
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            # PLZ extrahieren
            plz = row.get('Postleitzahl', '').strip()
            if not plz:
                skipped_no_plz += 1
                continue
            
            plz = str(plz).zfill(5)
            
            # Koordinaten nachschlagen
            if plz not in plz_coords:
                skipped_no_coords += 1
                continue
            
            lat, lng = plz_coords[plz]
            
            # Jahr extrahieren
            date_str = row.get('Inbetriebnahmedatum der Einheit', '')
            year = parse_date(date_str)
            
            if year is None:
                skipped_year += 1
                continue
            
            # Jahr-Filter anwenden
            if year_filter and year > year_filter:
                continue
            
            # Leistung extrahieren
            try:
                power_str = row.get('Bruttoleistung der Einheit', '0')
                power_kw = float(power_str.replace(',', '.'))
            except ValueError:
                power_kw = 1000  # Fallback
            
            # GPS zu 3D konvertieren
            x, z = gps_to_3d(lat, lng)
            
            # Prüfen ob innerhalb der Grenzen
            if not (-1.2 <= x <= 1.2 and -1.4 <= z <= 1.4):
                skipped_outside += 1
                continue
            
            windmills.append({
                'plz': plz,
                'x': round(x, 6),
                'z': round(z, 6),
                'power_kw': round(power_kw, 1),
                'year': year
            })
    
    print(f"    ✓ {len(windmills)} Windräder verarbeitet")
    if skipped_no_plz > 0:
        print(f"    ⚠ {skipped_no_plz} übersprungen (keine PLZ)")
    if skipped_no_coords > 0:
        print(f"    ⚠ {skipped_no_coords} übersprungen (PLZ nicht gefunden)")
    if skipped_year > 0:
        print(f"    ⚠ {skipped_year} übersprungen (ungültiges Datum)")
    if skipped_outside > 0:
        print(f"    ⚠ {skipped_outside} übersprungen (außerhalb Deutschlands)")
    
    return windmills


def save_prepared_data(windmills, output_path):
    """Speichert die aufbereiteten Daten als CSV."""
    print(f"  Speichere nach {os.path.basename(output_path)}...")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['plz', 'x', 'z', 'power_kw', 'year'])
        writer.writeheader()
        writer.writerows(windmills)
    
    print(f"    ✓ {len(windmills)} Einträge gespeichert")


def print_statistics(windmills):
    """Gibt Statistiken über die Daten aus."""
    if not windmills:
        return
    
    years = [w['year'] for w in windmills]
    powers = [w['power_kw'] for w in windmills]
    
    print("\n  Statistiken:")
    print(f"    • Jahre: {min(years)} - {max(years)}")
    print(f"    • Leistung: {min(powers):.0f} - {max(powers):.0f} kW")
    print(f"    • Durchschnitt: {sum(powers)/len(powers):.0f} kW")
    
    # Verteilung nach Jahren
    year_counts = {}
    for y in years:
        decade = (y // 10) * 10
        year_counts[decade] = year_counts.get(decade, 0) + 1
    
    print("\n    Verteilung nach Jahrzehnten:")
    for decade in sorted(year_counts.keys()):
        count = year_counts[decade]
        bar = '█' * (count // 100)
        print(f"      {decade}s: {count:5d} {bar}")


def main():
    """Hauptfunktion."""
    print("\n" + "=" * 60)
    print("  WINDMILL DATA PREPROCESSOR")
    print("=" * 60 + "\n")
    
    # Jahr-Filter aus Argumenten (optional)
    year_filter = None
    if len(sys.argv) > 1:
        try:
            year_filter = int(sys.argv[1])
            print(f"  Filter: Nur Windräder bis {year_filter}\n")
        except ValueError:
            pass
    
    # 1. PLZ-Koordinaten laden
    plz_coords = load_plz_coordinates()
    
    # 2. Windräder verarbeiten
    windmills = process_windmills(plz_coords, year_filter)
    
    # 3. Statistiken anzeigen
    print_statistics(windmills)
    
    # 4. Speichern
    print()
    save_prepared_data(windmills, OUTPUT_CSV)
    
    print("\n" + "=" * 60)
    print(f"  ✅ Fertig! Datei: {OUTPUT_CSV}")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
