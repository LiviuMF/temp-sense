from collections import Counter
import logging

from api import utils
from api import discord
from api import mail
from api.models import DeviceReading

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import F, Count

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        devs_with_temp_breach = DeviceReading.objects.filter(
            timestamp__gte=utils.minutes_ago(settings.ONE_HOUR_AGO_WITH_ERROR + 60),
            tempc_ds__gte=F("dev_eui__dev_max_accepted_temp")
        ).values_list(
            "dev_eui__dev_owner",
            "dev_eui__dev_owner_email",
            "dev_eui__dev_name",
            "dev_eui__dev_max_accepted_temp",
            "tempc_ds",
        ).order_by('-timestamp')

        dev_breach = {}
        for reading in devs_with_temp_breach:
            owner, owner_email, dev_name, max_temp, recent_temp = reading
            if owner in dev_breach:
                dev_breach[owner]['counter'] += 1
                if dev_name not in dev_breach[owner]['data'][-1][2]:
                    dev_breach[owner]['data'].append(reading)
            else:
                dev_breach[owner] = {
                        'counter': 1,
                        'data': [reading],
                    }

        if dev_breach:
            dev_and_owner = []
            for owner, data in dev_breach.items():
                dev_and_owner.extend(['_'.join((d[0], d[2])) for d in data['data']])
                devices = [d[2] for d in data['data']]
                emails = [d[1] for d in data['data']]

                message = mail.build_message_body(
                    to_email=','.join(emails),
                    subject=f"Temp limit breach {owner}: {','.join(devices)}",
                    message_body=build_html_message(owner, data['data']),
                    to_html=True,
                )

                mail.send_email(
                    to_email=emails,
                    message_body=message
                )

            notification_message = "\n".join(dev_and_owner)
            discord.send_message(f"Temp limit breach >1/h on devices:" f"\n {notification_message}")
            logger.info("Successfully sent discord notification")

        else:
            logger.info("\n No temp limit breach")


def build_html_message(dev_owner: str, devices: list):
    with open('api/media/temp_breach_email_notification.html', 'r') as html_file:
        device_datas = []
        for owner, owner_email, dev_name, max_temp, recent_temp in devices:
            device_tags = '<td>' + '</td><td>'.join((dev_name, str(recent_temp), str(max_temp))) + '</td>'
            device_datas.append(device_tags)

        html_text = html_file.read()
        devices_with_html_tags = '<tr>' + '</tr><tr>\n'.join(device_datas) + '</tr>'

        html_text = html_text.replace(
            '{{client_name}}', dev_owner
        ).replace(
            '{{temp_breach_devices}}', f'<tr>{devices_with_html_tags}</tr>'
        )
        return html_text
