from django.http import HttpResponseRedirect
from django.urls import reverse

from jnestagram.settings import STAGING
from .models import LandingPage

def landingpage_middleware(get_response):
    def middleware(request):
        # Before middleware
        if page_is_enabled('Maintenance'):
            if (request.path != reverse('maintenance')) and ('jnestagram-boss' not in request.path) and STAGING != 'True':
                return HttpResponseRedirect(reverse('maintenance'))

        response = get_response(request)

        # After middleware

        return response
    return middleware

def page_is_enabled(page_name):
    page=LandingPage.objects.filter(name=page_name).first()
    if page:
        return page.is_active
    else:
        return False