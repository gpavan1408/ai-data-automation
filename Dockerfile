# --- Stage 1: Base Image ---
FROM python:3.11-slim

# --- Stage 2: Set up the Environment ---
WORKDIR /app

# --- Stage 3: Copy requirements file and install dependencies ---
# Do this early to take advantage of Docker caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 4: Copy application code ---
COPY . .

# --- Stage 5: Streamlit config for live reload ---
RUN mkdir -p /root/.streamlit
COPY .streamlit/config.toml /root/.streamlit/config.toml

# --- Stage 6: Expose Streamlit default port ---
EXPOSE 8501

# --- Stage 7: Run the app ---
CMD ["streamlit", "run", "dashboard_app/app.py"]
