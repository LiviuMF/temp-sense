from rest_framework import permissions

from .models import DeviceData


class IsInAllowedGroup(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.username.lower() == "chirpstack":
            return True

        if (request.method == "GET") and (
            dev_eui := request.query_params.get("dev_eui")
        ):
            allowed_groups = ["api"]
            obj = DeviceData.objects.filter(dev_eui=dev_eui).first()
            if obj:
                user_groups = request.user.groups.values_list("name", flat=True)
                if (
                    any(group in allowed_groups for group in user_groups)
                    and view.get_view_name() == "Device Reading List"
                ) and obj.dev_owner.lower() == request.user.username.lower():
                    return True

        return False
