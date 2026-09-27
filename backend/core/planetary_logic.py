import argparse
import os
import math
import ephem
import pytz
from datetime import datetime, timedelta, date
from astral import Observer
from astral import sun
from timezonefinder import TimezoneFinder

# Singleton per TimezoneFinder per evitare re-inizializzazioni costose (~0.7s ciascuna)
_tf = TimezoneFinder()

# --- Dati Astrologici Fondamentali ---

PLANETS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
RULERS = {"Sunday": "Sun", "Monday": "Moon", "Tuesday": "Mars", "Wednesday": "Mercury", "Thursday": "Jupiter", "Friday": "Venus", "Saturday": "Saturn"}

ZODIAC_SIGNS = [
    (0, "Ariete"), (30, "Toro"), (60, "Gemelli"), (90, "Cancro"),
    (120, "Leone"), (150, "Vergine"), (180, "Bilancia"), (210, "Scorpione"),
    (240, "Sagittario"), (270, "Capricorno"), (300, "Aquario"), (330, "Pesci")
]

MOON_PHASES = [
    "Luna Nuova", "Luna Crescente", "Primo Quarto", "Gibbosa Crescente",
    "Luna Piena", "Gibbosa Calante", "Ultimo Quarto", "Luna Calante"
]

PHASE_TRANSLATIONS = {
    "new moon": "Luna Nuova",
    "waxing crescent": "Luna Crescente",
    "first quarter": "Primo Quarto",
    "waxing gibbous": "Gibbosa Crescente",
    "full moon": "Luna Piena",
    "waning gibbous": "Gibbosa Calante",
    "last quarter": "Ultimo Quarto",
    "waning crescent": "Luna Calante",
    "luna nuova": "Luna Nuova",
    "luna crescente": "Luna Crescente",
    "primo quarto": "Primo Quarto",
    "gibbosa crescente": "Gibbosa Crescente",
    "luna piena": "Luna Piena",
    "gibbosa calante": "Gibbosa Calante",
    "ultimo quarto": "Ultimo Quarto",
    "luna calante": "Luna Calante",
}

PLANET_TRANSLATIONS = {
    "saturn": "Saturn", "saturno": "Saturn",
    "jupiter": "Jupiter", "giove": "Jupiter",
    "mars": "Mars", "marte": "Mars",
    "sun": "Sun", "sole": "Sun",
    "venus": "Venus", "venere": "Venus",
    "mercury": "Mercury", "mercurio": "Mercury",
    "moon": "Moon", "luna": "Moon"
}


