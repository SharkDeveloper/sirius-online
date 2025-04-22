from enum import Enum
from datetime import datetime

from asgiref.sync import sync_to_async
import requests

from ..models import Device
from .consts import LKType, LKApi, LKStatus

class TokensNames(Enum):
    ACCESS_TOKEN = "access"
    REFRESH_TOKEN = "refresh"


class TokensStore:
    #TODO получать refresh и access из фронта
    DEFAULT_REFRESH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0MTkzOTQ2NSwiaWF0IjoxNzM2NzU1NDY1LCJqdGkiOiIwNmExYmMwMTIzNjY0MTZhOGE0YzIyMWYxYWQ3NzMzZiIsInVzZXJfaWQiOjF9.ov5Y8KfeEk5Mo2QAHcuIyUesUS3lninjG4PY5Mbcucg"
    def __init__(self) -> None:
        self.access_token = None
        self.refresh_token = None     

    def get_access_token(self) -> str:
        return self.access_token

    def get_refresh_token(self) -> str:
        return self.refresh_token


class LKRequestSender(TokensStore):
    lk_verify_url = LKApi.token_verify
    lk_refresh_url = LKApi.token_refresh
    lk_device_update = LKApi.patch_device_by_id
    lk_device_create = LKApi.post_device
    lk_device_delete = LKApi.delete_device_by_id
    lk_get_all_devices = LKApi.get_all_devices
    lk_device_refistry = LKApi.post_device_registry
    lk_device_local = LKApi.patch_device_local

    home_path = LKApi.LK_SIRIUS_PATH

    common_headers = {"Content-Type": "application/json", "Accept": "application/json"}

    api_headers = common_headers | {"X-API-KEY": LKApi.LK_API_KEY} 

    def __init__(self):
        super().__init__()

    def check_token(self) -> bool:
        if not self.refresh_token:
            self.refresh_token = self.DEFAULT_REFRESH_TOKEN
        self.refresh(self.refresh_token)

    def verify(self, access_token: str) -> int:
        verify_request = requests.post(
            url=self.lk_verify_url,
            headers=self.common_headers,
            json={"token": access_token},
        )
        return verify_request

    def refresh(self, refresh_token: str) -> int:
        refresh_request = requests.post(
            url=self.lk_refresh_url,
            headers=self.common_headers,
            json={"refresh": refresh_token},
        )
        if refresh_request.status_code == 200:
            self.access_token = refresh_request.json().get("access")
            print("Access token refreshed")
        print("Refresh token verify: ", refresh_request.status_code)
        return refresh_request

    def registry_device_in_lk(self, device_id: int):
        response = requests.post(
            url=self.lk_device_refistry,
            headers=self.api_headers,
            json={
                "id_dev": device_id,
                "type": LKType.SIRIUS
            },
        )
        print("Device registry in LK:", response.status_code)
        if response.status_code != 200:
            print(response.json())
        return response

    def create_device_in_lk(self, lk_device_id: int, device_id: int, name: str, is_active: bool,  device_status: int):
        headers = self.api_headers | {"Authorization": "JWT " + self.get_access_token()}
        response = requests.post(
            url=self.lk_device_create,
            headers=headers,
            json=
            {
                #"id": lk_device_id,
                "id_dev": device_id,
                "name": name,
                "status": device_status,
                "type_num": LKType.SIRIUS,
                "is_active": is_active,
                "device_info": {
                    "start_zones": 0,
                    "fire_zones": 0,
                    "fault_zones": 0,
                    "disableauto_zones": 0
                },
                "facilities": [],
                "last_connection": "2025-03-03T07:13:44.400518+03:00",#last_connection.isoformat(), #ToDo добавить дату последнего подключения
                "connection_type": "Ethernet"
            },
        )
        print("Device created in LK:", response.status_code)
        if response.status_code != 200:
            print(response.json())
        return response

    def update_device_in_lk(self, lk_device_id: int, device_id: int, name: str, is_active: bool, device_status: int):
        response = requests.patch(
            url=self.lk_device_local.format(device_id=device_id),
            headers=self.api_headers,
            json=
            {
                "id_dev": str(device_id),
                "status": device_status,
                "type": LKType.SIRIUS,
                "is_active": is_active,
            },
        )
        print("Device updated in LK:", response.status_code)
        if response.status_code != 200 and response.status_code != 204:
            print(response.json())
        print({
                "id_dev": device_id,
                "status": device_status,
                "type": LKType.SIRIUS,
                "is_active": is_active,
            },)
        return response

    def delete_device_in_lk(self, lk_device_id: int):
        headers = self.api_headers | {"Authorization": "JWT " + self.get_access_token()}
        response = requests.delete(
            url=self.lk_device_delete.format(device_id=lk_device_id),
            headers=headers,
        )
        print("Device deleted in LK:", response.status_code)
        if response.status_code != 200:
            print(response.json())
        return response
    
    def get_all_devices_in_lk(self):
        headers = self.common_headers | {"Authorization": "JWT " + self.get_access_token()}
        response = requests.get(
            url=self.lk_get_all_devices,
            headers=headers,
        )
        print("Get all devices in LK:", response.status_code)
        if response.status_code != 200:
            print(response.json())
        return response

