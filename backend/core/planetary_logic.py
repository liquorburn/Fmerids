import argparse
import os
import math
import ephem
from datetime import datetime, timedelta, date
from astral import Observer
from astral import sun

# --- Dati Astrologici Fondamentali ---

PLANETS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
RULERS = {"Sunday": "Sun", "Monday": "Moon", "Tuesday": "Mars", "Wednesday": "Mercury", "Thursday": "Jupiter", "Friday": "Venus", "Saturday": "Saturn"}

ZODIAC_SIGNS = [
    (0, "Aries"), (30, "Taurus"), (60, "Gemini"), (90, "Cancer"),
    (120, "Leo"), (150, "Virgo"), (180, "Libra"), (210, "Scorpio"),
    (240, "Sagittarius"), (270, "Capricorn"), (300, "Aquarius"), (330, "Pisces")
]

# --- Funzioni di Calcolo con PyEphem ---

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
            return "-"
    except (AttributeError, TypeError):
        # Gestisce casi in cui il nome del pianeta non è valido o altri errori
        return "N/D"


def get_zodiac_sign(current_date: date) -> str:
    """Calcola il segno zodiacale basandosi sulla posizione del Sole usando PyEphem."""
    try:
        sun_ephem = ephem.Sun()
        sun_ephem.compute(current_date)
        ecliptic_coords = ephem.Ecliptic(sun_ephem)
        lon_radians = ecliptic_coords.lon
        lon_degrees = math.degrees(lon_radians)
        
        for lon_deg, sign in reversed(ZODIAC_SIGNS):
            if lon_degrees >= lon_deg:
                return sign
    except Exception as e:
        print(f"ERROR in get_zodiac_sign: {e}")
        return "Unknown"
    return "Unknown"

def get_moon_phase(current_date: date) -> dict:
    """Calcola la fase lunare e l'illuminazione usando PyEphem."""
    try:
        moon_ephem = ephem.Moon()
        moon_ephem.compute(current_date)
        
        illumination = moon_ephem.phase

        # Calcolo del nome della fase basato sulla lunazione
        ephem_date = ephem.Date(current_date)
        pnm = ephem.previous_new_moon(ephem_date)
        nnm = ephem.next_new_moon(ephem_date)
        lunation = (ephem_date - pnm) / (nnm - pnm)

        if 0 <= lunation < 0.03 or 0.97 <= lunation <= 1: phase_name = "New Moon"
        elif 0.03 <= lunation < 0.22: phase_name = "Waxing Crescent"
        elif 0.22 <= lunation < 0.28: phase_name = "First Quarter"
        elif 0.28 <= lunation < 0.47: phase_name = "Waxing Gibbous"
        elif 0.47 <= lunation < 0.53: phase_name = "Full Moon"
        elif 0.53 <= lunation < 0.72: phase_name = "Waning Gibbous"
        elif 0.72 <= lunation < 0.78: phase_name = "Last Quarter"
        elif 0.78 <= lunation < 0.97: phase_name = "Waning Crescent"
        else: phase_name = "Unknown"

        return {"phase": phase_name, "illumination": round(illumination, 2)}
    except Exception as e:
        print(f"ERROR in get_moon_phase: {e}")
        return {"phase": "Unknown", "illumination": 0, "error": str(e)}

