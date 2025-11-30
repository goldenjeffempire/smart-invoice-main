web: gunicorn invoiceflow.wsgi:application --config gunicorn.conf.py
scheduler: python manage.py generate_recurring_invoices
