import os
import atexit
import threading
from django.apps import AppConfig


class InvoicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # type: ignore[misc]
    name = "invoices"

    def ready(self):
        import invoices.signals  # noqa: F401
        
        from invoices.async_tasks import shutdown_executor
        from invoices.services import CacheWarmingService
        
        atexit.register(shutdown_executor)
        atexit.register(CacheWarmingService.shutdown_executor)
        
        run_once_key = "_invoiceflow_cache_init_done"
        if not hasattr(self.__class__, run_once_key):
            setattr(self.__class__, run_once_key, True)
            
            def delayed_cache_init():
                import time
                time.sleep(3)
                try:
                    CacheWarmingService.bump_cache_version()
                    CacheWarmingService.warm_active_users_cache()
                except Exception:
                    pass
            
            warmup_thread = threading.Thread(
                target=delayed_cache_init, 
                daemon=True,
                name="cache_warmup_startup"
            )
            warmup_thread.start()

        if os.environ.get("RENDER"):
            from invoices.keep_alive import start_keep_alive
            start_keep_alive()
