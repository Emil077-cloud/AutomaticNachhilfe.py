# Playwright Base-Image mit Python
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# Arbeitsverzeichnis setzen
WORKDIR /app

# Deine Dateien ins Image kopieren
COPY requirements.txt .
COPY nachhilfe.py .

# Abhängigkeiten installieren
RUN pip install --no-cache-dir -r requirements.txt

# Browser installieren und fehlende Systempakete mitbringen
RUN playwright install --with-deps

# Skript starten
CMD ["python", "nachhilfe.py"]
