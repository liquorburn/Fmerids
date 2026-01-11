#!/bin/bash

# --- start_dev.sh ---
# Script per configurare l'ambiente virtuale e avviare l'app Flask in modalità sviluppo.

# Imposta la directory del backend
BACKEND_DIR="backend"

# Controlla se la directory del backend esiste
if [ ! -d "$BACKEND_DIR" ]; then
  echo "Errore: La directory '$BACKEND_DIR' non è stata trovata."
  echo "Assicurati di eseguire questo script dalla directory principale del progetto."
  exit 1
fi

# Vai nella directory del backend
cd "$BACKEND_DIR" || exit

# --- Configurazione dell'Ambiente Virtuale ---

VENV_DIR=".venv"

# Controlla se python3 è disponibile
if ! command -v python3 &> /dev/null; then
    echo "Errore: python3 non è installato o non è nel PATH."
    exit 1
fi

# Crea l'ambiente virtuale se non esiste
if [ ! -d "$VENV_DIR" ]; then
    echo "Creazione dell'ambiente virtuale in '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Errore durante la creazione dell'ambiente virtuale."
        exit 1
    fi
fi

# Attiva l'ambiente virtuale
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# --- Installazione delle Dipendenze ---

REQUIREMENTS_FILE="requirements.txt"

# Installa le dipendenze se il file esiste
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installazione delle dipendenze da '$REQUIREMENTS_FILE'..."
    pip install -r "$REQUIREMENTS_FILE"
    if [ $? -ne 0 ]; then
        echo "Errore durante l'installazione delle dipendenze."
        exit 1
    fi
else
    echo "Attenzione: Il file '$REQUIREMENTS_FILE' non è stato trovato. Le dipendenze non verranno installate."
fi

# --- Avvio dell'Applicazione Flask ---

# Imposta le variabili d'ambiente per Flask
export FLASK_APP=app.py
export FLASK_ENV=development

echo "Avvio del server di sviluppo Flask..."
echo "L'applicazione sarà disponibile su http://127.0.0.1:5000"
echo "Premi CTRL+C per fermare il server."

# Avvia l'applicazione
flask run

# Disattiva l'ambiente virtuale all'uscita
deactivate
