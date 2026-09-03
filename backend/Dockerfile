FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed by psycopg (PostgreSQL driver) and
# sentence-transformers (some ML libs need build tools for certain wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (before copying app code) so Docker
# can cache this layer — rebuilds are much faster when only code changes,
# not dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the actual application code
COPY app/ ./app/
COPY pytest.ini .

# Copy a startup script that runs both the MCP server and FastAPI
COPY start.sh .
RUN chmod +x start.sh

EXPOSE 8000
EXPOSE 8001

CMD ["./start.sh"]