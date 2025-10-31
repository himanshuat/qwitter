from django.urls import path
from .views import (
    QwitterTokenObtainPairView,
    QwitterTokenRefreshView,
    QwitterTokenVerifyView,
)

app_name = "core_api"

urlpatterns = [
    path("token/", QwitterTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", QwitterTokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", QwitterTokenVerifyView.as_view(), name="token_verify"),
]
