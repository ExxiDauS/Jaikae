#!/bin/bash

echo "Starting Django application..."

echo "Applying database migrations..."
python manage.py makemigrations --noinput

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

echo "tailwindcss build"
./static/css/tailwindcss.exe -i ./static/css/input.css -o ./static/css/output.css

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start development server
echo "Starting server on 0.0.0.0:8000"
python manage.py runserver 0.0.0.0:8000
