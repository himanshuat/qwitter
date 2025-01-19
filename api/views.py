from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from api.permissions import IsOwnerOrReadOnly
from network.models import *
from .serializers import *


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    lookup_field = 'id'

    @action(detail=True, methods=['post'], url_name="react", permission_classes=[IsAuthenticated])
    def react(self, request, id=None):
        post = self.get_object()
        reaction, created = Reaction.objects.get_or_create(user=request.user, post=post)

        if not created:
            reaction.delete()
            return Response({"message": "Like removed."}, status=status.HTTP_204_NO_CONTENT)

        return Response({"message": "Post liked."}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], url_name="bookmark", permission_classes=[IsAuthenticated])
    def bookmark(self, request, id=None):
        post = self.get_object()
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)

        if not created:
            bookmark.delete()
            return Response({"message": "Bookmark removed."}, status=status.HTTP_204_NO_CONTENT)

        return Response({"message": "Post bookmarked."}, status=status.HTTP_201_CREATED)

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
    

class BookmarkedPosts(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.bookmarked_posts