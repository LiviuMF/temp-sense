from datetime import datetime, timedelta

from api.discord import send_message
from api.models import DeviceReading
from django.core.management.base import BaseCommand

YESTERDAY = datetime.now() - timedelta(days=1)


class Command(BaseCommand):
    def handle(self, *args, **options):
        device_health = DeviceReading.get_all_device_health_since_date(
            since_date=YESTERDAY
        )
        device_health_message = "\n".join(
            [
                f'{dev_name}{(24-len(str(dev_name))) * ".."}{round(health, 0)}%'
                for dev_name, health in device_health
                if health <= 80
            ]
        )
        send_message(device_health_message)
