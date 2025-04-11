FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Separate layer for requirements to cache dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

EXPOSE 8080
ENV PORT=8080

# Healthcheck for Streamlit
HEALTHCHECK --interval=30s --timeout=3s CMD curl --fail http://localhost:8080/_stcore/health || exit 1

CMD ["streamlit", "run", "retirement.py", "--server.port=8080", "--server.address=0.0.0.0"]
