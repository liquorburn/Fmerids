const API_BASE_URL = 'http://127.0.0.1:5001/api';

/**
 * Gestisce le chiamate fetch e la risposta JSON.
 * @param {string} url - L'URL completo da chiamare.
 * @param {object} options - Opzioni per la chiamata fetch.
 * @returns {Promise<any>} - I dati JSON dalla risposta.
 * @throws {Error} - Se la risposta di rete non è ok.
 */
async function fetchJSON(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Errore di rete o risposta non-JSON' }));
        throw new Error(errorData.error || `Errore HTTP: ${response.status}`);
    }
    // Per le risposte 204 No Content, non c'è un corpo JSON
    if (response.status === 204) {
        return null;
    }
    return response.json();
}

/**
 * Chiama l'endpoint /api/meta per ottenere i metadati.
 * @returns {Promise<object>} - Un oggetto con le liste di pianeti, segni, etc.
 */
export function getMetadata() {
    return fetchJSON(`${API_BASE_URL}/meta`);
}

/**
 * Chiama l'endpoint /api/calculate con i parametri forniti.
 * @param {object} params - Oggetto con { date, lat, lon, alt }.
 * @returns {Promise<object>} - Il risultato del calcolo delle ore planetarie.
 */
export function getCalculation({ date, lat, lon, alt }) {
    const queryParams = new URLSearchParams({ date, lat, lon, alt });
    const url = `${API_BASE_URL}/calculate?${queryParams}`;
    return fetchJSON(url);
}

/**
 * Chiama l'endpoint /api/search. (Non ancora implementato nel backend)
 * @param {object} params - Oggetto con i criteri di ricerca.
 * @returns {Promise<object>} - I risultati della ricerca.
 */
export function getSearchResults(params) {
    const queryParams = new URLSearchParams(params);
    const url = `${API_BASE_URL}/search?${queryParams}`;
    return fetchJSON(url);
}

// --- Funzioni per la gestione dei luoghi ---

/**
 * Ottiene tutti i luoghi salvati.
 * @returns {Promise<object>}
 */
export function getLocations() {
    return fetchJSON(`${API_BASE_URL}/locations`);
}

/**
 * Salva un nuovo luogo.
 * @param {string} name - Il nome del luogo.
 * @param {object} data - Oggetto con { lat, lon, alt }.
 * @returns {Promise<object>}
 */
export function saveLocation(name, data) {
    return fetchJSON(`${API_BASE_URL}/locations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, ...data })
    });
}

/**
 * Aggiorna un luogo esistente.
 * @param {string} name - Il nome del luogo da aggiornare.
 * @param {object} data - Oggetto con i nuovi dati { lat, lon, alt }.
 * @returns {Promise<object>}
 */
export function updateLocation(name, data) {
    return fetchJSON(`${API_BASE_URL}/locations/${name}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
}

/**
 * Cancella un luogo.
 * @param {string} name - Il nome del luogo da cancellare.
 * @returns {Promise<void>}
 */
export function deleteLocation(name) {
    const url = `${API_BASE_URL}/locations/${name}`;
    return fetchJSON(url, { method: 'DELETE' });
}
