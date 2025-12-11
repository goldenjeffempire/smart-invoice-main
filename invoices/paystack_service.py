"""
Paystack Payment Service for InvoiceFlow.
Handles payment processing, verification, and webhook handling.
"""

import hashlib
import hmac
import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

import requests
from django.conf import settings


class PaystackService:
    """Service for handling Paystack payment operations."""
    
    BASE_URL = "https://api.paystack.co"
    
    def __init__(self):
        self.secret_key = os.environ.get("PAYSTACK_SECRET_KEY", "")
        self.public_key = os.environ.get("PAYSTACK_PUBLIC_KEY", "")
        self.is_configured = bool(self.secret_key)
        
    @property
    def headers(self):
        """Get authorization headers for Paystack API."""
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }
    
    def initialize_payment(
        self,
        email: str,
        amount: Decimal,
        currency: str = "NGN",
        reference: Optional[str] = None,
        callback_url: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Initialize a payment transaction.
        
        Args:
            email: Customer's email address
            amount: Amount in the currency's base unit (e.g., Naira for NGN)
            currency: Currency code (NGN, USD, GHS, ZAR, KES)
            reference: Unique transaction reference
            callback_url: URL to redirect to after payment
            metadata: Additional data to attach to the transaction
        
        Returns:
            dict with authorization_url and reference, or error details
        """
        if not self.is_configured:
            return {
                "status": "error",
                "message": "Paystack is not configured. Please set PAYSTACK_SECRET_KEY.",
                "configured": False,
            }
        
        amount_kobo = int(amount * 100)
        
        payload = {
            "email": email,
            "amount": amount_kobo,
            "currency": currency,
        }
        
        if reference:
            payload["reference"] = reference
        if callback_url:
            payload["callback_url"] = callback_url
        if metadata:
            payload["metadata"] = metadata
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/transaction/initialize",
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get("status"):
                return {
                    "status": "success",
                    "authorization_url": data["data"]["authorization_url"],
                    "access_code": data["data"]["access_code"],
                    "reference": data["data"]["reference"],
                }
            else:
                return {
                    "status": "error",
                    "message": data.get("message", "Failed to initialize payment"),
                }
        
        except requests.RequestException as e:
            return {
                "status": "error",
                "message": f"Network error: {str(e)}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
            }
    
    def verify_payment(self, reference: str) -> dict[str, Any]:
        """
        Verify a payment transaction.
        
        Args:
            reference: Transaction reference to verify
        
        Returns:
            dict with transaction status and details
        """
        if not self.is_configured:
            return {
                "status": "error",
                "message": "Paystack is not configured.",
                "configured": False,
            }
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/transaction/verify/{reference}",
                headers=self.headers,
                timeout=30,
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get("status"):
                transaction = data["data"]
                return {
                    "status": "success",
                    "verified": transaction["status"] == "success",
                    "amount": Decimal(transaction["amount"]) / 100,
                    "currency": transaction["currency"],
                    "reference": transaction["reference"],
                    "paid_at": transaction.get("paid_at"),
                    "channel": transaction.get("channel"),
                    "customer_email": transaction.get("customer", {}).get("email"),
                    "metadata": transaction.get("metadata", {}),
                    "raw_data": transaction,
                }
            else:
                return {
                    "status": "error",
                    "message": data.get("message", "Failed to verify payment"),
                    "verified": False,
                }
        
        except requests.RequestException as e:
            return {
                "status": "error",
                "message": f"Network error: {str(e)}",
                "verified": False,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "verified": False,
            }
    
    def create_payment_link(
        self,
        name: str,
        amount: Decimal,
        description: str = "",
        currency: str = "NGN",
        redirect_url: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Create a reusable payment link/page.
        
        Args:
            name: Name of the payment page
            amount: Amount in currency's base unit
            description: Description of what customer is paying for
            currency: Currency code
            redirect_url: URL to redirect after payment
            metadata: Additional data
        
        Returns:
            dict with payment link details
        """
        if not self.is_configured:
            return {
                "status": "error",
                "message": "Paystack is not configured.",
                "configured": False,
            }
        
        amount_kobo = int(amount * 100)
        
        payload = {
            "name": name,
            "amount": amount_kobo,
            "currency": currency,
        }
        
        if description:
            payload["description"] = description
        if redirect_url:
            payload["redirect_url"] = redirect_url
        if metadata:
            payload["metadata"] = metadata
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/page",
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            
            data = response.json()
            
            if response.status_code in [200, 201] and data.get("status"):
                page = data["data"]
                return {
                    "status": "success",
                    "id": page["id"],
                    "slug": page["slug"],
                    "url": f"https://paystack.com/pay/{page['slug']}",
                }
            else:
                return {
                    "status": "error",
                    "message": data.get("message", "Failed to create payment link"),
                }
        
        except requests.RequestException as e:
            return {
                "status": "error",
                "message": f"Network error: {str(e)}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
            }
    
    def list_banks(self, country: str = "nigeria") -> dict[str, Any]:
        """
        Get list of supported banks for transfers.
        
        Args:
            country: Country code (nigeria, ghana, south-africa, kenya)
        
        Returns:
            dict with list of banks
        """
        if not self.is_configured:
            return {
                "status": "error",
                "message": "Paystack is not configured.",
                "configured": False,
            }
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/bank",
                headers=self.headers,
                params={"country": country},
                timeout=30,
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get("status"):
                return {
                    "status": "success",
                    "banks": data["data"],
                }
            else:
                return {
                    "status": "error",
                    "message": data.get("message", "Failed to fetch banks"),
                }
        
        except requests.RequestException as e:
            return {
                "status": "error",
                "message": f"Network error: {str(e)}",
            }
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Paystack webhook signature.
        
        Args:
            payload: Raw request body bytes
            signature: X-Paystack-Signature header value
        
        Returns:
            True if signature is valid
        """
        if not self.secret_key:
            return False
        
        expected_signature = hmac.new(
            self.secret_key.encode("utf-8"),
            payload,
            hashlib.sha512,
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def get_transaction_history(
        self,
        page: int = 1,
        per_page: int = 50,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Get transaction history.
        
        Args:
            page: Page number
            per_page: Number of transactions per page
            status: Filter by status (success, failed, abandoned)
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
        
        Returns:
            dict with transaction list
        """
        if not self.is_configured:
            return {
                "status": "error",
                "message": "Paystack is not configured.",
                "configured": False,
            }
        
        params: dict[str, Any] = {
            "page": page,
            "perPage": per_page,
        }
        
        if status:
            params["status"] = status
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/transaction",
                headers=self.headers,
                params=params,
                timeout=30,
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get("status"):
                return {
                    "status": "success",
                    "transactions": data["data"],
                    "meta": data.get("meta", {}),
                }
            else:
                return {
                    "status": "error",
                    "message": data.get("message", "Failed to fetch transactions"),
                }
        
        except requests.RequestException as e:
            return {
                "status": "error",
                "message": f"Network error: {str(e)}",
            }


def get_paystack_service():
    """Get Paystack service instance."""
    return PaystackService()
