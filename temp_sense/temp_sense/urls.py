from api import views
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"readings", views.DeviceReadingViewSet, basename="reading")
router.register(r"devices", views.DeviceDataViewSet, basename="device")

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/", include("api.urls")),
    path("admin", admin.site.urls),
]
