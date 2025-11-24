"""
Dynamic sitemap for SEO.
"""
from typing import Any, List
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Invoice


class StaticSitemap(Sitemap):
    """Static pages sitemap."""
    
    changefreq = 'monthly'
    priority = 0.8
    
    def items(self) -> List[str]:
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
    
    def location(self, item: str) -> str:
        return reverse(item)


class InvoiceSitemap(Sitemap):
    """Dynamic invoice pages sitemap."""
    
    changefreq = 'weekly'
    priority = 0.6
    
    def items(self) -> List[Any]:
        # Only include paid invoices in sitemap for public visibility
        from typing import cast
        return cast(List[Any], list(Invoice.objects.filter(status='paid').order_by('-invoice_date')[:50000]))
    
    def location(self, item: Any) -> str:
        return reverse('invoice_detail', args=[item.id])
    
    def lastmod(self, item: Any) -> Any:
        return item.updated_at


sitemaps = {
    'static': StaticSitemap,
    'invoices': InvoiceSitemap,
}
