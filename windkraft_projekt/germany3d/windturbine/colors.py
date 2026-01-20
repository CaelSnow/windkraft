"""
Farben für Windrad-Komponenten
==============================

Definiert alle Farben die für die Windrad-Visualisierung verwendet werden.
"""

# Strukturfarben (RGB Tupel, Werte 0-1)
COLOR_TOWER = (0.92, 0.91, 0.88)      # Hellgrau (Beton/Stahl)
COLOR_NACELLE = (0.94, 0.93, 0.90)    # Weißgrau (Gondel)
COLOR_HUB = (0.45, 0.48, 0.52)        # Dunkelgrau (Metall-Nabe)
COLOR_BLADE = (0.97, 0.97, 0.95)      # Fast weiß (GFK-Rotorblätter)

# Schatten (RGBA mit Alpha für Transparenz)
COLOR_SHADOW = (0.0, 0.0, 0.0, 0.25)


def get_power_color(power_kw: float) -> tuple:
    """
    Farbkodierung nach Leistung.
    
    Vorlesung: Wissenschaftliche Visualisierung - Farbkodierung von Daten
    
    Args:
        power_kw: Leistung in Kilowatt
        
    Returns:
        RGB-Tupel (r, g, b)
    """
    if power_kw < 1000:
        return (0.4, 0.85, 0.4)   # Grün - klein
    elif power_kw < 3000:
        return (0.9, 0.9, 0.4)    # Gelb - mittel
    elif power_kw < 5000:
        return (0.95, 0.65, 0.3)  # Orange - groß
    else:
        return (0.95, 0.4, 0.35)  # Rot - sehr groß
