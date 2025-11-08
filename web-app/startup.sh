#!/bin/bash

# Wait for the database to be ready (optional, but good practice)
sleep 10

# Initialize the database
python application.py &

# Start Gunicorn
gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=300 "application:app"
