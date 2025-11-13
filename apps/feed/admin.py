from django.contrib import admin
from apps.feed.models import Post, Comment, Reaction, Bookmark


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "short_body", "type", "created_date")
    search_fields = ("author__username", "body")
    list_filter = ("is_pinned", "created_date")
    ordering = ("-created_date",)

    def short_body(self, obj):
        return (obj.body[:30] + "...") if obj.body and len(obj.body) > 30 else obj.body

    short_body.short_description = "Body"


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
