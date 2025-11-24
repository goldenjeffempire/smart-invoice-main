## 🏗️ Build & Deploy

### Development Build
```bash
# Watch mode for CSS (auto-rebuild on changes)
npm run watch:css

# Start development server
python manage.py runserver 0.0.0.0:5000
```

### Production Build
```bash
# Build all optimized assets (CSS + JS minification)
npm run build:prod

# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn smart_invoice.wsgi:application --bind 0.0.0.0:5000 --workers 4
```

**📖 Complete guides:**
- [BUILD_GUIDE.md](BUILD_GUIDE.md) - Development setup and build commands
- [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) - Production deployment to Render

### Performance Metrics
- **JavaScript**: 23KB → 12KB (50% reduction)
- **CSS**: 128KB → 89KB (32% reduction)
- **Cache**: 1-year cache headers for static assets
- **Compression**: Brotli/Gzip via WhiteNoise
