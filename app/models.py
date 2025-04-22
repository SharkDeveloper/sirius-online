from djongo import models
from django.utils import timezone
#TODO mongo --username "admin" --password "admin" --authenticationDatabase "admin" mongodb://localhost:27017/siriusdb

def device_directory_path(instance, filename):
    # Создание пути на основе значения device_id
    return f'devices/{instance.device_id}/{filename}'

class Device(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    name = models.CharField(max_length=100, default="Сириус")
    device_id = models.IntegerField(unique=True)
    lk_id = models.IntegerField(unique=True, default=0)
    firmware_version = models.CharField(max_length=100, blank=True)
    firmware_hex = models.FileField(verbose_name="firmware_hex", upload_to=device_directory_path, blank=True)
    firmware_chp = models.FileField(verbose_name="firmware_chp", upload_to=device_directory_path, blank=True)
    web_client = models.FileField(verbose_name="web_client", upload_to=device_directory_path, blank=True)
    live_view_panel = models.FileField(verbose_name="live_view_panel", upload_to=device_directory_path, blank=True)
    session = models.CharField(max_length=100, default="")  
    is_active = models.BooleanField(default=False)
    access_token = models.CharField(max_length=250, default="")
    verify_code = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'

class Events(models.Model):
    device_id = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='events')
    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'


class States(models.Model):
    device_id = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='states')
    class Meta:
        verbose_name = 'State'
        verbose_name_plural = 'States'

class Setting(models.Model):
    value = models.TextField()

    class Meta:
        abstract = True

class Configs(models.Model):
    device_id = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='config')
    settings_info = models.ArrayField(model_container=Setting)
    settings_read = models.ArrayField(model_container=Setting)

    class Meta:
        verbose_name = 'Config'
        verbose_name_plural = 'Configs'
