#!/usr/bin/env bash
# Démarre le CRM RevoluSolaire
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$SCRIPT_DIR/backend"

cd "$BACKEND"

# Créer l'environnement virtuel si absent
if [ ! -d ".venv" ]; then
  echo "Création de l'environnement virtuel Python…"
  python3 -m venv .venv
fi

source .venv/bin/activate

# Installer les dépendances
pip install -q -r requirements.txt

# Vérifier que le .env existe
if [ ! -f ".env" ]; then
  if [ -f "$SCRIPT_DIR/.env.example" ]; then
    echo "⚠️  Aucun fichier .env trouvé dans backend/."
    echo "   Copie et configure : cp .env.example backend/.env"
    exit 1
  fi
fi

echo "Démarrage du CRM RevoluSolaire sur http://0.0.0.0:58645"
uvicorn main:app --host 0.0.0.0 --port 58645 --reload