LUNAR_HOUSES = {
    1: {"name": "Alnath", "governor": "Sole", "degrees": "Ariete (0º00’)", "desc": "Favorevole ai viaggi e agli affari commerciali fortunati. Apportatrice di discordia tra marito e moglie, ma anche tra amici ed alleati."},
    2: {"name": "Allothaim", "governor": "Luna", "degrees": "Ariete (12º51’)", "desc": "Favorisce la scoperta dei tesori, lo scavare canali e pozzi. Contrasta i viaggi per mare, la costruzione di nuovi edifici e la guarigione dalle malattie. Procura un eccessiva impulsività."},
    3: {"name": "Alchaomazon", "governor": "Marte", "degrees": "Ariete (25º43’)", "desc": "Favorevole ai viaggi in mare, alle ricerche scientifiche, alle operazioni d’alchimia e ad infondere l’amore tra marito e moglie."},
    4: {"name": "Aldebaran", "governor": "Mercurio", "degrees": "Toro (8º34’)", "desc": "Favorevole a chi desidera catturare o uccidere rettili o altri animali velenosi. Sfavorevole alle proprietà immobiliari, alle città e allo sfruttamento delle miniere. Pone discordia tra marito e moglie."},
    5: {"name": "Alchataya", "governor": "Giove", "degrees": "Toro (21º26’)", "desc": "Favorisce il ritorno dei viaggiatori e l’apprendimento degli studiosi, è favorevole anche ai beni immobili, procura la salute e la benevolenza tra i coniugi. Sfavorevole all’inizio di nuove imprese e alle opere di carità. Distrugge l’amicizia tra due persone."},
    6: {"name": "Alhanna", "governor": "Venere", "degrees": "Gemelli (4º17’)", "desc": "Infonde amicizia tra due alleati, migliora la caccia di animali da terra. Favorisce le guerre mandando in rovina paesi o città, danneggia i raccolti, ostacola le cure mediche, procura sfortuna negli affari finanziari."},
    7: {"name": "Aldimiach", "governor": "Saturno", "degrees": "Gemelli (17º09’)", "desc": "Favorevole al guadagno, ai commerci, ai raccolti, all’amicizia, all’amore e alle guarigioni. Sfavorevole alle questioni riguardanti la giustizia e le leggi."},
    8: {"name": "Alnaza", "governor": "Sole", "degrees": "Cancro (0º00’)", "desc": "Favorisce l’amore e l’amicizia. Rende sicuri i viaggi, fabbricazione di talismani per scacciare topi o cimici. Procura un aumento della sofferenza presso coloro che soffrono già."},
    9: {"name": "Archaam", "governor": "Luna", "degrees": "Cancro (12º51’)", "desc": "Crea ostacoli in coloro che vogliono realizzare azioni malvage. Contraria alle coltivazioni, ai raccolti e ai viaggi, semina la discordia fra gli uomini, inimicizia tra alleati."},
    10: {"name": "Algelioche", "governor": "Marte", "degrees": "Cancro (25º43’)", "desc": "Infonde l’amore tra uomo e donna, rende più solidi gli edifici e ne facilita la realizzazione. Promuove l’amicizia tra associati. Procura la rovina dei nemici, manda in prigione persone innocenti."},
    11: {"name": "Azobra", "governor": "Mercurio", "degrees": "Leone (8º34’)", "desc": "Protegge nei viaggi, libera i prigionieri, aumenta i traffici commerciali e annessi guadagni. Fortifica gli edifici."},
    12: {"name": "Alzarpha", "governor": "Giove", "degrees": "Leone (21º26’)", "desc": "Ottimo momento per l’agricoltura. Contrario ai viaggi per mare. Annuncia discordie, scioperi e ribellioni."},
    13: {"name": "Alhayre", "governor": "Venere", "degrees": "Vergine (4º17’)", "desc": "Propizia all’altruismo e alle opere di carità, favorisce l’agricoltura, i viaggi e i guadagni. Purtroppo i guadagni che se ne ricaveranno passeranno in mano altrui."},
    14: {"name": "Achuret", "governor": "Saturno", "degrees": "Vergine (17º09’)", "desc": "Stimola l’amore fra gli sposi, fa guarire dalle malattie, favorisce gli studi. Favorevole ai viaggi per mare ma contraria ai viaggi terrestri."},
    15: {"name": "Agrapha", "governor": "Sole", "degrees": "Bilancia (0º00’)", "desc": "Influisce positivamente sulla scoperta di tesori e sulle perforazioni dei pozzi. Procura i divorzi e la discordia, distrugge i beni immobili e i nemici, ostacola i viaggiatori."},
    16: {"name": "Azubene", "governor": "Luna", "degrees": "Bilancia (12º51’)", "desc": "Impedisce i viaggi e i matrimoni, reca danno all’agricoltura e ai commerci. Favorevole agli investimenti finaziari."},
    17: {"name": "Alchil", "governor": "Marte", "degrees": "Bilancia (25º43’)", "desc": "Propizia nel cambiare in buona la cattiva sorte, a render duraturo l’amore e sicuri i viaggi sia per mare che per terra."},
    18: {"name": "Alchas", "governor": "Mercurio", "degrees": "Scorpione (8º34’)", "desc": "Provoca le discordie, le ribellioni, le guerre; rende possibile il vendicarsi dei propri nemici. Favorevole ai beni immobili, guarigione da febbre e dolori intestinali."},
    19: {"name": "Allatha", "governor": "Giove", "degrees": "Scorpione (21º26’)", "desc": "Contribuisce a far decadere l’uomo dal posto occupato, è propizia ai viaggi e al commercio con l’estero. Procura nuovi nemici."},
    20: {"name": "Abnahaya", "governor": "Venere", "degrees": "Sagittario (4º17’)", "desc": "Eccellente per addomesticare le bestie feroci. Propizia alle abitazioni, alle costruzioni, ai cambiamenti non voluti di residenza. Sfavorevole alla felicità coniugale."},
    21: {"name": "Abeda", "governor": "Saturno", "degrees": "Sagittario (17º09’)", "desc": "Favorevole all’agricoltura, ai guadagni, ai viaggiatori. Procura discussioni e divorzi in ambito affettivo."},
    22: {"name": "Sadahacha", "governor": "Sole", "degrees": "Capricorno (0º00’)", "desc": "Ottima per la guarigione delle malattie. Sfavorevole ai caratteri deboli e timorosi, favorisce chi è rude o violento."},
    23: {"name": "Sabadola", "governor": "Luna", "degrees": "Capricorno (12º51’)", "desc": "Propizia ai medici, politici, soldati e avvocati. Contraria alle intese commerciali e nuoce ai matrimoni e ai figli."},
    24: {"name": "Sadabath", "governor": "Marte", "degrees": "Capricorno (25º43’)", "desc": "Propizia all’amore coniugale e alle vittorie militari. Contraria a chi occupa delle cariche pubbliche."},
    25: {"name": "Sadalabra", "governor": "Mercurio", "degrees": "Aquario (8º34’)", "desc": "Asseconda la vendetta, è malefica per i matrimoni ed i parti. Favorisce le guarigioni."},
    26: {"name": "Alpharg", "governor": "Giove", "degrees": "Aquario (21º26’)", "desc": "Contribuisce all’accoppiamento e al diletto umano. Favorevole ai matrimoni, ai trasporti, all’agricoltura ma è sfavorevole ai viaggi via mare."},
    27: {"name": "Alcharya", "governor": "Venere", "degrees": "Pesci (4º17’)", "desc": "Propizia all’agricoltura, commerci, guadagni, guarire le malattie. Contraria ai beni immobili, eredità, prestiti di denaro."},
    28: {"name": "Albotham", "governor": "Saturno", "degrees": "Pesci (17º09’)", "desc": "Favorevole all’agricoltura e al commercio, preserva i viaggiatori dai pericoli, contribuisce all’amore. Sfavorevole ai malati."},
}

