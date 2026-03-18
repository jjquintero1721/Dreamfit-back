# ---- builder stage: compile wheels ----
FROM python:3.10-slim AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
 && pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt

# ---- runtime stage: lean image ----
FROM python:3.10-slim

# (optional) if timezone data or other OS deps are needed
# RUN apt-get update \
#  && apt-get install -y --no-install-recommends tzdata \
#  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENV=production

EXPOSE 8000

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", \
     "app.main:app", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-connections", "1000", \
     "--timeout", "120", \
     "--log-level", "info", \
     "--proxy-protocol"]
