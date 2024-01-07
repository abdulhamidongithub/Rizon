from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission

from users.models import MEDIC
from .models import Medic

class IsMedic(BasePermission):
    """
    Allows access only to medic.
    """

    def has_permission(self, request, view):
        try:
            medic = Medic.objects.get(user=request.user)
            return bool(request.user and medic.user.username and medic.user.user_roles == MEDIC)
        except:
            raise ValidationError({
                "success": False,
                "message": "User didn't match"
            })
