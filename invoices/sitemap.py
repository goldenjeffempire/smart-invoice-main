"""
Dynamic sitemap for SEO.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Invoice


class StaticSitemap(Sitemap):
    """Static pages sitemap."""
    
    changefreq = 'monthly'
    priority = 0.8
    
    def items(self):
        return [
            'home',
            'features',
            'pricing',
            'about',
            'contact',
            'faq',
            'terms',
            'privacy',
        ]
    
    def location(self, item):
        return reverse(item)


class InvoiceSitemap(Sitemap):
    """Dynamic invoice pages sitemap."""
    
    changefreq = 'weekly'
    priority = 0.6
    
    def items(self):
        # Only include paid invoices in sitemap for public visibility
        return Invoice.objects.filter(status='paid').order_by('-invoice_date')[:50000]
    
    def location(self, obj):
        return reverse('invoice_detail', args=[obj.id])
    
    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    'static': StaticSitemap,
    'invoices': InvoiceSitemap,
}
