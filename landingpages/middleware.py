from django.http import HttpResponseRedirect
from django.urls import reverse

from jnestagram.settings import STAGING
from .models import LandingPage

def landingpage_middleware(get_response):
    def middleware(request):
        # Before middleware
        exempt_urls = [
            reverse('maintenance'),
            '/robots.txt',
            '/sitemap.xml',
            '/favicon.ico',
        ]
        if page_is_enabled('Maintenance'):
            is_exempt = any(request.path == url for url in exempt_urls)
            is_admin = 'jnestagram-boss' in request.path

            if not is_exempt and not is_admin:
                return HttpResponseRedirect(reverse('maintenance'))

        response = get_response(request)

        # After middleware
        if request.path in ['/robots.txt', '/sitemap.xml']:
            response['X-Robots-Tag'] = 'all'

        return response
    return middleware

def page_is_enabled(page_name):
    page=LandingPage.objects.filter(name=page_name).first()
    if page:
        return page.is_active
    else:
        return False