# --- Funzioni di Calcolo con PyEphem ---

def _normalize_time(dt, tz):
    """Normalizza un datetime rispetto a un fuso orario pytz per gestire cambi ora legale (DST)."""
    if hasattr(tz, 'normalize'):
        try:
            return tz.normalize(dt)
        except Exception:
            pass
    return dt

def get_planet_position_status(observer, planet_name, calculation_time):
    """Calcola se un pianeta è sopra o sotto l'orizzonte."""
    try:
        # Imposta la data e l'ora dell'osservatore
        observer.date = ephem.Date(calculation_time)
        
        # Crea l'oggetto del pianeta corretto
        # PyEphem si aspetta nomi inglesi capitalizzati, es. "Mars", "Jupiter"
        planet_object = getattr(ephem, planet_name)()
        planet_object.compute(observer)
        
        # Controlla l'altitudine (in radianti). Positiva = sopra l'orizzonte.
        if planet_object.alt > 0:
            return "&#x2713;"
        else:
            return ""
    except Exception:
        # Gestisce casi in cui il nome del pianeta non è valido o altri errori
        return "N/D"


def is_moon_visible(observer, calculation_time):
    """Calcola se la Luna è sopra l'orizzonte."""
    try:
        observer.date = ephem.Date(calculation_time)
        moon = ephem.Moon()
        moon.compute(observer)
        return moon.alt > 0
    except Exception:
        return False


def get_zodiac_sign(current_date: date, calc_time: datetime = None) -> str:
    """Calcola il segno zodiacale basandosi sulla posizione del Sole usando PyEphem."""
    try:
        sun_ephem = ephem.Sun()
        if calc_time:
            utc_time = calc_time.astimezone(pytz.utc) if calc_time.tzinfo else calc_time
            sun_ephem.compute(ephem.Date(utc_time))
        else:
            sun_ephem.compute(current_date)
        ecliptic_coords = ephem.Ecliptic(sun_ephem)
        lon_radians = float(ecliptic_coords.lon)
        lon_degrees = (math.degrees(lon_radians) % 360.0) % 360.0
        
        for lon_deg, sign in reversed(ZODIAC_SIGNS):
            if lon_degrees >= lon_deg:
                return sign
    except Exception as e:
        print(f"ERROR in get_zodiac_sign: {e}")
        return "Unknown"
    return "Unknown"

