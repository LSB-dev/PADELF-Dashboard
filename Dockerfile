FROM python:3.11-slim

WORKDIR /app

# Install curl for container health checks.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy packaging metadata first for better layer caching.
COPY pyproject.toml README.md /app/
COPY src /app/src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# Copy the remaining project files.
COPY . /app

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "src/padelf_dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
