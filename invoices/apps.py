import os
from django.apps import AppConfig


class InvoicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "invoices"
    
    def ready(self):
        import invoices.signals
        
        # Start keep-alive on Render to prevent free tier spin-down
        if os.environ.get('RENDER'):
            from invoices.keep_alive import start_keep_alive
            start_keep_alive()
