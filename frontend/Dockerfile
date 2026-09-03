FROM python:3.11-slim

WORKDIR /app

# Install dependencies first so Docker can cache this layer separately
# from app code changes (same reasoning as backend/Dockerfile)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual app code
COPY streamlit_app.py .
COPY pages/ ./pages/


EXPOSE 8501

# --server.address=0.0.0.0 is required so Streamlit accepts connections
# from outside the container (default is localhost-only)
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
