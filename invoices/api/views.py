from io import BytesIO

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from django.db.models import Prefetch
from django.http import FileResponse

from invoices.models import Invoice, LineItem, InvoiceTemplate
from invoices.services import AnalyticsService, PDFService
from .serializers import (
    InvoiceListSerializer,
    InvoiceDetailSerializer,
    InvoiceCreateSerializer,
    InvoiceStatusSerializer,
    InvoiceTemplateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List invoices",
        description="Retrieve a paginated list of invoices for the authenticated user.",
        parameters=[
            OpenApiParameter(name="status", description="Filter by status (paid/unpaid)", required=False, type=str),
            OpenApiParameter(name="search", description="Search by client name or invoice ID", required=False, type=str),
            OpenApiParameter(name="ordering", description="Order by field (e.g., -created_at, due_date)", required=False, type=str),
        ],
    ),
    retrieve=extend_schema(
        summary="Get invoice details",
        description="Retrieve detailed information about a specific invoice including line items.",
    ),
    create=extend_schema(
        summary="Create invoice",
        description="Create a new invoice with line items.",
    ),
    update=extend_schema(
        summary="Update invoice",
        description="Update an existing invoice and its line items.",
    ),
    partial_update=extend_schema(
        summary="Partial update invoice",
        description="Partially update an invoice.",
    ),
    destroy=extend_schema(
        summary="Delete invoice",
        description="Delete an invoice.",
    ),
)
class InvoiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["invoice_id", "client_name", "client_email"]
    ordering_fields = ["created_at", "invoice_date", "due_date", "total", "status"]
    ordering = ["-created_at"]
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    def get_serializer_class(self):
        if self.action == "list":
            return InvoiceListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return InvoiceCreateSerializer
        elif self.action == "update_status":
            return InvoiceStatusSerializer
        return InvoiceDetailSerializer

    def get_queryset(self):
        queryset = Invoice.objects.filter(user=self.request.user).prefetch_related("line_items")
        
        status_filter = self.request.query_params.get("status")
        if status_filter in ["paid", "unpaid"]:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        AnalyticsService.invalidate_user_cache(self.request.user.id)
        return instance

    def perform_destroy(self, instance):
        user_id = self.request.user.id
        instance.delete()
        AnalyticsService.invalidate_user_cache(user_id)

    @extend_schema(
        summary="Update invoice status",
        description="Update the payment status of an invoice (paid/unpaid).",
        request=InvoiceStatusSerializer,
        responses={200: InvoiceDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="status")
    def update_status(self, request, pk=None, version=None):
        invoice = self.get_object()
        serializer = InvoiceStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invoice.status = serializer.validated_data["status"]
        invoice.save()
        AnalyticsService.invalidate_user_cache(request.user.id)
        
        return Response(InvoiceDetailSerializer(invoice).data)

    @extend_schema(
        summary="Generate PDF",
        description="Generate and download PDF for an invoice.",
        responses={200: {"type": "string", "format": "binary"}},
    )
    @action(detail=True, methods=["get"], url_path="pdf")
    def generate_pdf(self, request, pk=None, version=None):
        invoice = self.get_object()
        pdf_bytes = PDFService.generate_pdf_bytes(invoice)
        
        response = FileResponse(
            BytesIO(pdf_bytes),
            as_attachment=True,
            filename=f"Invoice_{invoice.invoice_id}.pdf",
            content_type="application/pdf",
        )
        return response

    @extend_schema(
        summary="Get dashboard statistics",
        description="Get aggregated statistics for the authenticated user's invoices.",
    )
    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request, version=None):
        stats = AnalyticsService.get_user_dashboard_stats(request.user)
        return Response(stats)


@extend_schema_view(
    list=extend_schema(
        summary="List invoice templates",
        description="Retrieve all invoice templates for the authenticated user.",
    ),
    retrieve=extend_schema(
        summary="Get template details",
        description="Retrieve a specific invoice template.",
    ),
    create=extend_schema(
        summary="Create template",
        description="Create a new invoice template.",
    ),
    update=extend_schema(
        summary="Update template",
        description="Update an existing invoice template.",
    ),
    destroy=extend_schema(
        summary="Delete template",
        description="Delete an invoice template.",
    ),
)
class InvoiceTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceTemplateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        return InvoiceTemplate.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
