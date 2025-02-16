import logging
from collections import Counter

from api import utils
from api import discord
from api import mail
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
        ).values_list("dev_eui__dev_owner", "dev_eui__dev_name", "dev_eui__dev_owner_email")

        readings_counter = Counter(devs_with_temp_breach)
        devs_with_issues = [
            device
            for device, count in readings_counter.items()
            if count >= settings.MAX_READING_BREACHES_PER_HOUR
        ]

        if devs_with_issues:
            dev_and_owner = ['_'.join((d_owner, d_name)) for d_owner, d_name, _ in devs_with_issues]
            notification_message = "\n".join(dev_and_owner)
            discord.send_message(f"Temp limit breach >1/h on devices:" f"\n {notification_message}")
            logger.info("Successfully sent discord notification")

            for d_owner, d_name, d_email in devs_with_issues:
                message = mail.build_message_body(
                    to_email=d_email,
                    subject=f"Temp limit breach {d_owner}_{d_name}",
                    message_body=f"This is an email from Lemongras.ro with temp limit breach on devices \n{notification_message}",
                )

                mail.send_email(
                    to_email=d_email.split(","),
                    message_body=message
                )
        else:
            logger.info("\n No temp limit breach")
