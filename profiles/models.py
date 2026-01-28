from django.db import models
from django.conf import settings

from django_resized import ResizedImageField


class Country(models.Model):
    name = models.CharField(max_length=50)
    abbr = models.CharField(max_length=5)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'countries'
        verbose_name='Country'
        verbose_name_plural='Countries'

    def __str__(self):
        return self.name

class Profile(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,related_name='profile',on_delete=models.CASCADE)
    phone_number=models.BigIntegerField(blank=True,null=True,unique=True,db_index=True)
    country=models.ForeignKey(to=Country,related_name='country',on_delete=models.SET_NULL,null=True,blank=True)
    avatar=ResizedImageField(size=[600,600],quality=85,blank=True,upload_to='avatars/')
    bio=models.TextField(max_length=500,blank=True,null=True)
    verified=models.BooleanField(default=False)

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
