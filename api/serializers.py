from rest_framework import serializers
from network.models import *


class PostSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "content", "date", "ispinned", "reactions_count", "comments_count", "user", "liked", "bookmarked"]
        read_only_fields = ["id", "date", "ispinned", "reactions_count", "comments_count", "user", "liked", "bookmarked"]

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        return Post.objects.create(user_id=user_id, **validated_data)
    
    def get_user(self, obj):
        user = obj.user
        
        return {
            "id": user.id,
            "username": user.username,
            "name": user.profile.name if user.profile else None,
            "image": user.profile.image if user.profile and user.profile.image else None,
        }
    
    def get_liked(self, obj):
        if self.context['request'].user.is_authenticated:
            result = Reaction.objects.filter(post_id=obj.id, user_id=self.context['request'].user.id)
            return bool(len(result))
        return False
    
    def get_bookmarked(self, obj):
        if self.context['request'].user.is_authenticated:
            result = Bookmark.objects.filter(post_id=obj.id, user_id=self.context['request'].user.id)
            return bool(len(result))
        return False
    

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