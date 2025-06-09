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
            timestamp__gte=utils.minutes_ago(
                settings.TEMP_BREACH_OBSERVATION_WINDOW
            ),
            tempc_ds__gte=F("dev_eui__dev_max_accepted_temp")
        ).values_list(
            "dev_eui__dev_owner__name",
            "dev_eui__dev_owner__email",
            "dev_eui__dev_name",
            "dev_eui__dev_max_accepted_temp",
            "tempc_ds",
            "timestamp",
        ).order_by('-timestamp')

        dev_breach = {}
        for reading in devs_with_temp_breach:
            owner, owner_email, dev_name, max_temp, recent_temp, timestamp = reading
            if owner in dev_breach:
                dev_breach[owner]['counter'] += 1
                dev_breach[owner]['data'].append(reading)
                if dev_name not in dev_breach[owner]['data'][-1][2]:
                    dev_breach[owner]['data'].append(reading)
            else:
                dev_breach[owner] = {
                        'counter': 1,
                        'data': [reading],
                    }

        if (
                (
                    len(dev_breach.items()) == 1 and
                    list(dev_breach.items())[0][1]['counter'] >= settings.MAX_READING_BREACHES
                ) or
                (len(dev_breach.items()) >= settings.MAX_READING_BREACHES)
        ):

            dev_and_owner = []
            for owner, data in dev_breach.items():
                dev_and_owner.extend(
                    [
                        '_'.join(
                            (owner,dev_name))
                    for owner, emails, dev_name, max_temp, temp, timestamp in data['data']])
                devices = [dev_name for owner, emails, dev_name, max_temp, temp, timestamp in data['data']]
                emails = [emails for owner, emails, dev_name, max_temp, temp, timestamp in data['data']]

                message = mail.build_message_body(
                    to_email=','.join(emails[0].split(',')),
                    subject=f"Temp limit breach {owner}: {','.join(devices)}",
                    message_body=build_html_message(owner, data['data']),
                    to_html=True,
                )
                breakpoint()
                mail.send_email(
                    to_email=emails[0].split(','),
                    message_body=message
                )

            notification_message = "\n".join(set(dev_and_owner))
            discord.send_message(f"Temp limit breach >1/h on devices:" f"\n {notification_message}")
            logger.info("Successfully sent discord notification")

        else:
            logger.info("\n No temp limit breach")


def build_html_message(dev_owner: str, devices: list):
    with open('api/media/temp_breach_email_notification.html', 'r') as html_file:
        device_datas = []
        for owner, owner_email, dev_name, max_temp, recent_temp, timestamp in devices:
            device_tags = '<td>' + '</td><td>'.join((dev_name, str(recent_temp), str(max_temp), str(timestamp))) + '</td>'
            device_datas.append(device_tags)

        html_text = html_file.read()
        devices_with_html_tags = '<tr>' + '</tr><tr>\n'.join(device_datas) + '</tr>'

        html_text = html_text.replace(
            '{{client_name}}', dev_owner
        ).replace(
            '{{temp_breach_devices}}', f'<tr>{devices_with_html_tags}</tr>'
        )
        return html_text
