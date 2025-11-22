"""Signal handlers for Smart Invoice emails."""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Invoice, UserProfile
from .sendgrid_service import SendGridEmailService
import threading


@receiver(post_save, sender=User)
def send_welcome_email_on_signup(sender, instance, created, **kwargs):
    """Send welcome email when new user is created."""
    if created:
        def _send_in_background():
            try:
                service = SendGridEmailService()
                result = service.send_welcome_email(instance)
                if result.get('status') == 'sent':
                    print(f"✓ Welcome email sent to {instance.email}")
                else:
                    print(f"✗ Failed to send welcome email to {instance.email}")
            except Exception as e:
                print(f"Error sending welcome email: {str(e)}")
        
        # Send in background thread to avoid blocking
        thread = threading.Thread(target=_send_in_background, daemon=True)
        thread.start()


@receiver(post_save, sender=Invoice)
def handle_invoice_status_change(sender, instance, created, **kwargs):
    """Send appropriate email when invoice status changes."""
    if not created:  # Only on update, not on create
        # Check if status was just changed to 'paid'
        try:
            old_instance = Invoice.objects.get(pk=instance.pk)
            if old_instance.status != instance.status and instance.status == 'paid':
                # Invoice was just marked as paid - send payment notification
                def _send_paid_email():
                    try:
                        service = SendGridEmailService()
                        result = service.send_invoice_paid(instance, instance.client_email)
                        if result.get('status') == 'sent':
                            print(f"✓ Invoice paid email sent for Invoice #{instance.invoice_id}")
                        else:
                            print(f"✗ Failed to send invoice paid email")
                    except Exception as e:
                        print(f"Error sending invoice paid email: {str(e)}")
                
                thread = threading.Thread(target=_send_paid_email, daemon=True)
                thread.start()
        except Exception as e:
            print(f"Error in invoice status change handler: {str(e)}")
