# Dockerfile

# Use the official Python image from the slim variant
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app/

# Install system dependencies for mysqlclient and WeasyPrint
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libpng-dev \
    libpango1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libpq-dev \
    libxml2 \
    libxslt1-dev \
    zlib1g-dev \
    pkg-config


# Install Python dependencies
COPY requirements.txt requirements.txt 
RUN pip install --no-cache-dir -r requirements.txt

# Remove unnecessary build dependencies
RUN apt-get remove -y \
    gcc \
    libmariadb-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libpng-dev \
    libpq-dev \
    libxml2 \
    libxslt1-dev \
    zlib1g-dev \
    && apt-get autoremove -y \
    && apt-get clean

# Install runtime libraries
RUN apt-get install -y \
    libmariadb3 \
    libpango1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    && apt-get clean

# Copy project
COPY . .

# Collect static files
RUN python manage.py makemigrations --noinput
RUN python manage.py migrate --noinput
RUN python manage.py collectstatic --noinput


# Run Gunicorn server
CMD gunicorn Student_Website.wsgi --bind=0.0.0.0:8000

# CMD python manage.py runserver 0.0.0.0:8000
# Expose the application port
EXPOSE 8000
