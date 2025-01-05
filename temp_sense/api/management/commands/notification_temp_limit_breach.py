from collections import Counter
from datetime import datetime, timedelta

from api.discord import send_message
from api.models import DeviceReading
from django.core.management.base import BaseCommand
from django.db.models import F

YESTERDAY = datetime.now() - timedelta(days=1)


class Command(BaseCommand):
    def handle(self, *args, **options):
        devs_with_temp_breach = DeviceReading.objects.filter(
            timestamp__gte=datetime.now() - timedelta(minutes=62),
            tempc_ds__gte=F("dev_eui__dev_max_accepted_temp"),
        ).values_list("dev_eui", flat=True)

        message = Counter(devs_with_temp_breach)
        devs_with_issues = {k: v for k, v in message.items() if v > 1}
        if devs_with_issues:
            send_message(f"{''.join([str(k) for k in devs_with_issues.keys()])}")
