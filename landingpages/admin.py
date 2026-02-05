from django.contrib import admin

from .models import LandingPage

@admin.register(LandingPage)
class LandingPageAdmin(admin.ModelAdmin):
    list_display = ('id','name','is_active')
