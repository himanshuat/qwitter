from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from apps.core.api.throttles import AuthLoginThrottle, TokenRefreshThrottle, TokenVerifyThrottle


class QwitterTokenObtainPairView(TokenObtainPairView):
    """Obtain JWT access and refresh tokens."""
    throttle_classes = [AuthLoginThrottle]


class QwitterTokenRefreshView(TokenRefreshView):
    """Refresh JWT access token."""
    throttle_classes = [TokenRefreshThrottle]


class QwitterTokenVerifyView(TokenVerifyView):
    """Verify JWT token validity."""
    throttle_classes = [TokenVerifyThrottle]
