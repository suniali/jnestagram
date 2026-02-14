from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Tag,Post

class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 1.0
    def items(self):
        return ['home','about']

    def location(self, item):
        return reverse(item)

class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    def items(self):
        return Tag.objects.all()

    def location(self, item):
        return item.get_absolute_url().strip()

class PostPageSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Post.objects.all()[:100]

    def location(self, item):
        return item.get_absolute_url().strip()

    def lastmod(self, item):
        return item.updated_at