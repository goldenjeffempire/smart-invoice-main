"""
Dynamic sitemap for SEO.
"""

from typing import List

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticSitemap(Sitemap):
    """Static pages sitemap."""

    changefreq = "monthly"
    priority = 0.8

    def items(self) -> List[str]:
        return [
            "home",
            "features",
            "pricing",
            "about",
            "contact",
            "faq",
            "terms",
            "privacy",
        ]

    def location(self, item: str) -> str:
        return reverse(item)


sitemaps = {
    "static": StaticSitemap,
}
