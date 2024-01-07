import django_filters
from users.models import User


class UserModelFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = (
            'user_id',
            'first_name',
            'last_name',
        )
