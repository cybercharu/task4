FROM python:3.13.5    

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app folder into the container
COPY . .

# Run FastAPI app
EXPOSE 8000 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]