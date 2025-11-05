from django.db.models import Exists, OuterRef, Value, BooleanField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.feed.models import Post, Comment, Reaction, Bookmark, Follow
from apps.core.api.serializers import NoInputSerializer
from apps.feed.api.serializers import PostSerializer, CommentSerializer
from apps.core.api.pagination import QwitterPagination
from apps.core.api.permissions import IsOwnerOrReadOnly
from apps.feed.api.filters import PostFilter


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing posts in Qwitter.

    Supports listing, creating, updating, deleting, and interacting with posts
    (like, bookmark, pin, following feed, and bookmarks).
    """

    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = QwitterPagination
    lookup_field = "id"

    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter

    def get_queryset(self):
        """
        Optimize post queryset with author and parent prefetching.
        Annotate with `is_liked` and `is_bookmarked` to avoid N+1 queries.
        """
        queryset = (
            Post.objects.all()
            .select_related("author", "parent__author")
            .prefetch_related("reactions", "bookmarks", "comments")
        )

        request = self.request
        if request and request.user.is_authenticated:
            queryset = queryset.annotate(
                is_liked=Exists(
                    Reaction.objects.filter(user=request.user, post=OuterRef("id"))
                ),
                is_bookmarked=Exists(
                    Bookmark.objects.filter(user=request.user, post=OuterRef("id"))
                ),
            )
        else:
            queryset = queryset.annotate(
                is_liked=Value(False, output_field=BooleanField()),
                is_bookmarked=Value(False, output_field=BooleanField()),
            )

        return queryset

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        serializer_class=NoInputSerializer,
    )
    def react(self, request, id=None):
        """
        Toggle like (reaction) on a post for the authenticated user.
        """
        post = self.get_object()
        reaction, created = Reaction.objects.get_or_create(user=request.user, post=post)

        if not created:
            reaction.delete()
            return Response(
                {"success": True, "detail": "Post unliked."}, status=status.HTTP_200_OK
            )

        return Response(
            {"success": True, "detail": "Post liked."}, status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        serializer_class=NoInputSerializer,
    )
    def bookmark(self, request, id=None):
        """
        Toggle bookmark on a post for the authenticated user.
        """
        post = self.get_object()
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)

        if not created:
            bookmark.delete()
            return Response(
                {"success": True, "detail": "Post unbookmarked."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "detail": "Post bookmarked."},
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsOwnerOrReadOnly],
        serializer_class=NoInputSerializer,
    )
    def pin(self, request, id=None):
        """
        Toggle pin/unpin on a post. Only the post's author can pin it.
        """
        post = self.get_object()
        if post.author != request.user:
            return Response(
                {"success": False, "detail": "You can only pin your own posts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        post.is_pinned = not post.is_pinned
        post.save(update_fields=["is_pinned"])
        status_msg = "Post pinned." if post.is_pinned else "Post unpinned."
        return Response(
            {"success": True, "detail": status_msg}, status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="bookmarks",
    )
    def bookmarks(self, request):
        """
        Retrieve a paginated list of bookmarked posts for the current user.
        """
        bookmarked_posts = (
            self.get_queryset()
            .filter(bookmarks__user=request.user)
            .order_by("-bookmarks__created_date")
        )
        page = self.paginate_queryset(bookmarked_posts)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="following",
    )
    def following(self, request):
        """
        Retrieve a feed of posts from users that the current user follows.
        """
        following_users = Follow.objects.filter(follower=request.user).values_list(
            "followed", flat=True
        )
        posts = self.get_queryset().filter(author__in=following_users)
        page = self.paginate_queryset(posts)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        url_path="repost",
        serializer_class=NoInputSerializer,
        permission_classes=[IsAuthenticated],
    )
    def repost(self, request, id=None):
        """
        Create a repost of an existing post.
        """
        parent_post = self.get_object()

        if Post.objects.filter(
            author=request.user, parent=parent_post, body=""
        ).exists():
            return Response(
                {"success": False, "detail": "You have already reposted this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PostSerializer(
            data={},
            context={"request": request, "parent_post": parent_post},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"success": True, "detail": "Post reposted successfully."},
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="quote",
        permission_classes=[IsAuthenticated],
    )
    def quote(self, request, id=None):
        """
        Create a quote post referencing another post.
        """
        parent_post = self.get_object()

        serializer = PostSerializer(
            data=request.data,
            context={"request": request, "parent_post": parent_post},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments on posts.

    Provides endpoints for:
      - Listing comments for a post (paginated)
      - Creating new comments
      - Retrieving, updating, and deleting comments (owner-only edits)
    """

    serializer_class = CommentSerializer
    pagination_class = QwitterPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = "id"

    def get_queryset(self):
        """
        Return comments for a specific post (from nested route)
        with related author preloaded for performance.
        """
        post_id = self.kwargs.get("post_id")
        return (
            Comment.objects.filter(post_id=post_id)
            .select_related("author")
            .order_by("-created_date")
        )
