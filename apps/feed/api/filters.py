from django_filters import rest_framework as filters
from apps.feed.models import Post


class PostFilter(filters.FilterSet):
    """
    Custom filter for posts.
    Allows filtering by author's username.
    Example: /api/posts/?author=johndoe
    """

    author = filters.CharFilter(
        field_name="author__username", lookup_expr="iexact", label="Author Username"
    )

    class Meta:
        model = Post
        fields = ["author"]
