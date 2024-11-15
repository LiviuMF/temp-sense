from django.contrib import admin
from .models import DeviceData, DeviceReading


class ReadingsAdmin(admin.ModelAdmin):
    list_display = ('dev_eui', 'timestamp')
    ordering = ('-id', )


admin.site.register(DeviceData)
admin.site.register(DeviceReading, ReadingsAdmin)
admin.site.site_header = "LemonGrass Tech"
admin.site.site_title = "Temperature sensors"
admin.site.index_title = "Welcome to the device management portal"
