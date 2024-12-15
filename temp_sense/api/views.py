from datetime import datetime

from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from . import utils
from .models import DeviceData, DeviceReading
from .permissions import IsInAllowedGroup
from .serializers import DeviceDataSerializer, DeviceReadingSerializer


def index(request):
    return HttpResponse("Battlecruiser Operational")


@permission_classes((IsAuthenticated, IsInAllowedGroup))
def device_health(request):
    if request.method == "GET":
        since_date = request.GET.get("since_date", utils.get_yesterday().isoformat())
        devices_health = DeviceReading.get_all_device_health_since_date(
            datetime.strptime(since_date, "%Y-%m-%d")
        )
        if devices_health:
            devices_health_cleaned = {"data": [{str(d): h} for d, h in devices_health]}

            return JsonResponse(devices_health_cleaned)
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
