from datetime import datetime

from api.discord import send_message
from api.models import DeviceData, DeviceReading

from django.core.management.base import BaseCommand
from django.conf import settings


def get_remaining_tokens_and_days():
    days_from_first_reading = (
            datetime.today() - DeviceReading.objects.order_by('id').first().timestamp
    ).days
    total_tokens_used = DeviceReading.objects.count() * settings.TOKEN_USAGE_PER_MESSAGE
    total_available_tokens = settings.TOTAL_AVAILABLE_TOKENS - total_tokens_used
    token_consumption_per_day = total_available_tokens / days_from_first_reading
    days_left_of_tokens = total_available_tokens / token_consumption_per_day

    return total_available_tokens, days_left_of_tokens


class Command(BaseCommand):
    def handle(self, *args, **options):
        devices_without_readings = (
            DeviceData.devices_without_readings_in_the_last_hour()
        )
        total_available_tokens, days_left_of_tokens = get_remaining_tokens_and_days()
        token_message = f'         {total_available_tokens} tokens left ({int(days_left_of_tokens)} days)         '

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
                f'{35 * "="}\n         ❗Devices without readings❗    \n{token_message}\n{message}'
            )
        else:
            send_message(
                f'{35 * "="}\n        ✅     ~Systems functional~     ✅\n{token_message}\n{35 * "="}'
            )
