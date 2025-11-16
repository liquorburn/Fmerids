import { getLocations, saveLocation, updateLocation, deleteLocation } from './apiService.js';

// --- Elementi del DOM ---
const latInput = document.getElementById('lat');
const lonInput = document.getElementById('lon');
const altInput = document.getElementById('alt');

// Elementi per la gestione dei luoghi
const locationNameInput = document.getElementById('location-name');
const savedLocationsSelect = document.getElementById('saved-locations');
const saveLocationBtn = document.getElementById('btn-save-location');
const updateLocationBtn = document.getElementById('btn-update-location');
const deleteLocationBtn = document.getElementById('btn-delete-location');

// Elementi del form di ricerca (per la sincronizzazione)
const latSearchInput = document.getElementById('lat_search');
const lonSearchInput = document.getElementById('lon_search');


// --- Logica di Gestione Luoghi (Client-Side) ---

/**
 * Popola il menu a tendina dei luoghi salvati.
 * @param {object} locations - Un oggetto dove le chiavi sono i nomi dei luoghi.
 */
function populateLocations(locations) {
    savedLocationsSelect.innerHTML = '<option selected disabled>Carica un luogo...</option>';
    for (const name in locations) {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        savedLocationsSelect.appendChild(option);
    }
}

/**
 * Carica i luoghi dal backend e popola il menu a tendina.
 */
async function loadLocations() {
    try {
        const locations = await getLocations();
        populateLocations(locations);
    } catch (error) {
        console.error("Impossibile caricare i luoghi:", error);
        alert("Non è stato possibile caricare i luoghi salvati.");
    }
}

/**
 * Gestisce il salvataggio di un nuovo luogo.
 */
async function handleSaveLocation() {
    const name = locationNameInput.value.trim();
    const locationData = {
        lat: latInput.value,
        lon: lonInput.value,
        alt: altInput.value
    };

    if (!name || !locationData.lat || !locationData.lon) {
        alert("Per salvare un luogo, inserisci un nome, una latitudine e una longitudine.");
        return;
    }

    try {
        await saveLocation(name, locationData);
        locationNameInput.value = ''; // Pulisci l'input
        await loadLocations(); // Ricarica la lista
        alert(`Luogo "${name}" salvato con successo!`);
    } catch (error) {
        alert(`Errore nel salvataggio: ${error.message}`);
    }
}

/**
 * Gestisce l'aggiornamento di un luogo esistente.
 */
async function handleUpdateLocation() {
    const name = savedLocationsSelect.value;
    if (!name || name === 'Carica un luogo...') {
        alert("Seleziona un luogo da aggiornare.");
        return;
    }
    
    const locationData = {
        lat: latInput.value,
        lon: lonInput.value,
        alt: altInput.value
    };

    try {
        await updateLocation(name, locationData);
        await loadLocations();
        alert(`Luogo "${name}" aggiornato con successo!`);
    } catch (error) {
        alert(`Errore nell'aggiornamento: ${error.message}`);
    }
}

/**
 * Gestisce la cancellazione di un luogo.
 */
async function handleDeleteLocation() {
    const name = savedLocationsSelect.value;
    if (!name || name === 'Carica un luogo...') {
        alert("Seleziona un luogo da cancellare.");
        return;
    }

    if (!confirm(`Sei sicuro di voler eliminare il luogo "${name}"?`)) {
        return;
    }

    try {
        await deleteLocation(name);
        locationNameInput.value = '';
        latInput.value = '';
        lonInput.value = '';
        altInput.value = '0';
        await loadLocations();
        alert(`Luogo "${name}" eliminato.`);
    } catch (error) {
        alert(`Errore nella cancellazione: ${error.message}`);
    }
}

/**
 * Carica i dati di un luogo selezionato nei campi del form.
 */
async function handleLoadSelectedLocation() {
    const name = savedLocationsSelect.value;
    if (!name || name === 'Carica un luogo...') return;

    try {
        const locations = await getLocations();
        const location = locations[name];
        if (location) {
            locationNameInput.value = name;
            latInput.value = location.lat;
            lonInput.value = location.lon;
            altInput.value = location.alt;
            // Aggiorna anche i campi nascosti della ricerca
            if(latSearchInput) latSearchInput.value = location.lat;
            if(lonSearchInput) lonSearchInput.value = location.lon;
        }
    } catch (error) {
        alert(`Impossibile caricare i dati per "${name}": ${error.message}`);
    }
}

/**
 * Sincronizza i valori di lat/lon del form principale con i campi nascosti del form di ricerca.
 */
function syncSearchCoords() {
    if(latSearchInput) latSearchInput.value = latInput.value;
    if(lonSearchInput) lonSearchInput.value = lonInput.value;
}


// --- Event Listeners ---

// Listeners per la gestione dei luoghi
if (saveLocationBtn) saveLocationBtn.addEventListener('click', handleSaveLocation);
if (updateLocationBtn) updateLocationBtn.addEventListener('click', handleUpdateLocation);
if (deleteLocationBtn) deleteLocationBtn.addEventListener('click', handleDeleteLocation);
if (savedLocationsSelect) savedLocationsSelect.addEventListener('change', handleLoadSelectedLocation);

// Listeners per sincronizzare le coordinate per la ricerca
if (latInput) latInput.addEventListener('input', syncSearchCoords);
if (lonInput) lonInput.addEventListener('input', syncSearchCoords);


// --- Inizializzazione dell'Applicazione ---

/**
 * Funzione di avvio eseguita al caricamento completo del DOM.
 */
function initializeApp() {
    // La data di oggi è impostata dal backend se non già presente
    const dateInput = document.getElementById('date');
    if (!dateInput.value) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }

    // Carica i luoghi salvati (l'unica operazione asincrona necessaria all'avvio)
    loadLocations();

    // Sincronizza le coordinate una volta al caricamento
    syncSearchCoords();
}

// Avvia l'applicazione quando il DOM è pronto
document.addEventListener('DOMContentLoaded', initializeApp);
