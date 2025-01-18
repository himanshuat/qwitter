from rest_framework import serializers
from network.models import *


class PostSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "content", "date", "ispinned", "reactions_count", "comments_count", "user"]
        read_only_fields = ["id", "date", "ispinned", "reactions_count", "comments_count", "user"]

    def get_user(self, obj):
        user = obj.user
        
        return {
            "id": user.id,
            "username": user.username,
            "name": user.profile.name if user.profile else None,
            "image": user.profile.image if user.profile and user.profile.image else None,
        }