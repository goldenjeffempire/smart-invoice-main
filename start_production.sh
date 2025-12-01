#!/bin/bash
"""
InvoiceFlow Production Startup Script
Handles SSL setup, migrations, and server startup
"""

set -e

echo "[InvoiceFlow] Starting production environment setup..."

# Setup SSL certificates from environment variables
echo "[InvoiceFlow] Setting up SSL certificates..."
python setup_ssl.py

# Run Django migrations
echo "[InvoiceFlow] Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "[InvoiceFlow] Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn server
echo "[InvoiceFlow] Starting Gunicorn server with HTTPS support..."

# Determine SSL files location
SSL_CERT="/tmp/invoiceflow-certs/certificate.pem"
SSL_KEY="/tmp/invoiceflow-certs/private-key-rsa.pem"

# Check if SSL files exist
if [ -f "$SSL_CERT" ] && [ -f "$SSL_KEY" ]; then
    echo "[InvoiceFlow] HTTPS enabled - starting Gunicorn with SSL support"
    gunicorn invoiceflow.wsgi:application \
        --config gunicorn.conf.py \
        --certfile="$SSL_CERT" \
        --keyfile="$SSL_KEY" \
        --ssl-version=TLSv1_2
else
    echo "[InvoiceFlow] WARNING: SSL files not found - starting Gunicorn without HTTPS"
    gunicorn invoiceflow.wsgi:application --config gunicorn.conf.py
fi
