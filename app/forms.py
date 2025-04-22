from django import forms
from .models import Device

class UpdateWebForm(forms.Form):
    class Meta:
      model = Device
      fields = ['web_client']
