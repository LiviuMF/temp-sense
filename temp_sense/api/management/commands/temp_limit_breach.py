import logging

from api import utils
from api import discord
from api import mail
from api.models import DeviceReading, DeviceData, DeviceOwner

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import F

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        devices_with_temp_breach = (
            DeviceData.objects
            .filter(
                device_readings__timestamp__gte=utils.minutes_ago(
                    settings.TEMP_BREACH_OBSERVATION_WINDOW
                ),
                device_readings__tempc_ds__gte=F("dev_max_accepted_temp"),
                dev_stop_notification_until__lte=utils.get_current_time()
            ).distinct()
        )

        breaching_devices = [
            device
            for device in devices_with_temp_breach
            if device_has_2_consecutive_breaches(device)
        ]

        for owner in [device.dev_owner for device in breaching_devices]:
            owner_devices = [
                device
                for device in breaching_devices
                if device.dev_owner == owner
            ]
            device_names = [device.dev_name for device in owner_devices]
            message = mail.build_message_body(
                to_email=','.join(owner.email.split(',')),
                subject=f"Temp limit breach {owner.name}: {','.join(device_names)}",
                message_body=build_html_message(owner.name, owner_devices),
                to_html=True,
            )

            mail.send_email(
                to_email=owner.email.split(','),
                message_body=message
            )

            discord.send_message(f"Temp limit breach >1/h on devices:" f"\n {device_names}")
            logger.info("Successfully sent discord notification")

        else:
            logger.info("\n No temp limit breach")


def device_has_2_consecutive_breaches(device: DeviceData):
    last_2_readings = device.device_readings.order_by('-timestamp')[:2]
    cleaned_readings = clean_readings_for_probe_malfunction(last_2_readings)
    consecutive_breaches = [r for r in cleaned_readings if r >= device.dev_max_accepted_temp]
    if consecutive_breaches:
        return True
    return False


def clean_readings_for_probe_malfunction(readings):
    reading_values = readings.values_list('tempc_ds', 'tempc_sht')
    cleaned_readings = []
    for probe_reading, sensor_reading in reading_values:
        if probe_reading == settings.PROBE_MALFUNCTION_TEMP_VALUE:
            cleaned_readings.append(sensor_reading)
        else:
            cleaned_readings.append(probe_reading)
    return cleaned_readings


def build_html_message(dev_owner: str, devices: list):
    with open('api/media/temp_breach_email_notification.html', 'r') as html_file:
        device_datas = []
        for device in devices:
            device_tags = '<td>' + '</td><td>'.join(
                (
                    device.dev_name,
                    str(device.device_readings.first().tempc_ds),
                    str(device.dev_max_accepted_temp),
                    str(device.device_readings.first().timestamp)
                )
            ) + '</td>'
            device_datas.append(device_tags)

        html_text = html_file.read()
        devices_with_html_tags = '<tr>' + '</tr><tr>\n'.join(device_datas) + '</tr>'

        html_text = html_text.replace(
            '{{client_name}}', dev_owner
        ).replace(
            '{{temp_breach_devices}}', f'<tr>{devices_with_html_tags}</tr>'
        )
        return html_text
