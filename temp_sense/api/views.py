from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import DeviceData, DeviceReading
from .permissions import IsInAllowedGroup
from .serializers import DeviceDataSerializer, DeviceReadingSerializer


def index(request):
    return HttpResponse("Battlecruiser Operational")


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
