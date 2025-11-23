from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Invoice, LineItem, UserProfile, InvoiceTemplate, RecurringInvoice, Waitlist
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

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

    def clean_email(self) -> str:
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class LoginForm(forms.Form):
    """Custom login form with styling."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })
    )


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['business_name', 'business_email', 'business_phone', 'business_address',
                 'client_name', 'client_email', 'client_phone', 'client_address',
                 'invoice_date', 'due_date', 'currency', 'tax_rate', 'notes']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'input-field'}),
            'business_email': forms.EmailInput(attrs={'class': 'input-field'}),
            'business_phone': forms.TextInput(attrs={'class': 'input-field'}),
            'business_address': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
            'client_name': forms.TextInput(attrs={'class': 'input-field'}),
            'client_email': forms.EmailInput(attrs={'class': 'input-field'}),
            'client_phone': forms.TextInput(attrs={'class': 'input-field'}),
            'client_address': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
            'invoice_date': forms.DateInput(attrs={'class': 'input-field', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'input-field', 'type': 'date'}),
            'currency': forms.Select(attrs={'class': 'input-field'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'input-field', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
        }

    def clean(self) -> dict:
        cleaned_data = super().clean()
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['company_name', 'company_logo', 'default_currency', 'default_tax_rate', 'invoice_prefix', 'timezone']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'input-field'}),
            'company_logo': forms.FileInput(attrs={'class': 'input-field', 'accept': 'image/*'}),
            'default_currency': forms.Select(attrs={'class': 'input-field'}),
            'default_tax_rate': forms.NumberInput(attrs={'class': 'input-field', 'step': '0.01'}),
            'invoice_prefix': forms.TextInput(attrs={'class': 'input-field'}),
            'timezone': forms.Select(attrs={'class': 'input-field'}),
        }


class NotificationPreferencesForm(forms.Form):
    email_on_invoice_created = forms.BooleanField(
        required=False,
        label='Email me when an invoice is created',
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-field'})
    )
    email_on_payment_received = forms.BooleanField(
        required=False,
        label='Email me when payment is received',
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-field'})
    )
    email_on_invoice_overdue = forms.BooleanField(
        required=False,
        label='Email me when an invoice is overdue',
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-field'})
    )
    weekly_summary = forms.BooleanField(
        required=False,
        label='Send me a weekly summary',
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-field'})
    )


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'Current Password',
            'autocomplete': 'current-password',
        })
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'New Password',
            'autocomplete': 'new-password',
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password',
        })
    )

    def clean(self) -> dict:
        cleaned_data = super().clean()
        if cleaned_data.get('new_password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class InvoiceTemplateForm(forms.ModelForm):
    class Meta:
        model = InvoiceTemplate
        fields = ['name', 'description', 'business_name', 'business_email', 'business_phone',
                 'business_address', 'currency', 'tax_rate', 'bank_name', 'account_name', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field'}),
            'description': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
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


class WaitlistForm(forms.ModelForm):
    """Form for email capture from landing page and Coming Soon pages."""
    class Meta:
        model = Waitlist
        fields = ['email', 'feature']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-4 focus:ring-indigo-600/20 focus:border-indigo-600 transition-all',
                'placeholder': 'your.email@example.com',
                'required': True,
            }),
            'feature': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-4 focus:ring-indigo-600/20 focus:border-indigo-600 transition-all',
            })
        }

    def clean_email(self) -> str:
        email = self.cleaned_data.get('email')
        if Waitlist.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already on our waitlist!")
        return email
