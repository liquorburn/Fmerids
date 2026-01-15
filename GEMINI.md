# Fmerids - Documentazione del Progetto

## 1. Sommario

**Fmerids** è un'applicazione web per il calcolo e la ricerca delle ore planetarie. L'applicazione fornisce dati accurati basati su data e coordinate geografiche, calcolando le ore planetarie, il segno zodiacale del Sole e la fase lunare.

L'architettura è basata su un backend Python/Flask che utilizza il motore di templating Jinja2 per renderizzare l'interfaccia utente lato server, garantendo performance e manutenibilità.

## 2. Architettura e Tecnologie

L'applicazione adotta un'architettura monolitica con rendering lato server (Server-Side Rendering). Il backend Flask gestisce sia la logica di business che la presentazione dell'interfaccia utente.

### Backend
- **Tecnologie:** Python 3, Flask, Jinja2.
- **Server WSGI di Produzione:** Gunicorn.
- **Librerie Chiave:**
    - `pyephem`: Utilizzata per i calcoli astronomici di precisione.
    - `astral`: Utilizzata per il calcolo degli orari di alba e tramonto.
- **Logica di Business:**
    - La logica di calcolo risiede in `core/planetary_logic.py`.
    - La gestione dei luoghi (CRUD) è in `core/locations_logic.py`.
- **Routing e Rendering:**
    - Le rotte sono definite in `app.py` e gestiscono le richieste HTTP.
    - Invece di restituire JSON, le rotte utilizzano `render_template()` per servire pagine HTML complete, passando i dati necessari ai template Jinja2.

### Frontend
- **Tecnologie:** HTML5, CSS3 (Bootstrap 5), JavaScript (ES6+).
- **Templating:**
    - L'intera UI è gestita tramite template Jinja2 situati nella cartella `backend/templates`.
    - Vi è un `base.html` e template parziali (es. `daily_results.html`, `_pagination.html`) per i componenti riutilizzabili.
- **Logica Client-Side:**
    - `main.js`: Gestisce unicamente le interazioni dinamiche che non richiedono un ricaricamento della pagina, come la funzionalità CRUD per i "Luoghi Salvati".
    - `apiService.js`: Utilizzato esclusivamente per le chiamate API relative alla gestione dei luoghi.
    - `uiUpdater.js`: **Obsoleto**. La sua funzionalità è stata interamente sostituita dal rendering lato server con Jinja2.

### Struttura delle Directory (Post-Refactoring)
```
/fmerids/
├── backend/
│   ├── app.py                # Entry point Flask, routing e logica di rendering
│   ├── Dockerfile            # Istruzioni per creare l'immagine Docker
│   ├── requirements.txt      # Dipendenze Python (incluso gunicorn)
│   ├── core/
│   │   ├── planetary_logic.py
│   │   └── locations_logic.py
│   ├── api/                  # API legacy (usata solo per i luoghi)
│   │   └── ...
│   ├── static/               # File statici (CSS, JS)
│   │   ├── css/style.css
│   │   └── js/
│   │       ├── main.js
│   │       └── apiService.js
│   └── templates/            # Template Jinja2
│       ├── base.html
│       ├── index.html
│       ├── daily_results.html
│       ├── search_results.html
│       └── ... (partials)
└── GEMINI.md                   # Questo file
```

## 3. Funzionalità Dettagliate
(La descrizione delle funzionalità rimane invariata, ma il meccanismo di implementazione è cambiato da SPA a Server-Side Rendering).

... (contenuto precedente omesso per brevità) ...

## 4. Deployment in Produzione

Questa sezione descrive come effettuare il deployment dell'applicazione Fmerids in un ambiente di produzione utilizzando Docker.

### Requisiti Hardware e Software

- **Hardware (Minimi Raccomandati):**
    - **CPU:** 1 core
    - **RAM:** 1-2 GB
    - **Disco:** 20 GB di spazio libero

- **Software:**
    - **Sistema Operativo:** Una distribuzione Linux moderna (es. Ubuntu 22.04 LTS).
    - **Container Engine:** Docker (versione 20.10.x o successiva).
    - **Orchestrazione (Raccomandato):** Docker Compose (versione 1.29.x o successiva).
    - **Certificato TLS:** Un certificato SSL/TLS valido (es. `cert.pem`) e la relativa chiave privata (`key.pem`). Questi file possono essere ottenuti da una Certificate Authority come Let's Encrypt.

### Creazione del Dockerfile

L'applicazione è containerizzata per garantire coerenza tra ambiente di sviluppo e produzione. In produzione (es. Railway), il proxy gestisce l'HTTPS, quindi il container espone HTTP semplice sulla porta 5001.

**`backend/Dockerfile`:**
```dockerfile
# Usa un'immagine Python ufficiale come base
FROM python:3.11-slim

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia il file delle dipendenze e installale
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto dell'applicazione backend
COPY . .

# Crea la directory data per i volumi persistenti
RUN mkdir -p data

# Esponi la porta su cui Gunicorn sarà in ascolto
EXPOSE 5001

# Comando per avviare l'applicazione con Gunicorn
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5001", "app:app"]
```

### Istruzioni di Deployment (Railway.app)

Il metodo raccomandato per il deployment è tramite **Railway.app**, che offre integrazione nativa con Docker e gestione automatica dei certificati SSL.

1.  **Preparazione del Volume Persistente:**
    - Per evitare la perdita dei luoghi salvati (`locations.json`), è **obbligatorio** configurare un volume persistente.
    - Nella dashboard di Railway, aggiungi un Volume e imposta il punto di montaggio (Mount Path) su `/app/data`.

2.  **Configurazione del Dominio:**
    - In Railway, vai in `Settings > Domains` e aggiungi il tuo dominio personalizzato.
    - Configura i record DNS (CNAME per `www` e Record A per il dominio root) seguendo le istruzioni fornite dalla piattaforma.

3.  **Variabili d'Ambiente:**
    - `FLASK_ENV`: Impostata su `production`.
    - `FLASK_DEBUG`: Impostata su `false`.

**Vantaggi di questa configurazione:**
- **Zero Maintenance:** Non occorre gestire manualmente i certificati SSL.
- **Persistenza:** I dati rimangono integri anche dopo il riavvio o il redeploy dei container.
- **Scalabilità:** Gunicorn gestisce più worker per servire contemporaneamente più utenti.

3.  **Avviare il Container:**
    Apri un terminale nella directory radice del progetto ed esegui il seguente comando:

    ```bash
    # Costruisce l'immagine (se non esiste) e avvia il container in background
    docker-compose up --build -d
    ```

4.  **Verifica:**
    L'applicazione dovrebbe ora essere accessibile tramite `https` all'indirizzo IP del server (es. `https://tuo_server_ip`).

5.  **Gestione del Container:**
    - **Per fermare l'applicazione:** `docker-compose down`
    - **Per visualizzare i log:** `docker-compose logs -f`

**Alternativa senza TLS diretto in Gunicorn:**
In un ambiente di produzione più complesso, è prassi comune terminare la connessione TLS a livello di un reverse proxy (come Nginx o Traefik). In questo scenario, il reverse proxy gestisce HTTPS con il client, e comunica con Gunicorn in HTTP semplice all'interno della rete Docker. Se si adotta questo approccio, si dovrebbe rimuovere la configurazione `--certfile` e `--keyfile` dal `Dockerfile` e la sezione `volumes` dal `docker-compose.yml`.