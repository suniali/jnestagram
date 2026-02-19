import os
from django import template

from cryptography.fernet import Fernet

register = template.Library()
ENCRYPT_KEY = os.environ.get('ENCRYPT_KEY')
f = Fernet(ENCRYPT_KEY)

@register.filter
def decrypt_chat_message(message):
    if not message:
        return ""

    decrypt_message=f.decrypt(message)
    return decrypt_message.decode("utf-8")