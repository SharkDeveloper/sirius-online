from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
import json
import logging

from .schemas import ReceiveUserMethodSerializer
from ..doc.ws_doc import *
from ..models import Device

# Настройка логирования
logger = logging.getLogger('app')

class UserConsumer(AsyncWebsocketConsumer):
    """Обрабодчик работы по app для пользователей"""
    #active_user_rooms = list()
    async def connect(self):
        #TODO добавить проверку на соединение с устройством
        # пользователь пытается много постучаться, а устройство еще не подключено, когда устройство подключается, комнаты уже забиты
        #проверка на одно подключение к одному устройствию
        #if self.room_group_name not in self.active_user_rooms :#and self.device_id+"_device" in channels_is_open :
        print("User try connect")
        self.room_group_name = 'users'
        self.device_id = str(self.scope["url_route"]["kwargs"]["device_id"])
        
        try:
            self.Device = await Device.objects.aget(device_id=int(self.device_id))
        except Device.DoesNotExist:
            await self.disconnect(502)
            return  
        print(f"self.Device: {self.Device}")
        print(f"self.device_id: {self.device_id}")
        print(f"self.Device.is_active: {self.Device.is_active}")
        if self.Device and self.device_id and self.Device.is_active:
            print("Model device:",self.Device.is_active)
            self.room_group_name = self.device_id+"_user"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept() 
            self.access_token = self.scope["cookies"].get("access")
            self.Device.access_token = self.access_token
            sync_to_async(Device.save)
            print("User connected")
        else:
            await self.disconnect(502)


    async def disconnect(self, close_code):
        
        logger.info(f"User {self.device_id} disconnected: {close_code}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @reveive_user_schema
    async def receive(self, text_data):
        """Получение сообщения от пользователя"""
        try:
            print(f"receive message from user {self.device_id}")
            data = json.loads(text_data)
            request = ReceiveUserMethodSerializer(data=data)
            print(1)
            if request.is_valid(raise_exception=True):
                print(2)
                message = request.validated_data
                if message["method"] == "/ping":
                    print("Send 'ping' to user session:",message["session"])
                    await self.send_ping(message["session"])
                    return 
                elif message["method"] == "/offline_journal":
                    if message["data"] == True:     
                        pass
            else:
                print(3)
                raise ValueError
            print(4)
            print(self.device_id+"_device")
            await self.channel_layer.group_send(
                self.device_id+"_device",
                {
                    'type': 'send_to_device',
                    'message': message
                }
            )
        except Exception as e:
            print(5)
            print(f"Error: {e}")
            message = {"method": "", "session": "","status_code": 400}
            await self.channel_layer.group_send(
                self.device_id+"_user",
                {
                    'type': 'send_to_user',
                    'message': message
                }
            )
        

    @send_device_schema
    async def send_to_user(self, event):
        """Отправление сообщения пользователю"""
        try:
            print(f"send message to user {self.device_id}")
            message = event['message']
            data = message
            response = SendDeviceMessageSerializer(data=data)
            if response.is_valid(raise_exception=True):
                message = response.validated_data
                print(f"{message=}")
            else:
                raise ValueError
        except Exception as e:
            print(f"Error: {e}")
            message = {"method": "", "session": "","status_code": 400}
        finally:
            await self.send(json.dumps(message))

    async def send_ping(self, device_session = ""):
        message = json.dumps({"method":"/ping","session":device_session,"status_code": 200})
        await self.send(message)
        print("Send 'ping' to user:",message)
        