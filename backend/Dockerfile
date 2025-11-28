# Use a base image with Python installed
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt /app/

# Install dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the container
COPY . .

# Expose the port the Django app runs on
EXPOSE 8001

# Run the Django development server
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "backend.wsgi:application"]
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]