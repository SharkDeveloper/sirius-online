from rest_framework.fields import Field
from rest_framework.serializers import (Serializer, 
                                        CharField, JSONField,IntegerField,
                                        ListField, ValidationError)
from rest_framework import serializers


class DataField(serializers.Field):
    def to_representation(self, value):
        # Преобразование значения в удобный для вывода формат
        if isinstance(value, dict):
            return value  # Если это словарь, просто возвращаем его
        elif isinstance(value, list):
            return value  # Если это список, тоже возвращаем его
        elif isinstance(value, str):
            return value  # Если это строка, возвращаем строку
        return None

    def to_internal_value(self, data):
        # Проверка входящих данных и их приведение к нужному формату
        if isinstance(data, dict):
            return data  # Если это словарь, возвращаем
        elif isinstance(data, list):
            return data  # Если это список, возвращаем
        elif isinstance(data, str):
            return data  # Если это строка, возвращаем
        raise ValidationError("Invalid input - must be a string, dictionary, or list.")


class ReceiveUserMethodSerializer(Serializer):
    """Сериализатор принимает dict"""
    method = CharField()
    data = DataField(allow_null=True,required=False)
    session = CharField(required=False)

class SendUserMessageSerializer(Serializer):
    """Сериализатор принимает dict"""
    method = CharField()
    data = DataField(allow_null=True,required=False)
    status_code = IntegerField(required=False)
    session = CharField(required=False)


class ReceiveDeviceMethodSerializer(Serializer):
    """Сериализатор принимает dict"""
    method = CharField()
    data = DataField(allow_null=True,required=False)
    status_code = IntegerField()
    session = CharField(max_length=255, allow_blank=True)

class SendDeviceMessageSerializer(Serializer):
    """Сериализатор принимает dict"""
    method = CharField()
    data = DataField(allow_null=True,required=False)
    status_code = IntegerField()
    session = CharField(max_length=255, allow_blank=True)


############ doc models ############

class BadRequest(Serializer):
    method = CharField()
    data = JSONField(default=None)
    status_code = IntegerField(default=400)
    session = CharField()

class SuccessResponseDict(Serializer):
    method = CharField()
    data = ListField()
    status_code = IntegerField(default=200)
    session = CharField()

class SuccessResponseStr(Serializer):
    method = CharField()
    data = CharField()
    status_code = IntegerField(default=200)
    session = CharField()
