#!/usr/bin/env python
"""
SSL Certificate Setup Script for InvoiceFlow Production Deployment
Writes SSL certificates from environment variables to secure files
"""

import os
import sys
from pathlib import Path


def setup_ssl_certificates():
    """Write SSL certificates from environment variables to files."""

    # Create certs directory
    certs_dir = Path("/tmp/invoiceflow-certs")
    certs_dir.mkdir(exist_ok=True, mode=0o700)

    cert_file = certs_dir / "certificate.pem"
    key_ec_file = certs_dir / "private-key-ec.pem"
    key_rsa_file = certs_dir / "private-key-rsa.pem"

    # Get certificates from environment
    ssl_certificate = os.environ.get("SSL_CERTIFICATE", "")
    ssl_key_ec = os.environ.get("SSL_PRIVATE_KEY_EC", "")
    ssl_key_rsa = os.environ.get("SSL_PRIVATE_KEY_RSA", "")

    if not all([ssl_certificate, ssl_key_ec, ssl_key_rsa]):
        print("WARNING: SSL certificates not fully configured in environment")
        print("HTTPS will not be available")
        return False

    try:
        # Write certificate
        with open(cert_file, "w") as f:
            f.write(ssl_certificate)
        cert_file.chmod(0o600)
        print(f"✓ SSL certificate written to {cert_file}")

        # Write EC private key
        with open(key_ec_file, "w") as f:
            f.write(ssl_key_ec)
        key_ec_file.chmod(0o600)
        print(f"✓ EC private key written to {key_ec_file}")

        # Write RSA private key
        with open(key_rsa_file, "w") as f:
            f.write(ssl_key_rsa)
        key_rsa_file.chmod(0o600)
        print(f"✓ RSA private key written to {key_rsa_file}")

        # Export paths as environment variables for Gunicorn
        os.environ["SSL_CERTFILE"] = str(cert_file)
        os.environ["SSL_KEYFILE"] = str(key_rsa_file)

        print("\n✓ SSL setup complete - HTTPS will be available")
        return True

    except Exception as e:
        print(f"ERROR: Failed to setup SSL certificates: {e}")
        return False


if __name__ == "__main__":
    success = setup_ssl_certificates()
    sys.exit(0 if success else 1)
