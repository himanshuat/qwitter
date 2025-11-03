from rest_framework import serializers
from apps.accounts.models import User


class UserBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for representing user information across the Qwitter API.
    """

    avatar = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ("username", "name", "avatar")


class NoInputSerializer(serializers.Serializer):
    """
    A reusable serializer for endpoints that do not require input data.

    This serializer:
    - Prevents DRF's browsable API from showing unnecessary input fields.
    - Provides a standardized response structure.
    """

    success = serializers.BooleanField(read_only=True)
    detail = serializers.CharField(read_only=True)
