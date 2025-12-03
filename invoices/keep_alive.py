import os
import threading
import time
import urllib.request
import urllib.error


def start_keep_alive():
    """
    Start a background thread that pings the app periodically
    to prevent Render's free tier from spinning down.
    """
    render_external_url = os.environ.get("RENDER_EXTERNAL_URL")
    
    if not render_external_url:
        return
    
    def ping():
        while True:
            try:
                health_url = f"{render_external_url}/health/"
                urllib.request.urlopen(health_url, timeout=10)
            except (urllib.error.URLError, urllib.error.HTTPError):
                pass
            except Exception:
                pass
            time.sleep(600)
    
    thread = threading.Thread(target=ping, daemon=True)
    thread.start()
