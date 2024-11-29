from api.discord import send_message
from api.models import DeviceData, DeviceReading
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        devices_without_readings = (
            DeviceData.devices_without_readings_in_the_last_hour()
        )
        if devices_without_readings:
            full_message = [f'{35 * "="}']
            for device in devices_without_readings:
                latest_timestamp: str = (
                    DeviceReading.objects.filter(dev_eui=device)
                    .latest("timestamp")
                    .timestamp.strftime("%H:%M")
                )

                device_name_length = len(device.__str__())
                full_message.append(
                    f'{device}{(40 - device_name_length) * "."}{latest_timestamp}'
                )
            message = "\n".join(full_message)
            send_message(
                f'{35 * "="}\n         ❗Devices without readings❗    {message}'
            )
        else:
            send_message(
                f'{35 * "="}\n        ✅     ~Systems functional~     ✅\n{35 * "="}'
            )
