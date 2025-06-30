from django.contrib import admin
from apps.feed.models import Follow, Post, Comment, Reaction, Bookmark


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "followed", "created_date")
    search_fields = ("follower__username", "followed__username")
    list_filter = ("created_date",)
    ordering = ("-created_date",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "short_body", "post_type", "created_date")
    search_fields = ("author__username", "body")
    list_filter = ("is_pinned", "created_date")
    readonly_fields = ("reactions_count", "comments_count", "reposts_count")
    ordering = ("-created_date",)

    def short_body(self, obj):
        return (obj.body[:30] + "...") if obj.body and len(obj.body) > 30 else obj.body
    short_body.short_description = "Body"

    def post_type(self, obj):
        if obj.is_quote:
            return "QUOTE"
        elif obj.is_repost:
            return "REPOST"
        return "ORIGINAL"
    post_type.short_description = "Type"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post__id", "short_body", "created_date")
    search_fields = ("author__username", "body", "post__id")
    list_filter = ("created_date",)
    ordering = ("-created_date",)

    def short_body(self, obj):
        return (obj.body[:30] + "...") if len(obj.body) > 30 else obj.body
    short_body.short_description = "Comment"


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_date")
    search_fields = ("user__username", "post__id")
    list_filter = ("created_date",)
    ordering = ("-created_date",)


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_date")
    search_fields = ("user__username", "post__id")
    list_filter = ("created_date",)
    ordering = ("-created_date",)
