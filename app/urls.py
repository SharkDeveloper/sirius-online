from django.urls import path
from .views import FirmwareChpUploadView, FirmwareHexUploadView, WebClientUploadView

urlpatterns = [
    path('sirius/users/<int:device_id>/firmware_hex', FirmwareHexUploadView.as_view(), name='firmware-hex-update'),
    path('sirius/devices/<int:device_id>/firmware_hex', FirmwareHexUploadView.as_view(), name='firmware-hex-update'),
    path('sirius/users/<int:device_id>/firmware_chp', FirmwareChpUploadView.as_view(), name='firmware-chp-update'),
    path('sirius/devices/<int:device_id>/firmware_chp', FirmwareChpUploadView.as_view(), name='firmware-chp-update'),
    path('sirius/users/<int:device_id>/update', WebClientUploadView.as_view(), name='web-client-update'),
    path('sirius/devices/<int:device_id>/update', WebClientUploadView.as_view(), name='web-server-update'),
    path('sirius/users/<int:device_id>/live_view', WebClientUploadView.as_view(), name='live-view-update'),
    path('sirius/devices/<int:device_id>/live_view', WebClientUploadView.as_view(), name='live-view-upload'),
]
