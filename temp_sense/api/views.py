from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import DeviceData, DeviceReading
from .serializers import DeviceDataSerializer, DeviceReadingSerializer


def index(request):
    return HttpResponse("Battlecruiser Operational")


class DeviceDataViewSet(viewsets.ModelViewSet):
    queryset = DeviceData.objects.all()
    serializer_class = DeviceDataSerializer

    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]


class DeviceReadingViewSet(viewsets.ModelViewSet):
    queryset = DeviceReading.objects.all()
    serializer_class = DeviceReadingSerializer

    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset

        param = self.request.query_params.get("dev_name", None)
        if param:
            dev_owner, dev_name = param.lower().split("_")
            device = DeviceData.objects.get(
                dev_name__iexact=dev_name, dev_owner__iexact=dev_owner
            )
            queryset = queryset.filter(dev_eui=device)
        return queryset
