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
    

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "content", "post", "date", "user"]
        read_only_fields = ["id", "post", "date", "user"]

    def create(self, validated_data):
        post_id = self.context['post_id']
        user_id = self.context['user_id']
        return Comment.objects.create(post_id=post_id, user_id=user_id, **validated_data)

    def get_user(self, obj):
        user = obj.user
        
        return {
            "id": user.id,
            "username": user.username,
            "name": user.profile.name if user.profile else None,
            "image": user.profile.image if user.profile and user.profile.image else None,
        }