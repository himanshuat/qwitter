from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.accounts.api.serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    UserRegisterSerializer,
    ChangePasswordSerializer,
    ChangeEmailSerializer,
    ChangeUsernameSerializer,
    UserDeactivateSerializer
)
from apps.core.api.serializers import UserBaseSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing Qwitter users.

    Provides endpoints for:
      - Listing users (admin sees all, normal users see only themselves)
      - Retrieving user details by username
      - Managing self profile via `/users/me/` actions:
          * view, update, change password/email/username, deactivate
    """

    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "username"

    def get_serializer_class(self):
        """Select serializer dynamically based on the action."""
        
        serializer_map = {
            "list": UserListSerializer,
            "retrieve": UserDetailSerializer,
            "edit": UserUpdateSerializer,
            "register": UserRegisterSerializer,
            "change_password": ChangePasswordSerializer,
            "change_email": ChangeEmailSerializer,
            "change_username": ChangeUsernameSerializer,
            "deactivate": UserDeactivateSerializer,
            "me": UserBaseSerializer,
        }

        return serializer_map.get(self.action, super().get_serializer_class())

    def list(self, request, *args, **kwargs):
        """
        List users.

        - Admins: See all users.
        - Authenticated non-admins: See only their own details.
        """
        if request.user.is_staff:
            queryset = self.get_queryset()
        else:
            queryset = self.get_queryset().filter(id=request.user.id)

        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        """
        Retrieve details of the currently authenticated user.
        """
        serializer = self.get_serializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["patch"], url_path="me/edit")
    def edit(self, request):
        """
        Update profile information of the current authenticated user.
        """
        serializer = self.get_serializer(request.user, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(partial=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["post"], url_path="register", permission_classes=[AllowAny])
    def register(self, request):
        """
        Register a new user account and return JWT tokens.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        tokens = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

        user_data = UserBaseSerializer(user, context={"request": request}).data
        return Response(
            {"user": user_data, "tokens": tokens},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="me/change-password")
    def change_password(self, request):
        """
        Change the current user's password.
        """
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="me/change-email")
    def change_email(self, request):
        """
        Change the current user's email address.
        """
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Email updated successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="me/change-username")
    def change_username(self, request):
        """
        Change the current user's username.
        """
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Username updated successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="me/deactivate")
    def deactivate(self, request):
        """
        Deactivate the current user's account (soft delete).
        """
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Account deactivated successfully."}, status=status.HTTP_200_OK)
