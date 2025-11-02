from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.accounts.models import User
from apps.core.api.serializers import UserBaseSerializer


class UserListSerializer(UserBaseSerializer):
    """
    Serializer for listing users.
    Shows basic user details along with limited administrative metadata.
    """

    class Meta(UserBaseSerializer.Meta):
        model = User
        fields = UserBaseSerializer.Meta.fields + (
            "is_active",
            "email",
            "date_joined",
            "is_staff",
        )


class UserDetailSerializer(UserBaseSerializer):
    """
    Serializer for retrieving detailed user profiles.
    Includes profile info, stats, and relationship metadata.
    """

    is_following = serializers.SerializerMethodField()
    following_count = serializers.IntegerField(source="following.count", read_only=True)
    followers_count = serializers.IntegerField(source="followers.count", read_only=True)
    posts_count = serializers.IntegerField(source="posts.count", read_only=True)

    class Meta(UserBaseSerializer.Meta):
        model = User
        fields = UserBaseSerializer.Meta.fields + (
            "dob",
            "bio",
            "is_active",
            "is_following",
            "is_staff",
            "date_joined",
            "following_count",
            "followers_count",
            "posts_count",
        )

    def get_is_following(self, obj):
        """Return True if the authenticated user follows this user."""
        
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.followers.filter(follower=request.user).exists()


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.

    - The `avatar` field is a writable alias for the internal `image` field.
    - When provided, its value updates `image`, while still returning the computed `avatar` URL.
    """

    avatar = serializers.URLField(required=False)

    class Meta:
        model = User
        fields = ("name", "bio", "dob", "avatar")

    def update(self, instance, validated_data):
        avatar_value = validated_data.pop("avatar", None)
        if avatar_value:
            instance.image = avatar_value
        return super().update(instance, validated_data)


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new users.
    Accepts username, email, name, and password.
    """

    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "name", "password")

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value.lower()

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User(
            username=validated_data["username"].lower(),
            email=validated_data["email"].lower(),
            name=validated_data["name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for securely changing the user's password.

    Validates the current password and ensures the new one meets Django’s password policies.
    """

    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class ChangeEmailSerializer(serializers.Serializer):
    """
    Serializer for changing the user's email address.

    Requires the current password and ensures the new email is unique.
    """

    new_email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context["request"].user
        if not user.check_password(data["password"]):
            raise serializers.ValidationError({"password": "Incorrect password."})
        if User.objects.filter(email__iexact=data["new_email"]).exists():
            raise serializers.ValidationError({"new_email": "Email already in use."})
        return data

    def save(self):
        user = self.context["request"].user
        user.email = self.validated_data["new_email"].lower()
        user.save()
        return user


class ChangeUsernameSerializer(serializers.Serializer):
    """
    Serializer for changing the user's username.

    Requires password validation and ensures the new username is unique.
    """

    new_username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context["request"].user
        if not user.check_password(data["password"]):
            raise serializers.ValidationError({"password": "Incorrect password."})
        if User.objects.filter(username__iexact=data["new_username"]).exists():
            raise serializers.ValidationError({"new_username": "Username already taken."})
        return data

    def save(self):
        user = self.context["request"].user
        user.username = self.validated_data["new_username"].lower()
        user.save()
        return user


class UserDeactivateSerializer(serializers.Serializer):
    """
    Serializer for deactivating a user account (soft delete).

    The user must confirm their password.
    """

    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect password.")
        return value

    def save(self):
        user = self.context["request"].user
        user.is_active = False
        user.save()
        return user
