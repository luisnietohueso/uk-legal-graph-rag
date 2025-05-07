# Use official lightweight Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Streamlit environment settings (suppress sharing prompt, logs, etc.)
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ENABLECORS=false

# Launch Streamlit
CMD ["streamlit", "run", "src/main_app.py"]
