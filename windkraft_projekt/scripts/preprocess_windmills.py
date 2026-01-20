#!/usr/bin/env python3
"""
Preprocessing-Skript für Windmühlen-Daten.

Liest MaStR-Daten (windmills.csv), fügt GPS-Koordinaten via PLZ hinzu,
konvertiert zu 3D-Koordinaten und speichert als vorbereitete CSV.

Nutzung:
    python scripts/preprocess_windmills.py

Input:
    - data/windmills.csv (MaStR-Daten mit PLZ, keine GPS)
    - data/plz_geocoord.csv (PLZ -> GPS Mapping)

Output:
    - data/windmills_processed.csv (fertig für Visualisierung)
"""

import csv
import math
import os
from collections import defaultdict
from datetime import datetime


# === Konfiguration ===
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
INPUT_CSV = os.path.join(DATA_DIR, 'windmills.csv')
PLZ_CSV = os.path.join(DATA_DIR, 'plz_geocoord.csv')
OUTPUT_CSV = os.path.join(DATA_DIR, 'windmills_processed.csv')

# GPS-Grenzen für Deutschland
LAT_MIN, LAT_MAX = 47.27, 55.06
LON_MIN, LON_MAX = 5.87, 15.04


def load_plz_lookup(csv_path: str) -> dict:
    """
    Lädt PLZ -> GPS Mapping aus CSV.
    
    Returns:
        Dict[plz: str, (lat: float, lon: float)]
    """
    lookup = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Das erste Feld hat keinen Header-Namen (leerer String)
                # Versuche verschiedene Keys
                plz = None
                for key in ['', 'plz', 'PLZ']:
                    if key in row:
                        plz = row[key]
                        break
                
                # Falls immer noch None, nimm den ersten Wert
                if not plz:
                    plz = list(row.values())[0]
                
                plz = str(plz).strip().zfill(5)
                lat = float(row.get('lat', 0))
                lon = float(row.get('lng', 0))  # Note: 'lng' in plz_geocoord.csv
                
                if plz and lat and lon:
                    lookup[plz] = (lat, lon)
            except (ValueError, KeyError):
                continue
    
    # Fehlende PLZ manuell ergänzen (benachbarte Koordinaten)
    missing_plz_coords = {
        '39628': (52.7891, 11.7223),  # Nahe 39606
        '15713': (52.2949, 13.6267),  # Nahe 15711
        '15712': (52.2949, 13.6267),  # Nahe 15711
        '06772': (51.0184, 12.1519),  # Nahe 06712
        '06868': (51.6867, 12.3245),  # Nahe 06800
        '99095': (50.9754, 11.0262),  # Nahe 99084
    }
    
    for plz, coords in missing_plz_coords.items():
        if plz not in lookup:
            lookup[plz] = coords
            print(f"    + PLZ {plz} manuell ergänzt")
    
    return lookup


def gps_to_3d(lat: float, lon: float) -> tuple:
    """
    Konvertiert GPS-Koordinaten zu 3D-Koordinaten.
    
    Returns:
        (x, z) Position im 3D-Raum
    """
    nx = (lon - LON_MIN) / (LON_MAX - LON_MIN)
    nz = (lat - LAT_MIN) / (LAT_MAX - LAT_MIN)
    
    x = (nx - 0.5) * 2.2
    z = -(nz - 0.5) * 2.6  # Negativ damit Norden oben ist
    
    return round(x, 6), round(z, 6)


def extract_year(date_str: str) -> int:
    """
    Extrahiert das Jahr aus dem Inbetriebnahmedatum.
    
    Args:
        date_str: Datum im Format 'MM/DD/YYYY', 'DD.MM.YYYY' oder 'YYYY-MM-DD'
    
    Returns:
        Jahr als int, oder 0 bei Fehler
    """
    if not date_str:
        return 0
    
    date_str = date_str.strip()
    
    try:
        # Format: MM/DD/YYYY (MaStR-Format)
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) >= 3:
                return int(parts[2][:4])  # Nur ersten 4 Zeichen für Jahr
        
        # Format: DD.MM.YYYY
        elif '.' in date_str:
            parts = date_str.split('.')
            if len(parts) >= 3:
                return int(parts[2][:4])
        
        # Format: YYYY-MM-DD
        elif '-' in date_str:
            return int(date_str[:4])
        
        # Nur Jahr
        elif len(date_str) == 4 and date_str.isdigit():
            return int(date_str)
            
    except (ValueError, IndexError):
        pass
    
    return 0


