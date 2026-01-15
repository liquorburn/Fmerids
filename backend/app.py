import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime

# Importa la logica di business e le costanti
from core.planetary_logic import calculate_planetary_hours, search_planetary_hours, PLANETS, ZODIAC_SIGNS
from core.locations_logic import get_all_locations, create_location, delete_location, update_location

# Importa i vecchi blueprint per mantenerli temporaneamente
from api.routes import api_bp
from api.locations_routes import locations_bp

def create_app():
    """
    Crea e configura l'istanza dell'applicazione Flask.
    """
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Configurazioni da variabili d'ambiente per la produzione
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')
    
    # CORS è ancora utile per l'API di gestione dei luoghi che rimane asincrona
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Manteniamo le vecchie API per ora, ma la nuova logica sarà gestita da route principali
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(locations_bp, url_prefix='/api/locations')

    # --- Filtri Jinja2 personalizzati ---
    def format_date_filter(iso_date):
        """Formatta una data ISO in un formato leggibile."""
        d = datetime.fromisoformat(iso_date).date()
        return d.strftime('%A, %d %B %Y')

    def format_time_filter(iso_string):
        """Formatta un orario ISO in HH:MM:SS."""
        if not iso_string: return ''
        return datetime.fromisoformat(iso_string).strftime('%H:%M:%S')

    def format_duration_filter(total_seconds):
        """Formatta una durata in secondi nel formato mm:ss."""
        if not isinstance(total_seconds, (int, float)): return 'N/A'
        minutes = int(total_seconds / 60)
        seconds = int(total_seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    app.jinja_env.filters['format_date'] = format_date_filter
    app.jinja_env.filters['format_time'] = format_time_filter
    app.jinja_env.filters['format_duration'] = format_duration_filter
    # --- Fine Filtri ---


    def get_render_context():
        """Helper per ottenere il contesto comune per il rendering dei template."""
        locations = get_all_locations()
        moon_phases = [
            "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
            "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"
        ]
        metadata = {
            "planets": PLANETS,
            "zodiac_signs": [sign[1] for sign in ZODIAC_SIGNS],
            "moon_phases": moon_phases
        }
        return {"locations": locations, "metadata": metadata}

    @app.route('/')
    def index():
        """
        Serve la pagina principale dell'applicazione.
        """
        context = get_render_context()
        return render_template('index.html', **context)

    @app.route('/calculate', methods=['POST'])
    def calculate():
        """
        Gestisce il calcolo giornaliero e renderizza i risultati nella pagina principale.
        """
        context = get_render_context()
        try:
            date_str = request.form.get('date')
            lat = float(request.form.get('lat'))
            lon = float(request.form.get('lon'))
            alt = float(request.form.get('alt', 0))
            location_name = request.form.get('location_name', '') # Read the location name
            
            context.update({
                "date": date_str,
                "lat": lat,
                "lon": lon,
                "alt": alt,
                "location_name": location_name # Add location name to context
            })

            calc_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            results = calculate_planetary_hours(
                calculation_date=calc_date,
                latitude=lat,
                longitude=lon,
                elevation=alt
            )
            # Add location_name to results for daily_results.html
            results['location_name'] = location_name if location_name else f"Lat: {lat:.4f}, Lon: {lon:.4f}, Alt: {alt:.0f}m"
            context['results'] = results
        except (ValueError, TypeError) as e:
            context['error'] = f"Dati non validi: {e}"

        return render_template('index.html', **context)

    @app.route('/search', methods=['GET'])
    def search():
        """
        Gestisce la ricerca avanzata con paginazione e renderizza i risultati.
        """
        context = get_render_context()
        # Inizializza sempre search_results per garantire che il template si comporti correttamente
        context['search_results'] = {
            "results_for_page": [], "total_results": 0, "total_pages": 1,
            "current_page": 1, "items_per_page": 15
        }
        
        try:
            # Parametri di paginazione
            page = request.args.get('page', 1, type=int)
            items_per_page = request.args.get('items_per_page', 15, type=int)
            context['search_results']['items_per_page'] = items_per_page

            # Parametri di ricerca
            planet = request.args.get('planet')
            sign = request.args.get('sign')
            moon_phase = request.args.get('moon_phase')
            
            # Coordinate (devono essere fornite per la ricerca)
            lat = request.args.get('lat', type=float)
            lon = request.args.get('lon', type=float)
            alt = request.args.get('alt', type=float) # Get alt from request.args
            location_name = request.args.get('location_name', '') # Get location_name from request.args

            if lat is None or lon is None:
                context['error'] = "Latitudine e Longitudine sono obbligatorie per la ricerca."
                return render_template('index.html', **context)
            
            # If alt is None, default to 0
            if alt is None:
                alt = 0

            # Se non è stato specificato nessun criterio, non eseguire la ricerca
            if not any([planet, sign, moon_phase]):
                 context['error'] = "Seleziona almeno un criterio di ricerca."
                 return render_template('index.html', **context)

            all_results = search_planetary_hours(
                lat=lat,
                lon=lon,
                alt=alt, # Pass alt to search_planetary_hours
                planet=planet or None,
                sign=sign or None,
                moon_phase=moon_phase or None,
                location_name=location_name # Pass location_name to search_planetary_hours
            )
            
            total_results = len(all_results)
            total_pages = (total_results + items_per_page - 1) // items_per_page or 1
            
            start = (page - 1) * items_per_page
            end = start + items_per_page
            results_for_page = all_results[start:end]

            context['search_results'].update({
                "results_for_page": results_for_page,
                "total_results": total_results,
                "total_pages": total_pages,
                "current_page": page,
            })

        except (ValueError, TypeError) as e:
            context['error'] = f"Dati di ricerca non validi: {e}"

        return render_template('index.html', **context)


    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
