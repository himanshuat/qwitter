from django.urls import path, include
from rest_framework_nested import routers
from apps.feed.api.views import PostViewSet, CommentViewSet

app_name = "feed_api"

router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="posts")

posts_router = routers.NestedDefaultRouter(router, "posts", lookup="post")
posts_router.register("comments", CommentViewSet, basename="post-comments")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(posts_router.urls)),
]
