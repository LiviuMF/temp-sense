from rest_framework import serializers

from .data_cleaner import process_payload
from .models import DeviceData, DeviceReading


class DeviceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceData
        fields = "__all__"


class DeviceReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceReading
        fields = "__all__"

    def to_internal_value(self, data):
        return process_payload(data)
