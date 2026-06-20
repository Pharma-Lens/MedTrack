#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "=== MedTrack Setup (Termux / Android) ==="

# Termux packages
pkg update -y
pkg install -y python libsqlite clang

# Python deps
pip install --upgrade pip
pip install -r requirements.txt

cp -n .env.example .env || true

echo ""
echo "✓ Setup complete."
echo ""
echo "To start:"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
