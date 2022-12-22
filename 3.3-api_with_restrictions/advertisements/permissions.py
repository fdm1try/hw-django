from rest_framework.permissions import BasePermission


class CanModerate(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True
        return bool(request.user and request.user == obj.creator or request.user.is_staff)
