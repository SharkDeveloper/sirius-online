from rest_framework import serializers
from .models import Device

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['name', 'device_id', 'firmware_version', 'firmware_hex', 'firmare_chp', 'web_client']
