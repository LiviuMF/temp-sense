from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.db.models.functions import TruncDate, JSONObject
from django.db.models import Value
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from . import utils
from .models import DeviceData, DeviceReading, HACCPReport
from .permissions import IsInAllowedGroup
from .serializers import DeviceDataSerializer, DeviceReadingSerializer, HACCPReportSerializer


def index(request):
    return HttpResponse("Battlecruiser Operational")


class LoginView(APIView):
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return HttpResponse(
            'Authentication successful',
            status=200
        )


@api_view(["GET"])
@permission_classes((IsAuthenticated, IsInAllowedGroup))
def device_health(request):
    if request.method == "GET":
        since_date = request.GET.get("since_date", utils.get_yesterday().isoformat())
        devices_health = DeviceReading.get_all_device_health_since_date(
            datetime.strptime(since_date, "%Y-%m-%d")
        )
        if devices_health:
            return JsonResponse(devices_health)
        return HttpResponse(
            "No device data exists for given interval, default is YESTERDAY"
        )


class DeviceDataViewSet(viewsets.ModelViewSet):
    queryset = DeviceData.objects.all()
    serializer_class = DeviceDataSerializer

    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_email = self.request.user.username
        queryset = self.queryset.filter(dev_owner__email__contains=user_email)
        return queryset


class DeviceReadingViewSet(viewsets.ModelViewSet):
    queryset = DeviceReading.objects.all()
    serializer_class = DeviceReadingSerializer

    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated, IsInAllowedGroup]

    def get_queryset(self):
        user_email = self.request.user.username
        user_data = {
            "email": Value(self.request.user.username),
            "first_name": Value(self.request.user.first_name),
            'last_name': Value(self.request.user.last_name)
        }
        queryset = self.queryset.filter(dev_eui__dev_owner__email__contains=user_email)

        # one day filter
        if filter_date := self.request.query_params.get('date'):
            queryset = self.queryset.annotate(
                date_only=TruncDate('timestamp')
            ).filter(
                dev_eui__dev_owner__email__contains=user_email,
                date_only=filter_date
            )

        # interval filter
        if all(
                param in self.request.query_params
                for param in ['start_date', 'end_date']
        ):
            start_date = self.request.query_params['start_date']
            end_date = self.request.query_params['end_date']
            queryset = self.queryset.filter(
                dev_eui__dev_owner__email__contains=user_email,
                timestamp__gte=datetime.strptime(start_date, "%Y-%m-%d"),
                timestamp__lte=datetime.strptime(end_date, "%Y-%m-%d"),
            )

        if dev_eui := self.request.query_params.get("dev_eui", None):
            device = DeviceData.objects.get(dev_eui=dev_eui.lower())
            queryset = queryset.filter(dev_eui=device)

        # add user data to queryset
        queryset = queryset.annotate(user_data=JSONObject(**user_data))
        return queryset


class HACCPReportViewSet(viewsets.ModelViewSet):
    queryset = HACCPReport.objects.all()
    serializer_class = HACCPReportSerializer

    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated, IsInAllowedGroup]

    def get_queryset(self):
        if self.action == 'list':
            dev_eui = self.request.query_params.get("dev_eui")
            report_date = self.request.query_params.get('report_date')

            if dev_eui and report_date:
                return self.queryset.filter(
                    device=dev_eui.lower(),
                    date=report_date
                )
            elif dev_eui and not report_date:
                return self.queryset.filter(
                    device=dev_eui.lower(),
                )
            else:
                raise ValidationError(
                    "Missing required parameters: dev_eui and/or report_date"
                )
        return self.queryset
