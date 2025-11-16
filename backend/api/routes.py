from flask import Blueprint, request, jsonify
from datetime import datetime
from core.planetary_logic import calculate_planetary_hours, search_planetary_hours, PLANETS, ZODIAC_SIGNS

# Definiamo un Blueprint per le rotte dell'API
api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/calculate', methods=['GET'])
def get_planetary_hours():
    """
    Endpoint per calcolare le ore planetarie.
    Richiede parametri query: date, lat, lon. Alt è opzionale.
    """
    # 1. Estrazione dei parametri
    date_str = request.args.get('date')
    lat_str = request.args.get('lat')
    lon_str = request.args.get('lon')
    alt_str = request.args.get('alt', '0') # Default a 0 se non fornito

    # 2. Validazione dei parametri
    if not all([date_str, lat_str, lon_str]):
        return jsonify({"error": "Parametri mancanti: 'date', 'lat' e 'lon' sono obbligatori."}), 400

    try:
        calc_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        latitude = float(lat_str)
        longitude = float(lon_str)
        altitude = float(alt_str)
    except ValueError as e:
        return jsonify({"error": f"Parametro non valido: {e}"}), 400

    # 3. Chiamata alla logica di calcolo
    results = calculate_planetary_hours(
        calculation_date=calc_date,
        latitude=latitude,
        longitude=longitude,
        elevation=altitude
    )

    if "error" in results:
        # Se la funzione di calcolo restituisce un errore
        return jsonify(results), 500

    # 4. Restituzione dei risultati
    return jsonify(results)

@api_bp.route('/search', methods=['GET'])
def handle_search():
    """
    Endpoint per la ricerca avanzata di ore planetarie.
    """
    # Parametri di ricerca
    planet = request.args.get('planet')
    sign = request.args.get('sign')
    moon_phase = request.args.get('moon_phase')
    
    # Parametri di localizzazione (necessari per i calcoli)
    lat_str = request.args.get('lat')
    lon_str = request.args.get('lon')
    alt_str = request.args.get('alt', '0')

    if not all([lat_str, lon_str]):
        return jsonify({"error": "Parametri di localizzazione mancanti: 'lat' e 'lon' sono obbligatori per la ricerca."}), 400

    if not any([planet, sign, moon_phase]):
        return jsonify({"error": "È richiesto almeno un criterio di ricerca (planet, sign, o moon_phase)."}), 400

    try:
        latitude = float(lat_str)
        longitude = float(lon_str)
        altitude = float(alt_str)
    except ValueError as e:
        return jsonify({"error": f"Parametro di localizzazione non valido: {e}"}), 400

    results = search_planetary_hours(
        lat=latitude,
        lon=longitude,
        alt=altitude,
        planet=planet if planet else None,
        sign=sign if sign else None,
        moon_phase=moon_phase if moon_phase else None
    )
    
    return jsonify(results)

@api_bp.route('/meta', methods=['GET'])
def get_metadata():
    """
    Endpoint per ottenere metadati utili per il frontend,
    come le liste di pianeti, segni, etc.
    """
    moon_phases = [
        "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
        "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"
    ]
    return jsonify({
        "planets": PLANETS,
        "zodiac_signs": [sign[1] for sign in ZODIAC_SIGNS],
        "moon_phases": moon_phases
    })
