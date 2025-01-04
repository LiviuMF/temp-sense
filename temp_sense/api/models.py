import logging
import sys
from datetime import date

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import chirpstack, utils

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class DeviceReading(models.Model):
    batv = models.CharField(max_length=50)
    bat_status = models.CharField(max_length=50)
    ext_sensor = models.CharField(max_length=50)
    hum_sht = models.CharField(max_length=50)
    tempc_ds = models.CharField(max_length=50)
    tempc_sht = models.CharField(max_length=50)
    dev_eui = models.ForeignKey(
        "DeviceData",
        on_delete=models.SET_NULL,
        related_name="device_readings",
        null=True,
    )
    timestamp = models.DateTimeField()
    legacy_id = models.CharField(max_length=50)

    class Meta:
        db_table = "device_reading"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.dev_eui}"

    @staticmethod
    def get_all_device_health_since_date(
        since_date: date = utils.get_yesterday(),
    ) -> dict:
        readings = DeviceReading.objects.filter(timestamp__gte=since_date)
        if readings.exists():
            actual_readings = {}
            for reading in readings:
                timestamp = reading.timestamp.strftime("%Y-%m-%d-%H")
                dev_eui_id = DeviceData.objects.get(id=reading.dev_eui_id).__str__()
                if dev_eui_id in actual_readings:
                    if timestamp not in actual_readings[dev_eui_id]:
                        actual_readings[dev_eui_id].append(timestamp)
                else:
                    actual_readings[dev_eui_id] = [timestamp]

            possible_readings = (
                1
                + (  # +1 is to take into account the readings of the current hour
                    utils.get_current_time() - since_date
                ).total_seconds()
                // 3600
            )  # one reading per hour
            return {
                k: round(len(v) / possible_readings * 100, 0)
                for k, v in actual_readings.items()
            }


class DeviceData(models.Model):
    dev_eui = models.CharField(max_length=50, unique=True)
    dev_join_eui = models.CharField(max_length=50)
    dev_app_key = models.CharField(max_length=50)
    dev_nwk_key = models.CharField(max_length=50, null=True, blank=True)
    dev_name = models.CharField(max_length=100)
    dev_owner = models.CharField(max_length=100)
    dev_owner_email = models.CharField(max_length=200)
    dev_owner_address = models.CharField(max_length=100)
    dev_normal_temp = models.CharField(max_length=10)
    dev_max_accepted_temp = models.CharField(max_length=10)

    def clean(self, *args, **kwargs):
        self.dev_eui = str(self.dev_eui).lower()
        self.dev_join_eui = str(self.dev_join_eui).lower()

    @staticmethod
    def devices_without_readings_in_the_last_hour():
        return DeviceData.objects.exclude(
            device_readings__timestamp__gte=utils.one_hour_ago()
        ).distinct()

    class Meta:
        db_table = "device_data"

    def __str__(self):
        return f"{self.dev_owner}_{self.dev_name}".upper()


@receiver(post_save, sender=DeviceData)
def create_chirpstack_entity(sender, instance, created, **kwargs):
    if created:
        chirpstack.create_device(
            dev_eui=instance.dev_eui,
            dev_name=f"{instance.dev_owner}_{instance.dev_name}",
            dev_join_eui=instance.dev_join_eui,
        )
        logger.info("Created chirpstack entity")

        chirpstack.register_device(
            dev_eui=instance.dev_eui,
            dev_app_key=instance.dev_app_key,
            dev_nwk_key=instance.dev_nwk_key,
        )
        logger.info("Registered chirpstack entity")
