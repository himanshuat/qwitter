from rest_framework import serializers
from apps.feed.models import Post, Comment
from apps.core.api.serializers import UserBaseSerializer


class PostBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for lightweight post representation.
    Used in nested relationships like parent posts or quotes.
    """

    author = UserBaseSerializer(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "body",
            "type",
            "created_date",
        )
        read_only_fields = (
            "id",
            "author",
            "type",
            "created_date",
        )


class PostSerializer(PostBaseSerializer):
    """
    Optimized serializer for detailed post representation, creation, and update.
    Integrates annotated fields for performance and model-level validation.
    """

    parent = PostBaseSerializer(read_only=True)

    is_liked = serializers.BooleanField(read_only=True)
    is_bookmarked = serializers.BooleanField(read_only=True)

    class Meta(PostBaseSerializer.Meta):
        model = Post
        fields = PostBaseSerializer.Meta.fields + (
            "parent",
            "is_pinned",
            "reactions_count",
            "comments_count",
            "reposts_count",
            "is_liked",
            "is_bookmarked",
        )
        read_only_fields = PostBaseSerializer.Meta.read_only_fields + (
            "parent",
            "is_pinned",
            "reactions_count",
            "comments_count",
            "reposts_count",
            "is_liked",
            "is_bookmarked",
        )

    def create(self, validated_data):
        """
        Create a new post and attach the current authenticated user.
        Validation for reposts, quotes, and originals is handled at the model level.
        """
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["author"] = request.user
        return super().create(validated_data)
