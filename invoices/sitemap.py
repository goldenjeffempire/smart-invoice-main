"""
Dynamic sitemap for SEO.
Includes all public-facing pages for search engine crawling.
"""

from typing import List

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class HomeSitemap(Sitemap):
    """Homepage with highest priority."""

    changefreq = "weekly"
    priority = 1.0

    def items(self) -> List[str]:
        return ["home"]

    def location(self, item: str) -> str:
        return reverse(item)


class CorePagesSitemap(Sitemap):
    """Core marketing and product pages."""

    changefreq = "weekly"
    priority = 0.9

    def items(self) -> List[str]:
        return [
            "features",
            "pricing",
            "templates",
        ]

    def location(self, item: str) -> str:
        return reverse(item)


class CompanyPagesSitemap(Sitemap):
    """Company and about pages."""

    changefreq = "monthly"
    priority = 0.7

    def items(self) -> List[str]:
        return [
            "about",
            "careers",
            "contact",
            "blog",
        ]

    def location(self, item: str) -> str:
        return reverse(item)


class SupportPagesSitemap(Sitemap):
    """Support and documentation pages."""

    changefreq = "monthly"
    priority = 0.6

    def items(self) -> List[str]:
        return [
            "faq",
            "support",
            "api",
            "changelog",
            "status",
        ]

    def location(self, item: str) -> str:
        return reverse(item)


class LegalPagesSitemap(Sitemap):
    """Legal and compliance pages."""

    changefreq = "yearly"
    priority = 0.4

    def items(self) -> List[str]:
        return [
            "terms",
            "privacy",
            "security",
        ]

    def location(self, item: str) -> str:
        return reverse(item)


sitemaps = {
    "home": HomeSitemap,
    "core": CorePagesSitemap,
    "company": CompanyPagesSitemap,
    "support": SupportPagesSitemap,
    "legal": LegalPagesSitemap,
}
