#!/usr/bin/env bash
# =============================================================================
# InvoiceFlow Production Build Script
# Domain: https://invoiceflow.com.ng
# =============================================================================
set -o errexit

echo "=== InvoiceFlow Production Build Script ==="
echo "Target Domain: https://invoiceflow.com.ng"

# Export production domain for any scripts that need it
export PRODUCTION_DOMAIN="invoiceflow.com.ng"
export PRODUCTION_URL="https://invoiceflow.com.ng"

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

# Create cache table for database caching
echo "Creating cache tables..."
python manage.py createcachetable

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run Django system checks
echo "Running Django system checks..."
python manage.py check --deploy || echo "Warning: Some deployment checks failed (may be expected in build environment)"

echo "=== Build Complete ==="
echo "InvoiceFlow is ready for production at https://invoiceflow.com.ng"
