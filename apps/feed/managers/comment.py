from django.db import models


class CommentQuerySet(models.QuerySet):
    def for_post(self, post):
        """Get comments for a post with author details prefetched."""
        return self.filter(post=post).select_related("author").order_by("-created_date")


class CommentManager(models.Manager):
    def get_queryset(self):
        return CommentQuerySet(self.model, using=self._db)

    def for_post(self, post):
        return self.get_queryset().for_post(post)
