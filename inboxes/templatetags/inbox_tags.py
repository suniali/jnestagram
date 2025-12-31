from django import template

register = template.Library()

@register.filter
def short_username(value):
    if not value:
        return ""
    parts = value.split()
    res = "".join([part[0].upper() for part in parts[:2]])
    return res