def preprocess_windmills():
    """
    Hauptfunktion: Verarbeitet alle Windmühlen.
    """
    print("=" * 60)
    print("Windmühlen-Preprocessing")
    print("=" * 60)
    
    # 1. PLZ-Lookup laden
    print(f"\n[1/4] Lade PLZ-Koordinaten: {PLZ_CSV}")
    if not os.path.exists(PLZ_CSV):
        print(f"    ✗ Datei nicht gefunden!")
        return
    
    plz_lookup = load_plz_lookup(PLZ_CSV)
    print(f"    ✓ {len(plz_lookup)} PLZ-Einträge geladen")
    
    # 2. MaStR-Daten lesen und verarbeiten
    print(f"\n[2/4] Verarbeite Windmühlen: {INPUT_CSV}")
    if not os.path.exists(INPUT_CSV):
        print(f"    ✗ Datei nicht gefunden!")
        return
    
    # Statistiken
    stats = {
        'total': 0,
        'processed': 0,
        'skipped_no_plz': 0,
        'skipped_plz_not_found': 0,
        'skipped_invalid': 0
    }
    
    # PLZ-Zähler für Streuung
    plz_counter = defaultdict(int)
    
    # Ergebnisse sammeln
    results = []
    
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        # MaStR ist Semikolon-separiert
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            stats['total'] += 1
            
            try:
                # PLZ extrahieren
                plz = str(row.get('Postleitzahl', '')).strip()
                
                # Überspringe leere oder ungültige PLZ
                if not plz or plz == '0' or plz == 'Postleitzahl':
                    stats['skipped_no_plz'] += 1
                    continue
                
                plz = plz.zfill(5)  # Führende Nullen
                
                # Überspringe PLZ '00000' (keine gültige deutsche PLZ)
                if plz == '00000':
                    stats['skipped_no_plz'] += 1
                    continue
                
                # GPS-Koordinaten nachschlagen
                if plz not in plz_lookup:
                    stats['skipped_plz_not_found'] += 1
                    continue
                
                lat, lon = plz_lookup[plz]
                
                # Leichte Streuung für Windräder mit gleicher PLZ
                plz_counter[plz] += 1
                scatter = plz_counter[plz] - 1
                if scatter > 0:
                    # Spiralförmige Streuung um den PLZ-Mittelpunkt
                    angle = scatter * 137.5  # Goldener Winkel
                    radius = 0.01 * (scatter ** 0.5)  # Langsam wachsender Radius
                    lat += radius * math.cos(math.radians(angle))
                    lon += radius * math.sin(math.radians(angle))
                
                # GPS zu 3D konvertieren
                x, z = gps_to_3d(lat, lon)
                
                # Leistung extrahieren (kW)
                power_str = row.get('Bruttoleistung der Einheit', '3000')
                power = float(power_str) if power_str else 3000.0
                
                # Jahr extrahieren
                date_str = row.get('Inbetriebnahmedatum der Einheit', '')
                year = extract_year(date_str)
                
                # Ergebnis speichern
                results.append({
                    'plz': plz,
                    'x': x,
                    'z': z,
                    'power_kw': power,
                    'year': year
                })
                stats['processed'] += 1
                
            except (ValueError, KeyError) as e:
                stats['skipped_invalid'] += 1
                continue
            
            # Fortschritt anzeigen
            if stats['total'] % 5000 == 0:
                print(f"    ... {stats['total']} Einträge verarbeitet")
    
    print(f"    ✓ {stats['processed']} Windräder verarbeitet")
    
    # 3. Statistiken ausgeben
    print(f"\n[3/4] Statistiken:")
    print(f"    Gesamt gelesen:     {stats['total']:,}")
    print(f"    Erfolgreich:        {stats['processed']:,}")
    print(f"    Ohne PLZ:           {stats['skipped_no_plz']:,}")
    print(f"    PLZ nicht gefunden: {stats['skipped_plz_not_found']:,}")
    print(f"    Ungültige Daten:    {stats['skipped_invalid']:,}")
    
    # Jahr-Verteilung
    year_dist = defaultdict(int)
    for r in results:
        if r['year'] > 0:
            year_dist[r['year']] += 1
    
    if year_dist:
        print(f"\n    Jahr-Verteilung (Top 10):")
        sorted_years = sorted(year_dist.items(), key=lambda x: x[1], reverse=True)[:10]
        for year, count in sorted_years:
            print(f"        {year}: {count:,} Windräder")
    
    # 4. Ergebnis speichern
    print(f"\n[4/4] Speichere Ergebnis: {OUTPUT_CSV}")
    
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['plz', 'x', 'z', 'power_kw', 'year'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"    ✓ {len(results):,} Einträge gespeichert")
    
    # Dateigröße
    size_mb = os.path.getsize(OUTPUT_CSV) / (1024 * 1024)
    print(f"    Dateigröße: {size_mb:.2f} MB")
    
    print("\n" + "=" * 60)
    print("Preprocessing abgeschlossen!")
    print("=" * 60)


if __name__ == '__main__':
    preprocess_windmills()
