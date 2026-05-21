#!/bin/sh
set -e

echo "🚀 FastAPI Platform Lab API starting..."
echo "⏳ Waiting for database connection..."

# Aguarda o Postgres responder
until pg_isready -h db -p 5432 -U postgres; do
    echo "Banco ainda não disponível... aguardando..."
    sleep 2
done

echo "✅ Banco conectado! Iniciando aplicação..."
exec uvicorn main:app --host 0.0.0.0 --port 8000