def get_moon_phase(current_date: date, observer: ephem.Observer = None, local_tz = None) -> dict:
    """Calcola la fase lunare, l'età della luna (giorni, ore, minuti) e il giorno lunare."""
    try:
        # Usiamo le 22:30 nel fuso orario locale specificato
        dt_naive = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=22, minutes=30)
        if local_tz:
            if isinstance(local_tz, str):
                local_tz = pytz.timezone(local_tz)
            if hasattr(local_tz, 'localize'):
                dt_aware = local_tz.localize(dt_naive)
            else:
                dt_aware = dt_naive.replace(tzinfo=local_tz)
            ephem_date = ephem.Date(dt_aware.astimezone(pytz.utc))
        else:
            ephem_date = ephem.Date(dt_naive)
        
        moon_ephem = ephem.Moon()
        
        # Se abbiamo un osservatore, usiamo la sua posizione per calcolare la visibilità
        is_visible = False
        if observer:
            observer.date = ephem_date
            moon_ephem.compute(observer)
            is_visible = moon_ephem.alt > 0
        else:
            moon_ephem.compute(ephem_date)
        
        illumination = moon_ephem.phase

        # Calcolo astronomico della fase basato sull'elongazione eclittica (continua e priva di salti)
        sun_ephem = ephem.Sun(ephem_date)
        ecl_sun = ephem.Ecliptic(sun_ephem)
        ecl_moon = ephem.Ecliptic(moon_ephem)
        elongation = (math.degrees(float(ecl_moon.lon) - float(ecl_sun.lon))) % 360.0
        lunation = elongation / 360.0

        if 0 <= lunation < 0.03 or 0.97 <= lunation <= 1.0: phase_name = "Luna Nuova"
        elif 0.03 <= lunation < 0.22: phase_name = "Luna Crescente"
        elif 0.22 <= lunation < 0.28: phase_name = "Primo Quarto"
        elif 0.28 <= lunation < 0.47: phase_name = "Gibbosa Crescente"
        elif 0.47 <= lunation < 0.53: phase_name = "Luna Piena"
        elif 0.53 <= lunation < 0.72: phase_name = "Gibbosa Calante"
        elif 0.72 <= lunation < 0.78: phase_name = "Ultimo Quarto"
        elif 0.78 <= lunation < 0.97: phase_name = "Luna Calante"
        else: phase_name = "Sconosciuta"

        # Calcolo Età della Luna (Giorni, Ore, Minuti)
        pnm = ephem.previous_new_moon(ephem_date)
        nnm = ephem.next_new_moon(ephem_date)
        # Se ephem.previous_new_moon ha saltato il novilunio in corso (intervallo > 35 giorni):
        if (nnm - pnm) > 35:
            pnm = ephem.previous_new_moon(ephem_date + 0.1)

        age_days_raw = max(0.0, float(ephem_date - pnm))
        days = int(age_days_raw)
        hours_raw = (age_days_raw - days) * 24
        hours = int(hours_raw)
        minutes = int((hours_raw - hours) * 60)
        lunar_age_str = f"{days}g {hours}h {minutes}m"

        # Calcolo Giorno Lunare (intero 1-30) e Pianeta Associato
        lunar_day = max(1, int(age_days_raw) + 1)
        
        # Sequenza pianeti: Sole, Marte, Giove, Saturno, Luna, Mercurio, Venere
        lunar_planets = ["Sole", "Marte", "Giove", "Saturno", "Luna", "Mercurio", "Venere"]
        lunar_day_planet = lunar_planets[(lunar_day - 1) % 7]

        # Calcolo Casa Lunare (1-28) basato sulla longitudine eclittica della Luna
        lon_deg = (math.degrees(float(ecl_moon.lon)) % 360.0) % 360.0
        house_num = (int(lon_deg / (360.0 / 28.0)) % 28) + 1
        lunar_house = LUNAR_HOUSES.get(house_num, {"name": "N/D", "desc": "", "governor": "N/D", "degrees": "N/D"})

        # Calcolo gradi esatti nel segno per la UI
        sign_index = int(lon_deg / 30.0) % 12
        sign_name = ZODIAC_SIGNS[sign_index][1]
        deg_in_sign = lon_deg % 30.0
        minutes_in_sign = (deg_in_sign - int(deg_in_sign)) * 60.0
        moon_lon_str = f"{sign_name} {int(deg_in_sign)}°{int(minutes_in_sign):02d}'"

        return {
            "phase": phase_name,
            "illumination": round(illumination, 1),
            "lunar_age": lunar_age_str,
            "lunar_day": lunar_day,
            "lunar_day_planet": lunar_day_planet,
            "lunar_house": lunar_house,
            "is_visible": is_visible,
            "moon_longitude": moon_lon_str
        }
    except Exception as e:
        print(f"ERROR in get_moon_phase: {e}")
        return {
            "phase": "Sconosciuta", 
            "illumination": 0,
            "lunar_age": "N/D",
            "lunar_day": "N/D", 
            "lunar_day_planet": "N/D", 
            "lunar_house": {"name": "N/D", "desc": "", "governor": "N/D", "degrees": "N/D"},
            "is_visible": False,
            "moon_longitude": "N/D",
            "error": str(e)
        }

