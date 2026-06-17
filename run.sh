#!/usr/bin/env bash
# run.sh - launcher for macOS / Linux
set -e

if ! command -v python >/dev/null 2>&1; then
  echo "Python no está instalado o no está en PATH. Instala Python 3.11+"
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Creando entorno virtual .venv ..."
  python -m venv .venv
fi

echo "Activando entorno virtual..."
source .venv/bin/activate

echo "Actualizando pip e instalando dependencias..."
python -m pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  echo "requirements.txt no encontrado. Omite instalación."
fi

if [ ! -f .env ]; then
  read -p "¿Deseas crear un archivo .env con GROQ_API_KEY ahora? (s/N): " resp
  if [[ $resp =~ ^([sS])$ ]]; then
    read -p "Introduce tu GROQ_API_KEY: " key
    if [ -n "$key" ]; then
      echo "GROQ_API_KEY=$key" > .env
      echo ".env creado."
    fi
  fi
fi

echo "Iniciando Streamlit..."
streamlit run app.py
