from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Invoice, LineItem, UserProfile, InvoiceTemplate, RecurringInvoice
from .validators import (
    validate_phone_number,
    validate_tax_rate,
    validate_invoice_date,
    validate_bank_account,
    validate_hex_color,
    validate_email_domain,
    validate_positive_decimal,
    InvoiceBusinessRules,
)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        validators=[validate_email_domain],
        widget=forms.EmailInput(attrs={
            'class': 'input-field',
            'placeholder': 'your.email@example.com',
            'autocomplete': 'email',
        })
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'First Name',
            'autocomplete': 'given-name',
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Last Name',
            'autocomplete': 'family-name',
        })
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Username',
                'autocomplete': 'username',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'input-field',
            'placeholder': 'Password',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'input-field',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password',
        })


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "business_name",
            "business_email",
            "business_phone",
            "business_address",
            "client_name",
            "client_email",
            "client_phone",
            "client_address",
            "invoice_date",
            "due_date",
            "currency",
            "tax_rate",
            "brand_name",
            "brand_color",
            "logo",
            "bank_name",
            "account_name",
            "account_number",
            "notes",
            "status",
        ]
        widgets = {
            "business_name": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "Your Business Name",
            }),
            "business_email": forms.EmailInput(attrs={
                "class": "input-field",
                "placeholder": "business@example.com",
            }),
            "business_phone": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "+1 (555) 123-4567",
            }),
            "business_address": forms.Textarea(attrs={
                "rows": 3,
                "class": "input-field",
                "placeholder": "123 Business St, City, State ZIP",
            }),
            "client_name": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "Client Name",
            }),
            "client_email": forms.EmailInput(attrs={
                "class": "input-field",
                "placeholder": "client@example.com",
            }),
            "client_phone": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "+1 (555) 987-6543",
            }),
            "client_address": forms.Textarea(attrs={
                "rows": 3,
                "class": "input-field",
                "placeholder": "456 Client Ave, City, State ZIP",
            }),
            "notes": forms.Textarea(attrs={
                "rows": 3,
                "class": "input-field",
                "placeholder": "Additional notes or payment terms...",
            }),
            "invoice_date": forms.DateInput(attrs={
                "type": "date",
                "class": "input-field",
            }),
            "due_date": forms.DateInput(attrs={
                "type": "date",
                "class": "input-field",
            }),
            "brand_color": forms.TextInput(attrs={
                "type": "color",
                "class": "h-12 w-full cursor-pointer",
            }),
            "brand_name": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "Your Brand",
            }),
            "bank_name": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "Bank Name",
            }),
            "account_name": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "Account Holder Name",
            }),
            "account_number": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "Account Number",
            }),
            "currency": forms.Select(attrs={
                "class": "input-field",
            }),
            "tax_rate": forms.NumberInput(attrs={
                "class": "input-field",
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0",
                "max": "100",
            }),
            "status": forms.Select(attrs={
                "class": "input-field",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom validators
        self.fields['business_phone'].validators.append(validate_phone_number)
        self.fields['client_phone'].validators.append(validate_phone_number)
        self.fields['business_email'].validators.append(validate_email_domain)
        self.fields['client_email'].validators.append(validate_email_domain)
        self.fields['tax_rate'].validators.append(validate_tax_rate)
        self.fields['invoice_date'].validators.append(validate_invoice_date)
        self.fields['brand_color'].validators.append(validate_hex_color)
        self.fields['account_number'].validators.append(validate_bank_account)
        
        # Mark required fields
        for field_name, field in self.fields.items():
            if field.required:
                field.label_suffix = " *"

    def clean(self):
        cleaned_data = super().clean()
        invoice_date = cleaned_data.get("invoice_date")
        due_date = cleaned_data.get("due_date")
        
        # Validate due date is after invoice date
        if invoice_date and due_date:
            InvoiceBusinessRules.validate_due_date(invoice_date, due_date)
        
        return cleaned_data


class LineItemForm(forms.ModelForm):
    class Meta:
        model = LineItem
        fields = ["description", "quantity", "unit_price"]
        widgets = {
            "description": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "Item description",
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "input-field",
                "step": "0.01",
                "min": "0.01",
                "placeholder": "1.00",
            }),
            "unit_price": forms.NumberInput(attrs={
                "class": "input-field",
                "step": "0.01",
                "min": "0",
                "placeholder": "0.00",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].validators.append(validate_positive_decimal)
        self.fields['unit_price'].validators.append(validate_positive_decimal)


class UserDetailsForm(forms.ModelForm):
    """Form for updating user account details."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition'
            }),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['company_name', 'company_logo', 'default_currency', 'default_tax_rate', 'invoice_prefix', 'timezone']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition',
                'placeholder': 'Company Name'
            }),
            'default_currency': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition'
            }),
            'default_tax_rate': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '0.00'
            }),
            'invoice_prefix': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition',
                'placeholder': 'INV',
                'maxlength': '10'
            }),
            'timezone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition',
                'placeholder': 'UTC'
            }),
        }


class NotificationPreferencesForm(forms.Form):
    """Form for notification preferences."""
    email_notifications = forms.BooleanField(
        required=False,
        label='Email Notifications',
        help_text='Receive email updates about your invoices'
    )
    payment_reminders = forms.BooleanField(
        required=False,
        label='Payment Reminders',
        help_text='Get notified when invoices are paid'
    )
    marketing_updates = forms.BooleanField(
        required=False,
        label='Marketing Updates',
        help_text='Receive updates about new features'
    )


class PasswordChangeForm(forms.Form):
    """Form for changing password."""
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition',
            'placeholder': 'Current password'
        }),
        label='Current Password'
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition',
            'placeholder': 'New password'
        }),
        label='New Password',
        help_text='Password must be at least 8 characters long'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition',
            'placeholder': 'Confirm password'
        }),
        label='Confirm Password'
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
            if len(new_password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")

        return cleaned_data


class InvoiceTemplateForm(forms.ModelForm):
    class Meta:
        model = InvoiceTemplate
        fields = ['name', 'description', 'business_name', 'business_email', 'business_phone', 
                 'business_address', 'currency', 'tax_rate', 'bank_name', 'account_name', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Template Name'}),
            'description': forms.Textarea(attrs={'class': 'input-field', 'rows': 3, 'placeholder': 'Description'}),
            'business_name': forms.TextInput(attrs={'class': 'input-field'}),
            'business_email': forms.EmailInput(attrs={'class': 'input-field'}),
            'business_phone': forms.TextInput(attrs={'class': 'input-field'}),
            'business_address': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
            'currency': forms.Select(attrs={'class': 'input-field'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'input-field', 'step': '0.01'}),
            'bank_name': forms.TextInput(attrs={'class': 'input-field'}),
            'account_name': forms.TextInput(attrs={'class': 'input-field'}),
        }


class RecurringInvoiceForm(forms.ModelForm):
    class Meta:
        model = RecurringInvoice
        fields = ['client_name', 'client_email', 'client_phone', 'client_address', 'frequency',
                 'start_date', 'end_date', 'business_name', 'business_email', 'currency', 
                 'tax_rate', 'status', 'next_generation', 'notes']
        widgets = {
            'client_name': forms.TextInput(attrs={'class': 'input-field'}),
            'client_email': forms.EmailInput(attrs={'class': 'input-field'}),
            'client_phone': forms.TextInput(attrs={'class': 'input-field'}),
            'client_address': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
            'frequency': forms.Select(attrs={'class': 'input-field'}),
            'start_date': forms.DateInput(attrs={'class': 'input-field', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'input-field', 'type': 'date'}),
            'business_name': forms.TextInput(attrs={'class': 'input-field'}),
            'business_email': forms.EmailInput(attrs={'class': 'input-field'}),
            'currency': forms.Select(attrs={'class': 'input-field'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'input-field', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'input-field'}),
            'next_generation': forms.DateInput(attrs={'class': 'input-field', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
        }


class InvoiceSearchForm(forms.Form):
    """Advanced search and filter form for invoices."""
    query = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'input-field',
        'placeholder': 'Search by invoice ID, client, or business name...',
        'aria-label': 'Search invoices'
    }))
    status = forms.ChoiceField(required=False, choices=[('', '-- All Statuses --'), ('paid', 'Paid'), ('unpaid', 'Unpaid')], 
                               widget=forms.Select(attrs={'class': 'input-field', 'aria-label': 'Filter by status'}))
    currency = forms.ChoiceField(required=False, choices=[('', '-- All Currencies --')] + list(Invoice.CURRENCY_CHOICES),
                                widget=forms.Select(attrs={'class': 'input-field', 'aria-label': 'Filter by currency'}))
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'input-field',
        'type': 'date',
        'aria-label': 'Invoice date from'
    }))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'input-field',
        'type': 'date',
        'aria-label': 'Invoice date to'
    }))
    min_amount = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'class': 'input-field',
        'placeholder': 'Min Amount',
        'step': '0.01',
        'aria-label': 'Minimum amount'
    }))
    max_amount = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'class': 'input-field',
        'placeholder': 'Max Amount',
        'step': '0.01',
        'aria-label': 'Maximum amount'
    }))
