from django import template

from cryptography.fernet import Fernet

from jnestagram.settings import env

register = template.Library()
f=Fernet(env('ENCRYPT_KEY'))

@register.filter
def short_username(value):
    if not value:
        return ""
    parts = value.split()
    res = "".join([part[0].upper() for part in parts[:2]])
    return res

@register.filter
def decrypt(value):
    if not value:
        return ""
    decrypt_message=f.decrypt(value)
    return decrypt_message.decode("utf-8")