from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, extend_schema_view
from drf_spectacular_websocket.decorators import extend_ws_schema
from drf_spectacular_websocket.settings import SWAGGER_UI_SETTINGS
from rest_framework import status
from rest_framework.response import Response
from app.consumers.schemas import *


#TODO Переделать описание
reveive_user_schema = extend_ws_schema(
        type='receive',
        tags=["Websockets"],
        summary="Обработка сообщений от пользователей через WebSocket",
        description="WebSocket для взаимодействия с пользователями. Позволяет пользователям отправлять сообщения",
        request= None,
        responses={
            status.HTTP_200_OK: SuccessResponseDict,
            status.HTTP_400_BAD_REQUEST: BadRequest
        },
    )

send_user_schema = extend_ws_schema(
        type='send',
        tags=["Websockets"],
        summary="Отправка сообщений пользователю через WebSocket",
        description="WebSocket для взаимодействия с устройствами. Позволяет отправлять сообщения, которые будут передаваться в группу пользователей.",
        request=SendUserMessageSerializer,
        responses={
            status.HTTP_200_OK: SuccessResponseDict,
            status.HTTP_202_ACCEPTED: SuccessResponseStr,
            status.HTTP_400_BAD_REQUEST: BadRequest
        },
    )

reveive_device_schema = extend_ws_schema(
        type='receive',
        tags=["Websockets"],
        summary="Обработка сообщений от устройства через WebSocket",
        description="WebSocket для взаимодействия с пользователями. Позволяет получать сообщения от устройств.",
        request=None,
        responses={
            status.HTTP_200_OK: SuccessResponseDict,
            status.HTTP_400_BAD_REQUEST: BadRequest
        },
    )

send_device_schema = extend_ws_schema(
        type='send',
        tags=["Websockets"],
        summary="Отправка сообщений устройству через WebSocket",
        description="WebSocket для взаимодействия с устройствами. Позволяет устройствам отправлять сообщения, которые будут передаваться в группу пользователей.",
        request=SendDeviceMessageSerializer,
        responses={
            status.HTTP_200_OK: SuccessResponseDict,
            status.HTTP_202_ACCEPTED: SuccessResponseStr,
            status.HTTP_400_BAD_REQUEST: BadRequest
        },
    )
