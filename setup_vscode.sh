#!/usr/bin/env bash
set -e

echo "=== MedTrack Backend Setup ==="
cd "$(dirname "$0")"

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

cp -n .env.example .env || true

echo ""
echo "✓ Setup complete."
echo ""
echo "To start the API:"
echo "  source .venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "API docs at: http://localhost:8000/docs"