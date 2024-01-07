from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.conf import settings
from django.conf.urls.static import static

from users.views import LoginView, LoginRefreshView

schema_view = get_schema_view(
   openapi.Info(
      title="Rizon Web App3 Platform API",
      default_version='v1',
      description="Rizon Web App3 Platform",
      contact=openapi.Contact(email="nurmuhammadtursunov001@gmail.com"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),

    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/', LoginView.as_view()),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/refresh/', LoginRefreshView.as_view()),

    # path("api/", include("admins.urls")),
    path("api/", include("employees.urls")),
    path("api/", include("medics.urls")),
    path("api/", include("products.urls")),
    path("api/", include("users.urls")),
    path("api/", include("warehouses.urls")),
    path("api/", include("others.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
