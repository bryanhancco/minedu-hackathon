#!/bin/bash

# Script de inicio para Render
echo "Starting MINEDU RAG API..."

# Instalar dependencias si es necesario
pip install -r requirements.txt

# Ejecutar la aplicación
exec uvicorn api.api:app --host 0.0.0.0 --port ${PORT:-8000}
