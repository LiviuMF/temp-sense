import json
from datetime import date, datetime, timedelta

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import DeviceData, DeviceReading
from .permissions import IsInAllowedGroup
from .serializers import DeviceDataSerializer, DeviceReadingSerializer

YESTERDAY = date.today() - timedelta(days=1)


def index(request):
    return HttpResponse("Battlecruiser Operational")


def device_health(request):
    if request.method == "GET":
        since_date = request.GET.get("since_date", YESTERDAY.isoformat())
        devices_health = DeviceReading.get_all_device_health_since_date(
            datetime.strptime(since_date, "%Y-%m-%d")
        )
        if devices_health:
            devices_health_cleaned = {"data": [{str(d): h} for d, h in devices_health]}

            return HttpResponse(json.dumps(devices_health_cleaned, indent=4))
        return HttpResponse(
            "No data for given interval, default value is set to YESTERDAY"
        )


class DeviceDataViewSet(viewsets.ModelViewSet):
    queryset = DeviceData.objects.all()
    serializer_class = DeviceDataSerializer

    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated, IsInAllowedGroup]


class DeviceReadingViewSet(viewsets.ModelViewSet):
    queryset = DeviceReading.objects.all()
    serializer_class = DeviceReadingSerializer

    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated, IsInAllowedGroup]

    def get_queryset(self):
        queryset = self.queryset

        param = self.request.query_params.get("dev_eui", None)
        if param:
            dev_eui = param.lower()
            device = DeviceData.objects.get(dev_eui=dev_eui)
            queryset = queryset.filter(dev_eui=device)
        return queryset
