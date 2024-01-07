from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission

from users.models import User, BRAND_MANAGER
from .models import Employee

class IsEmployee(BasePermission):
    """
    Allows access only to employees.
    """

    def has_permission(self, request, view):
        try:
            employee = User.objects.get(username=request.user.username, user_roles="employee")
            return bool(request.user and employee.username)
        except:
            raise ValidationError({
                "success": False,
                "message": "User didn't match"
            })

class IsBrandManager(BasePermission):
    """
    Allows access only to employees.
    """

    def has_permission(self, request, view):
        try:
            user = User.objects.get(username=request.user.username, user_roles=BRAND_MANAGER)
            return bool(request.user and user.username)
        except:
            raise ValidationError({
                "success": False,
                "message": "User didn't match"
            })
