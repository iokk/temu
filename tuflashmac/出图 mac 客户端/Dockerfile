FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    ECOMMERCE_WORKBENCH_DATA_DIR=/app/data \
    FILE_STORAGE_PATH=/app/data/files

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY image/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY image/ ./

RUN mkdir -p /root/.streamlit && \
    echo '[server]\nheadless = true\naddress = "0.0.0.0"\nport = 8501\nenableCORS = false\nmaxUploadSize = 100\n\n[browser]\ngatherUsageStats = false\n\n[theme]\nbase = "light"\nprimaryColor = "#667eea"' > /root/.streamlit/config.toml

RUN mkdir -p /app/data/files && chmod -R 777 /app/data

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["sh", "-c", "streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8501} --server.headless=true --browser.gatherUsageStats=false"]
