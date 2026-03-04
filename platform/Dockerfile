FROM python:3.12-slim

LABEL maintainer="CTF Docente"
LABEL description="Plataforma CTF educativa personalizada"

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY app.py models.py /app/
COPY templates/ /app/templates/

# Crear directorio de datos (la DB SQLite irá aquí)
RUN mkdir -p /data

EXPOSE 5000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]
