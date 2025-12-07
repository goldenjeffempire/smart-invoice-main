import pytest

from tests.factories import InvoiceFactory, UserFactory


@pytest.mark.django_db
class TestDashboardView:
    def test_dashboard_requires_login(self, client):
        response = client.get("/invoices/dashboard/")
        assert response.status_code == 302
        assert "login" in response.url.lower()

    def test_dashboard_authenticated(self, authenticated_client):
        response = authenticated_client.get("/invoices/dashboard/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestInvoiceViews:
    def test_invoice_list_authenticated(self, authenticated_client, user):
        InvoiceFactory(user=user)
        response = authenticated_client.get("/invoices/list/")
        assert response.status_code == 200

    def test_invoice_detail_own_invoice(self, authenticated_client, user):
        invoice = InvoiceFactory(user=user)
        response = authenticated_client.get(f"/invoices/view/{invoice.pk}/")
        assert response.status_code == 200

    def test_invoice_detail_other_user(self, authenticated_client, user):
        other_user = UserFactory()
        invoice = InvoiceFactory(user=other_user)
        response = authenticated_client.get(f"/invoices/view/{invoice.pk}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestLandingPage:
    def test_landing_page_loads(self, client):
        response = client.get("/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestHealthCheck:
    def test_health_endpoint(self, client):
        response = client.get("/health/")
        assert response.status_code == 200