class LKDeviceManager(LKRequestSender):
    def __init__(self) -> None:
        super().__init__()
        self.check_token()
        self.work_error = 200
        

    async def create_device(self, Device: Device):
        self.check_token()
        response = self.create_device_in_lk(Device.lk_id, Device.device_id, Device.name, Device.is_active, LKStatus.START)
        if response.status_code == 200:
            Device.name = response.json()["name"]
            Device.lk_id = response.json()["id"]
            sync_to_async(Device.save)
        else:
            self.work_error = response.status_code

    async def registry_device(self, Device: Device):
        response = self.registry_device_in_lk(Device.device_id)
        if response.status_code != 200:
            self.work_error = response.status_code

    async def update_device(self,  Device: Device, status: int):
        self.check_token()
        Device.access_token = self.get_access_token()
        # device_data_from_lk = await self.check_device_exist(Device)
        # if device_data_from_lk == None:
        #     #await self.create_device(Device)
        #     await self.registry_device(Device)
        #     device_data_from_lk = await self.check_device_exist(Device)
        # if device_data_from_lk: 
        #     Device.lk_id = device_data_from_lk["id"]
        sync_to_async(Device.save)
        response = self.update_device_in_lk(Device.lk_id, Device.device_id, Device.name, Device.is_active, status)
        if response.status_code == 200:
            Device.name = response.json()["name"]
            Device.lk_id = response.json()["id"]
            await sync_to_async(Device.save)()
        else:
            self.work_error = response.status_code
            

    async def delete_device(self,  Device: Device):
        self.check_token()
        self.delete_device_in_lk(Device.lk_id)
        Device.lk_id = 0
        sync_to_async(Device.save)

    async def check_device_exist(self,  Device: Device):
        self.check_token()
        response = self.get_all_devices_in_lk()
        if response.status_code == 200:
            device_data_from_lk = next((device for device in response.json() if device["id_dev"] == str(Device.device_id)), None)
        print("device_data_from_lk:", device_data_from_lk)
        
        if device_data_from_lk:
            return device_data_from_lk
        else:
            return None
        
    async def check_device_status_on(self,  Device: Device):
        self.check_token()
        response = self.get_all_devices_in_lk()
        if response.status_code == 200:
            device_data_from_lk = next((device for device in response.json() if device["status"] != LKStatus.DISABLED \
                                        and device["id_dev"] == str(Device.device_id) and device["is_active"]), None)
        print("Check status on: device_data_from_lk:", device_data_from_lk)
        if device_data_from_lk:
            return device_data_from_lk
        else:
            return None
