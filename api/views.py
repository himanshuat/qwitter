from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from api.permissions import IsOwnerOrReadOnly
from network.models import *
from .serializers import *


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrReadOnly()]
        elif self.action == "list":
            return [IsAuthenticatedOrReadOnly()]
        elif self.action == "retrieve":
            return [IsOwnerOrReadOnly()]
        return super().get_permissions()
    

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'])
    
    def get_serializer_context(self):
        return { 'post_id': self.kwargs['post_id'], 'user_id': self.request.user.id }
    
    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrReadOnly()]
        elif self.action == "list":
            return [IsAuthenticatedOrReadOnly()]
        elif self.action == "retrieve":
            return [IsOwnerOrReadOnly()]
        return super().get_permissions()


class PostsFollowing(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        following = self.request.user.following_list
        return Post.objects.filter(user__in=following)