"""
Performance optimization: Add database indexes for frequently queried fields
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0006_waitlist'),
    ]

    operations = [
        migrations.RunSQL(
            sql='CREATE INDEX IF NOT EXISTS idx_invoice_user_created ON invoices_invoice(user_id, created_at DESC)',
            reverse_sql='DROP INDEX IF EXISTS idx_invoice_user_created'
        ),
        migrations.RunSQL(
            sql='CREATE INDEX IF NOT EXISTS idx_invoice_user_status ON invoices_invoice(user_id, status)',
            reverse_sql='DROP INDEX IF EXISTS idx_invoice_user_status'
        ),
        migrations.RunSQL(
            sql='CREATE INDEX IF NOT EXISTS idx_invoice_id ON invoices_invoice(invoice_id)',
            reverse_sql='DROP INDEX IF EXISTS idx_invoice_id'
        ),
        migrations.RunSQL(
            sql='CREATE INDEX IF NOT EXISTS idx_invoice_status_created ON invoices_invoice(status, created_at DESC)',
            reverse_sql='DROP INDEX IF EXISTS idx_invoice_status_created'
        ),
    ]
