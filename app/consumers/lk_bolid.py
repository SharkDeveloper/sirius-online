import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from ..lk.consts import LKStatus, LKType
from ..models import Device



class LKBolidConsumer(AsyncWebsocketConsumer):
    path_to_errors_log = "logs/lk_errors.log"
    type_num = LKType.SIRIUS

    async def connect(self):
        self.device_id = self.scope["url_route"]["kwargs"]["device_id"]
        self.timestamp = self.scope["url_route"]["kwargs"]["timestamp"]
        self.Device = await Device.objects.aget(device_id=self.device_id)

        await self.accept()
        print(f"LK Websocket conected, device_id={self.device_id}")

    async def disconnect(self, code=None):
        print(f"LK Websocket disconected, device_id={self.device_id}")
        pass

    async def send_response(self, method: str, params: dict):
        await self.send(text_data=json.dumps({"method": method, "params": params}))

    async def send_response_with_status(self, method: str, params: dict, status: int):
        channel_layer = get_channel_layer()
        message = {"method": "/verify_code","data":None"session": "65a875-8c5e6f230b7ae36-31992a02a"}
        print(f"Message {self.device_id} /verify_code:", message)
        await channel_layer.group_send(
            str(self.device_id)+"_device",
            {
                'type': 'send_to_device',
                'message': message
            }
        )
        await self.send(text_data=json.dumps({"method": method, "params": params,"status": status}))

    async def receive(self, text_data=None):
       method = json.loads(text_data)['method']
       params = json.loads(text_data)['params']
       match method:#TODO доделать обработку
            case "device_status":
                await self.send_response(method,{"status": LKStatus.NORMAL})
            case "verify_code":
                await self.send_response_with_status(method, {"status": 1}, 200)
            case "device_params":
                await self.create_or_update_device(status=LKStatus.NORMAL)


    async def create_or_update_device(self,  name:str  = "Сириус", status:int=LKStatus.DISABLED, is_active:bool=False):
        params = {#FIXME переделать и проверить параметры(я хз какие должны быть)
            "id_dev": self.device_id,
            "name": name,
            "status": status,
            "type_num": self.type_num,
            "is_active": is_active,
            "last_connection": "2025-03-03T07:13:44.400518+03:00", 
            "connection_type": "Ethernet"
        }
        await self.send_response("device_params", params)
