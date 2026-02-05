from django.shortcuts import render
from django.views.generic import View

class MaintenanceView(View):
    template_name = 'landingpages/maintenance.html'

    def get(self, request):
       return render(request,self.template_name)
