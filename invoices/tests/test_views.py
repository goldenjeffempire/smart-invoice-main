import pytest
from django.contrib.auth.models import User
from django.test import Client
from invoices.models import Invoice


@pytest.mark.django_db
class TestAuthentication:
    def test_signup_creates_user(self):
        client = Client()
        response = client.post('/signup/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        })
        assert User.objects.filter(username='newuser').exists()
        
    def test_login_authenticates_user(self):
        client = Client()
        User.objects.create_user(username='testuser', password='12345')
        response = client.post('/login/', {
            'username': 'testuser',
            'password': '12345'
        })
        assert response.status_code == 302
        
    def test_home_page_accessible(self):
        client = Client()
        response = client.get('/')
        assert response.status_code == 200
