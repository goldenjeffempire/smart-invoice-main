# Smart Invoice API Documentation

## Health Check Endpoints

### Health Status
```
GET /health/
```
Returns basic health status.

### Readiness Check
```
GET /health/ready/
```
Verifies database connectivity - use for Kubernetes readiness probes.

### Liveness Check
```
GET /health/live/
```
Simple liveness probe - use for Kubernetes liveness probes.

## Invoice Endpoints

### Create Invoice
```
POST /invoices/create/
```
Create new invoice with line items.

**Request:**
```json
{
  "invoice_id": "INV-001",
  "client_name": "John Doe",
  "client_email": "john@example.com",
  "total": 1500.00,
  "currency": "USD"
}
```

### Get Invoice Details
```
GET /invoices/<id>/
```
Retrieve invoice details and line items.

### Generate PDF
```
GET /invoices/<id>/pdf/
```
Generate and download PDF invoice.

### Send Invoice
```
POST /invoices/<id>/send/
```
Send invoice via email or WhatsApp.

## Authentication
All invoice endpoints require login. Use Django's session authentication or JWT tokens.

## Error Responses
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "status": 400
}
```

## Rate Limiting
- Email sends: 100/hour per user
- PDF generation: 500/hour per user
- API calls: 1000/hour per user
