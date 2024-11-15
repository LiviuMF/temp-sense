from datetime import datetime, timedelta
from .models import DeviceData, DeviceReading


def process_payload(payload: dict) -> dict:
    device_data_instance = DeviceData.objects.get(
        dev_eui=payload["deviceInfo"]["devEui"])
    cleaned_data: dict = payload["object"]
    cleaned_data.update(
        {
            "dev_eui": device_data_instance,
            "timestamp": payload["time"],
            "legacy_id": payload["deviceInfo"]["devEui"],
        }
    )
    return {k.lower(): v for k, v in cleaned_data.items()}

