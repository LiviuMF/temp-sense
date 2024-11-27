from datetime import datetime, timedelta

from django.contrib import admin
from django.utils.html import format_html

from .models import DeviceData, DeviceReading

NOW = datetime.now()
last_hour = datetime.now() - timedelta(hours=1)


class DeviceDataAdmin(admin.ModelAdmin):
    list_display = ("dev_owner", "dev_name", "no_readings")

    def no_readings(self, device_data_obj):
        devices_with_readings_in_the_last_hour = DeviceData.objects.filter(
            device_readings__timestamp__gte=last_hour
        ).distinct()
        if device_data_obj not in devices_with_readings_in_the_last_hour:
            latest_reading = (
                DeviceReading.objects.filter(dev_eui=device_data_obj)
                .order_by("-timestamp")
                .first()
                .timestamp.strftime("%H:%M")
            )
            return format_html(
                '<span style="color: red; font-weight: bold;">{}</span>',
                f"No readings in the last hour, latest reading at: {latest_reading}",
            )

    no_readings.short_description = "No Readings"


class DeviceReadingAdmin(admin.ModelAdmin):
    list_display = ("dev_eui", "timestamp")
    ordering = ("-id",)


admin.site.register(DeviceData, DeviceDataAdmin)
admin.site.register(DeviceReading, DeviceReadingAdmin)
admin.site.site_header = "LemonGrass Tech"
admin.site.site_title = "Temperature sensors"
admin.site.index_title = "Welcome to the device management portal"
