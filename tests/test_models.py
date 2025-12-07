from decimal import Decimal

import pytest

from tests.factories import InvoiceFactory, InvoiceTemplateFactory, LineItemFactory


@pytest.mark.django_db
class TestInvoiceModel:
    def test_create_invoice(self):
        invoice = InvoiceFactory()
        assert invoice.pk is not None
        assert invoice.invoice_id.startswith("INV")
        assert invoice.status == "unpaid"

    def test_invoice_str(self):
        invoice = InvoiceFactory(client_name="Test Corp")
        assert "Test Corp" in str(invoice)

    def test_invoice_with_line_items(self):
        invoice = InvoiceFactory()
        LineItemFactory(invoice=invoice, quantity=Decimal("2"), unit_price=Decimal("50.00"))
        LineItemFactory(invoice=invoice, quantity=Decimal("1"), unit_price=Decimal("25.00"))

        assert invoice.line_items.count() == 2

    def test_invoice_subtotal_calculation(self):
        invoice = InvoiceFactory()
        LineItemFactory(invoice=invoice, quantity=Decimal("2"), unit_price=Decimal("50.00"))
        LineItemFactory(invoice=invoice, quantity=Decimal("1"), unit_price=Decimal("25.00"))

        assert invoice.subtotal == Decimal("125.00")

    def test_invoice_status_choices(self):
        invoice = InvoiceFactory(status="paid")
        assert invoice.status == "paid"

        invoice.status = "unpaid"
        invoice.save()
        invoice.refresh_from_db()
        assert invoice.status == "unpaid"


@pytest.mark.django_db
class TestLineItemModel:
    def test_create_line_item(self):
        line_item = LineItemFactory()
        assert line_item.pk is not None
        assert line_item.invoice is not None

    def test_line_item_total_calculation(self):
        line_item = LineItemFactory(quantity=Decimal("3"), unit_price=Decimal("100.00"))
        assert line_item.total == Decimal("300.00")


@pytest.mark.django_db
class TestInvoiceTemplateModel:
    def test_create_template(self):
        template = InvoiceTemplateFactory()
        assert template.pk is not None
        assert template.user is not None

    def test_template_str(self):
        template = InvoiceTemplateFactory(name="My Template")
        assert "My Template" in str(template)

    def test_template_tax_rate(self):
        template = InvoiceTemplateFactory(tax_rate=Decimal("15.00"))
        assert template.tax_rate == Decimal("15.00")
