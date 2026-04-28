# TEMU 智能出图系统 V8.0
# Nano Banana Pro 版本
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DATA_DIR=/app/data

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./

RUN mkdir -p /root/.streamlit && \
    echo '[server]\nheadless = true\naddress = "0.0.0.0"\nport = 8501\nenableCORS = false\nmaxUploadSize = 100\n\n[browser]\ngatherUsageStats = false\n\n[theme]\nbase = "light"\nprimaryColor = "#667eea"' > /root/.streamlit/config.toml

RUN mkdir -p /app/data && chmod 777 /app/data

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
