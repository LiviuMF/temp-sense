from django.contrib import admin

from .models import (
    DeviceData,
    DeviceReading,
    DeviceOwner,
    BulkDeviceUpload,
    HACCPReport,
)


class DeviceDataAdmin(admin.ModelAdmin):
    list_display = ("dev_name", "dev_eui", "dev_owner", 'latest_reading')

    def latest_reading(self, device_data_obj):
        device_readings = device_data_obj.device_readings
        if (device_data_obj.devices_without_readings_in_the_last_hour() and
                device_readings.exists()):
            latest_reading = (
                device_readings.order_by("-timestamp")
                .first()
                .timestamp.strftime("%d-%m-%Y %H:%M")
            )
            return f'{latest_reading}'
        else:
            return 'No readings yet'

    latest_reading.short_description = "Latest reading"


class DeviceReadingAdmin(admin.ModelAdmin):
    list_display = ("dev_eui", "timestamp", 'tempc_ds')
    list_filter = [
        'dev_eui'
    ]
    ordering = ("-id",)


class DeviceOwnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    ordering = ('name',)


class BulkDeviceUploadAdmin(admin.ModelAdmin):
    list_display = ('created_at', )


class HACCPReportAdmin(admin.ModelAdmin):
    list_display = ('device', 'date',)
    list_filter = [
        'device'
    ]


admin.site.register(DeviceData, DeviceDataAdmin)
admin.site.register(DeviceReading, DeviceReadingAdmin)
admin.site.register(DeviceOwner, DeviceOwnerAdmin)
admin.site.register(BulkDeviceUpload, BulkDeviceUploadAdmin)
admin.site.register(HACCPReport, HACCPReportAdmin)


admin.site.site_header = "LemonGrass Tech"
admin.site.site_title = "Temperature sensors"
admin.site.index_title = "Welcome to the device management portal"
