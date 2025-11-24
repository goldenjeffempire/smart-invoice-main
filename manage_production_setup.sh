#!/bin/bash
# Production Setup Script for Smart Invoice

set -e

echo "================================================"
echo "Smart Invoice - Production Setup Script"
echo "================================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "✅ Python 3 found"

# Check required env variables
echo ""
echo "Checking required environment variables..."
required_vars=("DJANGO_SECRET_KEY" "DATABASE_URL" "SENDGRID_API_KEY" "SENDGRID_FROM_EMAIL" "ALLOWED_HOSTS")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "⚠️  $var not set"
    else
        echo "✅ $var is set"
    fi
done

# Run migrations
echo ""
echo "Running database migrations..."
python3 manage.py migrate --no-input || echo "⚠️  Migrations may have issues - check logs"

# Collect static files
echo ""
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear || echo "⚠️  Static file collection may have issues"

# Check health
echo ""
echo "Checking application health..."
python3 manage.py check --deploy || echo "⚠️  Deployment checks found issues"

echo ""
echo "================================================"
echo "✅ Production setup complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Verify all environment variables are set"
echo "2. Test the application: gunicorn smart_invoice.wsgi:application"
echo "3. Deploy to Render"
echo ""
