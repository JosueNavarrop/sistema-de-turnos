# ---------- 1. Compilar el frontend (Vue 3 + Vite) ----------
FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# ---------- 2. Backend (FastAPI) que también sirve el frontend compilado ----------
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# tzdata: la hora de los turnos depende de la zona horaria (variable TZ)
RUN apt-get update && apt-get install -y --no-install-recommends tzdata && rm -rf /var/lib/apt/lists/*
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=frontend /frontend/dist /app/frontend/dist

RUN useradd --create-home turnofacil && chown -R turnofacil /app
USER turnofacil

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/salud')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