def calculate_planetary_hours(calculation_date: date, latitude: float, longitude: float, elevation: float) -> dict:
    """
    Calcola le ore planetarie per una data e una posizione geografica specifiche.
    """
    try:
        # 1. Trova il fuso orario corretto per le coordinate date
        timezone_str = _tf.timezone_at(lng=longitude, lat=latitude)
        if not timezone_str:
            # Fallback a UTC se il fuso orario non viene trovato
            timezone_str = "UTC"
        local_tz = pytz.timezone(timezone_str)

        # 2. Setup degli osservatori
        # Astral observer con fuso orario locale
        astral_observer = Observer(latitude=latitude, longitude=longitude, elevation=elevation)
        
        # PyEphem observer (lavora in UTC, quindi non necessita di fuso orario)
        ephem_observer = ephem.Observer()
        ephem_observer.lat = str(latitude)
        ephem_observer.lon = str(longitude)
        ephem_observer.elevation = float(elevation)
        ephem_observer.pressure = 0
        ephem_observer.horizon = '0'

        # 3. Calcolo alba e tramonto con Astral nel fuso orario locale
        sun_times = sun.sun(astral_observer, date=calculation_date, tzinfo=local_tz)
        sunrise = sun_times["sunrise"]
        sunset = sun_times["sunset"]
        
        # Per la durata della notte, serve l'alba del giorno dopo
        tomorrow = calculation_date + timedelta(days=1)
        sun_times_tomorrow = sun.sun(astral_observer, date=tomorrow, tzinfo=local_tz)
        sunrise_tomorrow = sun_times_tomorrow["sunrise"]

        # 4. Calcolo durata ore diurne e notturne
        day_duration = sunset - sunrise
        night_duration = sunrise_tomorrow - sunset
        
        day_hour_duration = day_duration / 12
        night_hour_duration = night_duration / 12

        # 5. Determinare il pianeta reggente del giorno
        day_of_week = calculation_date.strftime("%A")
        first_hour_planet = RULERS[day_of_week]
        
        # Trova l'indice di partenza nell'ordine Caldeo
        start_index = PLANETS.index(first_hour_planet)
        
        planetary_hours = []
        
        # 6. Calcolo ore diurne
        current_time = sunrise
        for i in range(12):
            planet_name = PLANETS[(start_index + i) % 7]
            hour_start = _normalize_time(current_time, local_tz)
            hour_midpoint = _normalize_time(current_time + (day_hour_duration / 2), local_tz)
            
            # Per PyEphem, usiamo l'orario convertito in UTC
            position_status = get_planet_position_status(ephem_observer, planet_name, hour_midpoint.astimezone(pytz.utc))
            moon_visible = is_moon_visible(ephem_observer, hour_midpoint.astimezone(pytz.utc))
            
            planetary_hours.append({
                "hour": i + 1,
                "type": "Day",
                "start_time": hour_start.isoformat(),
                "planet": planet_name,
                "planet_position_status": position_status,
                "is_moon_visible": moon_visible
            })
            current_time += day_hour_duration

        # 7. Calcolo ore notturne
        current_time = sunset
        for i in range(12):
            planet_name = PLANETS[(start_index + 12 + i) % 7]
            hour_start = _normalize_time(current_time, local_tz)
            hour_midpoint = _normalize_time(current_time + (night_hour_duration / 2), local_tz)
            
            # Per PyEphem, usiamo l'orario convertito in UTC
            position_status = get_planet_position_status(ephem_observer, planet_name, hour_midpoint.astimezone(pytz.utc))
            moon_visible = is_moon_visible(ephem_observer, hour_midpoint.astimezone(pytz.utc))

            planetary_hours.append({
                "hour": i + 13,
                "type": "Night",
                "start_time": hour_start.isoformat(),
                "planet": planet_name,
                "planet_position_status": position_status,
                "is_moon_visible": moon_visible
            })
            current_time += night_hour_duration
            
        # 8. Calcolo dati aggiuntivi
        zodiac_sign = get_zodiac_sign(calculation_date, calc_time=sunrise)
        moon_phase_info = get_moon_phase(calculation_date, ephem_observer, local_tz=local_tz)

        return {
            "date": calculation_date.isoformat(),
            "location": {"latitude": latitude, "longitude": longitude, "elevation": elevation, "timezone": timezone_str},
            "sun_info": {
                "sunrise": sunrise.isoformat(),
                "sunset": sunset.isoformat()
            },
            "durations": {
                "day_hour_seconds": day_hour_duration.total_seconds(),
                "night_hour_seconds": night_hour_duration.total_seconds()
            },
            "zodiac_sign": zodiac_sign,
            "moon_phase": moon_phase_info,
            "planetary_hours": planetary_hours
        }

    except Exception as e:
        # Aggiungiamo un log più dettagliato in caso di errore
        print(f"Error in calculate_planetary_hours: {e} at line {e.__traceback__.tb_lineno}")
        return {"error": "An error occurred during calculation. This might be due to the location being in a polar region where the sun does not set or rise."}

