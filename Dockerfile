FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências básicas + cliente Postgres (para pg_isready no start.sh)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copia o código para dentro da imagem
COPY . .

# Garante permissão de execução do script de inicialização
RUN chmod +x start.sh

EXPOSE 8000

# Usa o start.sh para:
# - esperar o banco responder
# - iniciar o uvicorn
CMD ["./start.sh"]