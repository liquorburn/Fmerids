// --- Gestore LocalStorage ---

const STORAGE_KEY = 'fmerids_saved_locations';

/**
 * Legge i luoghi salvati dal LocalStorage.
 * @returns {Object} Dizionario dei luoghi { nome: { lat, lon, alt } }
 */
function getLocationsFromStorage() {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : {};
}

/**
 * Salva i luoghi nel LocalStorage.
 * @param {Object} locations - Dizionario dei luoghi
 */
function saveLocationsToStorage(locations) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(locations));
}

/**
 * Aggiunge o aggiorna un luogo.
 * @param {string} name 
 * @param {Object} data { lat, lon, alt }
 */
function saveLocationLocal(name, data) {
    const locations = getLocationsFromStorage();
    locations[name] = data;
    saveLocationsToStorage(locations);
}

/**
 * Rimuove un luogo.
 * @param {string} name 
 */
function deleteLocationLocal(name) {
    const locations = getLocationsFromStorage();
    if (locations[name]) {
        delete locations[name];
        saveLocationsToStorage(locations);
    }
}

// --- Elementi del DOM ---
const latInput = document.getElementById('lat');
const lonInput = document.getElementById('lon');
const altInput = document.getElementById('alt');
const locationNameInputHidden = document.getElementById('location_name');

// Elementi per la gestione dei luoghi
const locationNameInput = document.getElementById('location-name');
const savedLocationsSelect = document.getElementById('saved-locations');
const saveLocationBtn = document.getElementById('btn-save-location');
const updateLocationBtn = document.getElementById('btn-update-location');
const deleteLocationBtn = document.getElementById('btn-delete-location');

// Elementi del form di ricerca (per la sincronizzazione)
const latSearchInput = document.getElementById('lat_search');
const lonSearchInput = document.getElementById('lon_search');
const altSearchInput = document.getElementById('alt_search');
const locationNameSearchInput = document.getElementById('location_name_search');

/**
 * Carica i luoghi dal LocalStorage e popola la select.
 */
function loadLocations() {
    const locations = getLocationsFromStorage();
    
    // Salva l'opzione attualmente selezionata per tentare di ripristinarla
    const currentSelection = savedLocationsSelect.value;

    // Pulisci la select mantenendo l'opzione di default
    savedLocationsSelect.innerHTML = '<option selected disabled>Carica un luogo...</option>';

    // Ordina i nomi alfabeticamente
    const sortedNames = Object.keys(locations).sort((a, b) => a.localeCompare(b));

    sortedNames.forEach(name => {
        const data = locations[name];
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        option.dataset.lat = data.lat;
        option.dataset.lon = data.lon;
        option.dataset.alt = data.alt;
        savedLocationsSelect.appendChild(option);
    });

    // Se il luogo selezionato esiste ancora, riselezionalo
    if (locations[currentSelection]) {
        savedLocationsSelect.value = currentSelection;
    }
}

/**
 * Gestisce il salvataggio di un nuovo luogo.
 */
function handleSaveLocation() {
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
        saveLocationLocal(name, locationData);
        locationNameInput.value = ''; // Pulisci l'input
        loadLocations(); // Ricarica la lista
        // Seleziona automaticamente il nuovo luogo
        savedLocationsSelect.value = name;
        alert(`Luogo "${name}" salvato con successo (nel browser)!`);
    } catch (error) {
        alert(`Errore nel salvataggio: ${error.message}`);
    }
}

/**
 * Gestisce l'aggiornamento di un luogo esistente.
 */
function handleUpdateLocation() {
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
        saveLocationLocal(name, locationData); // Sovrascrive
        loadLocations();
        alert(`Luogo "${name}" aggiornato con successo!`);
    } catch (error) {
        alert(`Errore nell'aggiornamento: ${error.message}`);
    }
}

/**
 * Gestisce la cancellazione di un luogo.
 */
function handleDeleteLocation() {
    const name = savedLocationsSelect.value;
    if (!name || name === 'Carica un luogo...') {
        alert("Seleziona un luogo da cancellare.");
        return;
    }

    if (!confirm(`Sei sicuro di voler eliminare il luogo "${name}"?`)) {
        return;
    }

    try {
        deleteLocationLocal(name);
        locationNameInput.value = '';
        latInput.value = '';
        lonInput.value = '';
        altInput.value = '0';
        loadLocations();
        alert(`Luogo "${name}" eliminato.`);
    } catch (error) {
        alert(`Errore nella cancellazione: ${error.message}`);
    }
}

/**
 * Carica i dati di un luogo selezionato nei campi del form.
 */
function handleLoadSelectedLocation() {
    const selectedOption = savedLocationsSelect.options[savedLocationsSelect.selectedIndex];
    if (!selectedOption || selectedOption.disabled) return;

    const name = selectedOption.value;
    const lat = selectedOption.dataset.lat;
    const lon = selectedOption.dataset.lon;
    const alt = selectedOption.dataset.alt;

    if (name && lat !== undefined && lon !== undefined && alt !== undefined) {
        locationNameInput.value = name;
        latInput.value = lat;
        lonInput.value = lon;
        altInput.value = alt;
        locationNameInputHidden.value = name;
        if (locationNameSearchInput) locationNameSearchInput.value = name; 
        
        // Aggiorna anche i campi nascosti della ricerca
        if (latSearchInput) latSearchInput.value = lat;
        if (lonSearchInput) lonSearchInput.value = lon;
        if (altSearchInput) altSearchInput.value = alt;
    }
}


// --- Event Listeners ---

// Listeners per la gestione dei luoghi
if (saveLocationBtn) saveLocationBtn.addEventListener('click', handleSaveLocation);
if (updateLocationBtn) updateLocationBtn.addEventListener('click', handleUpdateLocation);
if (deleteLocationBtn) deleteLocationBtn.addEventListener('click', handleDeleteLocation);
if (savedLocationsSelect) savedLocationsSelect.addEventListener('change', handleLoadSelectedLocation);

// Gestore unificato per la modifica manuale delle coordinate
const handleCoordinateInputChange = () => {
    // 1. Sincronizza i valori con i campi nascosti del form di ricerca
    if (latSearchInput) latSearchInput.value = latInput.value;
    if (lonSearchInput) lonSearchInput.value = lonInput.value;
    if (altSearchInput) altSearchInput.value = altInput.value;
    
    // 2. Svuota il nome del luogo perché le coordinate sono state modificate manualmente
    if (locationNameInputHidden) locationNameInputHidden.value = '';
    if (locationNameSearchInput) locationNameSearchInput.value = '';
};

if (latInput) latInput.addEventListener('input', handleCoordinateInputChange);
if (lonInput) lonInput.addEventListener('input', handleCoordinateInputChange);
if (altInput) altInput.addEventListener('input', handleCoordinateInputChange);


// --- Inizializzazione dell'Applicazione ---

/**
 * Funzione di avvio eseguita al caricamento completo del DOM.
 */
function initializeApp() {
    // La data di oggi è impostata dal backend se non già presente
    const dateInput = document.getElementById('date');
    if (dateInput && !dateInput.value) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }

    // Carica i luoghi salvati (client-side)
    loadLocations();
}

// Avvia l'applicazione quando il DOM è pronto
document.addEventListener('DOMContentLoaded', initializeApp);