def calculate_planetary_hours(calculation_date: date, latitude: float, longitude: float, elevation: float) -> dict:
    """
    Calcola le ore planetarie per una data e una posizione geografica specifiche.
    """
    try:
        # 1. Setup degli osservatori
        astral_observer = Observer(latitude=latitude, longitude=longitude, elevation=elevation)
        
        ephem_observer = ephem.Observer()
        ephem_observer.lat = str(latitude)
        ephem_observer.lon = str(longitude)
        ephem_observer.elevation = float(elevation)
        ephem_observer.pressure = 0
        ephem_observer.horizon = '0'

        # 2. Calcolo alba e tramonto con Astral
        sun_times = sun.sun(astral_observer, date=calculation_date)
        sunrise = sun_times["sunrise"]
        sunset = sun_times["sunset"]
        
        # Per la durata della notte, serve l'alba del giorno dopo
        tomorrow = calculation_date + timedelta(days=1)
        sun_times_tomorrow = sun.sun(astral_observer, date=tomorrow)
        sunrise_tomorrow = sun_times_tomorrow["sunrise"]

        # 3. Calcolo durata ore diurne e notturne
        day_duration = sunset - sunrise
        night_duration = sunrise_tomorrow - sunset
        
        day_hour_duration = day_duration / 12
        night_hour_duration = night_duration / 12

        # 4. Determinare il pianeta reggente del giorno
        day_of_week = calculation_date.strftime("%A")
        first_hour_planet = RULERS[day_of_week]
        
        # Trova l'indice di partenza nell'ordine Caldeo
        start_index = PLANETS.index(first_hour_planet)
        
        planetary_hours = []
        
        # 5. Calcolo ore diurne
        current_time = sunrise
        for i in range(12):
            planet_name = PLANETS[(start_index + i) % 7]
            hour_midpoint = current_time + (day_hour_duration / 2)
            position_status = get_planet_position_status(ephem_observer, planet_name, hour_midpoint)
            
            planetary_hours.append({
                "hour": i + 1,
                "type": "Day",
                "start_time": current_time.isoformat(),
                "planet": planet_name,
                "planet_position_status": position_status
            })
            current_time += day_hour_duration

        # 6. Calcolo ore notturne
        current_time = sunset
        for i in range(12):
            planet_name = PLANETS[(start_index + 12 + i) % 7]
            hour_midpoint = current_time + (night_hour_duration / 2)
            position_status = get_planet_position_status(ephem_observer, planet_name, hour_midpoint)

            planetary_hours.append({
                "hour": i + 13,
                "type": "Night",
                "start_time": current_time.isoformat(),
                "planet": planet_name,
                "planet_position_status": position_status
            })
            current_time += night_hour_duration
            
        # 7. Calcolo dati aggiuntivi
        zodiac_sign = get_zodiac_sign(calculation_date)
        moon_phase_info = get_moon_phase(calculation_date)

        return {
            "date": calculation_date.isoformat(),
            "location": {"latitude": latitude, "longitude": longitude},
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
        print(f"Error in calculate_planetary_hours: {e}")
        return {"error": "An error occurred during calculation. This might be due to the location being in a polar region where the sun does not set or rise."}

def search_planetary_hours(lat, lon, alt, planet=None, sign=None, moon_phase=None):
    """
    Cerca le ore planetarie che corrispondono ai criteri specificati in un anno.
    """
    today = date.today()
    one_year_from_now = today + timedelta(days=365)
    current_date = today
    
    found_hours = []

    while current_date < one_year_from_now:
        daily_data = calculate_planetary_hours(current_date, lat, lon, alt)
        
        if "error" in daily_data:
            # Salta i giorni con errori (es. regioni polari)
            current_date += timedelta(days=1)
            continue

        # Controlla le condizioni a livello giornaliero (segno, fase lunare)
        sign_match = (not sign) or (daily_data.get('zodiac_sign') == sign)
        moon_match = (not moon_phase) or (daily_data.get('moon_phase', {}).get('phase') == moon_phase)

        if sign_match and moon_match:
            # Se le condizioni giornaliere sono soddisfatte, controlla le ore
            for hour in daily_data['planetary_hours']:
                planet_match = (not planet) or (hour.get('planet') == planet)
                
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
                        "moon_phase": daily_data.get('moon_phase', {}).get('phase'),
                        "planet_position_status": hour.get('planet_position_status', 'N/D')
                    })
        
        current_date += timedelta(days=1)
        
    return found_hours
