web: gunicorn invoiceflow.wsgi:application --bind 0.0.0.0:$PORT --workers 2
scheduler: python manage.py generate_recurring_invoices
