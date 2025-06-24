from django.db import models


class BookmarkQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user)

    def has_bookmarked(self, user, post):
        return self.filter(user=user, post=post).exists()


class BookmarkManager(models.Manager):
    def get_queryset(self):
        return BookmarkQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user)

    def has_bookmarked(self, user, post):
        return self.get_queryset().has_bookmarked(user, post)

    def add_bookmark(self, user, post):
        obj, created = self.get_or_create(user=user, post=post)
        return obj, created

    def remove_bookmark(self, user, post):
        return self.filter(user=user, post=post).delete()
