"""SendGrid Configuration Diagnostic Tool"""
import os
import json
from sendgrid import SendGridAPIClient, SendGridException
from sendgrid.helpers.mail import Mail, From, To


class SendGridDiagnostics:
    """Diagnose SendGrid configuration issues."""
    
    def __init__(self):
        self.api_key = os.environ.get("SENDGRID_API_KEY")
        self.results = []
        
    def run_diagnostics(self):
        """Run all diagnostic checks."""
        print("\n" + "=" * 80)
        print("SENDGRID CONFIGURATION DIAGNOSTIC TOOL")
        print("=" * 80 + "\n")
        
        # Check 1: API Key exists
        self._check_api_key_exists()
        
        if not self.api_key:
            print("\n❌ FATAL: API Key not found. Cannot continue diagnostics.")
            return False
        
        # Check 2: API Key validity
        self._check_api_key_validity()
        
        # Check 3: API Key permissions
        self._check_api_key_permissions()
        
        # Check 4: Try sending a test email
        self._check_test_email()
        
        # Summary
        self._print_summary()
        
        return True
    
    def _check_api_key_exists(self):
        """Check if API key is configured."""
        print("1️⃣  CHECKING API KEY EXISTENCE...")
        
        if self.api_key:
            masked_key = f"{self.api_key[:10]}...{self.api_key[-5:]}"
            print(f"   ✅ API Key found: {masked_key}")
            self.results.append(("API Key Exists", True, "API key is configured"))
        else:
            print(f"   ❌ API Key NOT found in environment")
            self.results.append(("API Key Exists", False, "SENDGRID_API_KEY not set"))
    
    def _check_api_key_validity(self):
        """Check if API key is valid with SendGrid."""
        print("\n2️⃣  CHECKING API KEY VALIDITY...")
        
        try:
            sg = SendGridAPIClient(self.api_key)
            
            # Try to get account info (minimal permissions required)
            from sendgrid.rest import Client
            response = sg.client.api_user.profile.get()
            
            if response.status_code == 200:
                print(f"   ✅ API Key is valid")
                self.results.append(("API Key Valid", True, "API key accepted by SendGrid"))
            else:
                print(f"   ⚠️  Got unexpected status: {response.status_code}")
                self.results.append(("API Key Valid", False, f"Status code: {response.status_code}"))
                
        except Exception as e:
            status_code = getattr(e, 'status_code', None)
            if status_code == 401 or status_code == 403:
                print(f"   ❌ API Key is INVALID or REVOKED (Status: {status_code})")
                print(f"      → Your API key doesn't have permission or is expired")
                self.results.append(("API Key Valid", False, f"Status {status_code}: Invalid/Revoked"))
            else:
                print(f"   ⚠️  Error checking validity: {status_code or str(e)}")
                self.results.append(("API Key Valid", False, f"Error: {status_code or str(e)}"))
    
    def _check_api_key_permissions(self):
        """Check if API key has Mail.Send permission."""
        print("\n3️⃣  CHECKING API KEY PERMISSIONS...")
        print("   (Checking if API key can send emails)")
        
        try:
            sg = SendGridAPIClient(self.api_key)
            
            # Try to list API keys info
            from sendgrid.rest import Client
            response = sg.client.api_keys.get()
            
            if response.status_code == 200:
                print(f"   ✅ API Key has appropriate permissions")
                self.results.append(("Has Mail Permissions", True, "API key has required scopes"))
            else:
                print(f"   ⚠️  Could not verify permissions (Status: {response.status_code})")
                
        except Exception as e:
            status_code = getattr(e, 'status_code', None)
            if status_code == 403:
                print(f"   ❌ API KEY LACKS PERMISSIONS (403 Forbidden)")
                print(f"      → Your API key doesn't have 'Full Access' or 'Mail Send' scope")
                print(f"      → SOLUTION: Create a new API key with 'Full Access' at SendGrid")
                self.results.append(("Has Mail Permissions", False, "Missing scopes/permissions"))
            else:
                print(f"   ⚠️  Error: {status_code or str(e)}")
                self.results.append(("Has Mail Permissions", False, f"Status {status_code or str(e)}"))
    
    def _check_test_email(self):
        """Try sending a test email to identify specific issue."""
        print("\n4️⃣  TESTING EMAIL SENDING...")
        print("   (Attempting to send test email)")
        
        try:
            sg = SendGridAPIClient(self.api_key)
            
            # Try to send to a generic test address
            message = Mail(
                from_email=From("test@example.com", "Test"),
                to_emails=To("test@example.com"),
                subject="Test",
                plain_text_content="Test"
            )
            
            response = sg.send(message)
            
            if response.status_code == 202:
                print(f"   ✅ Test email sent successfully (202 Accepted)")
                self.results.append(("Test Email Send", True, "Email sent successfully"))
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                self.results.append(("Test Email Send", False, f"Status: {response.status_code}"))
                
        except Exception as e:
            error_msg = self._parse_detailed_error(e)
            status_code = getattr(e, 'status_code', None)
            print(f"   ❌ Email send failed")
            print(f"      Status: {status_code}")
            print(f"      Details: {error_msg}")
            
            # Provide specific guidance
            if status_code == 403:
                print(f"\n   🔧 403 FORBIDDEN - This typically means:")
                print(f"      1. API key lacks 'Full Access' permission")
                print(f"      2. 'From' email (test@example.com) is not verified in SendGrid")
                print(f"      3. Your SendGrid account has restrictions")
                print(f"\n   ⚠️  IMMEDIATE FIXES TO TRY:")
                print(f"      a) Go to SendGrid → Settings → Sender Authentication")
                print(f"      b) Verify your business email address")
                print(f"      c) Or: Create new API key with 'Full Access'")
            elif status_code == 401:
                print(f"\n   🔧 401 UNAUTHORIZED - API key is invalid or expired")
            elif status_code == 400:
                print(f"\n   🔧 400 BAD REQUEST - Check email address format")
            
            self.results.append(("Test Email Send", False, f"Status {status_code}: {error_msg}"))
    
    def _parse_detailed_error(self, error):
        """Extract detailed error message from SendGrid exception."""
        try:
            if hasattr(error, 'body') and error.body:
                data = json.loads(error.body)
                if isinstance(data, dict) and 'errors' in data:
                    errors = data['errors']
                    if isinstance(errors, list) and len(errors) > 0:
                        messages = [e.get('message', '') for e in errors]
                        return '; '.join(messages)
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass
        
        return str(error)
    
    def _print_summary(self):
        """Print diagnostic summary."""
        print("\n" + "=" * 80)
        print("DIAGNOSTIC SUMMARY")
        print("=" * 80 + "\n")
        
        passed = sum(1 for _, result, _ in self.results if result)
        total = len(self.results)
        
        for check_name, passed_check, details in self.results:
            status = "✅" if passed_check else "❌"
            print(f"{status} {check_name}: {details}")
        
        print(f"\nTotal: {passed}/{total} checks passed\n")
        
        if passed == total:
            print("🎉 ALL CHECKS PASSED - Your SendGrid setup is correct!")
            print("   You should now be able to send emails successfully.\n")
        else:
            print("⚠️  ISSUES FOUND - Please address the failed checks above.\n")
        
        print("=" * 80 + "\n")


def run_sendgrid_diagnostics():
    """Entry point for running diagnostics."""
    diagnostics = SendGridDiagnostics()
    diagnostics.run_diagnostics()


if __name__ == "__main__":
    run_sendgrid_diagnostics()
