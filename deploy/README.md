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
# Build and run
docker-compose up -d

# Or with custom environment
docker build -t invoiceflow .
docker run -p 5000:5000 --env-file .env invoiceflow
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `DATABASE_URL` | Yes | PostgreSQL connection URL |
| `SENDGRID_API_KEY` | Yes | SendGrid API key for emails |
| `ENCRYPTION_SALT` | Yes | 64-byte encryption salt |
| `ALLOWED_HOSTS` | Yes | Comma-separated allowed domains |
| `DEBUG` | No | Set to False in production |
| `SENTRY_DSN` | No | Sentry error tracking |

## Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate secure `SECRET_KEY`
- [ ] Generate secure `ENCRYPTION_SALT`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database
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

## Gunicorn Configuration

Production command:
```bash
gunicorn --bind=0.0.0.0:5000 --workers=2 --timeout=120 invoiceflow.wsgi:application
```

Adjust workers based on CPU cores: `(2 * CPU_CORES) + 1`
