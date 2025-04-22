from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from .models import Device
from .serializers import DeviceSerializer
from .forms import UpdateWebForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse, HttpResponseRedirect, FileResponse
from django.core.files.base import ContentFile
import requests
from requests.auth import HTTPProxyAuth
from django.shortcuts import redirect
from channels.layers import get_channel_layer
import json
from asgiref.sync import async_to_sync


#TODO добавить сохранение файла с таким же, названием как пришел
class FirmwareHexUploadView(generics.UpdateAPIView):
    @action(detail=False, methods=["post"], url_path="sirius/users/<int:device_id>/firmware_hex")
    def post(self, request, *args, **kwargs):
        device_id = kwargs.get('device_id')
        session = str(request.GET.get('session'))
        firmware_hex_file = request.body
        print("view device_id:", device_id)
        print("view session:", session)

        try:
            # Проверка наличия обязательных параметров
            if  not all([device_id, session, firmware_hex_file]):
                return JsonResponse({'status': 'Missing parameters'}, status=400)

            # Получаем или создаем устройство 
            instance, created = Device.objects.get_or_create(
                device_id=device_id,
                defaults={
                    'session': session
                }
            )

            # Удаляем старый файл если существует
            if instance.firmware_hex:
                instance.firmware_hex.delete(save=False)

            # Сохраняем новый файл
            filename = f"web_client_{device_id}.bin"  # Генерируем имя
            instance.web_client.save(
                name=filename,
                content=ContentFile(firmware_hex_file),
                save=False
            )

            # Обновляем сессию и сохраняем
            instance.session = session
            instance.save()
            
            # Отправление сообщения прибору, что надо принять прошивку
            channel_layer = get_channel_layer()
            message = {"method": "/firmware_hex", "data": None,"session": session}
            print(f"Message {device_id} /firmware_hex:", message)
            async_to_sync(channel_layer.group_send)(
                str(device_id)+"_device",
                {
                    'type': 'send_to_device',
                    'message': message
                }
            )
            return JsonResponse({'status': 'success'}, status=200)

        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="sirius/devices/<int:device_id>/firmware_hex")
    def get(self, request, *args, **kwargs):
        device_id = kwargs.get('device_id')
        session = request.GET.get('session')
        instance = Device.objects.filter(device_id=device_id, session=session).first()
        if not instance:
            return JsonResponse({'status': 'error','message': 'Device or user not authorized'}, status=401)
        if instance.web_client:
            return FileResponse(open(instance.firmware_hex.path, 'rb'))
        else:
            return JsonResponse({'status': 'error', 'message': 'File not found'}, status=404)

