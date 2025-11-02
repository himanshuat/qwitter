from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Allow full access to object owners; read-only for others.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # For objects with an 'author' or 'user' field
        return getattr(obj, "author", getattr(obj, "user", None)) == request.user


class DisallowDelete(BasePermission):
    """
    Completely disallow DELETE requests for protected resources.
    """
    def has_permission(self, request, view):
        return request.method != "DELETE"


class IsAdminOrReadOnly(BasePermission):
    """
    Allow full access to admins; read-only for all others.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsSelfOrAdmin(BasePermission):
    """
    Allow users to access or modify their own data, or admin access.
    """
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj == request.user
