FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY crosbi/ ./crosbi/
COPY notebook.py .

# Direktorij za disk cache (montirati kao volumen za trajnost)
RUN mkdir -p .cache

EXPOSE 2718

# Pokretanje: MODE=run (zadano) ili MODE=edit
# Primjeri:
#   docker run -p 2718:2718 crosbi-notebook
#   docker run -p 2718:2718 -e MODE=edit crosbi-notebook
ENTRYPOINT ["sh", "-c", "exec marimo ${MODE:-run} notebook.py --host 0.0.0.0 --port 2718 --no-token"]
