from enum import IntEnum, Enum
import enum
import os
from dotenv import load_dotenv

load_dotenv()

class LKType(IntEnum):
    KD = 1
    SIRIUS = 2
    SIGNAL = 3
    VCI_CAMERA = 4
    PGE = 5


class LKStatus(IntEnum):
    DISABLED: int = 1
    NORMAL: int = 2
    ALARM: int = 3
    FIRE: int = 4
    FAULT: int = 5
    START: int = 6
    STOP: int = 7
    DISABLING_AUTO: int = 8
    DISABLING: int = 9
    NO_AUTH: int = 10
    AUTH: int = 11
    TAKE_DELAY: int = 12
    INIT: int = 13


class LKApi():

    LK_BOLID_URL = os.getenv("LK_BOLID_URL")
    LK_API_KEY = os.getenv("LK_API_KEY")
    LK_SIRIUS_PATH = os.getenv("LK_SIRIUS_PATH")

    token_verify: str = LK_BOLID_URL + "/auth/jwt/verify/"
    token_refresh: str = LK_BOLID_URL + "/auth/jwt/refresh/"

    post_device_registry: str = LK_BOLID_URL + "/devices/registry/"
    patch_device_local: str = LK_BOLID_URL + "/devices/{device_id}/local/"
    post_device: str = LK_BOLID_URL + "/devices/"
    get_all_devices: str = LK_BOLID_URL + "/devices/"
    get_device_by_id: str = LK_BOLID_URL + "/devices/{device_id}/"
    patch_device_by_id: str = LK_BOLID_URL + "/devices/{device_id}/"
    delete_device_by_id: str = LK_BOLID_URL + "/devices/{device_id}/"
    
