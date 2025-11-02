from rest_framework import serializers
from apps.accounts.models import User


class UserBaseSerializer(serializers.ModelSerializer):
    avatar = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ("username", "name", "avatar")
