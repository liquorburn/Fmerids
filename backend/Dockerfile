# Usa un'immagine Python ufficiale come base
FROM python:3.11-slim

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia il file delle dipendenze e installale
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copia il resto dell'applicazione backend nella directory di lavoro
# Questo include app.py, le cartelle core/, api/, static/, templates/ etc.
COPY . .

# Esponi la porta su cui Gunicorn sarà in ascolto
EXPOSE 5001

# Comando per avviare l'applicazione in produzione con Gunicorn e TLS
# Avvia 4 worker processes. 'app:app' si riferisce all'oggetto 'app' nel file 'app.py'.
# I certificati verranno montati nel percorso /certs tramite Docker Compose.
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5001", "--certfile", "/certs/cert.pem", "--keyfile", "/certs/key.pem", "app:app"]
