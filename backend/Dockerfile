FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy everything from backend folder INTO /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Django/Gunicorn port
EXPOSE 8001

# Run Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "backend.wsgi:application"]
