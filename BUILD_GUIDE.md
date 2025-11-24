# Build & Development Guide - Smart Invoice

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (or SQLite for development)

### Initial Setup

1. **Clone and Install:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install
```

2. **Environment Configuration:**
```bash
# Create .env file
cp .env.example .env

# Edit .env with your settings
# Minimal development setup:
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
```

3. **Database Setup:**
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# (Optional) Load demo data
python manage.py create_demo_data
```

4. **Build Assets:**
```bash
# Build Tailwind CSS (development)
npm run watch:css

# Or build for production
npm run build:prod
```

5. **Run Development Server:**
```bash
# Start Django dev server
python manage.py runserver 0.0.0.0:5000

# Or use Gunicorn (production-like)
gunicorn smart_invoice.wsgi:application --bind 0.0.0.0:5000
```

## Build Scripts

### CSS Build Commands
```bash
# Development (watch mode)
npm run watch:css

# Production (minified)
npm run build:css
```

### JavaScript Build Commands
```bash
# Minify JavaScript
npm run minify:js
```

### CSS Optimization
```bash
# Minify all CSS files
npm run minify:css
```

### Complete Production Build
```bash
# Build everything (CSS, JS, images)
npm run build:prod
```

## Asset Pipeline

### Development Workflow
1. Edit source files in `static/css/` and `static/js/`
2. Run `npm run watch:css` for live CSS rebuilding
3. Refresh browser to see changes
4. Unminified assets loaded automatically in DEBUG=True mode

### Production Workflow
1. Edit source files
2. Run `npm run build:prod` to generate optimized assets
3. Minified assets automatically loaded when DEBUG=False
4. Deploy with `python manage.py collectstatic`

### File Structure
```
static/
├── css/
│   ├── main.css                    # Source CSS
│   ├── main.min.css                # Minified (generated)
│   ├── enterprise-design-system.css
│   ├── enterprise-design-system.min.css (generated)
│   ├── tailwind.input.css          # Tailwind source
│   └── tailwind.output.css         # Tailwind compiled (minified)
├── js/
│   ├── app.js                      # Source JavaScript
│   └── app.min.js                  # Minified (generated)
└── images/
    └── *.jpg                       # Optimized images
```

## Optimization Metrics

### Current Performance
**JavaScript:**
- Original: 23KB
- Minified: 12KB
- **Reduction: 50%**

**CSS:**
- Total Original: ~128KB
- Total Minified: ~89KB
- **Reduction: 30%**

**Images:**
- Total: 2.2MB (13 images)
- Lazy loading implemented
- WebP conversion available

## Testing

### Run Tests
```bash
# All tests
python manage.py test

# Specific app
python manage.py test invoices

# With coverage
coverage run manage.py test
coverage report
```

### Linting & Code Quality
```bash
# Django check
python manage.py check --deploy

# Python linting
flake8 .

# Security check
python manage.py check --deploy
```

## Database Management

### Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations
python manage.py showmigrations

# Rollback migration
python manage.py migrate <app_name> <migration_name>
```

### Data Management
```bash
# Create demo data
python manage.py create_demo_data

# Generate recurring invoices
python manage.py generate_recurring_invoices

# Database shell
python manage.py dbshell
```

## Debugging

### Django Debug Toolbar
Enabled automatically in DEBUG=True mode
Access at: http://localhost:5000/__debug__/

### Logging
Logs are written to:
- Console (all environments)
- `logs/django.log` (rotating file)

### Common Issues

**Port already in use:**
```bash
# Find and kill process
lsof -i :5000
kill -9 <PID>
```

**Static files not loading:**
```bash
# Collect static files
python manage.py collectstatic --clear

# Check STATIC_ROOT setting
python manage.py findstatic <filename>
```

**Database locked (SQLite):**
```bash
# Close all connections
# Restart development server
```

## Code Style

### Python (PEP 8)
- Line length: 88 characters (Black default)
- Use type hints where applicable
- Docstrings for all public functions

### JavaScript (ES6+)
- Use modern ES6+ syntax
- Prefer const/let over var
- Use template literals

### CSS
- BEM naming convention
- Mobile-first responsive design
- Use CSS custom properties for theming

## Git Workflow

### Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - Feature branches
- `hotfix/*` - Emergency fixes

### Commit Messages
```
feat: Add invoice PDF download feature
fix: Resolve database connection timeout
docs: Update deployment guide
style: Format code with Black
refactor: Optimize invoice query performance
test: Add unit tests for InvoiceService
```

## CI/CD Integration

### GitHub Actions (Recommended)
```yaml
name: Test and Deploy
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          python manage.py test
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Performance Profiling

### Django Debug Toolbar
- Query count and time
- Cache hit/miss ratios
- Template rendering time
- Signal execution

### Manual Profiling
```python
# Profile view
from django.utils.decorators import decorator_from_middleware
from django.middleware.profiling import ProfilerMiddleware

@decorator_from_middleware(ProfilerMiddleware)
def my_view(request):
    # View code
    pass
```

### Database Query Analysis
```python
# Enable query logging
import logging
logging.getLogger('django.db.backends').setLevel(logging.DEBUG)

# Analyze queries
from django.db import connection
print(connection.queries)
```

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)

---

**Happy Building! 🚀**
