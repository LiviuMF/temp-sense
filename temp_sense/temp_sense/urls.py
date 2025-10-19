from api import views
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"readings", views.DeviceReadingViewSet, basename="reading")
router.register(r"devices", views.DeviceDataViewSet, basename="device")
router.register(r"owners", views.DeviceOwnerViewSet, basename='owner')
router.register(r"reports", views.HACCPReportViewSet, basename="report")

urlpatterns = [
    path("api/", include(router.urls)),
    path("login/", views.LoginView.as_view()),
    path('', views.index),
    path("admin", admin.site.urls),
]
