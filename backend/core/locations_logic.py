import json
import os

# Definiamo il percorso del nostro file JSON
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
LOCATIONS_FILE = os.path.join(DATA_DIR, 'locations.json')

def _read_locations():
    """Funzione helper per leggere i dati dal file JSON."""
    if not os.path.exists(LOCATIONS_FILE) or os.path.getsize(LOCATIONS_FILE) == 0:
        return {}
    try:
        with open(LOCATIONS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def _write_locations(data):
    """Funzione helper per scrivere i dati nel file JSON."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LOCATIONS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_all_locations():
    """Restituisce tutti i luoghi salvati."""
    return _read_locations()

def get_location(name):
    """Restituisce un luogo specifico per nome."""
    locations = _read_locations()
    return locations.get(name)

def create_location(name, data):
    """Crea o aggiorna un luogo."""
    locations = _read_locations()
    if name in locations:
        return None, "Location with this name already exists."
    
    # Validazione semplice dei dati
    if not all(k in data for k in ['lat', 'lon', 'alt']):
        return None, "Missing required fields: lat, lon, alt."
    
    locations[name] = {
        "lat": float(data['lat']),
        "lon": float(data['lon']),
        "alt": float(data['alt'])
    }
    _write_locations(locations)
    return locations[name], None

def update_location(name, data):
    """Aggiorna un luogo esistente."""
    locations = _read_locations()
    if name not in locations:
        return None, "Location not found."
        
    locations[name].update({
        "lat": float(data.get('lat', locations[name]['lat'])),
        "lon": float(data.get('lon', locations[name]['lon'])),
        "alt": float(data.get('alt', locations[name]['alt']))
    })
    _write_locations(locations)
    return locations[name], None

def delete_location(name):
    """Cancella un luogo."""
    locations = _read_locations()
    if name not in locations:
        return False, "Location not found."
    
    del locations[name]
    _write_locations(locations)
    return True, None
