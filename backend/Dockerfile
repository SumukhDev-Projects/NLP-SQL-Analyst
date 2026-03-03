FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Seed the database if it doesn't exist yet
RUN python -c "
from pathlib import Path
db = Path('data/analyst.db')
db.parent.mkdir(parents=True, exist_ok=True)
if not db.exists():
    import subprocess, sys
    subprocess.run([sys.executable, '../scripts/seed_db.py'], check=True)
" 2>/dev/null || true

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
