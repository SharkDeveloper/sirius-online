from django.urls import  re_path
from .consumers.users import UserConsumer
from .consumers.devices import DeviceConsumer
from .consumers.lk_bolid import LKBolidConsumer
from .consumers.lk_update_user_data import LKBolidUpdateConsumer

websocket_urlpatterns = [
    re_path(r"^sirius/users/(?P<device_id>[0-9]+)/ws$", UserConsumer.as_asgi()),
    re_path(r"^sirius/devices/(?P<device_id>[0-9]+)/ws$", DeviceConsumer.as_asgi()),
    re_path(r"^sirius/users/ws/routing/(?P<device_id>[0-9]+)-(?P<timestamp>[0-9]+)/",
                LKBolidConsumer.as_asgi()),
]
