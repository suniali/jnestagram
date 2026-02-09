"""
URL configuration for jnestagram project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from django.views.generic import RedirectView,TemplateView

from .views import NotFoundView,InternalServerErrorView

# Site Maps
from django.contrib.sitemaps.views import sitemap
from posts.sitemaps import *

sitemaps = {
    'static':StaticSitemap,
    'category':CategorySitemap,
    'postpages':PostPageSitemap,
}

urlpatterns = [
    path('sitemap.xml',sitemap,{'sitemaps':sitemaps},name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
    path('admin/', include('admin_honeypot.urls')),
    path('jnestagram-boss/', admin.site.urls),
    path('',include('posts.urls')),
    path('',include('profiles.urls')),
    path('',include('inboxes.urls')),
    path('_/',include('landingpages.urls')),
]

handler404 = NotFoundView.as_view()
handler500 = InternalServerErrorView.as_view()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)