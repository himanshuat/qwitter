from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


class QwitterTokenObtainPairView(TokenObtainPairView):
    """Obtain JWT access and refresh tokens."""
    pass


class QwitterTokenRefreshView(TokenRefreshView):
    """Refresh JWT access token."""
    pass


class QwitterTokenVerifyView(TokenVerifyView):
    """Verify JWT token validity."""
    pass
