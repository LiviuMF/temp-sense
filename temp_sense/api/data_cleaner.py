from datetime import datetime, timedelta

from .models import DeviceData


def process_payload(payload: dict) -> dict:
    device_data_instance = DeviceData.objects.get(
        dev_eui=payload["deviceInfo"]["devEui"]
    )
    cleaned_data: dict = payload["object"]
    cleaned_data.update(
        {
            "dev_eui": device_data_instance,
            "timestamp": convert_timestamp_to_current_tz(payload["time"]),
            "legacy_id": payload["deviceInfo"]["devEui"],
        }
    )
    return {k.lower(): v for k, v in cleaned_data.items()}


def convert_timestamp_to_current_tz(timestamp: str) -> datetime:
    timestamp_cleaned = timestamp.split(".")[0]
    timestamp_as_datetime: datetime = datetime.strptime(
        timestamp_cleaned, "%Y-%m-%dT%H:%M:%S"
    )
    tz_diff: timedelta = datetime.now() - timestamp_as_datetime
    tz_hour_diff: int = round(tz_diff.total_seconds() / 3600)
    return timestamp_as_datetime + timedelta(hours=tz_hour_diff)