class FirmwareChpUploadView(generics.UpdateAPIView):
    @action(detail=False, methods=["post"], url_path="sirius/users/<int:device_id>/firmware_chp")
    def post(self, request, *args, **kwargs):
        device_id = kwargs.get('device_id')
        session = str(request.GET.get('session'))
        firmware_chp_file = request.body
        print("view device_id:", device_id)
        print("view session:", session)

        try:
            # Проверка наличия обязательных параметров
            if  not all([device_id, session, firmware_chp_file]):
                return JsonResponse({'status': 'Missing parameters'}, status=400)

            # Получаем или создаем устройство 
            instance, created = Device.objects.get_or_create(
                device_id=device_id,
                defaults={
                    'session': session
                }
            )

            # Удаляем старый файл если существует
            if instance.firmware_chp:
                instance.firmware_chp.delete(save=False)

            # Сохраняем новый файл
            filename = f"web_client_{device_id}.bin"  # Генерируем имя
            instance.web_client.save(
                name=filename,
                content=ContentFile(firmware_chp_file),
                save=False
            )

            # Обновляем сессию и сохраняем
            instance.session = session
            instance.save()
            
            # Отправление сообщения прибору, что надо принять прошивку
            channel_layer = get_channel_layer()
            message = {"method": "/firmware_chp", "data": None,"session": session}
            print(f"Message {device_id}/firmware_chp:", message)
            async_to_sync(channel_layer.group_send)(
                str(device_id)+"_device",
                {
                    'type': 'send_to_device',
                    'message': message
                }
            )
            return JsonResponse({'status': 'success'}, status=200)

        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="sirius/devices/<int:device_id>/firmware_chp")
    def get(self, request, *args, **kwargs):
        device_id = kwargs.get('device_id')
        session = request.GET.get('session')
        instance = Device.objects.filter(device_id=device_id, session=session).first()
        if not instance:
            return JsonResponse({'status': 'error','message': 'Device or user not authorized'}, status=401)
        if instance.web_client:
            return FileResponse(open(instance.firmware_chp.path, 'rb'))
        else:
            return JsonResponse({'status': 'error', 'message': 'File not found'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class WebClientUploadView(View):
    #@action(detail=False, methods=["post"], url_path="sirius/users/<int:device_id>/update")
    def post(self, request, *args, **kwargs):
        device_id = kwargs.get('device_id')
        session = str(request.GET.get('session'))
        web_client_file = request.body
        print("view device_id:", device_id)
        print("view session:", session)

        try:
            # Проверка наличия обязательных параметров
            if  not all([device_id, session, web_client_file]):
                print("view device_id:", device_id)
                print("view session:", session)
                return JsonResponse({'status': 'Missing parameters'}, status=400)

            # Получаем или создаем устройство 
            instance, created = Device.objects.get_or_create(
                device_id=device_id,
                defaults={
                    'session': session
                }
            )

            # Удаляем старый файл если существует
            if instance.web_client:
                instance.web_client.delete(save=False)

            # Сохраняем новый файл
            filename = f"web_client_{device_id}.bin"  # Генерируем имя
            instance.web_client.save(
                name=filename,
                content=ContentFile(web_client_file),
                save=False
            )

            # Обновляем сессию и сохраняем
            instance.session = session
            instance.save()
            
            # Отправление сообщения прибору, что надо принять прошивку
            channel_layer = get_channel_layer()
            message = {"method": "/update", "data": None,"session": session}
            print(f"Message {device_id}/update:", message)
            async_to_sync(channel_layer.group_send)(
                str(device_id)+"_device",
                {
                    'type': 'send_to_device',
                    'message': message
                }
            )
            return JsonResponse({'status': 'success'}, status=200)

        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    #@action(detail=False, methods=["get"], url_path="sirius/devices/<int:device_id>/update")
    def get(self, request, *args, **kwargs):
        device_id = kwargs.get('device_id')
        session = request.GET.get('session')
        instance = Device.objects.filter(device_id=device_id, session=session).first()
        if not instance:
            return JsonResponse({'status': 'error','message': 'Device or user not authorized'}, status=401)
        if instance.web_client:
            return FileResponse(open(instance.web_client.path, 'rb'))
        else:
            return JsonResponse({'status': 'error', 'message': 'File not found'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class LiveViewUploadView(View):
    #@action(detail=False, methods=["post"], url_path="sirius/users/<int:device_id>/update")
    def get(self, request, *args, **kwargs):
        device_id = kwargs.get('device_id')
        session = str(request.GET.get('session'))
        live_view_panel = request.body
        try:
            # Проверка наличия обязательных параметров
            if  not all([device_id, session, live_view_panel]):
                return JsonResponse({'status': 'Missing parameters'}, status=400)

            # Получаем или создаем устройство 
            instance, created = Device.objects.get_or_create(
                device_id=device_id,
                defaults={
                    'session': session
                }
            )

            # Удаляем старый файл если существует
            if instance.live_view_panel:
                instance.live_view_panel.delete(save=False)

            # Сохраняем новый файл
            filename = f"web_client_{device_id}.bmp"  # Генерируем имя
            instance.web_client.save(
                name=filename,
                content=ContentFile(live_view_panel),
                save=False
            )

            # Обновляем сессию и сохраняем
            instance.session = session
            instance.save()
            
            # Отправление сообщения прибору, что надо принять прошивку
            channel_layer = get_channel_layer()
            message = {"method": "/live_view_panel", "data": None,"session": session}
            print(f"Message {device_id}/live_view_panel:", message)
            async_to_sync(channel_layer.group_send)(
                str(device_id)+"_device",
                {
                    'type': 'send_to_device',
                    'message': message
                }
            )
            return JsonResponse({'status': 'success'}, status=200)

        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    #@action(detail=False, methods=["get"], url_path="sirius/devices/<int:device_id>/update")
    def get(self, request, *args, **kwargs):
        device_id = kwargs.get('device_id')
        session = request.GET.get('session')
        instance = Device.objects.filter(device_id=device_id, session=session).first()
        if not instance:
            return JsonResponse({'status': 'error','message': 'Device or user not authorized'}, status=401)
        if instance.live_view_panel:
            return FileResponse(open(instance.live_view_panel.path, 'rb'))
        else:
            return JsonResponse({'status': 'error', 'message': 'File not found'}, status=404)
