# Fmerids - Documentazione del Progetto

## 1. Sommario

**Fmerids** è un'applicazione web per il calcolo e la ricerca delle ore planetarie. L'applicazione fornisce dati accurati basati su data e coordinate geografiche, calcolando le ore planetarie, il segno zodiacale del Sole e la fase lunare.

L'architettura è basata su un backend Python/Flask che utilizza il motore di templating Jinja2 per renderizzare l'interfaccia utente lato server.

## 2. Architettura e Tecnologie

L'applicazione adotta un'architettura monolitica con rendering lato server (Server-Side Rendering).

### Backend
- **Tecnologie:** Python 3, Flask, Jinja2.
- **Server WSGI di Produzione:** Gunicorn.
- **Librerie Chiave:**
    - `pyephem`: Utilizzata per i calcoli astronomici di precisione.
    - `astral`: Utilizzata per il calcolo degli orari di alba e tramonto.
    - `timezonefinder`: Utilizzata per determinare il fuso orario corretto dalle coordinate geografiche.
    - `pytz`: Per la gestione e la conversione dei fusi orari.
- **Logica di Business:**
    - La logica di calcolo risiede in `core/planetary_logic.py`. **Correzione chiave**: I calcoli ora vengono eseguiti nel fuso orario locale della posizione geografica fornita, risolvendo il problema dei calcoli basati su UTC.
    - La gestione dei luoghi (CRUD) è in `core/locations_logic.py`.
- **Routing e Rendering:**
    - Le rotte sono definite in `app.py` e gestiscono le richieste HTTP, servendo pagine HTML complete tramite `render_template()`.

### Frontend
- **Tecnologie:** HTML5, CSS3 (Bootstrap 5), JavaScript (ES6+).
- **Templating:**
    - L'intera UI è gestita tramite template Jinja2 (`backend/templates`), con `base.html` come scheletro principale.
- **Logica Client-Side:**
    - `main.js`: Gestisce le interazioni dinamiche, inclusa la funzionalità CRUD per i "Luoghi Salvati" e la logica per il cambio di tema.
    - `apiService.js`: Utilizzato esclusivamente per le chiamate API relative alla gestione dei luoghi.
- **Theming Dinamico (Nuova Funzionalità):**
    - È stato implementato un selettore di temi che consente all'utente di scegliere tra diverse palette di colori in stile "dark".
    - La scelta viene salvata nel `localStorage` del browser per persistere tra le sessioni.
    - I temi sono definiti in file CSS separati (`palette_*.css`) che contengono variabili CSS, caricate dinamicamente.

### Struttura delle Directory (Aggiornata)
```
/fmerids/
├── backend/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt      # Aggiornato con timezonefinder e pytz
│   ├── core/
│   │   ├── planetary_logic.py
│   │   └── locations_logic.py
│   ├── api/
│   │   └── ...
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css
│   │   │   ├── palette_violet_eclipse.css   # Nuovo
│   │   │   ├── palette_crimson_noir.css     # Nuovo
│   │   │   └── palette_enchanted_forest.css # Nuovo
│   │   └── js/
│   │       ├── main.js
│   │       └── apiService.js
│   └── templates/
│       ├── base.html
│       └── ... (altri template)
└── GEMINI.md
```

## 3. Funzionalità Dettagliate

### Calcolo delle Ore Planetarie
- **Correttezza del Fuso Orario**: L'applicazione determina automaticamente il fuso orario locale basato sulle coordinate geografiche inserite, garantendo che l'ora di alba, tramonto e, di conseguenza, tutte le ore planetarie siano precise per quella località.

### Personalizzazione dell'Interfaccia
- **Selettore di Temi**: Nella barra di navigazione è presente un menu a discesa che permette di cambiare l'aspetto della UI. Le opzioni includono:
    - **Default Dark**: Il tema scuro standard di Bootstrap.
    - **Violet Eclipse**: Un tema scuro con accenti viola.
    - **Crimson Noir**: Un tema scuro con accenti rosso cremisi.
    - **Enchanted Forest**: Un tema scuro con accenti verde foresta.
- La scelta del tema viene salvata localmente nel browser.

*(Le altre funzionalità rimangono invariate)*

## 4. Deployment in Produzione
(La documentazione per il deployment con Docker e Gunicorn rimane invariata, ma è importante notare che le nuove dipendenze in `requirements.txt` verranno installate automaticamente durante la build dell'immagine Docker.)

**Nota:** Il comando `CMD` nel `Dockerfile` rimane valido. Le nuove dipendenze verranno installate dal `RUN pip install`.
