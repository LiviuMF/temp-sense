from django.conf import settings
from rest_framework import permissions

from .models import DeviceOwner


class IsInAllowedGroup(permissions.BasePermission):
    def has_permission(self, request, view):
        username = request.user.username.lower()
        if username in settings.API_PERMISSION_EXCEPTIONS:
            return True

        if request.method == "GET":
            allowed_groups = ["api"]
            obj = DeviceOwner.objects.filter(email__contains=username).first()
            if obj:
                user_groups = request.user.groups.values_list("name", flat=True)
                if (
                        any(group in allowed_groups for group in user_groups)
                ):
                    return True

        return False
