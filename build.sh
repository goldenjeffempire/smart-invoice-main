#!/usr/bin/env bash
# Build script for production deployment
set -o errexit

echo "=== Smart Invoice Production Build Script ==="

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-production.txt

# Install Node dependencies for Tailwind CSS
if [ -f "package.json" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
    
    # Build Tailwind CSS
    echo "🎨 Building Tailwind CSS..."
    npm run build:css
fi

# Run Django migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser if needed (optional, for first deployment)
# echo "👤 Creating superuser..."
# python manage.py createsuperuser --noinput --email admin@example.com || true

echo "✅ Build complete!"
