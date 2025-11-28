# type: ignore
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap as sitemap_view
from invoices import views
from invoices.health import health_check, readiness_check, liveness_check
from invoices.sitemap import sitemaps

handler404 = "invoices.views.custom_404"
handler500 = "invoices.views.custom_500"

urlpatterns = [
    # Health checks
    path("health/", health_check, name="health_check"),
    path("health/ready/", readiness_check, name="readiness_check"),
    path("health/live/", liveness_check, name="liveness_check"),
    # Robots.txt (dynamic)
    path("robots.txt", views.robots_txt, name="robots_txt"),
    # Sitemap for SEO
    path(
        "sitemap.xml",
        sitemap_view,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # Admin
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Settings pages
    path("settings/", views.settings_view, name="settings"),
    path("settings/profile/", views.settings_profile, name="settings_profile"),
    path("settings/business/", views.settings_business, name="settings_business"),
    path("settings/security/", views.settings_security, name="settings_security"),
    path("settings/notifications/", views.settings_notifications, name="settings_notifications"),
    path("settings/billing/", views.settings_billing, name="settings_billing"),
    # Design System (Phase 1)
    path("components-showcase/", views.components_showcase, name="components_showcase"),
    # Footer pages
    path("features/", views.features, name="features"),
    path("pricing/", views.pricing, name="pricing"),
    path("templates/", views.templates_page, name="templates"),
    path("api-access/", views.api_access, name="api"),
    path("about/", views.about, name="about"),
    path("careers/", views.careers, name="careers"),
    path("contact/", views.contact, name="contact"),
    path("changelog/", views.changelog, name="changelog"),
    path("system-status/", views.system_status, name="status"),
    path("support/", views.support, name="support"),
    path("faq/", views.faq, name="faq"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("newsletter/signup/", views.newsletter_signup, name="newsletter_signup"),
    # User features
    path("profile/", views.profile, name="profile"),
    path("my-templates/", views.invoice_templates, name="invoice_templates"),
    path("my-templates/<int:template_id>/delete/", views.delete_template, name="delete_template"),
    path("recurring/", views.recurring_invoices, name="recurring_invoices"),
    path("bulk/export/", views.bulk_export, name="bulk_export"),
    path("bulk/delete/", views.bulk_delete, name="bulk_delete"),
    # Admin endpoints
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-users/", views.admin_users, name="admin_users"),
    path("admin-content/", views.admin_content, name="admin_content"),
    path("admin-settings/", views.admin_settings, name="admin_settings"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("invoices/", include("invoices.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
