from django.db import models

class LandingPage(models.Model):
    name = models.CharField(max_length=255,unique=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
