from django.contrib import admin

from .models import Country,Profile

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name','abbr','is_active')
    search_fields = ('name','abbr')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','phone_number','country','verified')
    search_fields = ('user','phone_number')