def search_planetary_hours(lat, lon, alt, planet=None, sign=None, moon_phase=None, location_name=""):
    """
    Cerca le ore planetarie che corrispondono ai criteri specificati nei prossimi 30 giorni.
    Supporta filtri sia in italiano che in inglese.
    """
    today = date.today()
    one_year_from_now = today + timedelta(days=30)
    current_date = today
    
    # Normalizza i criteri di ricerca per supportare sia italiano che inglese
    norm_moon_phase = None
    if moon_phase:
        norm_moon_phase = PHASE_TRANSLATIONS.get(moon_phase.strip().lower(), moon_phase.strip())
        
    norm_planet = None
    if planet:
        norm_planet = PLANET_TRANSLATIONS.get(planet.strip().lower(), planet.strip())

    norm_sign = sign.strip() if sign else None

    found_hours = []

    while current_date < one_year_from_now:
        daily_data = calculate_planetary_hours(current_date, lat, lon, alt)
        
        if "error" in daily_data:
            # Salta i giorni con errori (es. regioni polari)
            current_date += timedelta(days=1)
            continue

        # Controlla le condizioni a livello giornaliero (segno, fase lunare)
        sign_match = (not norm_sign) or (daily_data.get('zodiac_sign') == norm_sign)
        moon_match = (not norm_moon_phase) or (daily_data.get('moon_phase', {}).get('phase') == norm_moon_phase)

        if sign_match and moon_match:
            # Se le condizioni giornaliere sono soddisfatte, controlla le ore
            for hour in daily_data['planetary_hours']:
                planet_match = (not norm_planet) or (hour.get('planet') == norm_planet)
                
                if planet_match:
                    # Determina la durata corretta per l'ora trovata
                    duration_seconds = 0
                    if hour['type'] == 'Day':
                        duration_seconds = daily_data['durations']['day_hour_seconds']
                    else: # Night
                        duration_seconds = daily_data['durations']['night_hour_seconds']

                    # Se anche la condizione oraria è soddisfatta, aggiungi ai risultati
                    found_hours.append({
                        "date": daily_data['date'],
                        "start_time": hour['start_time'],
                        "planet": hour['planet'],
                        "type": hour['type'],
                        "duration_seconds": duration_seconds,
                        "zodiac_sign": daily_data.get('zodiac_sign'),
                        "moon_phase": daily_data.get('moon_phase'),
                        "planet_position_status": hour.get('planet_position_status', 'N/D'),
                        "is_moon_visible": hour.get('is_moon_visible', False),
                        "search_location_data": { # Add location data here
                            "latitude": lat,
                            "longitude": lon,
                            "elevation": alt,
                            "name": location_name
                        }
                    })
        
        current_date += timedelta(days=1)
        
    return found_hours

