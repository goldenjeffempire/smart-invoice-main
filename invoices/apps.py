import os
import atexit
from django.apps import AppConfig


class InvoicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "invoices"

    def ready(self):
        from invoices.async_tasks import shutdown_executor
        atexit.register(shutdown_executor)

        if os.environ.get("RENDER"):
            from invoices.keep_alive import start_keep_alive
            start_keep_alive()
