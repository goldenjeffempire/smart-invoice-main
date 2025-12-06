"""Environment variable validation for application startup."""

import os
import sys
import logging
from typing import NamedTuple

logger = logging.getLogger(__name__)


class EnvVar(NamedTuple):
    name: str
    required: bool
    description: str
    default: str | None = None


REQUIRED_ENV_VARS = [
    EnvVar("SECRET_KEY", True, "Django secret key for cryptographic signing"),
    EnvVar("DATABASE_URL", True, "PostgreSQL database connection URL"),
]

OPTIONAL_ENV_VARS = [
    EnvVar("DEBUG", False, "Enable debug mode", "False"),
    EnvVar("ALLOWED_HOSTS", False, "Comma-separated list of allowed hosts", "*"),
    EnvVar("PAYSTACK_SECRET_KEY", False, "Paystack API key for payments"),
    EnvVar("SENTRY_DSN", False, "Sentry DSN for error tracking"),
    EnvVar("MFA_ENABLED", False, "Enable multi-factor authentication", "True"),
]

# These are managed by Replit connectors and should not trigger warnings
CONNECTOR_MANAGED_VARS = [
    EnvVar("SENDGRID_API_KEY", False, "SendGrid API key (managed by Replit connector)"),
    EnvVar("SENDGRID_FROM_EMAIL", False, "Default sender email (managed by Replit connector)"),
]


def validate_environment(exit_on_error: bool = True) -> dict[str, list[str]]:
    """
    Validate required environment variables on startup.
    
    Args:
        exit_on_error: If True, exit the application on missing required vars
        
    Returns:
        Dictionary with 'missing' and 'warnings' lists
    """
    results = {
        "missing": [],
        "warnings": [],
        "configured": [],
    }
    
    for env_var in REQUIRED_ENV_VARS:
        value = os.environ.get(env_var.name)
        if not value:
            results["missing"].append(f"{env_var.name}: {env_var.description}")
            logger.error(f"Missing required environment variable: {env_var.name}")
        else:
            results["configured"].append(env_var.name)
    
    for env_var in OPTIONAL_ENV_VARS:
        value = os.environ.get(env_var.name)
        if not value and env_var.default is None:
            results["warnings"].append(f"{env_var.name}: {env_var.description}")
            logger.warning(f"Optional environment variable not set: {env_var.name}")
        elif value:
            results["configured"].append(env_var.name)
    
    if results["missing"]:
        error_msg = (
            f"\n{'='*60}\n"
            f"CRITICAL: Missing required environment variables!\n"
            f"{'='*60}\n"
            + "\n".join(f"  - {var}" for var in results["missing"])
            + f"\n{'='*60}\n"
            f"Please configure these variables before starting the application.\n"
        )
        logger.critical(error_msg)
        
        if exit_on_error:
            print(error_msg, file=sys.stderr)
            sys.exit(1)
    
    if results["configured"]:
        logger.info(f"Environment validation passed. Configured: {len(results['configured'])} variables")
    
    return results


def _check_replit_sendgrid_connector() -> bool:
    """Check if SendGrid is available via Replit connector."""
    try:
        import urllib.request
        import json
        
        hostname = os.environ.get("REPLIT_CONNECTORS_HOSTNAME")
        token = os.environ.get("REPL_IDENTITY") or os.environ.get("WEB_REPL_RENEWAL")
        
        if not hostname or not token:
            return False
        
        token_header = f"repl {token}" if "REPL_IDENTITY" in os.environ else f"depl {token}"
        url = f"https://{hostname}/api/v2/connection?include_secrets=true&connector_names=sendgrid"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/json")
        req.add_header("X_REPLIT_TOKEN", token_header)
        
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            connection = data.get("items", [{}])[0]
            settings = connection.get("settings", {})
            return bool(settings.get("api_key") and settings.get("from_email"))
    except Exception:
        return False


def get_env_status() -> dict:
    """Get current environment configuration status for health checks."""
    status = {
        "required": {},
        "optional": {},
        "connector_managed": {},
    }
    
    for env_var in REQUIRED_ENV_VARS:
        value = os.environ.get(env_var.name)
        status["required"][env_var.name] = {
            "configured": bool(value),
            "description": env_var.description
        }
    
    for env_var in OPTIONAL_ENV_VARS:
        value = os.environ.get(env_var.name)
        status["optional"][env_var.name] = {
            "configured": bool(value),
            "description": env_var.description,
            "has_default": env_var.default is not None
        }
    
    # Check connector-managed variables
    sendgrid_connected = _check_replit_sendgrid_connector()
    for env_var in CONNECTOR_MANAGED_VARS:
        env_value = os.environ.get(env_var.name)
        status["connector_managed"][env_var.name] = {
            "configured": sendgrid_connected or bool(env_value),
            "description": env_var.description,
            "via_connector": sendgrid_connected
        }
    
    return status
