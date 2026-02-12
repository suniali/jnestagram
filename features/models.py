from django.db import models
from django.utils.translation import gettext_lazy as _

class Feature(models.Model):
    name = models.CharField(max_length=255, unique=True,verbose_name=_('Name'))
    developer = models.CharField(max_length=255, unique=True,verbose_name=_('Developer'))
    staging_enabled = models.BooleanField(default=False,verbose_name=_('Staging Enabled'))
    production_enabled = models.BooleanField(default=False,verbose_name=_('Production Enabled'))
    created_at = models.DateTimeField(auto_now_add=True,verbose_name=_('Created At'))

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['-created_at']
