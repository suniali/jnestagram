from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class Country(models.Model):
    name = models.CharField(max_length=50,verbose_name=_('Country Name'))
    abbr = models.CharField(max_length=5,verbose_name=_('Country Abbreviation'))
    is_active = models.BooleanField(default=True,verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True,verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True,verbose_name=_('Updated At'))

    class Meta:
        db_table = 'countries'
        verbose_name='Country'
        verbose_name_plural='Countries'

    def __str__(self):
        return self.name

class Profile(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,related_name='profile',on_delete=models.CASCADE,verbose_name=_('User'))
    phone_number=models.BigIntegerField(blank=True,null=True,unique=True,db_index=True,verbose_name=_('Phone Number'))
    country=models.ForeignKey(to=Country,related_name='country',on_delete=models.SET_NULL,null=True,blank=True,verbose_name=_('Country'))
    avatar=ProcessedImageField(
        blank=True,
        upload_to='avatars/',
        processors=[ResizeToFill(150,150)],
        format='WEBP',
        options={'quality': 80},
        verbose_name=_('Avatar'),
    )
    bio=models.TextField(max_length=500,blank=True,null=True,verbose_name=_('Bio'))
    verified=models.BooleanField(default=False,verbose_name=_('Verified'))

    class Meta:
        db_table = 'profiles'
        verbose_name='Profile'
        verbose_name_plural='Profiles'

    def __str__(self):
        return self.user.username

    @property
    def realname(self):
        if self.user.first_name and self.user.last_name:
            return f'{self.user.first_name} {self.user.last_name}'
        else:
            return self.user.username
    

# TODO: Add Device Model Too
# class Device(models.Model):
#     DEVICE_WEB=1
#     DEVICE_IOS=2
#     DEVICE_ANDROID=3
#     DEVICE_CHOICES=(
#         (DEVICE_WEB,'Web'),
#         (DEVICE_IOS,'IOS'),
#         (DEVICE_ANDROID,'Android'),
#     )
#     user=models.ForeignKey(to=settings.AUTH_USER_MODEL,related_name='user',on_delete=models.CASCADE)
#     device_uuid = models.UUIDField('device UUID', null=True)
#     last_login = models.DateTimeField('last login date', null=True)
#     device_type = models.PositiveSmallIntegerField(choices=DEVICE_CHOICES, default=DEVICE_WEB)
#     device_os = models.CharField('device OS', max_length=50, blank=True)
#     device_model = models.CharField('device model', max_length=50, blank=True)
#     app_version = models.CharField('app version', max_length=20, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         db_table = 'devices'
#         verbose_name = 'Device'
#         verbose_name_plural = 'Devices'
