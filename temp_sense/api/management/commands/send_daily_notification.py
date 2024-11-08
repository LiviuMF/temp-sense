from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Max
from django.db.models.functions import TruncHour

from datetime import datetime, timedelta

from api.models import DeviceData, DeviceReading
from api import mail


class Command(BaseCommand):
    help = 'Send daily notification on latest 24h device readings'

    def handle(self, *args, **kwargs):
        dev_owners = DeviceData.objects.all().values_list('dev_owner', flat=True).distinct()
        for owner in dev_owners:
            attachment_details: list[tuple] = []
            owner_devices: list[DeviceData] = DeviceData.objects.filter(dev_owner=owner)
            for device in owner_devices:
                sensor_data = (((((((
                    DeviceReading.objects.filter(dev_eui=device)
                    .filter(date__gte=(datetime.now() - timedelta(days=1)).date()))
                    .annotate(hour=TruncHour('time')))
                    .values('date', 'hour'))
                    .annotate(time=Max('time')))
                    .order_by('-date', '-hour'))
                    .distinct())
                    .values('date', 'time', 'tempc_ds')
                )[:24]
                if sensor_data:
                    pdf_table = mail.plot_report(
                        data=sensor_data,
                        client_name=owner,
                        client_address=device.dev_owner_address,
                        device_name=device.dev_name,
                    )
                    attachment_details.append((pdf_table, device))
                else:
                    print(f'Device {device.dev_eui} has not sent any data yet')
                    continue
            owner_details = DeviceData.objects.get(dev_owner=owner)
            message = mail.build_message_body(
                to_email=owner_details.dev_owner_email,
                subject=f'Hourly temperature for {owner_details.dev_owner}',
                message_body='This is an email from Horepa.ro with hourly temperature',
                attachments=attachment_details,
            )
            mail.send_email(to_email=settings.ADMIN_EMAIL, message_body=message)

        self.stdout.write(self.style.SUCCESS('Successfully sent notifications'))
