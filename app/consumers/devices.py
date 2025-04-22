from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from django.db.utils import DatabaseError
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK,HTTP_401_UNAUTHORIZED
import logging
from asgiref.sync import sync_to_async
import time

from .schemas import ReceiveDeviceMethodSerializer, SendUserMessageSerializer
from ..doc.ws_doc import *
from ..models import Device
from ..lk.utils import LKDeviceManager
from ..lk.consts import LKStatus


# Настройка логирования
logger = logging.getLogger('app')

class DeviceConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ping_task = None
        self.last_pong_time = None

    async def connect(self):
        try:

            self.lk_manager = LKDeviceManager()
            self.device_session = ""
            origin = dict(self.scope["headers"]).get(b"origin")[4:]
            logger.critical(f"Origin: {origin}")
            mac = int(origin)
            self.device_id = str(self.scope["url_route"]["kwargs"]["device_id"])
            mac_to_id = (mac & 0x00FFFFFF) + 80_000_000
            if int(self.device_id) == mac_to_id:
                self.scope["device"] = True
                self.room_group_name = self.device_id + "_device"
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()

                # Создание или обновление объекта Device
                try:
                    self.Device, created = await sync_to_async(Device.objects.update_or_create)(
                        device_id=int(self.device_id),
                        defaults={'is_active': True}
                    )
                except DatabaseError as e:
                    print(f"Database error: {e}")
                    await self.disconnect()
                    return
                except Device.MultipleObjectsReturned as e:
                    # Получаем все записи с данным device_id
                    devices = await sync_to_async(Device.objects.aget)(device_id=int(self.device_id))
                    # Удаляем все записи, кроме первой
                    for device in devices[1:]:
                        await sync_to_async(device.delete)()
                    self.Device = devices[0]
                print("self.Device:", self.Device)

                # Обновление статуса устройства
                await self.lk_manager.registry_device(self.Device)
                await self.lk_manager.update_device(self.Device, LKStatus.NORMAL)
                if self.lk_manager.work_error >= 300:
                   await self.disconnect(self.lk_manager.work_error)
                # Запуск периодической задачи для отправки "ping"
                self.last_pong_time = asyncio.get_running_loop().time()
                self.ping_task = asyncio.create_task(self.send_ping())

                logger.critical(f"Device id: {self.device_id}")
                logger.critical("Device connected")
            else:
                logger.critical("Device not connected")
                await self.disconnect(401)
        except Exception as e:
            logger.critical(f"Error Device Consumer: {e}")
            await self.disconnect(502)

    async def disconnect(self, close_code):
        logger.info(f"Device {self.device_id} disconnected: {close_code}")
        self.Device.is_active = False
        sync_to_async(Device.save)
        self.device_session = ""
        # Отмена фоновой задачи для пинг-понга
        if self.ping_task:
            self.ping_task.cancel()
        await self.lk_manager.update_device(self.Device, LKStatus.DISABLED)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    @reveive_device_schema
    async def receive(self, text_data):
        """Получение сообщения от устройства"""
        try:
            self.last_pong_time = asyncio.get_running_loop().time()
            await self.lk_manager.update_device(self.Device, LKStatus.NORMAL)
            logger.critical(f"Device {self.device_id} send message: {text_data}")
            data = json.loads(text_data)
            request = ReceiveDeviceMethodSerializer(data=data)
            if request.is_valid(raise_exception=True):
                message = request.validated_data
            else:
                raise ValueError
            if message["method"] == "/ping":
                if message["status_code"] == HTTP_401_UNAUTHORIZED:
                    self.device_session = ""
                return
        except Exception as e:
            logger.critical(f"Error: {e}")
            message = {"method": "", "session": "", "status_code": 400}
        await self.channel_layer.group_send(
            self.device_id + "_user",
            {
                'type': 'send_to_user',
                'message': message
            }
        )

    @send_user_schema
    async def send_to_device(self, event):
        """Отправление сообщения на устройство"""
        try:
            logger.critical(f"Send message to device {self.device_id}")
            message = event['message']
            data = message
            response = SendUserMessageSerializer(data=data)
            if response.is_valid(raise_exception=True):
                message = response.validated_data
                # TODO убрать в handler
                if message["method"] == "/login":
                    self.device_session = message["data"]["session"]
                else:
                    self.device_session = message["session"]
                # device_ws_handler(message)
            else:
                raise ValueError
        except Exception as e:
            logger.critical(f"Error: {e}")
            message = {"method": "", "session": "", "status_code": 400}
        finally:
            logger.critical(f"Send message to device{self.device_id}: {json.dumps(message)}")
            await self.send(json.dumps(message))

    async def send_ping(self):
        try:
            while True:
                
                print("Разница во времени оптравки и получения пинга:", asyncio.get_running_loop().time() - self.last_pong_time)
                if asyncio.get_running_loop().time() - self.last_pong_time > 31:
                    print("No pong received for 31 seconds")
                    await self.disconnect(1013)
                    break
                # if await self.lk_manager.check_device_exist(self.Device) == None:
                #     await self.disconnect(401)
                #     break
                # if await self.lk_manager.check_device_status_on(self.Device) == None:
                #     await self.lk_manager.update_device(self.Device, LKStatus.NORMAL)
                await asyncio.sleep(10)
                message = json.dumps({"method": "/ping", "session": self.device_session})
                await self.send(message)
                ip_addr = self.scope["client"]
                logger.critical(f"Send 'ping' to device {ip_addr}: {message}")
        except Exception as e:
            logger.critical(f"Error sending ping: {e}")
            await self.disconnect(1013)
