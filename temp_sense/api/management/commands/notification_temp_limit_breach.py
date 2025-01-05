import logging
from collections import Counter

from api import utils
from api.discord import send_message
from api.models import DeviceReading
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import F

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        devs_with_temp_breach = DeviceReading.objects.filter(
            timestamp__gte=utils.minutes_ago(settings.ONE_HOUR_AGO_WITH_ERROR),
            tempc_ds__gte=F("dev_eui__dev_max_accepted_temp"),
        ).values_list("dev_eui__dev_owner", "dev_eui__dev_name")

        message = Counter(devs_with_temp_breach)
        devs_with_issues = [
            "_".join(dev_name) for dev_name, k in message.items() if k > 1
        ]
        if devs_with_issues:
            discord_message = "\n".join(devs_with_issues)
            send_message(f"Temp limit breach >1/h on devices:" f"\n {discord_message}")
            logger.info("Successfully sent discord notification")
        else:
            logger.info("\n No temp limit breach")
