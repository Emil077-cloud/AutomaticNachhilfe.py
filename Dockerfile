FROM mcr.microsoft.com/playwright/python:v1.54.1-jammy
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN playwright install-deps
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
