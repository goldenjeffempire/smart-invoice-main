#!/usr/bin/env bash
# Build script for production deployment
set -o errexit

echo "=== InvoiceFlow Production Build Script ==="

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node dependencies and build assets
if [ -f "package.json" ]; then
    echo "Installing Node.js dependencies..."
    npm install --production=false
    
    # Build all production assets (CSS + minified JS/CSS)
    echo "Building production assets..."
    npm run build:prod
fi

# Run Django migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser if needed (optional, for first deployment)
# echo "Creating superuser..."
# python manage.py createsuperuser --noinput --email admin@example.com || true

echo "Build complete!"
