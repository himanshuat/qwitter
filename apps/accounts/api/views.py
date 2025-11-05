from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.feed.models import Follow
from apps.core.api.pagination import QwitterPagination
from apps.core.api.permissions import IsSelfOnly
from apps.core.api.serializers import UserBaseSerializer, NoInputSerializer
from apps.accounts.api.serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    UserRegisterSerializer,
    ChangePasswordSerializer,
    ChangeEmailSerializer,
    ChangeUsernameSerializer,
    UserDeactivateSerializer,
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing Qwitter users.

    Provides endpoints for:
      - Listing users (admin sees all, normal users see only themselves)
      - Registering new accounts with JWT token response
      - Retrieving user details by username
      - Managing self profile via `/users/me/` actions:
          * view, update, change password/email/username, deactivate
      - Follow/Unfollow users
      - Retrieve followers and following lists
    """

    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "username"

    filter_backends = [SearchFilter]
    search_fields = ["username", "name"]

    def get_serializer_class(self):
        """Select serializer dynamically based on the action."""

        serializer_map = {
            "list": UserListSerializer,
            "retrieve": UserDetailSerializer,
            "register": UserRegisterSerializer,
            "me": UserBaseSerializer,
            "edit": UserUpdateSerializer,
            "change_username": ChangeUsernameSerializer,
            "change_email": ChangeEmailSerializer,
            "change_password": ChangePasswordSerializer,
            "deactivate": UserDeactivateSerializer,
            "follow": NoInputSerializer,
            "followers": UserBaseSerializer,
            "following": UserBaseSerializer,
        }

        return serializer_map.get(self.action, super().get_serializer_class())

    def list(self, request, *args, **kwargs):
        """
        List users.

        - Admins: See all users.
        - Authenticated non-admins: See only their own details.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        if request.user.is_staff:
            queryset = self.filter_queryset(self.get_queryset())
        else:
            queryset = self.filter_queryset(
                self.get_queryset().filter(id=request.user.id)
            )

        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve detailed profile information for a specific user by username.
        """
        return super().retrieve(request, *args, **kwargs)

    @action(
        detail=False,
        methods=["post"],
        url_path="register",
        permission_classes=[AllowAny],
    )
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

    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        """
        Retrieve details of the currently authenticated user.
        """
        serializer = self.get_serializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["patch"],
        url_path="me/edit",
        permission_classes=[IsSelfOnly],
    )
    def edit(self, request):
        """
        Update profile information of the current authenticated user.
        """
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(partial=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="me/change-username",
        permission_classes=[IsSelfOnly],
    )
    def change_username(self, request):
        """
        Change the current user's username.
        """
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "detail": "Username updated successfully."},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="me/change-email",
        permission_classes=[IsSelfOnly],
    )
    def change_email(self, request):
        """
        Change the current user's email address.
        """
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "detail": "Email updated successfully."},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="me/change-password",
        permission_classes=[IsSelfOnly],
    )
    def change_password(self, request):
        """
        Change the current user's password.
        """
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "detail": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="me/deactivate",
        permission_classes=[IsSelfOnly],
    )
    def deactivate(self, request):
        """
        Deactivate the current user's account (soft delete).
        """
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "detail": "Account deactivated successfully."},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="follow",
        permission_classes=[IsAuthenticated],
    )
    def follow(self, request, username=None):
        """
        Follow or unfollow a user.
        """

        target_user = self.get_object()
        if target_user == request.user:
            return Response(
                {"success": False, "detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow_qs = Follow.objects.filter(follower=request.user, followed=target_user)
        if follow_qs.exists():
            follow_qs.delete()
            return Response(
                {
                    "success": True,
                    "detail": f"You have unfollowed @{target_user.username}.",
                },
                status=status.HTTP_200_OK,
            )

        Follow.objects.create(follower=request.user, followed=target_user)
        return Response(
            {
                "success": True,
                "detail": f"You are now following @{target_user.username}.",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="followers",
        pagination_class=QwitterPagination,
        permission_classes=[AllowAny],
    )
    def followers(self, request, username=None):
        """
        Retrieve a paginated list of users who follow the specified user.
        """
        user = self.get_object()
        follower_users = User.objects.filter(following__followed=user).order_by(
            "-following__created_date"
        )

        page = self.paginate_queryset(follower_users)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        url_path="following",
        pagination_class=QwitterPagination,
        permission_classes=[AllowAny],
    )
    def following(self, request, username=None):
        """
        Retrieve a paginated list of users that the specified user is following.
        """
        user = self.get_object()
        following_users = User.objects.filter(followers__follower=user).order_by(
            "-followers__created_date"
        )

        page = self.paginate_queryset(following_users)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)
