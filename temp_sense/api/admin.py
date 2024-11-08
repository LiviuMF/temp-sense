from django.contrib import admin
from .models import DeviceData, DeviceReading


admin.site.register(DeviceData)
admin.site.register(DeviceReading)
