from rest_framework import serializers

from .data_cleaner import process_readings_payload, process_device_payload
from .models import (
    DeviceData,
    DeviceReading,
    HACCPReport,
)


class DeviceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceData
        fields = "__all__"

    def to_internal_value(self, data):
        internal = super().to_internal_value(data)
        internal.update(process_device_payload(data))

        return internal


class DeviceReadingUserSerializer(serializers.ModelSerializer):
    user_data = serializers.JSONField(read_only=True)
    class Meta:
        model = DeviceReading
        all_model_fields = [
            f.name
            for f in
            DeviceReading._meta.get_fields()
        ]
        fields = all_model_fields + ['user_data']

    def to_internal_value(self, data):
        return process_readings_payload(data)


class DeviceReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceReading
        fields = '__all__'

    def to_internal_value(self, data):
        return process_readings_payload(data)


class HACCPReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = HACCPReport
        fields = "__all__"
