# Usa un'immagine Python ufficiale come base
FROM python:3.11-slim

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia il file delle dipendenze e installale
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto dell'applicazione backend nella directory di lavoro
COPY . .

# Crea la directory data se non esiste
RUN mkdir -p data

# Esponi la porta su cui Gunicorn sarà in ascolto
EXPOSE 5001

# Comando per avviare l'applicazione con Gunicorn usando la porta dinamica (Railway) o 5001 come default
CMD gunicorn --workers 4 --bind 0.0.0.0:${PORT:-5001} app:app

