from django.db import models
from django.utils.translation import gettext_lazy as _

class LandingPage(models.Model):
    name = models.CharField(max_length=255,unique=True,verbose_name=_('Name'))
    is_active = models.BooleanField(default=False,verbose_name=_('Is Active'))

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
