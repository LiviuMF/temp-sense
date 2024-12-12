from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("device-health/", views.device_health, name="device_health"),
]
