from django.urls import path

from landingpages.views import MaintenanceView

urlpatterns = [
    path('maintenanace/', MaintenanceView.as_view(), name='maintenance'),
]