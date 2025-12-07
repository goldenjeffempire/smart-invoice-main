# InvoiceFlow Deployment Guide

## Quick Deploy Options

### Replit Deployment
1. Click the "Deploy" button in your Replit project
2. Configure environment variables in the Secrets tab
3. Your app will be live at your Replit domain

### Render Deployment
1. Connect your GitHub repository to Render
2. Use the `render.yaml` configuration file
3. Add required environment variables:
   - `SECRET_KEY`
   - `DATABASE_URL` (auto-provisioned)
   - `SENDGRID_API_KEY`
   - `ENCRYPTION_SALT`

### Railway Deployment
1. Connect your GitHub repository
2. Railway will auto-detect the Dockerfile
3. Add environment variables in the Railway dashboard

### Docker Deployment
```bash
# Build and run with docker-compose (recommended)
# This uses the bundled PostgreSQL service with auto-configured DATABASE_URL
docker-compose up -d

# Or with custom environment for standalone container
docker build -t invoiceflow .
docker run -p 5000:5000 --env-file .env invoiceflow
```

**Note:** When using `docker-compose`, the `DATABASE_URL` is automatically configured to connect to the bundled PostgreSQL service. The password uses the `DB_PASSWORD` environment variable (defaults to `changeme`).

To use an external database, override `DATABASE_URL` in your `.env` file or environment.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | Django secret key |
| `DATABASE_URL` | No* | Bundled Postgres | PostgreSQL connection URL (auto-configured in docker-compose) |
| `DB_PASSWORD` | No | changeme | PostgreSQL password (used by docker-compose for bundled database) |
| `SENDGRID_API_KEY` | Yes | - | SendGrid API key for emails |
| `ENCRYPTION_SALT` | Yes | - | 64-byte encryption salt |
| `ALLOWED_HOSTS` | No | localhost,127.0.0.1 | Comma-separated allowed domains |
| `DEBUG` | No | False | Set to False in production |
| `SENTRY_DSN` | No | - | Sentry error tracking |

*When using `docker-compose`, `DATABASE_URL` is automatically configured to use the bundled PostgreSQL service.

## Security Features

The Docker image includes:
- Non-root user execution (appuser)
- Health checks for both web and database services
- Proper service dependency ordering
- Start period for graceful startup

## Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate secure `SECRET_KEY`
- [ ] Generate secure `ENCRYPTION_SALT`
- [ ] Set secure `DB_PASSWORD` (not the default)
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database (or use bundled service)
- [ ] Configure SendGrid for emails
- [ ] Enable HTTPS/SSL
- [ ] Set up Sentry for error monitoring
- [ ] Run `python manage.py migrate`
- [ ] Run `python manage.py collectstatic`
- [ ] Create superuser: `python manage.py createsuperuser`

## Health Check

The application exposes a health check endpoint at `/api/health/` that returns:
- Database connectivity status
- Cache availability
- Email service status

Both the web and database services have health checks configured in docker-compose.

## Gunicorn Configuration

Production command:
```bash
gunicorn --bind=0.0.0.0:5000 --workers=2 --timeout=120 invoiceflow.wsgi:application
```

Adjust workers based on CPU cores: `(2 * CPU_CORES) + 1`
